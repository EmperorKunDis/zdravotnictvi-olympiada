"""
LEARNING MODULE

Učení z feedbacku lékařů - continuous improvement
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import sqlite3


class FeedbackDatabase:
    """
    Databáze feedbacku od lékařů
    """

    def __init__(self, db_path: str = "feedback.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Inicializuje databázi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                patient_id TEXT NOT NULL,
                ai_priority INTEGER NOT NULL,
                physician_priority INTEGER NOT NULL,
                agreement INTEGER NOT NULL,
                physician_notes TEXT,
                patient_diagnosis TEXT,
                patient_age INTEGER,
                patient_gender TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_cases INTEGER,
                agreement_rate REAL,
                undertriage_count INTEGER,
                overtriage_count INTEGER,
                avg_response_time REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_feedback(
        self,
        patient_id: str,
        ai_decision: Dict[str, Any],
        physician_decision: Dict[str, Any],
        patient_data: Dict[str, Any] = None
    ) -> int:
        """
        Přidá feedback od lékaře

        Args:
            patient_id: ID pacienta
            ai_decision: Rozhodnutí AI
            physician_decision: Rozhodnutí lékaře
            patient_data: Dodatečná data o pacientovi

        Returns:
            ID záznamu
        """
        ai_priority = ai_decision.get("priority", 0)
        physician_priority = physician_decision.get("priority", 0)
        agreement = 1 if ai_priority == physician_priority else 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO feedback (
                timestamp, patient_id, ai_priority, physician_priority,
                agreement, physician_notes, patient_diagnosis,
                patient_age, patient_gender
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            patient_id,
            ai_priority,
            physician_priority,
            agreement,
            physician_decision.get("notes", ""),
            patient_data.get("diagnosis", "") if patient_data else "",
            patient_data.get("age", 0) if patient_data else 0,
            patient_data.get("gender", "") if patient_data else ""
        ))

        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return feedback_id

    def get_feedback_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Získá statistiky feedbacku za poslední N dní

        Args:
            days: Počet dní zpět

        Returns:
            Statistiky
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Celkový počet případů
        cursor.execute("""
            SELECT COUNT(*) FROM feedback
            WHERE date(created_at) >= date('now', '-' || ? || ' days')
        """, (days,))
        total_cases = cursor.fetchone()[0]

        # Agreement rate
        cursor.execute("""
            SELECT AVG(agreement) * 100 FROM feedback
            WHERE date(created_at) >= date('now', '-' || ? || ' days')
        """, (days,))
        agreement_rate = cursor.fetchone()[0] or 0

        # Undertriage (AI nižší priorita než lékař O 2+)
        cursor.execute("""
            SELECT COUNT(*) FROM feedback
            WHERE date(created_at) >= date('now', '-' || ? || ' days')
            AND (physician_priority - ai_priority) >= 2
        """, (days,))
        undertriage_count = cursor.fetchone()[0]

        # Overtriage (AI vyšší priorita než lékař O 2+)
        cursor.execute("""
            SELECT COUNT(*) FROM feedback
            WHERE date(created_at) >= date('now', '-' || ? || ' days')
            AND (ai_priority - physician_priority) >= 2
        """, (days,))
        overtriage_count = cursor.fetchone()[0]

        conn.close()

        return {
            "period_days": days,
            "total_cases": total_cases,
            "agreement_rate": round(agreement_rate, 1),
            "undertriage_count": undertriage_count,
            "undertriage_rate": round(undertriage_count / total_cases * 100, 1) if total_cases > 0 else 0,
            "overtriage_count": overtriage_count,
            "overtriage_rate": round(overtriage_count / total_cases * 100, 1) if total_cases > 0 else 0
        }

    def get_learning_insights(self) -> List[Dict[str, Any]]:
        """
        Získá insights pro zlepšení modelu

        Returns:
            Seznam insights
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        insights = []

        # Insight 1: Nejčastější undertriage případy
        cursor.execute("""
            SELECT patient_diagnosis, COUNT(*) as count
            FROM feedback
            WHERE (physician_priority - ai_priority) >= 2
            AND patient_diagnosis != ''
            GROUP BY patient_diagnosis
            ORDER BY count DESC
            LIMIT 5
        """)

        undertriage_patterns = cursor.fetchall()
        if undertriage_patterns:
            insights.append({
                "category": "undertriage_patterns",
                "title": "Nejčastější podhodnocené diagnózy",
                "data": [{"diagnosis": row[0], "count": row[1]} for row in undertriage_patterns],
                "recommendation": "Zvýšit váhu těchto diagnóz v modelu"
            })

        # Insight 2: Demografické biasy
        cursor.execute("""
            SELECT patient_gender,
                   AVG(CASE WHEN agreement = 1 THEN 1.0 ELSE 0.0 END) * 100 as agreement_rate,
                   COUNT(*) as count
            FROM feedback
            WHERE patient_gender != ''
            GROUP BY patient_gender
        """)

        gender_performance = cursor.fetchall()
        if len(gender_performance) > 1:
            rates = {row[0]: row[1] for row in gender_performance}
            if abs(rates.get("male", 0) - rates.get("female", 0)) > 10:
                insights.append({
                    "category": "demographic_bias",
                    "title": "Rozdíl ve výkonu podle pohlaví",
                    "data": [{"gender": row[0], "agreement_rate": row[1], "count": row[2]} for row in gender_performance],
                    "recommendation": "⚠️ MOŽNÝ BIAS - Přezkoumat výkon modelu podle pohlaví"
                })

        # Insight 3: Zlepšení v čase
        cursor.execute("""
            SELECT
                strftime('%Y-%m', created_at) as month,
                AVG(agreement) * 100 as agreement_rate
            FROM feedback
            GROUP BY month
            ORDER BY month DESC
            LIMIT 6
        """)

        trend = cursor.fetchall()
        if len(trend) >= 2:
            latest = trend[0][1]
            oldest = trend[-1][1]
            improvement = latest - oldest

            insights.append({
                "category": "learning_trend",
                "title": "Trend zlepšování",
                "data": [{"month": row[0], "agreement_rate": row[1]} for row in trend],
                "improvement": round(improvement, 1),
                "recommendation": f"{'📈 Systém se zlepšuje' if improvement > 0 else '📉 Pozor - výkon klesá'}"
            })

        conn.close()
        return insights


class AdaptiveLearning:
    """
    Adaptivní učení - úprava rozhodovacích parametrů na základě feedbacku
    """

    def __init__(self, feedback_db: FeedbackDatabase):
        self.feedback_db = feedback_db
        self.adjustments = {}

    def calculate_adjustments(self) -> Dict[str, Any]:
        """
        Vypočítá doporučené úpravy modelu na základě feedbacku

        Returns:
            Doporučené úpravy
        """
        insights = self.feedback_db.get_learning_insights()
        stats = self.feedback_db.get_feedback_stats(days=30)

        adjustments = {
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "recommended_changes": []
        }

        # Undertriage > 5% → zvýšit opatrnost
        if stats["undertriage_rate"] > 5:
            adjustments["recommended_changes"].append({
                "parameter": "escalation_threshold",
                "current": 0.7,
                "recommended": 0.6,
                "reason": f"Undertriage rate {stats['undertriage_rate']}% je nad limitem 5%",
                "impact": "Více případů bude eskalováno k lékaři"
            })

        # Overtriage > 15% → snížit senzitivitu
        if stats["overtriage_rate"] > 15:
            adjustments["recommended_changes"].append({
                "parameter": "priority_threshold",
                "current": 0.5,
                "recommended": 0.6,
                "reason": f"Overtriage rate {stats['overtriage_rate']}% je nad limitem 15%",
                "impact": "Méně falešných poplachů"
            })

        # Undertriage patterns
        for insight in insights:
            if insight["category"] == "undertriage_patterns":
                for diagnosis in insight["data"][:3]:
                    adjustments["recommended_changes"].append({
                        "parameter": f"diagnosis_weight_{diagnosis['diagnosis']}",
                        "recommended": "INCREASE",
                        "reason": f"Častá podhodnocení u {diagnosis['diagnosis']} ({diagnosis['count']}x)",
                        "impact": "Vyšší priorita pro tuto diagnózu"
                    })

        return adjustments

    def apply_learning(self) -> Dict[str, Any]:
        """
        Aplikuje naučené úpravy

        V produkci by:
        - Fine-tunoval model
        - Upravil váhy
        - Retrénoval na nových datech
        """
        adjustments = self.calculate_adjustments()

        return {
            "status": "APPLIED",
            "adjustments": adjustments,
            "note": "V produkci by fine-tunoval model. Pro demo: simulované úpravy."
        }


# Demonstrace
if __name__ == "__main__":
    print("="*80)
    print("LEARNING MODULE - DEMONSTRACE")
    print("="*80)

    # Vytvoř databázi
    db = FeedbackDatabase("demo_feedback.db")

    # Simuluj feedback
    print("\n1. SIMULACE FEEDBACKU")
    print("-" * 80)

    feedbacks = [
        # Agreement
        ("P001", {"priority": 1}, {"priority": 1}, {"diagnosis": "Infarkt", "age": 45, "gender": "female"}),
        ("P003", {"priority": 2}, {"priority": 2}, {"diagnosis": "Zlomenina", "age": 72, "gender": "female"}),

        # Undertriage (AI podhodnotil)
        ("P007", {"priority": 3}, {"priority": 1}, {"diagnosis": "Pneumonie", "age": 8, "gender": "female"}),
        ("P009", {"priority": 3}, {"priority": 1}, {"diagnosis": "SAH", "age": 63, "gender": "female"}),

        # Overtriage (AI nadhodnotil)
        ("P010", {"priority": 2}, {"priority": 4}, {"diagnosis": "Panická ataka", "age": 25, "gender": "male"}),
    ]

    for pid, ai_dec, phys_dec, patient_data in feedbacks:
        feedback_id = db.add_feedback(pid, ai_dec, phys_dec, patient_data)
        agreement = "✅" if ai_dec["priority"] == phys_dec["priority"] else "❌"
        print(f"  {agreement} {pid}: AI={ai_dec['priority']}, Lékař={phys_dec['priority']} (ID: {feedback_id})")

    # Stats
    print("\n\n2. STATISTIKY")
    print("-" * 80)

    stats = db.get_feedback_stats(days=30)
    print(f"Celkem případů: {stats['total_cases']}")
    print(f"Agreement rate: {stats['agreement_rate']}%")
    print(f"Undertriage: {stats['undertriage_count']} ({stats['undertriage_rate']}%)")
    print(f"Overtriage: {stats['overtriage_count']} ({stats['overtriage_rate']}%)")

    # Insights
    print("\n\n3. LEARNING INSIGHTS")
    print("-" * 80)

    insights = db.get_learning_insights()
    for insight in insights:
        print(f"\n📊 {insight['title']}")
        print(f"   Kategorie: {insight['category']}")
        if 'data' in insight:
            for item in insight['data']:
                print(f"   - {item}")
        print(f"   💡 {insight['recommendation']}")

    # Adaptive learning
    print("\n\n4. ADAPTIVNÍ UČENÍ")
    print("-" * 80)

    adaptive = AdaptiveLearning(db)
    adjustments = adaptive.calculate_adjustments()

    print(f"\nDoporučené úpravy:")
    for change in adjustments["recommended_changes"]:
        print(f"\n  📝 Parametr: {change['parameter']}")
        print(f"     Důvod: {change['reason']}")
        print(f"     Doporučení: {change.get('recommended', change.get('recommended'))}")
        print(f"     Dopad: {change['impact']}")

    # Aplikuj
    result = adaptive.apply_learning()
    print(f"\n✅ {result['status']}: {result['note']}")

    print("\n" + "="*80)
    print("Learning module funkční!")
    print("="*80)

    # Cleanup
    import os
    if os.path.exists("demo_feedback.db"):
        os.remove("demo_feedback.db")

"""
PREDIKTIVNÍ MODUL

Předpovídá vývoj epidemií, nápor pacientů a rizika
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import json


class EpidemicPredictor:
    """
    Predikuje vývoj epidemií a nápor pacientů
    Využívá jednoduchou time-series analýzu
    """

    def __init__(self):
        self.historical_data = []

    def predict_epidemic_trend(
        self,
        current_incidence: float,
        historical_incidences: List[float]
    ) -> Dict[str, Any]:
        """
        Předpoví vývoj epidemie

        Args:
            current_incidence: Aktuální incidence na 100k obyvatel
            historical_incidences: Historická data (např. posledních 7 dní)

        Returns:
            Predikce trendu
        """
        if len(historical_incidences) < 3:
            return {
                "trend": "unknown",
                "predicted_next_week": current_incidence,
                "confidence": "low"
            }

        # Jednoduchý lineární trend
        x = np.arange(len(historical_incidences))
        y = np.array(historical_incidences)

        # Linear regression
        slope = np.polyfit(x, y, 1)[0]

        # Predikce za týden
        predicted_next_week = current_incidence + (slope * 7)

        # Určení trendu
        if slope > 10:
            trend = "rapidly_increasing"
        elif slope > 2:
            trend = "increasing"
        elif slope < -10:
            trend = "rapidly_decreasing"
        elif slope < -2:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "predicted_next_week": max(0, predicted_next_week),
            "weekly_change": slope * 7,
            "confidence": "moderate" if len(historical_incidences) >= 7 else "low"
        }

    def predict_patient_surge(
        self,
        epidemiology_data: Dict,
        weather_data: Dict = None,
        events: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Předpoví nápor pacientů na urgentní příjem

        Args:
            epidemiology_data: Epidemiologická data
            weather_data: Data o počasí
            events: Lokální události

        Returns:
            Predikce náporu
        """
        surge_factors = []
        total_surge_multiplier = 1.0

        # Faktor 1: Epidemie
        if epidemiology_data.get("conditions"):
            for condition_name, condition_data in epidemiology_data["conditions"].items():
                if condition_data.get("status") == "epidemic":
                    surge_factors.append({
                        "factor": f"Epidemie {condition_name}",
                        "impact": "+30-50% respiračních případů"
                    })
                    total_surge_multiplier *= 1.4

        # Faktor 2: Počasí
        if weather_data:
            temp = weather_data.get("temperature", 20)
            conditions = weather_data.get("conditions", "normal")

            if conditions == "heat_wave" or temp > 30:
                surge_factors.append({
                    "factor": "Vedra",
                    "impact": "+15-20% kardiovaskulárních případů u seniorů"
                })
                total_surge_multiplier *= 1.15

            elif temp < 0:
                surge_factors.append({
                    "factor": "Mráz",
                    "impact": "+10% úrazů (pády), hypotermie"
                })
                total_surge_multiplier *= 1.1

        # Faktor 3: Události
        if events:
            for event in events:
                if "festival" in event.get("event", "").lower():
                    surge_factors.append({
                        "factor": f"Festival: {event['event']}",
                        "impact": "+25% úrazů, intoxikací, dehydratace"
                    })
                    total_surge_multiplier *= 1.25

                elif "zápas" in event.get("event", "").lower():
                    surge_factors.append({
                        "factor": f"Sportovní zápas",
                        "impact": "+15% úrazů"
                    })
                    total_surge_multiplier *= 1.15

        # Baseline průměr: 50 pacientů/den na velkém urgentním příjmu
        baseline_daily_patients = 50
        predicted_patients = int(baseline_daily_patients * total_surge_multiplier)

        return {
            "baseline_daily_patients": baseline_daily_patients,
            "predicted_daily_patients": predicted_patients,
            "surge_multiplier": round(total_surge_multiplier, 2),
            "surge_factors": surge_factors,
            "recommendation": self._get_surge_recommendation(total_surge_multiplier)
        }

    def _get_surge_recommendation(self, multiplier: float) -> str:
        """Doporučení podle očekávaného náporu"""
        if multiplier >= 1.5:
            return "KRITICKÝ NÁPOR - Aktivovat krizový plán, volat posily"
        elif multiplier >= 1.3:
            return "VYSOKÝ NÁPOR - Připravit extra kapacitu, prodloužit směny"
        elif multiplier >= 1.15:
            return "MÍRNÝ NÁPOR - Monitorovat situaci, mít zálohu"
        else:
            return "NORMÁLNÍ PROVOZ - Standardní kapacita postačuje"


class PatientOutcomePredictor:
    """
    Předpovídá vývoj stavu pacienta
    """

    def predict_deterioration_risk(
        self,
        vital_signs: Dict,
        medical_history: Dict,
        age: int
    ) -> Dict[str, Any]:
        """
        Předpoví riziko zhoršení stavu pacienta

        Args:
            vital_signs: Vitální funkce
            medical_history: Zdravotní anamnéza
            age: Věk pacienta

        Returns:
            Rizikové skóre a faktory
        """
        risk_score = 0
        risk_factors = []

        # Věk
        if age >= 75:
            risk_score += 3
            risk_factors.append("Věk 75+")
        elif age >= 65:
            risk_score += 2
            risk_factors.append("Věk 65+")

        # Vitální funkce
        hr = vital_signs.get("heart_rate", 70)
        spo2 = vital_signs.get("oxygen_saturation", 98)
        bp_str = vital_signs.get("blood_pressure", "120/80")
        systolic = int(bp_str.split("/")[0])

        if hr > 110 or hr < 50:
            risk_score += 2
            risk_factors.append("Abnormální srdeční frekvence")

        if spo2 < 94:
            risk_score += 3
            risk_factors.append("Hypoxie")

        if systolic < 90:
            risk_score += 3
            risk_factors.append("Hypotenze")

        # Chronická onemocnění
        conditions = medical_history.get("conditions", [])
        high_risk_conditions = ["Diabetes mellitus", "CHOPN", "Srdeční selhání", "Imunodeficience"]

        for condition in conditions:
            for high_risk in high_risk_conditions:
                if high_risk.lower() in condition.lower():
                    risk_score += 2
                    risk_factors.append(f"Chronické: {condition}")

        # Klasifikace rizika
        if risk_score >= 8:
            risk_level = "VYSOKÉ"
            recommendation = "Intenzivní monitorování, riziko ICU"
        elif risk_score >= 5:
            risk_level = "STŘEDNÍ"
            recommendation = "Časté kontroly, pozor na deterioraci"
        elif risk_score >= 3:
            risk_level = "MÍRNÉ"
            recommendation = "Standardní monitorování"
        else:
            risk_level = "NÍZKÉ"
            recommendation = "Rutinní péče"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendation": recommendation,
            "estimated_icu_probability": min(risk_score * 8, 90)  # %
        }

    def estimate_length_of_stay(
        self,
        priority: int,
        age: int,
        conditions: List[str]
    ) -> Dict[str, Any]:
        """
        Odhadne délku hospitalizace

        Args:
            priority: Triážní priorita
            age: Věk
            conditions: Chronická onemocnění

        Returns:
            Odhad délky pobytu
        """
        # Baseline podle priority
        baseline_hours = {
            1: 48,  # 2 dny
            2: 24,  # 1 den
            3: 12,  # 12 hodin
            4: 4,   # 4 hodiny
            5: 2    # 2 hodiny
        }.get(priority, 12)

        # Modifikátory
        multiplier = 1.0

        if age >= 75:
            multiplier *= 1.5
        elif age >= 65:
            multiplier *= 1.2

        if len(conditions) >= 3:
            multiplier *= 1.3
        elif len(conditions) >= 1:
            multiplier *= 1.15

        estimated_hours = int(baseline_hours * multiplier)

        return {
            "estimated_hours": estimated_hours,
            "estimated_days": round(estimated_hours / 24, 1),
            "confidence": "moderate",
            "factors": [
                f"Priorita {priority}",
                f"Věk {age}",
                f"{len(conditions)} chronických onemocnění"
            ]
        }


# Demonstrace
if __name__ == "__main__":
    print("="*80)
    print("PREDIKTIVNÍ MODUL - DEMONSTRACE")
    print("="*80)

    # Test 1: Predikce epidemie
    epidemic_predictor = EpidemicPredictor()

    print("\n1. PREDIKCE VÝVOJE EPIDEMIE CHŘIPKY")
    print("-" * 80)

    historical = [300, 320, 350, 390, 420, 450]
    current = 450

    trend = epidemic_predictor.predict_epidemic_trend(current, historical)
    print(f"Aktuální incidence: {current}/100k")
    print(f"Trend: {trend['trend']}")
    print(f"Predikce za týden: {trend['predicted_next_week']:.1f}/100k")
    print(f"Týdenní změna: {trend['weekly_change']:+.1f}")

    # Test 2: Predikce náporu
    print("\n\n2. PREDIKCE NÁPORU PACIENTŮ")
    print("-" * 80)

    epi_data = {
        "conditions": {
            "influenza": {"status": "epidemic", "incidence_per_100k": 450}
        }
    }

    weather = {
        "temperature": 32,
        "conditions": "heat_wave"
    }

    events = [
        {"event": "Hudební festival Plzeň", "date": "2026-06-22"}
    ]

    surge = epidemic_predictor.predict_patient_surge(epi_data, weather, events)

    print(f"Baseline: {surge['baseline_daily_patients']} pacientů/den")
    print(f"Predikce: {surge['predicted_daily_patients']} pacientů/den")
    print(f"Násobek: {surge['surge_multiplier']}x")
    print(f"\nFaktory:")
    for factor in surge['surge_factors']:
        print(f"  - {factor['factor']}: {factor['impact']}")
    print(f"\n💡 Doporučení: {surge['recommendation']}")

    # Test 3: Riziko deteriorace
    print("\n\n3. PREDIKCE RIZIKA ZHORŠENÍ STAVU")
    print("-" * 80)

    outcome_predictor = PatientOutcomePredictor()

    vitals = {
        "heart_rate": 105,
        "oxygen_saturation": 92,
        "blood_pressure": "95/60"
    }

    history = {
        "conditions": ["Diabetes mellitus typ 2", "CHOPN"]
    }

    risk = outcome_predictor.predict_deterioration_risk(vitals, history, age=72)

    print(f"Rizikové skóre: {risk['risk_score']}/15")
    print(f"Úroveň rizika: {risk['risk_level']}")
    print(f"Pravděpodobnost ICU: {risk['estimated_icu_probability']}%")
    print(f"\nRizikové faktory:")
    for rf in risk['risk_factors']:
        print(f"  - {rf}")
    print(f"\n💡 Doporučení: {risk['recommendation']}")

    print("\n" + "="*80)
    print("Prediktivní modul funkční!")
    print("="*80)

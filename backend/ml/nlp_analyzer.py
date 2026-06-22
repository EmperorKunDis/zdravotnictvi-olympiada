"""
NLP MODUL PRO ANALÝZU ZDRAVOTNÍCH ZÁZNAMŮ

Extrahuje rizikové faktory, analyzuje sentiment, detekuje red flags
"""

import re
from typing import Dict, List, Any, Tuple
from datetime import datetime


class MedicalRecordAnalyzer:
    """
    Analyzuje zdravotní záznamy a extrahuje klinicky relevantní informace
    """

    def __init__(self):
        # Mapování rizikových faktorů
        self.risk_factor_keywords = {
            "kardiovaskulární": [
                "diabetes", "cukrovka", "hypertenze", "vysoký tlak",
                "kouření", "kuřák", "infarkt", "mrtvice", "angina",
                "ateroskleróza", "fibrilace", "arytmie"
            ],
            "respirační": [
                "astma", "CHOPN", "chronická bronchitida", "emfyzém",
                "plicní", "dýchací potíže"
            ],
            "neurologické": [
                "epilepsie", "záchvaty", "Parkinson", "demence",
                "migréna", "neuropatie"
            ],
            "imunosuprese": [
                "imunodeficience", "HIV", "chemoterapie", "kortikosteroidy",
                "transplantace", "biologická léčba"
            ],
            "gastrointestinální": [
                "vřed", "Crohnova nemoc", "ulcerózní kolitida",
                "jaterní cirhóza", "pankreatitida"
            ]
        }

        # Red flags - varovné signály
        self.red_flags = {
            "kardio": ["rodinná anamnéza infarktu", "náhlá bolest na hrudi", "palpitace"],
            "neuro": ["nejhorší bolest hlavy v životě", "thunderclap", "jednostranná slabost"],
            "respirační": ["SpO2 < 90", "stridor", "cyanóza"],
            "trauma": ["antikoagulace + trauma hlavy", "páteřní poranění"],
            "infekce": ["imunosuprese + horečka", "sepse", "meningitida"]
        }

    def analyze_medical_history(self, medical_history: Dict) -> Dict[str, Any]:
        """
        Analyzuje zdravotní anamnézu

        Args:
            medical_history: Dict se conditions, medications, risk_factors

        Returns:
            Analýza s extrahovanými rizikovými faktory
        """
        conditions = medical_history.get("conditions", [])
        medications = medical_history.get("medications", [])
        risk_factors = medical_history.get("risk_factors", [])

        # Kombinuj všechny texty
        all_text = " ".join(conditions + medications + risk_factors).lower()

        # Detekuj kategorie rizika
        detected_risks = {}
        for category, keywords in self.risk_factor_keywords.items():
            matches = []
            for keyword in keywords:
                if keyword in all_text:
                    matches.append(keyword)

            if matches:
                detected_risks[category] = {
                    "detected": True,
                    "keywords": matches,
                    "severity": self._assess_risk_severity(category, matches)
                }

        # Detekuj red flags
        detected_red_flags = []
        for category, flags in self.red_flags.items():
            for flag in flags:
                if flag in all_text:
                    detected_red_flags.append({
                        "category": category,
                        "flag": flag,
                        "action": "IMMEDIATE_ESCALATION_REQUIRED"
                    })

        # Analýza medikace
        medication_insights = self._analyze_medications(medications)

        return {
            "risk_categories": detected_risks,
            "red_flags": detected_red_flags,
            "medication_insights": medication_insights,
            "overall_risk_score": self._calculate_overall_risk(detected_risks, detected_red_flags),
            "clinical_recommendations": self._generate_recommendations(detected_risks, detected_red_flags)
        }

    def _assess_risk_severity(self, category: str, matches: List[str]) -> str:
        """Posoudí závažnost rizika"""
        if len(matches) >= 3:
            return "HIGH"
        elif len(matches) >= 2:
            return "MODERATE"
        else:
            return "LOW"

    def _analyze_medications(self, medications: List[str]) -> Dict[str, Any]:
        """Analyzuje medikaci pro rizikové interakce"""
        insights = []

        meds_lower = [m.lower() for m in medications]

        # Antikoagulace
        anticoagulants = ["warfarin", "apixaban", "rivaroxaban", "dabigatran"]
        if any(ac in " ".join(meds_lower) for ac in anticoagulants):
            insights.append({
                "category": "anticoagulation",
                "risk": "Zvýšené riziko krvácení",
                "note": "POZOR při jakémkoliv traumatu!"
            })

        # NSAID dlouhodobě
        nsaids = ["ibuprofen", "diklofenak", "naproxen"]
        if any(ns in " ".join(meds_lower) for ns in nsaids):
            insights.append({
                "category": "NSAID",
                "risk": "Riziko peptického vředu, GI krvácení",
                "note": "Při bolesti břicha nebo meléně URGENTNĚ vyšetřit"
            })

        # Imunosuprese
        immunosuppressants = ["kortikosteroid", "prednison", "methotrexat", "azathioprin"]
        if any(im in " ".join(meds_lower) for im in immunosuppressants):
            insights.append({
                "category": "immunosuppression",
                "risk": "Zvýšené riziko infekcí",
                "note": "Při horečce nízký práh pro antibiotika"
            })

        return insights

    def _calculate_overall_risk(self, risks: Dict, red_flags: List) -> int:
        """Vypočítá celkové rizikové skóre 0-100"""
        score = 0

        # Body za kategorie rizika
        for category, data in risks.items():
            if data["severity"] == "HIGH":
                score += 20
            elif data["severity"] == "MODERATE":
                score += 10
            else:
                score += 5

        # Body za red flags
        score += len(red_flags) * 25

        return min(score, 100)

    def _generate_recommendations(self, risks: Dict, red_flags: List) -> List[str]:
        """Generuje klinická doporučení"""
        recommendations = []

        if red_flags:
            recommendations.append("🚨 RED FLAGS DETECTED - Urgentní vyšetření!")

        if "kardiovaskulární" in risks:
            recommendations.append("🫀 Kardiovaskulární riziko - při netypických příznacích vyloučit ACS")

        if "respirační" in risks:
            recommendations.append("🫁 Respirační riziko - monitorovat SpO2, dechovou frekvenci")

        if "imunosuprese" in risks:
            recommendations.append("🦠 Imunosuprese - nízký práh pro antibiotika při infekci")

        return recommendations


class SentimentAnalyzer:
    """
    Analyzuje sentiment a psychický stav pacienta
    """

    def __init__(self):
        # Klíčová slova pro detekci úzkosti/stresu
        self.anxiety_keywords = [
            "strach", "úzkost", "panika", "nervozita", "stres",
            "bojím se", "neklid", "nespavost"
        ]

        # Klíčová slova pro depresi
        self.depression_keywords = [
            "beznaděj", "deprese", "smutek", "únava", "ztráta zájmu",
            "nechci žít", "sebevražda"
        ]

    def analyze_patient_communication(
        self,
        chief_complaint: str,
        symptoms: List[str]
    ) -> Dict[str, Any]:
        """
        Analyzuje tón a sentiment komunikace pacienta

        Args:
            chief_complaint: Hlavní stížnost
            symptoms: Seznam symptomů

        Returns:
            Sentiment analýza
        """
        all_text = (chief_complaint + " " + " ".join(symptoms)).lower()

        # Detekuj úzkost
        anxiety_score = 0
        for keyword in self.anxiety_keywords:
            if keyword in all_text:
                anxiety_score += 1

        # Detekuj depresi
        depression_score = 0
        suicide_risk = False
        for keyword in self.depression_keywords:
            if keyword in all_text:
                depression_score += 1
            if "sebevražda" in keyword or "nechci žít" in keyword:
                suicide_risk = True

        # Celkový sentiment
        if suicide_risk:
            sentiment = "CRISIS"
            recommendation = "🚨 RIZIKO SEBEVRAŽDY - Psychiatrická konzultace OKAMŽITĚ, nepouštět domů!"
        elif anxiety_score >= 3 or depression_score >= 3:
            sentiment = "DISTRESSED"
            recommendation = "Vysoký level stresu/úzkosti - zvážit psychiatrickou konzultaci"
        elif anxiety_score >= 1 or depression_score >= 1:
            sentiment = "ANXIOUS"
            recommendation = "Lehká úzkost - empatická komunikace, poskytnout ujištění"
        else:
            sentiment = "NEUTRAL"
            recommendation = "Normální psychický stav"

        return {
            "sentiment": sentiment,
            "anxiety_indicators": anxiety_score,
            "depression_indicators": depression_score,
            "suicide_risk": suicide_risk,
            "recommendation": recommendation,
            "note": "Psychický stav může ovlivnit prezentaci fyzických symptomů"
        }


class SymptomExtractor:
    """
    Extrahuje a standardizuje symptomy z volného textu
    """

    def __init__(self):
        # Mapování laických termínů na klinické
        self.symptom_mapping = {
            "bolí mě hlava": "bolest hlavy",
            "mám horečku": "febrilní stav",
            "je mi špatně": "nevolnost",
            "zvracím": "zvracení",
            "bolí břicho": "abdominální bolest",
            "bolí na hrudi": "hrudní bolest",
            "nemohu dýchat": "dušnost",
            "točí se mi hlava": "vertigo/závratě",
            "mám průjem": "průjem",
            "kašlu": "kašel"
        }

    def extract_symptoms(self, free_text: str) -> Dict[str, Any]:
        """
        Extrahuje symptomy z volného textu

        Args:
            free_text: Volný text od pacienta

        Returns:
            Strukturované symptomy
        """
        text_lower = free_text.lower()

        # Extrahuj mapované symptomy
        found_symptoms = []
        for layman_term, clinical_term in self.symptom_mapping.items():
            if layman_term in text_lower:
                found_symptoms.append({
                    "original": layman_term,
                    "standardized": clinical_term
                })

        # Extrahuj časové informace
        duration = self._extract_duration(text_lower)

        # Extrahuj závažnost
        severity = self._extract_severity(text_lower)

        return {
            "extracted_symptoms": found_symptoms,
            "duration": duration,
            "severity": severity,
            "structured_for_ehr": [s["standardized"] for s in found_symptoms]
        }

    def _extract_duration(self, text: str) -> str:
        """Extrahuje trvání symptomů"""
        if "hodinu" in text or "1 hodina" in text:
            return "1 hodina"
        elif "hodiny" in text or re.search(r"\d+ hodin", text):
            match = re.search(r"(\d+) hodin", text)
            return f"{match.group(1)} hodin" if match else "několik hodin"
        elif "den" in text or "včera" in text:
            return "1 den"
        elif "dny" in text or "týden" in text:
            return "několik dní"
        else:
            return "nespecifikováno"

    def _extract_severity(self, text: str) -> str:
        """Extrahuje závažnost"""
        if any(word in text for word in ["velmi", "strašně", "nesnesitelně", "nejhorší"]):
            return "SEVERE"
        elif any(word in text for word in ["silně", "hodně"]):
            return "MODERATE"
        else:
            return "MILD"


# Demonstrace
if __name__ == "__main__":
    print("="*80)
    print("NLP MODUL - DEMONSTRACE")
    print("="*80)

    # Test 1: Analýza zdravotních záznamů
    print("\n1. ANALÝZA ZDRAVOTNÍCH ZÁZNAMŮ")
    print("-" * 80)

    analyzer = MedicalRecordAnalyzer()

    history = {
        "conditions": ["Diabetes mellitus typ 2", "Hypertenze", "Fibrilace síní"],
        "medications": ["Metformin", "Warfarin", "Enalapril"],
        "risk_factors": ["Rodinná anamnéza infarktu myokardu", "Kouření 20 let"]
    }

    analysis = analyzer.analyze_medical_history(history)

    print(f"Rizikové kategorie:")
    for category, data in analysis["risk_categories"].items():
        print(f"  - {category.upper()}: {data['severity']}")
        print(f"    Keywords: {', '.join(data['keywords'])}")

    if analysis["red_flags"]:
        print(f"\n🚨 RED FLAGS:")
        for flag in analysis["red_flags"]:
            print(f"  - [{flag['category']}] {flag['flag']}")

    print(f"\n💊 Medikační insights:")
    for insight in analysis["medication_insights"]:
        print(f"  - {insight['category']}: {insight['risk']}")
        print(f"    Note: {insight['note']}")

    print(f"\n📊 Celkové rizikové skóre: {analysis['overall_risk_score']}/100")

    print(f"\n💡 Klinická doporučení:")
    for rec in analysis["clinical_recommendations"]:
        print(f"  {rec}")

    # Test 2: Sentiment analýza
    print("\n\n2. SENTIMENT ANALÝZA")
    print("-" * 80)

    sentiment_analyzer = SentimentAnalyzer()

    complaint = "Bolí mě na hrudi a mám strach že umřu, jsem velmi nervózní"
    symptoms = ["Palpitace", "Úzkost", "Strach"]

    sentiment = sentiment_analyzer.analyze_patient_communication(complaint, symptoms)

    print(f"Sentiment: {sentiment['sentiment']}")
    print(f"Úzkost: {sentiment['anxiety_indicators']} indikátorů")
    print(f"Deprese: {sentiment['depression_indicators']} indikátorů")
    print(f"Riziko sebevraždy: {sentiment['suicide_risk']}")
    print(f"\n💡 {sentiment['recommendation']}")

    # Test 3: Extrakce symptomů
    print("\n\n3. EXTRAKCE SYMPTOMŮ Z VOLNÉHO TEXTU")
    print("-" * 80)

    extractor = SymptomExtractor()

    free_text = "Už 3 dny mě velmi bolí hlava a je mi špatně, zvracím a mám horečku"

    symptoms = extractor.extract_symptoms(free_text)

    print(f"Nalezené symptomy:")
    for symp in symptoms["extracted_symptoms"]:
        print(f"  - {symp['original']} → {symp['standardized']}")

    print(f"\nTrvání: {symptoms['duration']}")
    print(f"Závažnost: {symptoms['severity']}")

    print(f"\nStrukturováno pro EHR:")
    for s in symptoms["structured_for_ehr"]:
        print(f"  - {s}")

    print("\n" + "="*80)
    print("NLP modul funkční!")
    print("="*80)

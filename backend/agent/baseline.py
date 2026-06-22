"""
BASELINE TRIÁŽNÍ SYSTÉM

Jednoduché řešení založené pouze na:
- Vitálních funkcích
- Hlavní stížnosti pacienta
- Škále bolesti

NEPOUŽÍVÁ:
- Zdravotní záznamy (medical history)
- Epidemiologickou situaci
- Kontextuální informace

Tento baseline slouží jako referenční bod pro srovnání s AI agentem.
"""

from typing import Dict, Any
import re


class BaselineTriageSystem:
    """
    Baseline systém pro triáž pacientů
    Založen na českém triážním standardu, ale bez pokročilého rozhodování
    """

    def __init__(self):
        # Prahové hodnoty pro vitální funkce
        self.critical_thresholds = {
            "heart_rate": {"min": 50, "max": 120},
            "respiratory_rate": {"min": 12, "max": 25},
            "oxygen_saturation": {"min": 94},
            "systolic_bp": {"min": 90, "max": 180},
            "temperature": {"min": 35.5, "max": 39.0}
        }

        # Klíčová slova pro prioritizaci podle stížnosti
        self.high_priority_keywords = [
            "bolest na hrudi", "chest pain", "infarkt",
            "dušnost", "dýchací potíže", "nemohu dýchat",
            "mrtvice", "slabost", "paralýza",
            "zmatený", "dezorientace", "bezvědomí",
            "krvácení", "trauma hlavy",
            "záchvat", "křeče"
        ]

        self.moderate_keywords = [
            "bolest břicha", "nevolnost", "zvracení",
            "teplota", "horečka",
            "úraz", "pád", "zlomenina"
        ]

    def triage(self, patient_id: str, presentation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provede triáž pacienta pouze na základě prezentace

        Args:
            patient_id: ID pacienta
            presentation: Dict s vital_signs, chief_complaint, symptoms, pain_scale

        Returns:
            Dict s priority (1-5), reasoning, warning flags
        """
        vital_signs = presentation["vital_signs"]
        chief_complaint = presentation["chief_complaint"]
        symptoms = presentation.get("symptoms", [])
        pain_scale = presentation.get("pain_scale", 0)

        # Kontrola vitálních funkcí
        vital_flags = self._check_vitals(vital_signs)

        # Kontrola klíčových slov ve stížnosti
        complaint_priority = self._assess_complaint(chief_complaint, symptoms)

        # Škála bolesti
        pain_priority = self._assess_pain(pain_scale)

        # Finální priorita = nejhorší z kategorií
        priority = min(vital_flags["priority"], complaint_priority, pain_priority)

        # Reasoning
        reasoning_parts = []
        if vital_flags["abnormal"]:
            reasoning_parts.append(f"Abnormální vitální funkce: {', '.join(vital_flags['abnormal'])}")
        reasoning_parts.append(f"Hlavní stížnost: {chief_complaint}")
        if pain_scale >= 7:
            reasoning_parts.append(f"Vysoká bolest ({pain_scale}/10)")

        return {
            "patient_id": patient_id,
            "priority": priority,
            "priority_name": self._get_priority_name(priority),
            "reasoning": " | ".join(reasoning_parts),
            "vital_flags": vital_flags["abnormal"],
            "decision_basis": "POUZE prezentace (vitální funkce + stížnost)",
            "limitations": "Nepoužívá zdravotní záznamy, epidemiologii, kontextuální faktory"
        }

    def _check_vitals(self, vital_signs: Dict) -> Dict[str, Any]:
        """Zkontroluje vitální funkce a vrátí priority"""
        abnormal = []
        priority = 5  # Default: nízká priorita

        # Heart rate
        hr = vital_signs.get("heart_rate", 70)
        if hr < self.critical_thresholds["heart_rate"]["min"]:
            abnormal.append("Bradykardie")
            priority = min(priority, 2)
        elif hr > self.critical_thresholds["heart_rate"]["max"]:
            abnormal.append("Tachykardie")
            priority = min(priority, 2)

        # Respiratory rate
        rr = vital_signs.get("respiratory_rate", 16)
        if rr < self.critical_thresholds["respiratory_rate"]["min"]:
            abnormal.append("Bradypnoe")
            priority = min(priority, 2)
        elif rr > self.critical_thresholds["respiratory_rate"]["max"]:
            abnormal.append("Tachypnoe")
            priority = min(priority, 2)

        # Oxygen saturation - KRITICKÉ
        spo2 = vital_signs.get("oxygen_saturation", 98)
        if spo2 < self.critical_thresholds["oxygen_saturation"]["min"]:
            abnormal.append(f"Hypoxie (SpO2 {spo2}%)")
            priority = min(priority, 1)  # Resuscitace!

        # Blood pressure
        bp = vital_signs.get("blood_pressure", "120/80")
        systolic = int(bp.split("/")[0])
        if systolic < self.critical_thresholds["systolic_bp"]["min"]:
            abnormal.append("Hypotenze")
            priority = min(priority, 2)
        elif systolic > self.critical_thresholds["systolic_bp"]["max"]:
            abnormal.append("Hypertenze")
            priority = min(priority, 3)

        # Temperature
        temp = vital_signs.get("temperature", 36.6)
        if temp < self.critical_thresholds["temperature"]["min"]:
            abnormal.append("Hypotermie")
            priority = min(priority, 2)
        elif temp > self.critical_thresholds["temperature"]["max"]:
            abnormal.append("Vysoká teplota")
            priority = min(priority, 3)

        return {
            "priority": priority,
            "abnormal": abnormal
        }

    def _assess_complaint(self, chief_complaint: str, symptoms: list) -> int:
        """Posoudí závažnost podle stížnosti"""
        complaint_lower = chief_complaint.lower()
        symptoms_text = " ".join(symptoms).lower()
        combined = f"{complaint_lower} {symptoms_text}"

        # Vysoká priorita - klíčová slova
        for keyword in self.high_priority_keywords:
            if keyword in combined:
                # Baseline VŽDY eskaluje "bolest na hrudi" -> může být OVERTRIAGE
                if "bolest na hrudi" in combined or "chest pain" in combined:
                    return 2  # Eskaluje kvůli možnému infarktu

                # Neurologické příznaky
                if any(word in combined for word in ["mrtvice", "slabost", "paralýza", "zmatený"]):
                    return 1

                return 2

        # Střední priorita
        for keyword in self.moderate_keywords:
            if keyword in combined:
                return 3

        # Default
        return 4

    def _assess_pain(self, pain_scale: int) -> int:
        """Posoudí prioritu podle škály bolesti"""
        if pain_scale >= 9:
            return 2  # Emergentní
        elif pain_scale >= 7:
            return 3  # Urgentní
        elif pain_scale >= 5:
            return 4
        else:
            return 5

    def _get_priority_name(self, priority: int) -> str:
        """Vrátí název priority podle českého standardu"""
        priority_names = {
            1: "Resuscitace (červená)",
            2: "Emergentní (oranžová)",
            3: "Urgentní (žlutá)",
            4: "Méně urgentní (zelená)",
            5: "Necitlivé (modrá)"
        }
        return priority_names.get(priority, "Neznámá")


# Demonstrace baseline systému
if __name__ == "__main__":
    from backend.data.interface import TriageDataInterface

    interface = TriageDataInterface()
    baseline = BaselineTriageSystem()

    print("=" * 80)
    print("BASELINE TRIÁŽ - DEMONSTRACE")
    print("=" * 80)

    # Testujeme na záludných případech
    test_patient_ids = ["P001", "P004", "P007", "P009", "P010"]

    for pid in test_patient_ids:
        print(f"\n{'='*80}")
        presentation = interface.get_presentation(pid)

        # Najdeme pacienta pro true diagnosis
        patient = None
        for p in interface.patients["patients"]:
            if p["id"] == pid:
                patient = p
                break

        print(f"PACIENT: {patient['name']} ({pid})")
        print(f"Stížnost: {presentation['chief_complaint']}")
        print(f"Vitální funkce: TK {presentation['vital_signs']['blood_pressure']}, "
              f"Puls {presentation['vital_signs']['heart_rate']}, "
              f"SpO2 {presentation['vital_signs']['oxygen_saturation']}%")

        # Baseline rozhodnutí
        decision = baseline.triage(pid, presentation)

        print(f"\n--- BASELINE ROZHODNUTÍ ---")
        print(f"Priorita: {decision['priority']} - {decision['priority_name']}")
        print(f"Odůvodnění: {decision['reasoning']}")

        print(f"\n--- SKUTEČNOST ---")
        print(f"Skutečná diagnóza: {patient['true_diagnosis']}")
        print(f"Správná priorita: {patient['true_priority']}")

        # Evaluace
        if decision['priority'] > patient['true_priority'] + 1:
            print(f"\n⚠️  UNDERTRIAGE! Baseline podhodnotil závažnost")
            print(f"   Note: {patient.get('notes', '')}")
        elif decision['priority'] < patient['true_priority'] - 1:
            print(f"\n⚠️  OVERTRIAGE! Baseline nadhodnotil závažnost")
        else:
            print(f"\n✅ Správná nebo přijatelná triáž")

        print("="*80)

    print(f"\n\nBASELINE OMEZENÍ:")
    print("❌ Nepoužívá zdravotní záznamy")
    print("❌ Nepoužívá epidemiologickou situaci")
    print("❌ Nerozpoznává atypické prezentace")
    print("❌ Pevná pravidla bez kontextu")
    print("\nToto je přesně to, co má AI agent překonat!")

"""
Datové rozhraní pro triážní agentní systém
Poskytuje 5 základních funkcí podle zadání AI Olympiády
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

class TriageDataInterface:
    def __init__(self, data_dir: str = "../../data/sandbox"):
        self.data_dir = Path(data_dir)
        self.patients = self._load_patients()
        self.epidemiology = self._load_epidemiology()
        self.interaction_log = []  # Pro tracking ask_patient volání

    def _load_patients(self) -> Dict:
        """Načte syntetická data pacientů"""
        with open(self.data_dir / "patients.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_epidemiology(self) -> Dict:
        """Načte epidemiologická data"""
        with open(self.data_dir / "epidemiology.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def get_presentation(self, patient_id: str) -> Dict[str, Any]:
        """
        VIDITELNÉ PRO VŠECHNY
        Vrací příznaky a vitální funkce pacienta při příchodu

        Args:
            patient_id: ID pacienta (např. "P001")

        Returns:
            Dict obsahující:
            - chief_complaint: Hlavní stížnost
            - vital_signs: Vitální funkce (TK, puls, RR, teplota, SpO2)
            - symptoms: Seznam symptomů
            - pain_scale: Škála bolesti 0-10
            - arrival_time: Čas příchodu
        """
        patient = self._find_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        self._log_interaction(patient_id, "get_presentation", patient["presentation"])
        return patient["presentation"]

    def get_history(self, patient_id: str) -> Dict[str, Any]:
        """
        NEPŘETĚŽUJE PACIENTA - data z EHR
        Vrací zdravotní záznamy z elektronické zdravotní dokumentace

        Args:
            patient_id: ID pacienta

        Returns:
            Dict obsahující:
            - conditions: Chronická onemocnění
            - medications: Současná medikace
            - allergies: Alergie
            - previous_visits: Předchozí návštěvy
            - risk_factors: Rizikové faktory
        """
        patient = self._find_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        self._log_interaction(patient_id, "get_history", patient["medical_history"])
        return patient["medical_history"]

    def get_epidemiology(self, date: str) -> Dict[str, Any]:
        """
        KONTEXT PRO ROZHODOVÁNÍ
        Vrací epidemiologickou situaci k danému datu

        Args:
            date: Datum ve formátu "YYYY-MM-DD"

        Returns:
            Dict obsahující:
            - conditions: Aktuální epidemiologická situace
            - expected_surge: Očekávaný nápor
            - weather: Počasí a alerty
            - local_events: Lokální události
            - hospital_capacity: Kapacita nemocnice
            - specialist_availability: Dostupnost specialistů
        """
        epi_data = None
        for data in self.epidemiology["epidemiology_data"]:
            if data["date"] == date:
                epi_data = data
                break

        if not epi_data:
            raise ValueError(f"No epidemiology data for {date}")

        # Přidej i kapacitu nemocnice a dostupnost specialistů
        result = {
            **epi_data,
            "hospital_capacity": self.epidemiology.get("hospital_capacity", {}),
            "specialist_availability": self.epidemiology.get("specialist_availability", {})
        }

        self._log_interaction("SYSTEM", "get_epidemiology", {"date": date})
        return result

    def ask_patient(self, patient_id: str, question: str) -> str:
        """
        PŘÍMÝ DOTAZ NA PACIENTA - POČÍTÁ SE!
        Položí otázku přímo pacientovi (simulace)

        MINIMALIZOVAT POUŽITÍ - každé volání snižuje efektivitu agenta

        Args:
            patient_id: ID pacienta
            question: Otázka

        Returns:
            Odpověď pacienta (simulovaná)
        """
        patient = self._find_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        # Simulace odpovědi podle diagnózy a příznaků
        answer = self._simulate_patient_answer(patient, question)

        self._log_interaction(patient_id, "ask_patient", {
            "question": question,
            "answer": answer,
            "NOTE": "TOTO VOLÁNÍ SE POČÍTÁ DO EVALUACE!"
        })

        return answer

    def escalate(self, patient_id: str, reason: str) -> Dict[str, Any]:
        """
        ESKALACE K LÉKAŘI
        Předá případ lékaři s odůvodněním

        Args:
            patient_id: ID pacienta
            reason: Důvod eskalace (musí být jasný a konkrétní)

        Returns:
            Potvrzení eskalace
        """
        patient = self._find_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        escalation = {
            "patient_id": patient_id,
            "patient_name": patient["name"],
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "status": "ESCALATED_TO_PHYSICIAN"
        }

        self._log_interaction(patient_id, "escalate", escalation)

        return escalation

    def _find_patient(self, patient_id: str) -> Optional[Dict]:
        """Najde pacienta podle ID"""
        for patient in self.patients["patients"]:
            if patient["id"] == patient_id:
                return patient
        return None

    def _simulate_patient_answer(self, patient: Dict, question: str) -> str:
        """
        Simuluje odpověď pacienta na otázku
        V reálném systému by toto bylo skutečné vyptávání
        """
        q_lower = question.lower()

        # Jednoduché odpovědi podle klíčových slov
        if "bolest" in q_lower or "pain" in q_lower:
            return f"Bolest hodnotím {patient['presentation']['pain_scale']}/10"

        if "kdy" in q_lower or "when" in q_lower:
            if "začalo" in q_lower or "started" in q_lower:
                symptoms = patient['presentation']['symptoms']
                if symptoms:
                    return f"Příznaky začaly {symptoms[0].lower()}"
                return "Přesně nevím, postupně"

        if "kde" in q_lower or "where" in q_lower:
            chief = patient['presentation']['chief_complaint']
            return f"Bolí mě {chief.lower()}"

        if "alergie" in q_lower or "allergy" in q_lower:
            allergies = patient['medical_history']['allergies']
            if allergies:
                return f"Ano, {', '.join(allergies)}"
            return "Žádné alergie"

        # Default odpověď
        return f"Ohledně {question}: {patient['presentation']['chief_complaint']}"

    def _log_interaction(self, patient_id: str, action: str, data: Any):
        """Loguje interakci pro účely evaluace"""
        self.interaction_log.append({
            "timestamp": datetime.now().isoformat(),
            "patient_id": patient_id,
            "action": action,
            "data": data
        })

    def get_interaction_stats(self, patient_id: str = None) -> Dict[str, Any]:
        """
        Vrací statistiky interakcí pro evaluaci

        Args:
            patient_id: Volitelně filtruje podle pacienta

        Returns:
            Statistiky volání jednotlivých funkcí
        """
        logs = self.interaction_log
        if patient_id:
            logs = [log for log in logs if log["patient_id"] == patient_id]

        stats = {
            "total_interactions": len(logs),
            "ask_patient_count": len([l for l in logs if l["action"] == "ask_patient"]),
            "get_presentation_count": len([l for l in logs if l["action"] == "get_presentation"]),
            "get_history_count": len([l for l in logs if l["action"] == "get_history"]),
            "escalate_count": len([l for l in logs if l["action"] == "escalate"]),
            "efficiency_score": self._calculate_efficiency(logs)
        }

        return stats

    def _calculate_efficiency(self, logs: List[Dict]) -> float:
        """
        Vypočítá skóre efektivity
        Nižší počet ask_patient = vyšší efektivita
        """
        ask_count = len([l for l in logs if l["action"] == "ask_patient"])
        total = len(logs)

        if total == 0:
            return 0.0

        # Penalizace za každé ask_patient
        penalty = ask_count * 0.2
        base_score = 1.0

        return max(0.0, base_score - penalty)

    def reset_log(self):
        """Resetuje log pro novou evaluaci"""
        self.interaction_log = []


# Příklad použití
if __name__ == "__main__":
    interface = TriageDataInterface()

    # Příklad triáže pacienta P001
    print("=== TRIÁŽ PACIENTA P001 ===\n")

    # 1. Vidíme prezentaci
    presentation = interface.get_presentation("P001")
    print(f"Prezentace: {presentation['chief_complaint']}")
    print(f"Vitální funkce: TK {presentation['vital_signs']['blood_pressure']}, "
          f"Puls {presentation['vital_signs']['heart_rate']}")

    # 2. Zkontrolujeme zdravotní záznamy (AGENT TO MĚLY DĚLAT, NE DOTAZNÍK!)
    history = interface.get_history("P001")
    print(f"\nZdravotní anamnéza: {history['conditions']}")
    print(f"Rizikové faktory: {history['risk_factors']}")

    # 3. Zkontrolujeme epidemiologickou situaci
    epi = interface.get_epidemiology("2026-06-22")
    print(f"\nEpidemie: {epi['conditions']['influenza']['status']}")

    # 4. Jen pokud je opravdu nutné, ptáme se pacienta
    # answer = interface.ask_patient("P001", "Kdy bolest začala?")
    # print(f"\nOdpověď pacienta: {answer}")

    # 5. Eskalujeme
    escalation = interface.escalate("P001",
        "Podezření na atypický infarkt myokardu - diabetes, hypertenze, "
        "rodinná anamnéza KV, netypické příznaky u ženy")
    print(f"\n{escalation['status']}: {escalation['reason']}")

    # Statistiky
    stats = interface.get_interaction_stats("P001")
    print(f"\n=== STATISTIKY ===")
    print(f"Počet ask_patient volání: {stats['ask_patient_count']}")
    print(f"Skóre efektivity: {stats['efficiency_score']:.2f}")

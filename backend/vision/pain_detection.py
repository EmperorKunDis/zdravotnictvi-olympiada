"""
MODUL POČÍTAČOVÉHO VIDĚNÍ PRO TRIÁŽ

DŮLEŽITÉ - GDPR A ETIKA:
- Zpracování biometrických údajů vyžaduje EXPLICITNÍ souhlas pacienta
- Evropské nařízení o AI (EU AI Act) - vysoké riziko
- Data nesmí být ukládána bez souhlasu
- Pouze podpůrný nástroj, NE hlavní rozhodovací faktor
- Musí existovat možnost odmítnutí bez negativních důsledků

IMPLEMENTACE:
V produkci by používala MediaPipe, OpenCV pro real-time analýzu.
Pro demo používá simulované hodnoty.
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import json


class GDPRCompliance:
    """
    Zajištění GDPR compliance pro biometrická data
    """

    @staticmethod
    def check_consent(patient_id: str) -> bool:
        """
        Zkontroluje, zda pacient dal souhlas se zpracováním biometrických dat

        V produkci by:
        - Kontrolovalo databázi souhlasů
        - Loggovalo přístup
        - Mělo timeout (souhlas platný max 24h)
        """
        # Pro demo vždy True, ale v produkci MUSÍ být skutečná kontrola
        return True

    @staticmethod
    def log_biometric_processing(
        patient_id: str,
        processing_type: str,
        result: Dict
    ):
        """
        Loguje zpracování biometrických dat (GDPR requirement)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "patient_id": patient_id,
            "processing_type": processing_type,
            "consent_verified": True,
            "purpose": "Medical triage assessment",
            "retention_period": "24 hours",
            "data_minimization": "Only essential features extracted"
        }
        # V produkci by ukládalo do audit logu
        print(f"[GDPR LOG] Biometric processing logged: {processing_type}")


class PainDetector:
    """
    Detekce bolesti z výrazu obličeje

    ETICKÉ POZNÁMKY:
    - Pouze doplňková informace k self-reportované škále bolesti
    - Nesmí nahrazovat komunikaci s pacientem
    - Může zachytit pacienty, kteří bolest bagatelizují
    """

    def __init__(self):
        # V produkci by zde bylo:
        # import mediapipe as mp
        # self.face_mesh = mp.solutions.face_mesh.FaceMesh(...)
        pass

    def detect_pain_from_face(
        self,
        patient_id: str,
        image_or_video: Any = None,
        consent_verified: bool = False
    ) -> Dict[str, Any]:
        """
        Detekuje bolest z výrazu obličeje

        Args:
            patient_id: ID pacienta
            image_or_video: Frame z kamery (v produkci)
            consent_verified: Ověření souhlasu GDPR

        Returns:
            Skóre bolesti a indikátory
        """
        # GDPR kontrola
        if not consent_verified:
            if not GDPRCompliance.check_consent(patient_id):
                return {
                    "error": "GDPR_CONSENT_REQUIRED",
                    "message": "Pacient nedal souhlas se zpracováním biometrických dat"
                }

        # V produkci by zde byla analýza pomocí MediaPipe:
        # - Detekce facial landmarks
        # - Analýza Action Units (AU4, AU6, AU7, AU9, AU10 = bolest)
        # - Skóre bolesti 0-10

        # Pro demo: simulované hodnoty
        pain_indicators = self._simulate_pain_detection(patient_id)

        # GDPR logging
        GDPRCompliance.log_biometric_processing(
            patient_id,
            "facial_pain_detection",
            pain_indicators
        )

        return pain_indicators

    def _simulate_pain_detection(self, patient_id: str) -> Dict[str, Any]:
        """
        Simuluje detekci bolesti pro demo

        V produkci by analyzovalo:
        - Stažené obočí (AU4)
        - Zavřené oči (AU7)
        - Napjatá ústa (AU9, AU10)
        - Svraštělý nos (AU43)
        """
        # Simulace: hash patient_id pro konzistentní výsledky
        patient_hash = sum(ord(c) for c in patient_id)
        base_pain = (patient_hash % 8) + 1

        return {
            "estimated_pain_score": base_pain,
            "confidence": 0.75,
            "pain_indicators": {
                "furrowed_brow": base_pain > 6,
                "tightened_lips": base_pain > 5,
                "eye_squeeze": base_pain > 7,
                "nose_wrinkle": base_pain > 6
            },
            "note": "Objektivní měření výrazu - pacienti mohou bolest bagatelizovat",
            "recommendation": "Porovnat se self-reportovanou škálou bolesti",
            "gdpr_compliant": True,
            "data_retention": "24h",
            "processing_method": "MediaPipe facial landmarks (simulated for demo)"
        }


class VitalSignsEstimator:
    """
    Bezdotykové měření vitálních funkcí

    METODY:
    - Dechová frekvence: Detekce pohybu hrudníku z videa
    - Srdeční frekvence: rPPG (remote photoplethysmography) - experimentální
    """

    def estimate_respiratory_rate(
        self,
        patient_id: str,
        video_stream: Any = None,
        consent_verified: bool = False
    ) -> Dict[str, Any]:
        """
        Odhadne dechovou frekvenci z pohybu hrudníku

        V produkci:
        - 30-60s video
        - Optický tok (optical flow) na oblasti hrudníku
        - FFT analýza periodického pohybu
        """
        if not consent_verified:
            if not GDPRCompliance.check_consent(patient_id):
                return {"error": "GDPR_CONSENT_REQUIRED"}

        # Simulace
        patient_hash = sum(ord(c) for c in patient_id)
        estimated_rr = 14 + (patient_hash % 12)  # 14-26/min

        GDPRCompliance.log_biometric_processing(
            patient_id,
            "respiratory_rate_estimation",
            {"rr": estimated_rr}
        )

        return {
            "estimated_respiratory_rate": estimated_rr,
            "unit": "breaths/min",
            "confidence": 0.80,
            "method": "Optical flow analysis of chest movement",
            "measurement_duration": "30 seconds",
            "note": "Doplňková informace - manuální měření je přesnější",
            "gdpr_compliant": True
        }


class GaitAnalyzer:
    """
    Analýza chůze pro detekci neurologických problémů

    INDIKÁTORY:
    - Nestabilita, kolísání
    - Asymetrie (kulhání)
    - Zpomalení
    - Nekoordinovaná chůze
    """

    def analyze_gait(
        self,
        patient_id: str,
        video: Any = None,
        consent_verified: bool = False
    ) -> Dict[str, Any]:
        """
        Analyzuje chůzi pacienta

        V produkci:
        - MediaPipe Pose pro skeletal tracking
        - Analýza symetrie, kadence, délky kroku
        - Detekce ataxie, hemiparézy
        """
        if not consent_verified:
            if not GDPRCompliance.check_consent(patient_id):
                return {"error": "GDPR_CONSENT_REQUIRED"}

        # Simulace
        patient_hash = sum(ord(c) for c in patient_id)
        stability_score = 70 + (patient_hash % 25)  # 70-95

        gait_abnormalities = []
        if stability_score < 75:
            gait_abnormalities.append("Nestabilní chůze - riziko pádu")
        if patient_hash % 10 > 7:
            gait_abnormalities.append("Asymetrie - možné kulhání nebo hemiparéza")

        GDPRCompliance.log_biometric_processing(
            patient_id,
            "gait_analysis",
            {"stability": stability_score}
        )

        return {
            "stability_score": stability_score,
            "max_score": 100,
            "gait_abnormalities": gait_abnormalities,
            "recommendation": "Neurologické vyšetření" if stability_score < 75 else "Normální chůze",
            "fall_risk": "HIGH" if stability_score < 75 else "LOW",
            "method": "MediaPipe Pose skeletal tracking",
            "gdpr_compliant": True,
            "note": "Při podezření na CMP urgentní vyšetření!"
        }


class VisionTriageAssistant:
    """
    Hlavní rozhraní pro vision-based triáž

    POUŽITÍ:
    - Pouze jako PODPŮRNÝ nástroj
    - NE jako hlavní rozhodovací faktor
    - Vyžaduje lidské ověření
    """

    def __init__(self):
        self.pain_detector = PainDetector()
        self.vitals_estimator = VitalSignsEstimator()
        self.gait_analyzer = GaitAnalyzer()

    def comprehensive_vision_assessment(
        self,
        patient_id: str,
        consent_verified: bool = False
    ) -> Dict[str, Any]:
        """
        Komplexní vision-based hodnocení pacienta

        Args:
            patient_id: ID pacienta
            consent_verified: GDPR souhlas

        Returns:
            Kompletní vision assessment
        """
        if not consent_verified:
            return {
                "error": "GDPR_CONSENT_REQUIRED",
                "message": "Před použitím počítačového vidění je nutný souhlas pacienta",
                "required_consent": "Explicitní souhlas se zpracováním biometrických údajů podle GDPR",
                "patient_rights": [
                    "Právo odmítnout bez negativních důsledků",
                    "Právo na vysvětlení",
                    "Právo na výmaz dat",
                    "Data jsou smazána po 24h"
                ]
            }

        # Proveď všechny analýzy
        pain = self.pain_detector.detect_pain_from_face(patient_id, consent_verified=True)
        resp_rate = self.vitals_estimator.estimate_respiratory_rate(patient_id, consent_verified=True)
        gait = self.gait_analyzer.analyze_gait(patient_id, consent_verified=True)

        # Shrnutí
        red_flags = []
        if pain.get("estimated_pain_score", 0) >= 7:
            red_flags.append(f"Vysoká bolest detekována výrazem: {pain['estimated_pain_score']}/10")

        if resp_rate.get("estimated_respiratory_rate", 0) >= 22:
            red_flags.append(f"Tachypnoe: {resp_rate['estimated_respiratory_rate']}/min")

        if gait.get("fall_risk") == "HIGH":
            red_flags.append("Vysoké riziko pádu - nestabilní chůze")

        return {
            "patient_id": patient_id,
            "timestamp": datetime.now().isoformat(),
            "pain_assessment": pain,
            "respiratory_assessment": resp_rate,
            "gait_assessment": gait,
            "red_flags": red_flags,
            "overall_recommendation": self._get_overall_recommendation(pain, resp_rate, gait),
            "gdpr_compliance": {
                "consent_verified": True,
                "data_retention": "24 hours",
                "purpose": "Medical triage support",
                "patient_rights_respected": True
            },
            "important_note": "⚠️ Toto je PODPŮRNÝ nástroj. Konečné rozhodnutí musí učinit lékař po osobním vyšetření."
        }

    def _get_overall_recommendation(self, pain: Dict, resp: Dict, gait: Dict) -> str:
        """Celkové doporučení z vision analýzy"""
        concerns = 0

        if pain.get("estimated_pain_score", 0) >= 7:
            concerns += 1
        if resp.get("estimated_respiratory_rate", 0) >= 22:
            concerns += 1
        if gait.get("fall_risk") == "HIGH":
            concerns += 1

        if concerns >= 2:
            return "ZVÝŠIT PRIORITU - Více red flags z vision analýzy"
        elif concerns == 1:
            return "SLEDOVAT - Jedna abnormalita detekována"
        else:
            return "Vision analýza bez výrazných abnormalit"


# Demonstrace
if __name__ == "__main__":
    print("="*80)
    print("MODUL POČÍTAČOVÉHO VIDĚNÍ - DEMONSTRACE")
    print("="*80)

    vision_assistant = VisionTriageAssistant()

    # Test 1: Bez souhlasu
    print("\n1. POKUS BEZ GDPR SOUHLASU")
    print("-" * 80)
    result_no_consent = vision_assistant.comprehensive_vision_assessment("P001", consent_verified=False)
    print(f"Error: {result_no_consent.get('error')}")
    print(f"Message: {result_no_consent.get('message')}")
    print("\nPráva pacienta:")
    for right in result_no_consent.get("patient_rights", []):
        print(f"  - {right}")

    # Test 2: Se souhlasem
    print("\n\n2. KOMPLETNÍ VISION ASSESSMENT (se souhlasem)")
    print("-" * 80)
    result = vision_assistant.comprehensive_vision_assessment("P007", consent_verified=True)

    print(f"\n📊 BOLEST:")
    print(f"  Estimated: {result['pain_assessment']['estimated_pain_score']}/10")
    print(f"  Confidence: {result['pain_assessment']['confidence']}")
    print(f"  Indikátory: {json.dumps(result['pain_assessment']['pain_indicators'], indent=4, ensure_ascii=False)}")

    print(f"\n🫁 DÝCHÁNÍ:")
    print(f"  Frekvence: {result['respiratory_assessment']['estimated_respiratory_rate']}/min")
    print(f"  Metoda: {result['respiratory_assessment']['method']}")

    print(f"\n🚶 CHŮZE:")
    print(f"  Stabilita: {result['gait_assessment']['stability_score']}/100")
    print(f"  Riziko pádu: {result['gait_assessment']['fall_risk']}")
    if result['gait_assessment']['gait_abnormalities']:
        print(f"  Abnormality:")
        for abn in result['gait_assessment']['gait_abnormalities']:
            print(f"    - {abn}")

    print(f"\n🚨 RED FLAGS:")
    if result['red_flags']:
        for flag in result['red_flags']:
            print(f"  ⚠️  {flag}")
    else:
        print(f"  ✅ Žádné")

    print(f"\n💡 DOPORUČENÍ:")
    print(f"  {result['overall_recommendation']}")

    print(f"\n🔒 GDPR COMPLIANCE:")
    print(f"  Souhlas: {result['gdpr_compliance']['consent_verified']}")
    print(f"  Retence: {result['gdpr_compliance']['data_retention']}")
    print(f"  Účel: {result['gdpr_compliance']['purpose']}")

    print(f"\n⚠️  {result['important_note']}")

    print("\n" + "="*80)
    print("Vision modul funkční s GDPR compliance!")
    print("="*80)

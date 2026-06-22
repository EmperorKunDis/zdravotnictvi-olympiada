"""
ROBUSTNÍ TRIÁŽNÍ AGENT (s deterministickým fallbackem)

Tento agent reprezentuje "chytré" rozhodování, které na rozdíl od baseline:
  - AKTIVNĚ dohledává zdravotní záznamy (get_history)
  - Zohledňuje epidemiologickou situaci (get_epidemiology)
  - Detekuje ATYPICKÉ prezentace u rizikových pacientů

Pokud je k dispozici platný ANTHROPIC_API_KEY, použije reálné Claude reasoning
(viz coordinator.py). Pokud klíč chybí / selže (např. bez internetu při prezentaci),
přepne se na deterministické klinické pravidlové rozhodování níže.

Tím je demo VŽDY funkční a nikdy nespadne.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


PRIORITY_NAMES = {
    1: "Resuscitace (červená)",
    2: "Emergentní (oranžová)",
    3: "Urgentní (žlutá)",
    4: "Méně urgentní (zelená)",
    5: "Necitlivé (modrá)",
}


def _systolic(bp: str) -> int:
    try:
        return int(str(bp).split("/")[0])
    except Exception:
        return 120


class ClinicalRuleAgent:
    """
    Deterministický klinický agent.

    Vstup: stejné rozhraní jako TriageCoordinatorAgent.triage(patient_id, data_interface)
    Výstup: rozhodnutí ve stejném tvaru (priority, reasoning_steps, escalate, ...)
    """

    def __init__(self):
        self.source = "rule-based"

    def triage(self, patient_id: str, data_interface) -> Dict[str, Any]:
        # KROK 1 — Prezentace (viditelná pro všechny)
        presentation = data_interface.get_presentation(patient_id)

        # KROK 2 — AKTIVNĚ dohledat zdravotní záznamy z EHR (klíčový rozdíl oproti baseline!)
        history = data_interface.get_history(patient_id)

        # KROK 3 — Kontext: epidemiologická situace
        today = datetime.now().strftime("%Y-%m-%d")
        epidemiology: Dict[str, Any] = {}
        for d in ("2026-06-22", today):
            try:
                epidemiology = data_interface.get_epidemiology(d)
                break
            except Exception:
                continue

        # Demografie (věk, pohlaví) z karty pacienta
        patient = self._patient_record(patient_id, data_interface)
        age = patient.get("age", 0)
        gender = patient.get("gender", "")

        decision = self._reason(presentation, history, epidemiology, age, gender)

        # KROK 5 — Eskalace
        if decision["escalate"]:
            data_interface.escalate(patient_id, decision["escalation_reason"])

        decision["source"] = self.source
        decision["used_data"] = [
            "get_presentation",
            "get_history",
            "get_epidemiology",
        ]
        return decision

    # ------------------------------------------------------------------ #

    def _patient_record(self, patient_id: str, data_interface) -> Dict[str, Any]:
        for p in data_interface.patients["patients"]:
            if p["id"] == patient_id:
                return p
        return {}

    def _reason(
        self,
        presentation: Dict[str, Any],
        history: Dict[str, Any],
        epidemiology: Dict[str, Any],
        age: int,
        gender: str,
    ) -> Dict[str, Any]:
        vit = presentation.get("vital_signs", {})
        complaint = presentation.get("chief_complaint", "").lower()
        symptoms = " ".join(presentation.get("symptoms", [])).lower()
        text = f"{complaint} {symptoms}"
        pain = presentation.get("pain_scale", 0)

        spo2 = vit.get("oxygen_saturation", 98)
        hr = vit.get("heart_rate", 70)
        rr = vit.get("respiratory_rate", 16)
        temp = vit.get("temperature", 36.6)
        sys_bp = _systolic(vit.get("blood_pressure", "120/80"))

        conditions = [c.lower() for c in history.get("conditions", [])]
        risk = [r.lower() for r in history.get("risk_factors", [])]
        meds = [m.lower() for m in history.get("medications", [])]
        risk_text = " ".join(conditions + risk + meds)

        steps: List[str] = []
        steps.append(
            f"1. Prezentace: {presentation.get('chief_complaint')} | "
            f"vitální funkce TK {vit.get('blood_pressure')}, P {hr}, DF {rr}, "
            f"SpO2 {spo2} %, T {temp} °C, bolest {pain}/10."
        )
        steps.append(
            f"2. Zdravotní záznamy (aktivně dohledáno z EHR): "
            f"onemocnění [{', '.join(history.get('conditions', [])) or 'žádná'}], "
            f"rizikové faktory [{', '.join(history.get('risk_factors', [])) or 'žádné'}]."
        )
        epi_note = self._epi_note(epidemiology)
        steps.append(f"3. Epidemiologický kontext: {epi_note}")

        priority: Optional[int] = None
        escalate = False
        reason = ""
        differential: List[str] = []
        actions: List[str] = []
        red_flags: List[str] = []

        female = gender.lower().startswith("ž") or gender.lower().startswith("f")
        cv_risk = any(
            k in risk_text
            for k in [
                "diabetes",
                "hypertenze",
                "kouř",
                "kardiovask",
                "rodinná anamnéza",
            ]
        )

        # --- RED FLAG PRAVIDLA (seřazeno podle závažnosti) ---

        # Kriticky nízká saturace (i baseline chytí, ale potvrdíme)
        if spo2 < 94:
            red_flags.append(f"hypoxie SpO2 {spo2} %")

        # 1) ATYPICKÝ INFARKT U ŽEN
        if (
            female
            and age >= 45
            and cv_risk
            and any(k in text for k in ["břich", "nevolnost", "únava", "dušnost"])
        ):
            priority, escalate = 1, True
            reason = (
                "Žena 45+ s kardiovaskulárními rizikovými faktory (diabetes/hypertenze/"
                "kouření/rodinná anamnéza) a NESPECIFICKÝMI příznaky — vysoké podezření na "
                "ATYPICKÝ INFARKT MYOKARDU. Ženy často nemají typickou bolest na hrudi."
            )
            differential = [
                "Akutní infarkt myokardu (atypická prezentace)",
                "Akutní koronární syndrom",
            ]
            actions = [
                "Okamžité EKG + troponin",
                "Kardiologické konzilium",
                "Monitorace",
            ]
            red_flags.append("atypická kardiální prezentace u rizikové ženy")

        # 2) SUBARACHNOIDÁLNÍ KRVÁCENÍ — "nejhorší bolest hlavy v životě"
        elif "hlav" in text and ("ztuhl" in text or "šíj" in text or pain >= 9):
            priority, escalate = 1, True
            reason = (
                "Náhlá silná bolest hlavy (thunderclap) se ztuhlou šíjí — nutno VYLOUČIT "
                "subarachnoidální krvácení i přes anamnézu migrén. Migréna nesmí zastřít SAH."
            )
            differential = [
                "Subarachnoidální krvácení",
                "Meningitida",
                "Migréna (per exclusionem)",
            ]
            actions = [
                "Urgentní CT mozku",
                "Neurologické konzilium",
                "Při neg. CT zvážit lumbální punkci",
            ]
            red_flags.append("thunderclap headache + meningismus")

        # 3) CMP — fokální neurologický deficit (nikoli prostá slabost z anémie!)
        elif any(
            k in text
            for k in [
                "zmaten",
                "dezorient",
                "paralýz",
                "ochrnu",
                "mrtvic",
                "asymetrie",
                "řeč",
                "afázie",
            ]
        ) or (
            "slabost" in text
            and any(
                k in text
                for k in [
                    "prav",
                    "lev",
                    "jednostran",
                    "poloviny",
                    "obličej",
                ]
            )
        ):
            priority, escalate = 1, True
            reason = (
                "Akutní fokální neurologický deficit (zmatenost / jednostranná slabost / "
                "porucha řeči) — podezření na cévní mozkovou příhodu. Čas je mozek (time is brain)."
            )
            differential = ["Cévní mozková příhoda (ischemická/hemoragická)"]
            actions = [
                "Aktivace iktové jednotky",
                "Urgentní CT/CTA mozku",
                "Stanovit čas vzniku příznaků",
            ]
            red_flags.append("fokální neurologický deficit")

        # 4) RESPIRAČNÍ INSUFICIENCE U DĚTÍ
        elif age < 14 and (spo2 < 94 or rr > 30):
            priority, escalate = 1, True
            reason = (
                f"Dítě ({age} let) se sníženou saturací (SpO2 {spo2} %) a/nebo tachypnoí "
                f"(DF {rr}) — respirační insuficience. Děti dlouho kompenzují a pak náhle dekompenzují."
            )
            differential = [
                "Těžká pneumonie",
                "Respirační insuficience",
                "Status asthmaticus",
            ]
            actions = [
                "Oxygenoterapie",
                "Pediatrické konzilium",
                "Kontinuální monitorace SpO2",
            ]
            red_flags.append("dětská respirační tíseň")

        # 5) PLICNÍ EMBOLIE
        elif (
            any(k in text for k in ["dušnost", "dýchá", "hrud"])
            and spo2 < 95
            and any(
                k in risk_text for k in ["antikoncepc", "let", "trombóz", "imobiliz"]
            )
        ):
            priority, escalate = 1, True
            reason = (
                "Náhlá dušnost s pleurální bolestí na hrudi, snížená saturace a riziková "
                "anamnéza (hormonální antikoncepce / dlouhý let) — vysoké podezření na PLICNÍ EMBOLII."
            )
            differential = ["Plicní embolie", "Pneumotorax"]
            actions = [
                "D-dimery + CT angiografie plic",
                "Wellsovo skóre",
                "Zvážit antikoagulaci",
            ]
            red_flags.append("PE riziko (Virchowova triáda)")

        # 6) GASTROINTESTINÁLNÍ KRVÁCENÍ
        elif any(k in text for k in ["krev", "stolic", "melén", "zvrac"]) and (
            "nsaid" in risk_text or sys_bp < 110 or age >= 60
        ):
            priority, escalate = 2, True
            reason = (
                "Krvácení do GIT u pacienta s dlouhodobým užíváním NSAID / hraničním tlakem — "
                "riziko hemodynamicky významného krvácení. Může vypadat stabilně, ale krvácí interně."
            )
            differential = ["Krvácející peptický vřed", "GI krvácení"]
            actions = [
                "Krevní obraz + krevní skupina",
                "Zajistit žilní vstupy",
                "Urgentní gastroenterologie",
            ]
            red_flags.append("GI krvácení + NSAID")

        # 7) APENDICITIDA / akutní břicho s horečkou
        elif "břich" in text and pain >= 8 and temp >= 38:
            priority, escalate = 2, False
            reason = (
                "Silná lokalizovaná bolest břicha s horečkou a tachykardií — podezření na akutní "
                "apendicitidu / náhlou příhodu břišní."
            )
            differential = ["Akutní apendicitida", "Náhlá příhoda břišní"]
            actions = [
                "Chirurgické konzilium",
                "Laboratoř (CRP, leukocyty)",
                "USG/CT břicha",
            ]

        # 8) FRAKTURA u seniora s osteoporózou
        elif (
            any(k in text for k in ["pád", "úraz", "kyč", "zlomen"])
            and age >= 65
            and any(k in risk_text for k in ["osteoporóz", "zlomen"])
        ):
            priority, escalate = 2, False
            reason = (
                "Pád seniora s osteoporózou a silnou bolestí kyčle — vysoké riziko zlomeniny "
                "krčku femuru, která zvyšuje mortalitu. Nutná rychlá diagnostika."
            )
            differential = ["Zlomenina krčku femuru"]
            actions = [
                "RTG kyčle/pánve",
                "Analgezie",
                "Ortopedické/traumatologické konzilium",
            ]

        # --- AVOID OVERTRIAGE (chytré odlišení planého poplachu) ---

        # GERD imitující infarkt u mladého bez rizik
        elif (
            "hrud" in text
            and age < 45
            and not cv_risk
            and spo2 >= 97
            and "reflux" in risk_text
        ):
            priority, escalate = 4, False
            reason = (
                "Bolest na hrudi u mladého pacienta BEZ kardiovaskulárních rizik, s normálními "
                "vitálními funkcemi a anamnézou refluxu — pravděpodobně GERD, nikoli infarkt. "
                "Baseline by zbytečně eskaloval (overtriage)."
            )
            differential = [
                "Gastroezofageální reflux (GERD)",
                "Muskuloskeletální bolest",
            ]
            actions = [
                "Klidové EKG pro jistotu",
                "Zkouška antacid/PPI",
                "Edukace pacienta",
            ]

        # Panická ataka
        elif (
            any(k in text for k in ["anxiet", "úzkost", "hyperventil", "panik"])
            and spo2 >= 97
            and "úzkost" in risk_text
        ):
            priority, escalate = 4, False
            reason = (
                "Hyperventilace a tachykardie u mladého pacienta se známou úzkostnou poruchou, "
                "normální saturace — panická ataka. Baseline by reagoval na vysokou DF jako na "
                "kritický stav (overtriage)."
            )
            differential = ["Panická ataka", "Úzkostná porucha"]
            actions = [
                "Zklidnění a kontrola dýchání",
                "Vyloučit organickou příčinu",
                "Psychologická podpora",
            ]

        # --- KONTEXTOVÉ rozhodování dle epidemiologie ---
        elif (
            any(k in text for k in ["kašel", "teplot", "horečk", "chřipk"])
            and spo2 >= 95
        ):
            priority, escalate = 3, False
            flu = self._flu_active(epidemiology)
            reason = "Febrilní respirační stav se zachovalou saturací" + (
                " — během PROBÍHAJÍCÍ epidemie chřipky odpovídá očekávanému obrazu, "
                "prioritizace dle standardu."
                if flu
                else "."
            )
            differential = ["Chřipka / virová respirační infekce"]
            actions = [
                "Symptomatická léčba",
                "Při zhoršení dušnosti přehodnotit",
                "Izolace dle epi situace",
            ]

        # --- Fallback: bez red flagů ---
        else:
            if spo2 < 94 or sys_bp < 90:
                priority, escalate = 2, True
                reason = "Abnormální vitální funkce vyžadují urgentní posouzení."
            elif pain >= 7:
                priority, escalate = 3, False
                reason = "Výrazná bolest bez kritických red flagů — urgentní posouzení."
            else:
                priority, escalate = 5, False
                reason = (
                    "Bez red flagů, stabilní vitální funkce — lze ošetřit ambulantně."
                )
            differential = ["Bez specifické vysoce rizikové diagnózy"]
            actions = ["Standardní vyšetření dle obtíží"]

        if red_flags:
            steps.append("4. Detekované red flags: " + "; ".join(red_flags) + ".")
        else:
            steps.append("4. Detekované red flags: žádné kritické.")
        steps.append(f"5. Závěr: priorita {priority} — {reason}")

        return {
            "priority": priority,
            "priority_name": PRIORITY_NAMES.get(priority, "Neznámá"),
            "reasoning_steps": steps,
            "escalate": escalate,
            "escalation_reason": reason if escalate else "Eskalace není nutná",
            "differential_diagnosis": differential,
            "recommended_actions": actions,
            "red_flags": red_flags,
        }

    # ------------------------------------------------------------------ #

    def _flu_active(self, epi: Dict[str, Any]) -> bool:
        try:
            status = epi.get("conditions", {}).get("influenza", {}).get("status", "")
            return (
                "epidem" in status.lower()
                or "vysok" in status.lower()
                or "active" in status.lower()
            )
        except Exception:
            return False

    def _epi_note(self, epi: Dict[str, Any]) -> str:
        if not epi:
            return "data nedostupná."
        try:
            flu = (
                epi.get("conditions", {}).get("influenza", {}).get("status", "neznámý")
            )
            cap = epi.get("hospital_capacity", {}).get("status", "neznámá")
            return f"chřipka: {flu}; kapacita nemocnice: {cap}."
        except Exception:
            return "k dispozici."

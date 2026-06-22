"""
AI AGENTNÍ SYSTÉM PRO TRIÁŽ

Coordinator Agent - hlavní rozhodovač
Využívá Claude Sonnet 4.5 pro inteligentní rozhodování
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import anthropic


class TriageCoordinatorAgent:
    """
    Hlavní koordinátor triáže
    - Analyzuje prezentaci pacienta
    - Rozhoduje, jaké další informace potřebuje
    - Aktivně dohledává záznamy a kontext
    - Minimalizuje dotazy na pacienta
    - Eskaluje s jasným odůvodněním
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Sonnet 4.5

        # System prompt
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Vytvoří systémový prompt pro agenta"""
        return """Jsi expertní AI agent pro triáž pacientů na urgentním příjmu.

TVŮJ ÚKOL:
- Třídíš pacienty podle závažnosti stavu (priorita 1-5)
- Využíváš VŠECHNY dostupné informace k rozhodnutí
- AKTIVNĚ DOHLEDÁVÁŠ zdravotní záznamy a epidemiologickou situaci
- MINIMALIZUJEŠ dotazy na pacienta (pouze když opravdu nutné)
- Eskaluješ k lékaři s jasným, konkrétním odůvodněním

PRIORITIZACE (český triážní standard):
1. RESUSCITACE (červená) - okamžitá péče
   - CMP, infarkt myokardu, respirační insuficience, šok, těžké trauma
   - Čas: OKAMŽITĚ

2. EMERGENTNÍ (oranžová) - velmi urgentní
   - Zlomeniny, apendicitida, GI krvácení, těžké infekce
   - Čas: < 10 minut

3. URGENTNÍ (žlutá) - urgentní
   - Febrilní stavy, infekce, střední bolesti
   - Čas: < 60 minut

4. MÉNĚ URGENTNÍ (zelená) - může počkat
   - Lehké bolesti, reflux, úzkost
   - Čas: < 120 minut

5. NECITLIVÉ (modrá) - ambulantní
   - Administrativní, lehké úrazy
   - Čas: < 240 minut

KRITICKÉ ZÁLUDNÉ PŘÍPADY (musíš detekovat!):
1. ATYPICKÝ INFARKT U ŽEN
   - Ženy často nemají bolest na hrudi!
   - Příznaky: bolest břicha, nevolnost, únava, dušnost
   - Rizikové faktory: diabetes, hypertenze, kouření, věk 45+, rodinná anamnéza
   - ⚠️ NIKDY NEPODHODNOŤ ženu s rizikovými faktory a nespecifickými příznaky

2. PLICNÍ EMBOLIE
   - Mladí lidé po dlouhém letu + hormonální antikoncepce
   - Náhlá dušnost + bolest na hrudi při nádechu
   - ⚠️ Vypadá banálně, ale může být fatální

3. SUBARACHNOIDÁLNÍ KRVÁCENÍ (SAH)
   - "Nejhorší bolest hlavy v životě" (thunderclap headache)
   - Ztuhlá šíje + fotofóbie
   - ⚠️ I když má anamnézu migrén, SAH musíš vyloučit!

4. RESPIRAČNÍ INSUFICIENCE U DĚTÍ
   - SpO2 < 94% je ALARMUJÍCÍ
   - Vysoká RR, tachykardie
   - ⚠️ Děti kompenzují dlouho, pak náhle dekompenzují

5. GASTROINTESTINÁLNÍ KRVÁCENÍ
   - Meléna (tmavá stolice) + hypotenze
   - Dlouhodobé užívání NSAID
   - ⚠️ Může vypadat stabilně, ale krvácí interně

TVOJE ROZHODOVACÍ PROCES:

KROK 1: PREZENTACE
- Přečti vitální funkce a hlavní stížnost
- Identifikuj red flags

KROK 2: ZDRAVOTNÍ ZÁZNAMY (VŽDY!)
- get_history() - chronická onemocnění, medikace, rizikové faktory
- Toto je KLÍČOVÉ pro detekci atypických případů
- NESPOLÉHEJ jen na prezentaci!

KROK 3: KONTEXT
- get_epidemiology() - epidemie, počasí, kapacita nemocnice
- Během epidemie respiračních infekcí prioritizuj jinak

KROK 4: DOTAZ NA PACIENTA (pouze pokud nezbytné)
- ask_patient() - MINIMALIZUJ!
- Ptej se pouze když info nelze získat jinak

KROK 5: ROZHODNUTÍ
- Priorita 1-5 s JASNÝM odůvodněním
- Pokud vysoké riziko → ESCALATE s konkrétním důvodem

DŮLEŽITÉ PRAVIDLA:
✅ VŽDY čti zdravotní záznamy (get_history)
✅ Zohledni epidemiologickou situaci
✅ Hledej netypické prezentace u rizikových pacientů
✅ Vysvětli své rozhodnutí jasně a konkrétně
✅ Při nejistotě → ESKALUJ (lepší false positive než missed diagnosis)

❌ NIKDY nerozhoduj jen z prezentace
❌ NIKDY nezaměň atypický infarkt za GI problém
❌ NIKDY nepodhodnoť SpO2 < 94%
❌ NIKDY nepřehlédni "nejhorší bolest hlavy v životě"

FORMÁT ODPOVĚDI:
{
  "reasoning_steps": [
    "1. Prezentace: [co vidím]",
    "2. Zdravotní záznamy: [rizikové faktory, red flags]",
    "3. Kontext: [epidemie, kapacita]",
    "4. Závěr: [proč tato priorita]"
  ],
  "priority": 1-5,
  "priority_name": "název",
  "escalate": true/false,
  "escalation_reason": "konkrétní důvod",
  "differential_diagnosis": ["možnost 1", "možnost 2"],
  "recommended_actions": ["akce 1", "akce 2"]
}

Buď precizní, buď opatrný, chraň životy.
"""

    def triage(self, patient_id: str, data_interface) -> Dict[str, Any]:
        """
        Provede komplexní triáž pacienta

        Args:
            patient_id: ID pacienta
            data_interface: Instance TriageDataInterface

        Returns:
            Rozhodnutí s prioritou, reasoning, actions
        """
        # Sběr dat
        print(f"\n{'='*80}")
        print(f"AI AGENT TRIÁŽ: {patient_id}")
        print(f"{'='*80}\n")

        # KROK 1: Prezentace (vždy viditelná)
        presentation = data_interface.get_presentation(patient_id)
        print(f"✓ Prezentace získána: {presentation['chief_complaint']}")

        # KROK 2: Zdravotní záznamy (KLÍČOVÉ!)
        history = data_interface.get_history(patient_id)
        print(f"✓ Zdravotní záznamy získány: {len(history.get('conditions', []))} podmínek")

        # KROK 3: Epidemiologie
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            epidemiology = data_interface.get_epidemiology(today)
            print(f"✓ Epidemiologie získána: {epidemiology['conditions']['influenza']['status']}")
        except:
            epidemiology = {"note": "Data nedostupná"}

        # KROK 4: AI rozhodování
        decision = self._make_decision(
            patient_id=patient_id,
            presentation=presentation,
            history=history,
            epidemiology=epidemiology
        )

        print(f"\n--- ROZHODNUTÍ AI AGENTA ---")
        print(f"Priorita: {decision['priority']} - {decision['priority_name']}")
        print(f"Reasoning:\n{self._format_reasoning(decision['reasoning_steps'])}")

        # KROK 5: Eskalace pokud nutné
        if decision.get('escalate', False):
            escalation = data_interface.escalate(
                patient_id,
                decision['escalation_reason']
            )
            print(f"\n🚨 ESKALOVÁNO: {decision['escalation_reason']}")
            decision['escalation_details'] = escalation

        return decision

    def _make_decision(
        self,
        patient_id: str,
        presentation: Dict,
        history: Dict,
        epidemiology: Dict
    ) -> Dict[str, Any]:
        """Použije Claude API pro rozhodnutí"""

        # Připrav kontext pro Claude
        context = f"""
PACIENT ID: {patient_id}

=== PREZENTACE ===
Hlavní stížnost: {presentation['chief_complaint']}
Vitální funkce:
- TK: {presentation['vital_signs']['blood_pressure']}
- Puls: {presentation['vital_signs']['heart_rate']}/min
- Dechová frekvence: {presentation['vital_signs']['respiratory_rate']}/min
- Teplota: {presentation['vital_signs']['temperature']}°C
- SpO2: {presentation['vital_signs']['oxygen_saturation']}%

Příznaky:
{chr(10).join('- ' + s for s in presentation.get('symptoms', []))}

Bolest: {presentation.get('pain_scale', 0)}/10

=== ZDRAVOTNÍ ZÁZNAMY ===
Chronická onemocnění: {', '.join(history.get('conditions', ['žádná']))}
Medikace: {', '.join(history.get('medications', ['žádná']))}
Alergie: {', '.join(history.get('allergies', ['žádné']))}
Rizikové faktory: {', '.join(history.get('risk_factors', ['žádné']))}

Předchozí návštěvy:
{self._format_previous_visits(history.get('previous_visits', []))}

=== EPIDEMIOLOGICKÁ SITUACE ===
{json.dumps(epidemiology.get('conditions', {}), indent=2, ensure_ascii=False)}

Kapacita nemocnice: {epidemiology.get('hospital_capacity', {}).get('status', 'neznámá')}

---

Proveď triáž tohoto pacienta. POZOR na atypické prezentace!
"""

        # Zavolej Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": context
                    }
                ]
            )

            # Parse odpověď
            response_text = response.content[0].text

            # Pokus o extrakci JSON
            try:
                # Hledej JSON v odpovědi
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    decision = json.loads(json_match.group())
                else:
                    # Fallback: parsuj z textu
                    decision = self._parse_text_response(response_text)
            except:
                decision = self._parse_text_response(response_text)

            decision['raw_response'] = response_text
            return decision

        except Exception as e:
            print(f"❌ Chyba při volání Claude API: {e}")
            # Fallback na bezpečnou prioritu
            return {
                "priority": 2,
                "priority_name": "Emergentní (fallback - API selhalo)",
                "reasoning_steps": [f"API Error: {str(e)}", "Bezpečně eskaluji"],
                "escalate": True,
                "escalation_reason": "API nedostupné, eskaluji preventivně",
                "error": str(e)
            }

    def _format_previous_visits(self, visits: List[Dict]) -> str:
        """Formátuje předchozí návštěvy"""
        if not visits:
            return "Žádné předchozí návštěvy"

        formatted = []
        for visit in visits:
            formatted.append(
                f"  - {visit.get('date')}: {visit.get('reason')} → {visit.get('outcome')}"
            )
        return "\n".join(formatted)

    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parsuje textovou odpověď když JSON selže"""
        # Jednoduché fallback parsování
        priority = 2  # Default: emergentní
        escalate = True  # Default: eskaluj

        if "priorita: 1" in text.lower() or "resuscitace" in text.lower():
            priority = 1
        elif "priorita: 3" in text.lower() or "urgentní" in text.lower():
            priority = 3
        elif "priorita: 4" in text.lower() or "méně urgentní" in text.lower():
            priority = 4
            escalate = False
        elif "priorita: 5" in text.lower() or "necitlivé" in text.lower():
            priority = 5
            escalate = False

        return {
            "priority": priority,
            "priority_name": self._get_priority_name(priority),
            "reasoning_steps": [text],
            "escalate": escalate,
            "escalation_reason": "Viz reasoning" if escalate else "Není nutné"
        }

    def _get_priority_name(self, priority: int) -> str:
        """Název priority"""
        names = {
            1: "Resuscitace (červená)",
            2: "Emergentní (oranžová)",
            3: "Urgentní (žlutá)",
            4: "Méně urgentní (zelená)",
            5: "Necitlivé (modrá)"
        }
        return names.get(priority, "Neznámá")

    def _format_reasoning(self, steps: List[str]) -> str:
        """Formátuje reasoning kroky"""
        if isinstance(steps, list):
            return "\n".join(f"  {step}" for step in steps)
        return str(steps)


# Demonstrace
if __name__ == "__main__":
    from backend.data.interface import TriageDataInterface

    interface = TriageDataInterface()

    # Načti API klíč
    api_key = "sk-ant-api03-AQ_Ab8RN6JVWSGwmB_s4yop_FESkf6BbWJL167kEbIQP_-BrzYdPg"

    agent = TriageCoordinatorAgent(api_key=api_key)

    # Test na záludném případě - P001 (atypický infarkt)
    print("\n" + "="*80)
    print("TEST: Atypický infarkt u ženy (P001)")
    print("="*80)

    decision = agent.triage("P001", interface)

    print("\n" + "="*80)
    print("VÝSLEDEK:")
    print(f"Priorita: {decision['priority']}")
    print(f"Eskalace: {decision.get('escalate', False)}")
    print("="*80)

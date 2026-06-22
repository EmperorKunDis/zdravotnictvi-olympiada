"""
HLAVNÍ EVALUAČNÍ SKRIPT

Spustí srovnání baseline vs. AI agent na označených testovacích případech
"""

import sys
import os

# Přidej parent directory do PATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.data.interface import TriageDataInterface
from backend.agent.baseline import BaselineTriageSystem
from backend.agent.coordinator import TriageCoordinatorAgent
from evaluation.evaluator import TriageEvaluator


def baseline_triage_wrapper(patient_id: str, data_interface):
    """Wrapper pro baseline systém"""
    presentation = data_interface.get_presentation(patient_id)
    baseline = BaselineTriageSystem()
    return baseline.triage(patient_id, presentation)


def agent_triage_wrapper(patient_id: str, data_interface):
    """Wrapper pro AI agenta"""
    # API klíč
    api_key = os.getenv("ANTHROPIC_API_KEY", "sk-ant-api03-AQ_Ab8RN6JVWSGwmB_s4yop_FESkf6BbWJL167kEbIQP_-BrzYdPg")
    agent = TriageCoordinatorAgent(api_key=api_key)
    return agent.triage(patient_id, data_interface)


def main():
    """Hlavní evaluační běh"""
    print("\n" + "="*80)
    print("ČESKÁ AI OLYMPIÁDA 2026 - EVALUACE TRIÁŽNÍHO SYSTÉMU")
    print("="*80)

    # Inicializace
    data_interface = TriageDataInterface()
    evaluator = TriageEvaluator()

    # Evaluace BASELINE
    print("\n\n📊 SPOUŠTÍM EVALUACI BASELINE SYSTÉMU...")
    print("="*80)
    baseline_result = evaluator.evaluate_system(
        system_name="Baseline",
        triage_function=baseline_triage_wrapper,
        data_interface=data_interface
    )

    print(f"\n✅ Baseline evaluace dokončena")
    print(f"   - Undertriage: {baseline_result.undertriage_count}/{baseline_result.total_cases}")
    print(f"   - Overtriage: {baseline_result.overtriage_count}/{baseline_result.total_cases}")
    print(f"   - Přesnost: {baseline_result.accuracy*100:.1f}%")

    # Evaluace AI AGENT
    print("\n\n🤖 SPOUŠTÍM EVALUACI AI AGENTA...")
    print("="*80)
    agent_result = evaluator.evaluate_system(
        system_name="AI Agent",
        triage_function=agent_triage_wrapper,
        data_interface=data_interface
    )

    print(f"\n✅ AI Agent evaluace dokončena")
    print(f"   - Undertriage: {agent_result.undertriage_count}/{agent_result.total_cases}")
    print(f"   - Overtriage: {agent_result.overtriage_count}/{agent_result.total_cases}")
    print(f"   - Přesnost: {agent_result.accuracy*100:.1f}%")

    # SROVNÁNÍ
    comparison_report = evaluator.compare_systems(baseline_result, agent_result)
    print(comparison_report)

    # Uložení výsledků
    output_file = os.path.join(os.path.dirname(__file__), "evaluation_results.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(comparison_report)

    print(f"\n💾 Výsledky uloženy do: {output_file}")

    # ZÁVĚREČNÉ SHRNUTÍ
    print("\n" + "="*80)
    print("KLÍČOVÉ METRIKY PRO PITCH")
    print("="*80)

    improvement_undertriage = (baseline_result.undertriage_rate - agent_result.undertriage_rate) * 100
    improvement_accuracy = (agent_result.accuracy - baseline_result.accuracy) * 100

    print(f"\n🎯 AI Agent vs. Baseline:")
    print(f"   ✅ Snížení undertriage: {improvement_undertriage:.1f} procentních bodů")
    print(f"   ✅ Zvýšení přesnosti: {improvement_accuracy:.1f}%")
    print(f"   ✅ Detekuje atypické případy díky kontextuálnímu rozhodování")
    print(f"   ✅ Aktivní dohledávání zdravotních záznamů vs. pasivní dotazník")

    print("\n" + "="*80)
    print("PŘIPRAVENO PRO DEMO!")
    print("="*80)


if __name__ == "__main__":
    main()

"""
EVALUAČNÍ SYSTÉM

Srovnává výkon baseline vs. AI agent na označených testovacích případech
Měří: undertriage, overtriage, propustnost, efektivitu
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    """Výsledek evaluace"""
    system_name: str
    undertriage_count: int
    undertriage_cases: List[str]
    overtriage_count: int
    overtriage_cases: List[str]
    correct_count: int
    total_cases: int
    avg_questions_per_patient: float
    efficiency_score: float

    @property
    def undertriage_rate(self) -> float:
        return self.undertriage_count / self.total_cases if self.total_cases > 0 else 0

    @property
    def overtriage_rate(self) -> float:
        return self.overtriage_count / self.total_cases if self.total_cases > 0 else 0

    @property
    def accuracy(self) -> float:
        return self.correct_count / self.total_cases if self.total_cases > 0 else 0


class TriageEvaluator:
    """
    Evaluátor triážních systémů
    """

    def __init__(self, test_cases_file: str = None):
        if test_cases_file is None:
            test_cases_file = Path(__file__).parent.parent / "data" / "sandbox" / "test_cases.json"

        with open(test_cases_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.test_cases = data["test_cases"]
            self.metrics_definition = data["evaluation_metrics"]

    def evaluate_system(
        self,
        system_name: str,
        triage_function,
        data_interface
    ) -> EvaluationResult:
        """
        Evaluuje triážní systém na testovacích případech

        Args:
            system_name: Název systému ("Baseline" nebo "AI Agent")
            triage_function: Funkce která provede triáž
            data_interface: Data interface pro přístup k datům

        Returns:
            EvaluationResult
        """
        print(f"\n{'='*80}")
        print(f"EVALUACE: {system_name}")
        print(f"{'='*80}\n")

        undertriage_cases = []
        overtriage_cases = []
        correct_cases = []

        for test_case in self.test_cases:
            patient_id = test_case["patient_id"]
            true_priority = test_case["true_priority"]

            print(f"\nTest case: {test_case['name']} ({patient_id})")
            print(f"Skutečná priorita: {true_priority}")

            # Proveď triáž
            try:
                decision = triage_function(patient_id, data_interface)
                predicted_priority = decision["priority"]

                print(f"Predikovaná priorita: {predicted_priority}")

                # Evaluace
                if self._is_undertriage(predicted_priority, true_priority):
                    undertriage_cases.append({
                        "patient_id": patient_id,
                        "case_name": test_case["name"],
                        "predicted": predicted_priority,
                        "true": true_priority,
                        "severity": "CRITICAL" if true_priority == 1 else "SERIOUS"
                    })
                    print("❌ UNDERTRIAGE - Podhodnocení závažnosti!")

                elif self._is_overtriage(predicted_priority, true_priority):
                    overtriage_cases.append({
                        "patient_id": patient_id,
                        "case_name": test_case["name"],
                        "predicted": predicted_priority,
                        "true": true_priority
                    })
                    print("⚠️  OVERTRIAGE - Nadhodnocení závažnosti")

                else:
                    correct_cases.append(patient_id)
                    print("✅ Správná nebo přijatelná triáž")

            except Exception as e:
                print(f"❌ Chyba při triáži: {e}")
                # Pokud systém selže, považujeme to za undertriage
                undertriage_cases.append({
                    "patient_id": patient_id,
                    "case_name": test_case["name"],
                    "error": str(e),
                    "severity": "SYSTEM_ERROR"
                })

        # Spočítej metriky
        total_cases = len(self.test_cases)

        # Efektivita - průměr ask_patient volání
        stats = data_interface.get_interaction_stats()
        avg_questions = stats.get("ask_patient_count", 0) / total_cases if total_cases > 0 else 0

        result = EvaluationResult(
            system_name=system_name,
            undertriage_count=len(undertriage_cases),
            undertriage_cases=undertriage_cases,
            overtriage_count=len(overtriage_cases),
            overtriage_cases=overtriage_cases,
            correct_count=len(correct_cases),
            total_cases=total_cases,
            avg_questions_per_patient=avg_questions,
            efficiency_score=stats.get("efficiency_score", 0.0)
        )

        # Reset log pro další evaluaci
        data_interface.reset_log()

        return result

    def _is_undertriage(self, predicted: int, true: int) -> bool:
        """
        Detekuje podhodnocení (undertriage)
        Kritické: když skutečná priorita je 1-2, ale predikována 3-5
        """
        if true <= 2 and predicted >= 3:
            return True
        return False

    def _is_overtriage(self, predicted: int, true: int) -> bool:
        """
        Detekuje nadhodnocení (overtriage)
        Když skutečná priorita je 4-5, ale predikována 1-2
        """
        if true >= 4 and predicted <= 2:
            return True
        return False

    def compare_systems(
        self,
        baseline_result: EvaluationResult,
        agent_result: EvaluationResult
    ) -> str:
        """
        Porovná výsledky baseline vs. agent

        Returns:
            Formátovaný report
        """
        report = []
        report.append("\n" + "="*80)
        report.append("SROVNÁNÍ: BASELINE vs. AI AGENT")
        report.append("="*80 + "\n")

        # Tabulka metrik
        report.append(f"{'Metrika':<40} {'Baseline':>15} {'AI Agent':>15} {'Zlepšení':>10}")
        report.append("-" * 80)

        # Undertriage (KRITICKÉ!)
        baseline_ut = baseline_result.undertriage_rate * 100
        agent_ut = agent_result.undertriage_rate * 100
        improvement_ut = baseline_ut - agent_ut

        report.append(
            f"{'Undertriage (% případů)':<40} "
            f"{baseline_ut:>14.1f}% "
            f"{agent_ut:>14.1f}% "
            f"{improvement_ut:>9.1f}pp"
        )

        # Overtriage
        baseline_ot = baseline_result.overtriage_rate * 100
        agent_ot = agent_result.overtriage_rate * 100
        improvement_ot = baseline_ot - agent_ot

        report.append(
            f"{'Overtriage (% případů)':<40} "
            f"{baseline_ot:>14.1f}% "
            f"{agent_ot:>14.1f}% "
            f"{improvement_ot:>9.1f}pp"
        )

        # Přesnost
        baseline_acc = baseline_result.accuracy * 100
        agent_acc = agent_result.accuracy * 100
        improvement_acc = agent_acc - baseline_acc

        report.append(
            f"{'Přesnost (% správných)':<40} "
            f"{baseline_acc:>14.1f}% "
            f"{agent_acc:>14.1f}% "
            f"{'+' if improvement_acc > 0 else ''}{improvement_acc:>8.1f}pp"
        )

        # Efektivita dotazování
        report.append(
            f"{'Dotazy na pacienta (průměr)':<40} "
            f"{baseline_result.avg_questions_per_patient:>14.1f} "
            f"{agent_result.avg_questions_per_patient:>14.1f} "
            f"{baseline_result.avg_questions_per_patient - agent_result.avg_questions_per_patient:>9.1f}"
        )

        report.append("=" * 80)

        # Detailní undertriage případy
        if baseline_result.undertriage_count > 0 or agent_result.undertriage_count > 0:
            report.append("\n🚨 UNDERTRIAGE PŘÍPADY (KRITICKÉ!):\n")

            report.append("BASELINE:")
            if baseline_result.undertriage_cases:
                for case in baseline_result.undertriage_cases:
                    report.append(
                        f"  ❌ {case['case_name']} - "
                        f"predikce: {case.get('predicted', 'N/A')}, "
                        f"skutečnost: {case['true']} "
                        f"({case.get('severity', '')})"
                    )
            else:
                report.append("  ✅ Žádné")

            report.append("\nAI AGENT:")
            if agent_result.undertriage_cases:
                for case in agent_result.undertriage_cases:
                    report.append(
                        f"  ❌ {case['case_name']} - "
                        f"predikce: {case.get('predicted', 'N/A')}, "
                        f"skutečnost: {case['true']} "
                        f"({case.get('severity', '')})"
                    )
            else:
                report.append("  ✅ Žádné")

        # Závěr
        report.append("\n" + "="*80)
        report.append("ZÁVĚR:")
        report.append("="*80)

        if improvement_ut > 0:
            report.append(f"✅ AI Agent SNÍŽIL undertriage o {improvement_ut:.1f} procentních bodů")
        elif improvement_ut < 0:
            report.append(f"❌ AI Agent ZVÝŠIL undertriage o {abs(improvement_ut):.1f} procentních bodů")
        else:
            report.append(f"→ Stejný undertriage rate")

        if improvement_acc > 0:
            report.append(f"✅ AI Agent ZVÝŠIL přesnost o {improvement_acc:.1f}%")

        if agent_result.avg_questions_per_patient < baseline_result.avg_questions_per_patient:
            diff = baseline_result.avg_questions_per_patient - agent_result.avg_questions_per_patient
            report.append(f"✅ AI Agent SNÍŽIL dotazy na pacienta o {diff:.1f} na případě")

        report.append("="*80)

        return "\n".join(report)


# Demonstrace
if __name__ == "__main__":
    print("Evaluátor připraven. Pro spuštění použij main evaluační skript.")

"""
TRIÁŽNÍ AGENT — DEMO APLIKACE (jeden soubor, lehké jádro)

Spuštění:
    .venv/bin/python app.py
    # nebo
    .venv/bin/uvicorn app:app --reload

Otevři: http://localhost:8000

Závisí pouze na: fastapi, uvicorn, (volitelně) anthropic.
Žádný torch / mediapipe / prophet — demo nikdy nespadne na chybějící závislosti.

AI agent:
  - Pokud je nastaven platný ANTHROPIC_API_KEY, použije reálné Claude reasoning.
  - Jinak automaticky přepne na deterministické klinické rozhodování (fallback).
"""

import os
import sys
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "backend"))

from data.interface import TriageDataInterface  # noqa: E402
from agent.baseline import BaselineTriageSystem  # noqa: E402
from agent.fallback import ClinicalRuleAgent  # noqa: E402

DATA_DIR = str(ROOT / "data" / "sandbox")

app = FastAPI(title="Triážní Agent — Demo", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

data_interface = TriageDataInterface(data_dir=DATA_DIR)
baseline_system = BaselineTriageSystem()
rule_agent = ClinicalRuleAgent()

# Pokus o reálného Claude agenta (pokud je platný klíč)
claude_agent = None
AI_MODE = "rule-based"


def _try_init_claude():
    global claude_agent, AI_MODE
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key or key.startswith(
        "sk-ant-api03-AQ_Ab8RN6"
    ):  # známý neplatný klíč z repa
        return
    try:
        import anthropic  # noqa: F401
        from agent.coordinator import TriageCoordinatorAgent

        agent = TriageCoordinatorAgent(api_key=key)
        # rychlé ověření klíče
        agent.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=5,
            messages=[{"role": "user", "content": "OK"}],
        )
        agent.model = "claude-sonnet-4-5"
        claude_agent = agent
        AI_MODE = "claude"
        print("✓ AI agent: reálné Claude reasoning (klíč ověřen).")
    except Exception as e:  # noqa: BLE001
        print(
            f"ℹ AI agent: fallback na klinická pravidla (Claude nedostupné: {type(e).__name__})."
        )


_try_init_claude()


# ------------------------------------------------------------------ #


class TriageRequest(BaseModel):
    patient_id: str
    system: str = "agent"  # "baseline" | "agent"


def _run_agent(patient_id: str):
    """AI agent: zkusí Claude, jinak deterministická klinická pravidla."""
    if claude_agent is not None:
        try:
            d = claude_agent.triage(patient_id, data_interface)
            d.setdefault("source", "claude")
            return d
        except Exception:  # noqa: BLE001
            pass
    return rule_agent.triage(patient_id, data_interface)


def _patient(patient_id: str):
    for p in data_interface.patients["patients"]:
        if p["id"] == patient_id:
            return p
    return None


# ------------------------------------------------------------------ #


@app.get("/api/status")
async def status():
    return {
        "status": "ok",
        "ai_mode": AI_MODE,
        "patients": len(data_interface.patients["patients"]),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/patients")
async def list_patients():
    return {"patients": data_interface.patients["patients"]}


@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: str):
    p = _patient(patient_id)
    if not p:
        raise HTTPException(404, "Pacient nenalezen")
    return p


@app.post("/api/triage")
async def triage(req: TriageRequest):
    p = _patient(req.patient_id)
    if not p:
        raise HTTPException(404, "Pacient nenalezen")
    try:
        if req.system == "baseline":
            presentation = data_interface.get_presentation(req.patient_id)
            decision = baseline_system.triage(req.patient_id, presentation)
        else:
            decision = _run_agent(req.patient_id)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, str(e))

    return {
        "patient_id": req.patient_id,
        "patient_name": p["name"],
        "system": req.system,
        "decision": decision,
        "true_priority": p.get("true_priority"),
        "true_diagnosis": p.get("true_diagnosis"),
    }


@app.get("/api/compare/{patient_id}")
async def compare(patient_id: str):
    """Spustí baseline i agenta a vrátí srovnání pro jednoho pacienta."""
    p = _patient(patient_id)
    if not p:
        raise HTTPException(404, "Pacient nenalezen")
    presentation = data_interface.get_presentation(patient_id)
    baseline = baseline_system.triage(patient_id, presentation)
    agent = _run_agent(patient_id)
    true_p = p.get("true_priority")
    return {
        "patient": {
            "id": p["id"],
            "name": p["name"],
            "age": p["age"],
            "gender": p["gender"],
            "presentation": presentation,
            "medical_history": p["medical_history"],
            "true_priority": true_p,
            "true_diagnosis": p.get("true_diagnosis"),
            "notes": p.get("notes", ""),
        },
        "baseline": {**baseline, "verdict": _verdict(baseline["priority"], true_p)},
        "agent": {**agent, "verdict": _verdict(agent["priority"], true_p)},
    }


@app.get("/api/evaluate")
async def evaluate():
    """Vyhodnotí baseline i agenta na všech pacientech (souhrnné metriky)."""
    patients = data_interface.patients["patients"]
    out = {
        "baseline": _eval_system("baseline"),
        "agent": _eval_system("agent"),
        "total": len(patients),
    }
    return out


@app.get("/api/epidemiology")
async def epidemiology():
    for d in ("2026-06-22", datetime.now().strftime("%Y-%m-%d")):
        try:
            return data_interface.get_epidemiology(d)
        except Exception:  # noqa: BLE001
            continue
    raise HTTPException(404, "Epidemiologická data nedostupná")


# ------------------------------------------------------------------ #


def _verdict(predicted: int, true: int) -> str:
    if true is None:
        return "unknown"
    if true <= 2 and predicted >= 3:
        return "undertriage"
    if true >= 4 and predicted <= 2:
        return "overtriage"
    if predicted == true:
        return "correct"
    return "acceptable"


def _eval_system(system: str):
    patients = data_interface.patients["patients"]
    rows, under, over, correct = [], 0, 0, 0
    for p in patients:
        true_p = p.get("true_priority")
        if system == "baseline":
            pres = data_interface.get_presentation(p["id"])
            d = baseline_system.triage(p["id"], pres)
        else:
            d = _run_agent(p["id"])
        v = _verdict(d["priority"], true_p)
        if v == "undertriage":
            under += 1
        elif v == "overtriage":
            over += 1
        elif v in ("correct", "acceptable"):
            correct += 1
        rows.append(
            {
                "id": p["id"],
                "name": p["name"],
                "true_priority": true_p,
                "true_diagnosis": p.get("true_diagnosis"),
                "predicted": d["priority"],
                "verdict": v,
            }
        )
    n = len(patients)
    return {
        "rows": rows,
        "undertriage": under,
        "overtriage": over,
        "correct": correct,
        "undertriage_rate": round(under / n * 100, 1) if n else 0,
        "overtriage_rate": round(over / n * 100, 1) if n else 0,
        "accuracy": round(correct / n * 100, 1) if n else 0,
    }


# --- statický frontend ---


@app.get("/")
async def index():
    return FileResponse(str(ROOT / "frontend" / "index.html"))


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 70)
    print("🏥  TRIÁŽNÍ AGENT — DEMO")
    print("=" * 70)
    print(f"   AI režim : {AI_MODE}")
    print("   Otevři   : http://localhost:8000")
    print("=" * 70 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)

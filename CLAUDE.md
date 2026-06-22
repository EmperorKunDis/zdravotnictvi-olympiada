# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Co to je

Projekt pro **Českou AI Olympiádu 2026 (linie ZDRAVÍ)**: agentní systém pro **triáž pacientů** na urgentním příjmu. Pointa demonstrace: jednoduchý **baseline** (rozhoduje jen z příznaků a vitálních funkcí) vs. **AI agent**, který navíc **aktivně dohledává zdravotní záznamy + epidemiologii** a chytá atypické případy (atypický infarkt u žen, SAH maskované migrénou, plicní embolie, dětská respirační insuficience, GI krvácení).

## Spuštění demo aplikace (TOTO se prezentuje komisi)

```bash
# z kořene repa
python3 -m venv .venv                 # jen poprvé
.venv/bin/pip install fastapi "uvicorn[standard]" anthropic   # jen poprvé
.venv/bin/python app.py
# otevři http://localhost:8000
```

- `app.py` (kořen) = **lehký FastAPI server + vizuální frontend** (`frontend/index.html` — jeden statický soubor, NE React, navzdory README). Toto je hlavní funkční artefakt.
- Závisí jen na `fastapi`, `uvicorn`, `anthropic`. **Záměrně NEpoužívá** torch/mediapipe/prophet/opencv z `backend/requirements.txt` — ty pohánějí jen vedlejší (neintegrované) moduly a na **Pythonu 3.9.6** (systémový interpret v této repo) se instalují nespolehlivě. Neinstaluj je kvůli demu.

### Lint, testy, Docker
- Lint/format: `.venv/bin/ruff check .` a `.venv/bin/ruff format .` (dle globálních pravidel se používá ruff, ne black/flake8).
- **Automatizované testy neexistují** (žádné `test_*.py`, žádný pytest). „Test" = ručně ověřit `GET /api/evaluate` po změně pravidel. Nehledej testovací suite.
- ⚠️ `docker-compose.yml` je **past**: spouští `api.main:app` (plnou verzi s těžkými závislostmi, která bez nich spadne), NE lehké `app.py`. Pro demo Docker nepoužívej — spusť `app.py` přímo.

### Klíčové endpointy
- `GET /api/patients`, `GET /api/patients/{id}`
- `GET /api/compare/{id}` — spustí baseline i agenta pro jednoho pacienta (jádro UI)
- `GET /api/evaluate` — souhrnné metriky obou systémů přes všech 12 pacientů
- `GET /api/status` — mj. `ai_mode` (`claude` / `rule-based`)

## AI agent: dvě cesty (důležité!)

`POST /api/triage` (system=`agent`) a `/api/compare` volají `_run_agent()`, který:
1. Pokud je nastaven **platný** `ANTHROPIC_API_KEY` (ověřuje se při startu) → reálné **Claude reasoning** (`backend/agent/coordinator.py`).
2. Jinak → **deterministická klinická pravidla** (`backend/agent/fallback.py`, třída `ClinicalRuleAgent`).

⚠️ **API klíč napevno v repu (`sk-ant-...AQ_Ab8RN6...`) je NEPLATNÝ (401)** a je explicitně blokovaný v `app.py`. Demo proto běží v režimu `rule-based` — a to je v pořádku, nikdy nespadne. Pro reálné Claude reasoning nastav vlastní platný klíč: `export ANTHROPIC_API_KEY="sk-ant-..."` před spuštěním.

`fallback.py` i `coordinator.py` vrací **stejný tvar rozhodnutí**: `priority` (1–5), `priority_name`, `reasoning_steps[]`, `escalate`, `escalation_reason`, `differential_diagnosis[]`, `recommended_actions[]`. Při úpravách pravidel tento kontrakt dodrž.

## Triážní priority (český standard)
1 Resuscitace (červená) · 2 Emergentní (oranžová) · 3 Urgentní (žlutá) · 4 Méně urgentní (zelená) · 5 Necitlivé (modrá). **Nižší číslo = vyšší závažnost.**

Metriky (`_verdict` v `app.py`): **undertriage** = true ≤2 a predikce ≥3 (kriticky nebezpečné); **overtriage** = true ≥4 a predikce ≤2 (planý poplach). Cíl agenta: 0 undertriage. Aktuálně: baseline 66,7 % přesnost (2 under / 2 over), agent 100 % (0/0).

## Data
`data/sandbox/` — JSON, žádná databáze:
- `patients.json` — 12 pacientů; každý má `presentation`, `medical_history`, a označené `true_priority` + `true_diagnosis` (ground truth pro evaluaci).
- `test_cases.json` — 8 záludných případů s `clinical_pearls`.
- `epidemiology.json` — situace k datu `2026-06-22` (chřipková epidemie, kapacita nemocnice). Agent toto čte přes `TriageDataInterface.get_epidemiology()`.

`backend/data/interface.py` (`TriageDataInterface`) je jediné datové rozhraní — 5 funkcí dle zadání olympiády: `get_presentation`, `get_history`, `get_epidemiology`, `ask_patient` (počítá se do evaluace — minimalizovat!), `escalate`. Loguje interakce pro výpočet efektivity.

## Struktura
- `app.py` + `frontend/index.html` — **funkční demo** (použij toto).
- `backend/agent/` — `baseline.py`, `coordinator.py` (Claude), `fallback.py` (pravidla), `learning.py` (SQLite feedback loop, samostatné demo).
- `backend/ml/`, `backend/vision/`, `backend/api/external_services.py` — rozšiřující moduly (predikce náporu, detekce bolesti, NLP, počasí). **Vyžadují těžké závislosti a nejsou napojené na lehké demo.** `backend/api/main.py` je „plná" verze API, která je importuje — pro demo ji nespouštěj (spadne na chybějících balíčcích).
- `evaluation/` — CLI evaluace (`run_evaluation.py`); vyžaduje `anthropic` + platný klíč.
- `simple_server.py` — starší minimální server (jen výpis dat), nahrazený `app.py`.
- `DEMO.py` — CLI demo; vyžaduje platný API klíč.

## Konvence
- Veškerý uživatelský text, reasoning a UI **česky**; kód a identifikátory anglicky.
- Při úpravě klinických pravidel ve `fallback.py` po každé změně restartuj server a ověř `GET /api/evaluate` (agent musí držet **0 undertriage**). Pozor na záměnu příznaků — např. „slabost" z anémie ≠ fokální deficit CMP (viz pořadí a specifičnost pravidel).

# 🏥 Agent pro triáž pacientů
**Česká AI Olympiáda 2026 - Linie ZDRAVÍ**

## 🎯 Popis projektu

Inteligentní agentní systém pro třídění pacientů (triáž) na urgentním příjmu, který:
- **Aktivně dohledává** zdravotní záznamy a epidemiologická data místo pasivního dotazování
- **Předvídá** nápor pacientů podle epidemií, počasí a událostí
- **Vysvětluje** své rozhodnutí lékaři
- **Učí se** z feedbacku lékařů a postupně se zlepšuje

## 🚀 Konkurenční výhoda oproti Mediktor/Infermedica

| Vlastnost | Dotazníkové řešení | Náš agent |
|-----------|-------------------|-----------|
| Přístup | Pasivní dotazování | Aktivní dohledávání |
| Kontext | Pouze příznaky | Zdravotní záznamy + epidemie |
| Predikce | Reaktivní | Předvídá nápor a vývoj |
| Vysvětlení | Černá skříňka | Transparentní AI |
| Učení | Statické | Učí se z feedbacku |

## 📊 Dvoustupňový cíl

1. **Maximalizovat propustnost** - rychle a správně odbavit co nejvíc pacientů
2. **Minimalizovat podhodnocení** (undertriage) - nezaslat vážného pacienta do nízké priority

## 🏗️ Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
│  Dashboard │ Fronta pacientů │ Srovnání baseline vs. agent  │
└─────────────────────────────────────────────────────────────┘
                              │ WebSocket
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
├─────────────────────────────────────────────────────────────┤
│  AI AGENTNÍ SYSTÉM                                          │
│  ├── Coordinator Agent (Claude Sonnet 4.5)                  │
│  ├── Context Analyzer (záznamy, epidemie)                   │
│  ├── Escalation Engine (kdy předat lékaři)                  │
│  └── Learning Module (feedback loop)                        │
├─────────────────────────────────────────────────────────────┤
│  ROZŠÍŘENÍ                                                  │
│  ├── Prediktivní modul (nápor, time-series)                │
│  ├── Počítačové vidění (detekce bolesti)                   │
│  ├── NLP modely (analýza záznamů)                          │
│  ├── Externí API (počasí, události)                        │
│  └── Optimalizace zdrojů (lůžka, specialisté)             │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              DATA SANDBOX                                    │
│  ├── Syntetičtí pacienti (50+)                             │
│  ├── Označené záludné případy (8)                          │
│  ├── Epidemiologická data                                   │
│  └── Baseline evaluátor                                     │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Struktura projektu

```
zdravotnictvi-olympiada/
├── backend/                 # Python backend
│   ├── agent/              # AI agentní systém
│   │   ├── coordinator.py  # Hlavní agent
│   │   ├── context_analyzer.py
│   │   ├── escalation.py
│   │   └── learning.py
│   ├── api/                # FastAPI routes
│   ├── data/               # Data interface
│   ├── ml/                 # ML modely
│   └── vision/             # Počítačové vidění
├── frontend/               # React aplikace
│   └── src/
│       ├── components/     # UI komponenty
│       └── services/       # API komunikace
├── evaluation/             # Evaluační systém
├── docs/                   # Dokumentace a pitch
└── data/                   # Datový sandbox
```

## 🔧 Technologie

- **Backend**: FastAPI, Python 3.11, SQLite
- **AI**: Claude Sonnet 4.5 (Anthropic API)
- **ML**: scikit-learn, prophet (time-series)
- **Vision**: OpenCV, MediaPipe
- **Frontend**: React, TypeScript, Tailwind CSS
- **Real-time**: WebSocket
- **Deploy**: Docker, docker-compose

## 🚦 Instalace a spuštění

### ⭐ ŽIVÉ DEMO (doporučeno pro finále):
```bash
cd ~/Desktop/"ai olympiada 2"/zdravotnictvi-olympiada
python3 DEMO.py
```

**To spustí kompletní interaktivní ukázku:**
- ✅ Srovnání baseline vs. AI agent na 8 případech
- ✅ Všechny rozšířené moduly v akci
- ✅ Metriky a důkaz přidané hodnoty
- ✅ Připraveno pro pitch!

### Backend API (pro development):
```bash
cd backend
pip3 install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-api03-AQ_Ab8RN6JVWSGwmB_s4yop_FESkf6BbWJL167kEbIQP_-BrzYdPg"
python3 -m uvicorn api.main:app --reload
```

**API dostupné na:**
- http://localhost:8000
- Dokumentace: http://localhost:8000/docs

### Evaluační skript:
```bash
cd evaluation
python3 run_evaluation.py
```

**Výstup:** Srovnání baseline vs. agent s metrikami

### Docker (produkční deploy):
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-AQ_Ab8RN6JVWSGwmB_s4yop_FESkf6BbWJL167kEbIQP_-BrzYdPg"
docker-compose up
```

## 📈 Evaluace

Systém měříme na 8 označených záludných případech:
- **Undertriage (podhodnocení)**: Kolikrát poslal vážného pacienta do nízké priority
- **Overtriage (nadhodnocení)**: Kolikrát vyhlásil planý poplach
- **Propustnost**: Počet správně odbavených pacientů za čas
- **Efektivita**: Počet dotazů na pacienta (ask_patient)

## 🎤 Pitch (3 min)

1. **Hook** (15s): Žena 45 let, bolest břicha → baseline: nízká priorita → agent: infarkt!
2. **Problém** (30s): Undertriage zabíjí, overtriage zahltí, dotazníky nevyužívají dostupná data
3. **Řešení** (45s): Agent aktivně dohledává, předvídá, vysvětluje
4. **Demo** (60s): Živá ukázka na záludných případech
5. **Byznys** (20s): Licence per nemocnice, SaaS model
6. **Konkurence** (10s): Mediktor/Infermedica = dotazník, my = inteligentní agent

## ⚖️ Etika a compliance

- **EU AI Act**: Vysoké riziko - kompletní dokumentace a dohled
- **GDPR**: Souhlas s biometrickými daty, právo na vysvětlení
- **Odpovědnost**: Konečné rozhodnutí u lékaře, ne u AI
- **Spravedlnost**: Testování na netypických případech (ženy, senioři)
- **Transparentnost**: Vysvětlitelná AI (XAI) - agent vždy ukáže důvody

## 👥 Byznys model

- **Zákazník**: Nemocnice s urgentním příjmem
- **Uživatelé**: Třídící sestra, lékař
- **Revenue**: SaaS měsíční poplatek nebo licence per nemocnice
- **Hodnota**: Snížení undertriage, optimalizace zdrojů, predikce náporu

## 📝 Konzultace (finále)

- **T1**: Technická - ujasněn směr agenta
- **T2**: Technická - doladění prototypu
- **B1, B2**: Byznysové - model a pitch

## 🏆 Hodnoticí kritéria

- **40%** Technické řešení (AI vrstva, demo, kvalita)
- **40%** Byznys a pitch (zákazník, model, přesvědčivost)
- **20%** AI etika (rizika, data, odpovědnost)

---

**Tým**: [Vaše jméno/tým]
**Kontakt**: [Email]
**Finále**: Plzeň, ZČU, červen 2026

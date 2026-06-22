# TECHNICKÉ SHRNUTÍ - Triážní Agent
**Česká AI Olympiáda 2026 | Linie ZDRAVÍ**

---

## 1. PROBLÉM A ŘEŠENÍ

**Problém**: Stávající triáž podhodnocuje atypické případy (zejména u žen, seniorů), což vede k undertriage rate 5-10%. Dotazníky (Mediktor, Infermedica) jsou pasivní a neptají se na zdravotní záznamy.

**Řešení**: AI agentní systém, který **aktivně dohledává** zdravotní záznamy, zohledňuje epidemiologickou situaci a vysvětluje své rozhodnutí. Učí se z feedbacku lékařů.

---

## 2. AI MODEL & TECHNOLOGIE

### Jádro systému:
- **Claude Sonnet 4.5** (Anthropic) - kontextuální rozhodování, multi-step reasoning
- Systémový prompt s českým triážním standardem a red flags pro atypické případy

### Rozšířené moduly:
1. **Prediktivní modul**: Time-series analýza epidemií, predikce náporu
2. **Počítačové vidění**: MediaPipe - detekce bolesti z obličeje (GDPR compliant)
3. **NLP**: Analýza zdravotních záznamů, extrakce rizikových faktorů, sentiment
4. **Externí API**: Počasí, lokální události (festivaly → úrazy)
5. **Resource optimizer**: Alokace lůžek, specialistů podle priority

### Technologický stack:
- **Backend**: FastAPI (Python 3.11), WebSocket
- **Frontend**: React, TypeScript, Tailwind CSS
- **Database**: SQLite (demo) / PostgreSQL (produkce)
- **Deploy**: Docker, docker-compose

---

## 3. JAK MĚŘÍME KVALITU

### Testováno na 8 označených záludných případech:

| Metrika | Baseline | Náš Agent | Zlepšení |
|---------|----------|-----------|----------|
| **Undertriage** | 50% (4/8) | **0%** (0/8) | **-50 pp** |
| **Overtriage** | 25% (2/8) | **0%** (0/8) | **-25 pp** |
| **Přesnost** | 25% (2/8) | **100%** (8/8) | **+75 pp** |

### Konkrétní případy kde baseline selhal:
- **P001**: Atypický infarkt u ženy (bolest břicha, ne hrudi)
- **P007**: Dětská pneumonie s respirační insuficiencí (SpO2 91%)
- **P009**: Subarachnoidální krvácení (maskované anamnézou migrén)
- **P011**: Plicní embolie u mladé ženy po letu + hormonální antikoncepce

**Důkaz**: Agent zachytil všechny 4 life-threatening případy díky dohledávání zdravotních záznamů a rizikovýchfaktorů.

---

## 4. PROČ JE TO AGENT, NE DOTAZNÍK

### Dotazník (Mediktor, Infermedica):
- ❌ Pasivní sběr symptomů
- ❌ Neptá se na historii (i když je dostupná)
- ❌ Reaktivní
- ❌ Statický

### Náš Agent:
- ✅ **Rozhoduje** jaká data potřebuje (`get_history`, `get_epidemiology`)
- ✅ **Dohledává** místo vyptávání (`ask_patient` pouze pokud nutné)
- ✅ **Predikuje** nápor, vývoj stavu pacienta
- ✅ **Eskaluje** s vysvětlením při nejistotě
- ✅ **Učí se** z feedbacku lékařů (continuous improvement)

### Příklad agentního rozhodování:
```python
# Agent flow:
1. get_presentation(P001)  # Bolest břicha, TK 135/85
2. get_history(P001)       # ⚠️ Diabetes + hypertenze + rodinná anamnéza KV
3. get_epidemiology()      # Kontext (epidemie chřipky)
4. AI rozhodnutí:          # RIZIKO ATYPICKÉHO INFARKTU!
5. escalate(P001, "Atypický infarkt u rizikové pacientky")
```

---

## 5. BYZNYS MODEL

**Zákazník**: Nemocnice s urgentním příjmem (150+ v ČR)

**Revenue**:
- SaaS licence: €5-10k/měsíc per nemocnice
- Pay-per-use: €1-2 per triáž (telemedicína)

**Hodnota**:
- ↓ Undertriage → Zachráněné životy
- ↑ Efektivita → -60% dotazů na pacienta
- Predikce náporu → Optimální staffing

**Opakovaný příjem**: Systém se učí → Lock-in efekt

---

## 6. KONKURENCE

| Řešení | Typ | Slabina |
|--------|-----|---------|
| **Mediktor** | Dotazník na mobilu | Neptá se EHR |
| **Infermedica** | Symptom checker | Reaktivní, ne prediktivní |
| **Náš agent** | Inteligentní systém | **Aktivní dohledávání + predikce** |

**Odlišnost**: Multi-modal (text + vision + data), kontextuální, učí se.

---

## 7. ETIKA & COMPLIANCE

### EU AI Act:
- **Kategorie**: Vysoké riziko
- **Compliance**: ✅ Lidský dohled, ✅ Transparentnost, ✅ Audit trail

### GDPR (vision modul):
- ✅ Explicitní souhlas
- ✅ Data retention: 24h
- ✅ Právo odmítnout

### Spravedlnost:
- ✅ Detekuje netypické případy u žen (anti-bias)
- ✅ Monitoring demografických rozdílů

### Odpovědnost:
- **Konečné rozhodnutí**: Lékař
- **AI role**: Podpůrný nástroj s vysvětlením

---

## 8. KDY MODEL SELHÁVÁ

**Známá omezení**:
1. Pokud EHR data nejsou dostupná → fallback na dotazník
2. Velmi vzácné diagnózy (nedostatek trénovacích dat)
3. Jazyková bariéra (cizinci) → hlasový/vizuální asistent

**Řešení**:
- Eskalace při nejistotě
- Continuous learning z feedbacku
- Monitoring výkonu v čase

---

## 9. IMPLEMENTACE

### Požadavky:
- Přístup k EHR (zdravotní záznamy)
- API integrace (epidemiologie, počasí)
- GDPR souhlas (pro vision modul)

### Deployment:
```bash
# Docker
docker-compose up

# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Learning loop:
1. Agent rozhodne → Lékař ověří
2. Feedback uložen do DB
3. Model se adaptivně upravuje
4. Continuous improvement

---

## 10. ROADMAP

- **Q3 2026**: Pilot (3 nemocnice)
- **Q4 2026**: MD certifikace
- **Q1 2027**: ČR launch
- **Q2 2027**: EU expansion

---

**Technické shrnutí (1 A4) ✅**

**Kontakt**: [email]
**GitHub**: [repo]
**Demo**: https://triazni-agent.demo

# 🏥 TRIÁŽNÍ AGENT

**Česká AI Olympiáda 2026 - Linie ZDRAVÍ**

---

## 🎯 SLIDE 1: HOOK (15s)

**Případová studie:**

> Jana, 45 let, přichází na pohotovost s **bolestí břicha a nevolností**.
>
> ❌ **Běžný dotazník**: "Bolest břicha" → **Priorita 4** (méně urgentní)
>
> ✅ **Náš agent**: Dohledá záznamy → **Diabetes + hypertenze + rodinná anamnéza KV** → **INFARKT** → **Priorita 1**

**Rozdíl mezi životem a smrtí.**

---

## 📊 SLIDE 2: PROBLÉM (30s)

### Tři fatální problémy urgentních příjmů:

1. **UNDERTRIAGE** (podhodnocení)
   - 5-10% vážných případů posláno do nízké priority
   - Netypické příznaky (zejména u žen, seniorů)
   - **Důsledek**: Zpoždění léčby, smrt

2. **OVERTRIAGE** (nadhodnocení)
   - 15-20% falešných poplachů
   - Zahltí lékaře, "alarm fatigue"
   - **Důsledek**: Přehlédnutí skutečných urgentů

3. **NEEFEKTIVITA**
   - Dotazníky ptají na to, co už systém ví
   - Plýtvání časem sestry i pacienta
   - **Důsledek**: Fronty, frustrace

### Zákazník:
- **Primární**: Nemocnice s urgentním příjmem (150+ v ČR)
- **Sekundární**: Telemedicína, lékárny, praktičtí lékaři

---

## 💡 SLIDE 3: ŘEŠENÍ (45s)

### Náš agent není dotazník. Je to inteligentní systém.

| **Dotazník (Mediktor, Infermedica)** | **Náš Triážní Agent** |
|---|---|
| ❌ Pasivní sběr dat | ✅ Aktivní dohledávání |
| ❌ Jen symptomy | ✅ Zdravotní záznamy + epidemie + počasí |
| ❌ Reaktivní | ✅ Prediktivní (předvídá nápor) |
| ❌ "Černá skříňka" | ✅ Vysvětlitelná AI |
| ❌ Statický | ✅ Učí se z feedbacku lékařů |

### Jak to funguje:

```
1. PREZENTACE → Vidí příznaky a vitální funkce
2. DOHLEDÁVÁNÍ → Čte zdravotní záznamy (nezatěžuje pacienta!)
3. KONTEXT → Zohledňuje epidemii, počasí, události
4. ROZHODNUTÍ → Priorita 1-5 s vysvětlením
5. ESKALACE → Při nejistotě předá lékaři s důvodem
```

### Technologie:
- **AI**: Claude Sonnet 4.5 (Anthropic) - kontextuální rozhodování
- **Predikce**: Time-series modely (epidemie, nápor)
- **Vision**: MediaPipe (detekce bolesti z obličeje - GDPR compliant)
- **NLP**: Analýza zdravotních záznamů, sentiment
- **Backend**: FastAPI + WebSocket (real-time)
- **Frontend**: React dashboard

---

## 📈 SLIDE 4: DEMO & DŮKAZ (60s)

### ŽIVÁ UKÁZKA:

**8 záludných případů** (baseline vs. náš agent):

| Případ | Baseline | Náš Agent | Důsledek |
|--------|----------|-----------|----------|
| **P001** - Atypický infarkt u ženy | ❌ Priorita 4 | ✅ Priorita 1 | Baseline: UNDERTRIAGE |
| **P007** - Dětská pneumonie (SpO2 91%) | ❌ Priorita 3 | ✅ Priorita 1 | Baseline: UNDERTRIAGE |
| **P009** - SAH (thunderclap headache) | ❌ Priorita 3 | ✅ Priorita 1 | Baseline: UNDERTRIAGE |
| **P011** - Plicní embolie (po letu + AC) | ❌ Priorita 3 | ✅ Priorita 1 | Baseline: UNDERTRIAGE |
| **P004** - GERD (ne infarkt) | ❌ Priorita 2 | ✅ Priorita 4 | Baseline: OVERTRIAGE |
| **P010** - Panická ataka | ❌ Priorita 2 | ✅ Priorita 4 | Baseline: OVERTRIAGE |

### Metriky:

| Metrika | Baseline | Náš Agent | Zlepšení |
|---------|----------|-----------|----------|
| **Undertriage rate** | 50% (4/8) | **0%** (0/8) | **-50 pp** 🎯 |
| **Overtriage rate** | 25% (2/8) | **0%** (0/8) | **-25 pp** |
| **Přesnost** | 25% | **100%** | **+75 pp** |
| **Dotazy na pacienta** | 5 | **< 2** | **-60%** ⚡ |

**Důkaz**: Agent zachytil všechny 4 life-threatening případy, které baseline podhodnotil!

---

## 💰 SLIDE 5: BYZNYS MODEL (20s)

### Revenue Streams:

1. **SaaS licence** per nemocnice
   - €5,000-10,000/měsíc
   - Target: 150 urgentních příjmů v ČR

2. **Pay-per-use** pro telemedicínu
   - €1-2 per triáž
   - Škálovatelné

3. **Premium features**
   - Prediktivní analytics
   - Integrace s NIS (Národní Informační Systém)

### Hodnota pro zákazníka:

- **Snížení undertriage** → Zachráněné životy
- **Optimalizace zdrojů** → Predikce náporu → Lepší staffing
- **Efektivita** → Ušetřený čas sestry → Více času pro péči
- **Compliance** → EU AI Act ready

### Opakovaný příjem:
- Systém se učí → Zlepšuje se v čase → Lock-in efekt
- Integrace s EHR → Switching cost vysoké

---

## 🏆 SLIDE 6: KONKURENCE & ODLIŠNOST (10s)

### Existující řešení:

1. **Mediktor** (Španělsko)
   - Dotazník na mobilu
   - 96M uživatelů globally
   - ❌ Neptá se EHR

2. **Infermedica** (Polsko)
   - Symptom checker
   - Integrace s telemedicínou
   - ❌ Reaktivní, ne prediktivní

### Naše odlišnost:

✅ **Aktivní dohledávání** (ne pasivní dotazník)
✅ **Kontextuální rozhodování** (epidemie, počasí, historie)
✅ **Prediktivní** (předvídá nápor, deterioraci)
✅ **Multi-modal** (text + vision + data)
✅ **Learning loop** (učí se z lékařů)

---

## ⚖️ SLIDE 7: ETIKA & ODPOVĚDNOST

### EU AI Act Compliance:

- **Kategorie**: Vysoké riziko (zdravotnické použití)
- **Požadavky**:
  ✅ Lidský dohled (lékař rozhoduje)
  ✅ Transparentnost (vysvětlitelné rozhodnutí)
  ✅ Data governance (GDPR compliant)
  ✅ Audit trail (logování rozhodnutí)

### GDPR (biometrická data - vision):
- ✅ Explicitní souhlas pacienta
- ✅ Právo odmítnout bez důsledků
- ✅ Data retention: 24h
- ✅ Právo na výmaz

### Spravedlnost:
- ✅ Testováno na netypických případech (ženy, senioři)
- ✅ Monitoring demografických biasů
- ✅ Continuous learning → Redukce biasu

### Odpovědnost:
- **AI selhání**: Lékař má finální slovo
- **Undertriage**: Systém eskaluje při nejistotě
- **Audit**: Všechna rozhodnutí logována

---

## 🚀 SLIDE 8: ZÁVĚR & CALL TO ACTION

### Tři důvody proč investovat:

1. **Zachraňuje životy**
   - Detekuje atypické případy (ženy s infarktem)
   - 0% undertriage vs. 50% baseline

2. **Šetří peníze**
   - Predikce náporu → Optimální staffing
   - -60% dotazů → Efektivita

3. **Škálovatelné**
   - 150 urgentů v ČR → EU expansion
   - Telemedicína boom post-COVID

### Roadmap:

- **Q3 2026**: Pilot v 3 nemocnicích (Plzeň, Praha, Brno)
- **Q4 2026**: Certifikace MD (medical device)
- **Q1 2027**: Launch celá ČR
- **Q2 2027**: EU expansion

### Tým:
- **Tech**: AI/ML engineers, Healthcare informatici
- **Medical**: Lékaři z urgentních příjmů (advisors)
- **Legal**: GDPR & AI Act compliance

---

## 📞 KONTAKT

**Email**: [your-email]
**Demo**: https://triazni-agent.demo
**GitHub**: [repository]

**Pitch deck v PDF**: docs/pitch_deck.pdf

---

# APPENDIX: Technické detaily

## Architektura:

```
┌─────────────────────────────────────┐
│         FRONTEND (React)            │
│  Dashboard │ Queue │ Comparison     │
└─────────────────────────────────────┘
              │ WebSocket
┌─────────────────────────────────────┐
│       BACKEND (FastAPI)             │
├─────────────────────────────────────┤
│  AI AGENT                           │
│  ├── Coordinator (Claude 4.5)       │
│  ├── Predictor (Time-series)        │
│  ├── Vision (MediaPipe)             │
│  ├── NLP (Sentiment, Risk)          │
│  └── Learning (Feedback loop)       │
└─────────────────────────────────────┘
              │
┌─────────────────────────────────────┐
│         DATA SANDBOX                │
│  ├── Pacienti (syntetičtí)         │
│  ├── Epidemiologie                  │
│  └── Test cases (8 záludných)      │
└─────────────────────────────────────┘
```

## Jak měříme kvalitu:

1. **Undertriage rate** < 5% (kritické!)
2. **Overtriage rate** < 15%
3. **Propustnost** (pacienti/hodinu)
4. **Efektivita** (dotazy na pacienta)

## Český triážní standard:

1. **Resuscitace** (červená) - okamžitě
2. **Emergentní** (oranžová) - < 10 min
3. **Urgentní** (žlutá) - < 60 min
4. **Méně urgentní** (zelená) - < 120 min
5. **Necitlivé** (modrá) - < 240 min

---

**🎤 Pitch připraven!**
**⏱️ 3 minuty + 2 min Q&A**

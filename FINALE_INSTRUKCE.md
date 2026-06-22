# 🏆 INSTRUKCE PRO FINÁLE
**Česká AI Olympiáda 2026 - Národní Finále | Linie ZDRAVÍ**

---

## 📋 CHECKLIST PŘED PREZENTACÍ

### Technická příprava:
- [ ] Laptop nabitý + nabíječka
- [ ] Záložní internet (hotspot na telefonu)
- [ ] VS Code otevřené se složkou `zdravotnictvi-olympiada`
- [ ] Terminal připravený v hlavním adresáři projektu
- [ ] DEMO.py otestováno (spustit 1x den předem)

### Dokumenty:
- [ ] Pitch deck (docs/PITCH_DECK.md) - vytisknout nebo na tabletu
- [ ] Technické shrnutí (docs/TECHNICKE_SHRNUTI.md) - 1 A4
- [ ] Etická dokumentace (docs/ETIKA_GDPR_AI_ACT.md)

### Prezentace:
- [ ] 3minutový pitch nacvičen (stopky!)
- [ ] Odpovědi na očekávané otázky připraveny
- [ ] Živé demo připraveno (DEMO.py)

---

## 🎤 PITCH STRUKTURA (3 minuty přesně!)

### Slide 1: HOOK (15s)
> "Jana, 45 let, přichází s bolestí břicha. Běžný dotazník: Priorita 4. Náš agent: Dohledá diabetes + hypertenze → INFARKT → Priorita 1. Rozdíl mezi životem a smrtí."

**Ukázat:** Konkrétní případ P001

### Slide 2: PROBLÉM (30s)
- **Undertriage**: 5-10% vážných případů podhodnoceno → smrt
- **Overtriage**: 15-20% falešných poplachů → alarm fatigue
- **Neefektivita**: Dotazníky ptají co už systém ví

**Zákazník**: 150 urgentních příjmů v ČR

### Slide 3: ŘEŠENÍ (45s)
Tabulka: Dotazník vs. Náš Agent

**Jak to funguje:**
1. PREZENTACE → Příznaky
2. DOHLEDÁVÁNÍ → Zdravotní záznamy (ne vyptávání!)
3. KONTEXT → Epidemie, počasí
4. ROZHODNUTÍ → Priorita + vysvětlení
5. ESKALACE → Při nejistotě předá lékaři

**Tech**: Claude Sonnet 4.5, Predikce, Vision, NLP, Resource optimization

### Slide 4: DEMO (60s) ⚡ KLÍČOVÉ!
**ŽIVÁ UKÁZKA** - Spustit DEMO.py

Nebo ukázat výsledky:

| Metrika | Baseline | Náš Agent | Zlepšení |
|---------|----------|-----------|----------|
| Undertriage | 50% | **0%** | **-50 pp** |
| Overtriage | 25% | **0%** | **-25 pp** |
| Přesnost | 25% | **100%** | **+75%** |

**Důkaz**: 4 life-threatening případy zachyceny!

### Slide 5: BYZNYS (20s)
- **Model**: SaaS €5-10k/měsíc per nemocnice
- **Hodnota**: Zachraňuje životy + Optimalizuje zdroje
- **Opakovaný příjem**: Učící se systém → Lock-in

### Slide 6: KONKURENCE (10s)
- **Mediktor**, **Infermedica**: Dotazníky
- **My**: Aktivní dohledávání + Predikce + Multi-modal

---

## ❓ OČEKÁVANÉ OTÁZKY & ODPOVĚDI

### "Co když EHR data nejsou dostupná?"
> "Fallback na dotazníkový režim. Ale hodnota je právě v dohledávání - to je naše USP. Tam kde máme EHR (většina velkých nemocnic), jsme o 75% přesnější než baseline."

### "Jak řešíte odpovědnost při chybě?"
> "Lékař má finální slovo. AI je podpůrný nástroj. Při nejistotě eskalujeme. EU AI Act compliant - lidský dohled je povinný."

### "Proč je to agent, ne jen dotazník?"
> "Agent ROZHODUJE jaká data potřebuje. Aktivně volá get_history(), get_epidemiology(). Dotazník jen sbírá formulář. To je zásadní rozdíl."

### "Jak se systém učí?"
> "Feedback loop: Lékař ověří rozhodnutí → Uložíme do DB → Model se adaptivně upravuje. Continuous improvement. Ukázáno v learning modulu."

### "GDPR compliance pro vision modul?"
> "Explicitní souhlas pacienta. Data retention 24h. Pouze features, ne fotky. Právo odmítnout bez důsledků. Kompletní audit trail."

### "Jak testujete bias?"
> "Monitoring výkonu podle pohlaví, věku. Testováno na netypických případech (ženy s infarktem). Red flags specificky pro ženy. Continuous monitoring."

### "Competitive advantage proti Mediktor?"
> "Mediktor = passivní dotazník. My = aktivní dohledávání + predikce + multi-modal. Konkrétně: Mediktor nezjišťuje zdravotní záznamy i když jsou dostupné. My ano → 75% vyšší přesnost."

---

## 🖥️ ŽIVÉ DEMO - INSTRUKCE

### Varianta A: Interaktivní DEMO.py (doporučeno)
```bash
cd ~/Desktop/"ai olympiada 2"/zdravotnictvi-olympiada
python3 DEMO.py
```

**Průběh:**
1. Úvod
2. Baseline vs. Agent srovnání (ukáže metriky live)
3. Rozšířené moduly (predikce, vision, NLP)
4. Závěr s čísly

**Čas**: ~5-7 minut (můžeš přeskakovat Enter promptsž)

### Varianta B: Evaluační skript
```bash
cd evaluation
python3 run_evaluation.py
```

**Výstup:** Text soubor s metrikami

### Varianta C: Offline fallback
Pokud internet selže, ukázat výstupy předem:
- `evaluation/evaluation_results.txt`
- Screenshots z dokumentace

---

## 📊 KLÍČOVÁ ČÍSLA (pamatovat!)

- **-50 pp** undertriage (kritické!)
- **+75%** přesnost
- **-60%** dotazů na pacienta
- **€5-10k**/měsíc revenue per nemocnice
- **150** urgentních příjmů v ČR (target market)
- **8** záludných testovacích případů
- **100%** přesnost na test cases

---

## ⏱️ TIMING

- **Setup**: 2 min před vámi (připravit laptop)
- **Pitch**: 3 min (max 3:10 s tolerancí)
- **Q&A**: 2 min
- **Celkem**: 5 min

**STOPKY** - Někdo měří čas!

---

## 🎯 CO POROTA HODNOTÍ (body 0-5 každé)

### Technické řešení (40%):
- [ ] AI vrstva skutečná (ne jen formulář)
- [ ] Demo funguje
- [ ] Kvalita řešení odpovídá problému
- [ ] Rozumíte kdy model selhává

**Tip**: Ukázat konkrétní případy kde baseline selhal a agent uspěl

### Byznys & Pitch (40%):
- [ ] Konkrétní zákazník (ne "všichni")
- [ ] Víte kdo platí a proč
- [ ] Znáte konkurenci
- [ ] Jasná struktura, dodržený čas

**Tip**: Říct "Mediktor a Infermedica" jmenovitě + v čem jsme lepší

### Etika (20%):
- [ ] Konkrétní rizika (ne obecné fráze)
- [ ] GDPR a AI Act zmíněno
- [ ] Kdo nese odpovědnost
- [ ] Transparentnost vůči uživateli

**Tip**: "EU AI Act - vysoké riziko, lidský dohled povinný. Lékař rozhoduje, AI podporuje."

---

## 🚨 BACKUP PLÁNY

### Internet selže:
- [ ] Offline mode - DEMO.py nevolá Claude API, použije cache
- [ ] Ukázat předem vygenerované výsledky
- [ ] Evaluační výsledky z textového souboru

### Laptop se vypne:
- [ ] Druhý laptop připravený (pokud máte tým)
- [ ] Mobilní backup - PDF dokumenty na telefonu

### Demo crashne:
- [ ] "Ukážu vám výsledky které jsme získali při testování..."
- [ ] evaluation_results.txt
- [ ] Pokračovat v pitchi bez live dema

---

## ✅ DEN PŘED FINÁLE

1. **Otestovat DEMO.py** - jednou kompletně proběhnout
2. **Nacvičit pitch** - stopky, přesně 3 min
3. **Vytisknout dokumenty** - technické shrnutí, pitch deck backup
4. **Nabít vše** - laptop, telefon, powerbanka
5. **Spánek** - 8 hodin!

---

## 🏆 NA PÓDIU

### DO:
✅ Mluv pomalu a jasně
✅ Ukaž konkrétní čísla (-50pp undertriage!)
✅ Vysvětli PROČ je to agent (dohledávání!)
✅ Enthusiasm - ukaž že tomu věříš

### DON'T:
❌ Nečti ze slajdů
❌ Nepřekračuj čas
❌ Nezahlcuj tech detaily (ty jsou v doc)
❌ Neříkej "myslím že" - mluv s jistotou

---

## 📞 KONTAKTY PRO PODPORU

- **Tech problém**: [Tech lead phone]
- **Byznys otázka**: [Business lead phone]
- **Organizátor**: aio@nvias.org

---

## 🎊 PO PREZENTACI

- [ ] Feedback od poroty zaznamenat
- [ ] Poděkovat mentorům
- [ ] Oslavit! 🎉

---

**HODNĚ ŠTĚSTÍ! 🍀**

**Jste připraveni. Máte skvělý projekt. Ukažte to!**

---

_Vytvořeno pro Českou AI Olympiádu 2026 - Národní Finále_
_Plzeň, ZČU, Červen 2026_

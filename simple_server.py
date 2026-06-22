"""
JEDNODUCHÝ SERVER PRO DEMO
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Přidej backend do PATH
backend_path = str(Path(__file__).parent / "backend")
sys.path.insert(0, backend_path)

from data.interface import TriageDataInterface

app = FastAPI(
    title="Triážní Agent API - Demo",
    description="Jednoduchá verze pro prezentaci",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data interface
data_interface = TriageDataInterface(data_dir=str(Path(__file__).parent / "data" / "sandbox"))


@app.get("/", summary="Hlavní stránka", tags=["Základní"])
async def root():
    """
    **Kontrola stavu serveru**

    Vrací základní informace o API a dostupných endpointech.
    """
    return {
        "status": "✅ Server běží!",
        "service": "Triážní Agent API",
        "version": "1.0.0",
        "endpoints": {
            "patients": "/api/patients",
            "epidemiology": "/api/epidemiology",
            "docs": "/docs"
        }
    }


@app.get("/api/patients", summary="Seznam pacientů", tags=["Pacienti"])
async def list_patients():
    """
    **Vrací seznam všech pacientů v datovém sandboxu**

    Obsahuje 12 syntetických pacientů včetně 8 záludných testovacích případů:
    - Atypický infarkt u žen
    - Respirační insuficience u dětí
    - Subarachnoidální krvácení maskované migrénami
    - Plicní embolie u mladých
    """
    return {"patients": data_interface.patients["patients"]}


@app.get("/api/patients/{patient_id}", summary="Detail pacienta", tags=["Pacienti"])
async def get_patient(patient_id: str):
    """
    **Vrací kompletní informace o konkrétním pacientovi**

    Parametry:
    - **patient_id**: ID pacienta (např. P001, P002, ...)

    Vrací:
    - Jméno, věk, pohlaví
    - Příznaky a vitální funkce
    - Zdravotní anamnéza
    - Správnou triážní prioritu (pro evaluaci)
    """
    for patient in data_interface.patients["patients"]:
        if patient["id"] == patient_id:
            return patient
    return {"error": "Pacient nenalezen"}


@app.get("/api/epidemiology", summary="Epidemiologická data", tags=["Kontext"])
async def get_epidemiology():
    """
    **Vrací aktuální epidemiologickou situaci**

    Obsahuje:
    - Aktuální epidemie (chřipka, COVID-19, atd.)
    - Kapacita nemocnice (lůžka, ICU)
    - Dostupnost specialistů
    - Regionální zdravotní upozornění

    Tato data agent využívá pro kontextuální rozhodování.
    """
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        data = data_interface.get_epidemiology(today)
        return data
    except:
        return {"error": "Data nejsou dostupná"}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*80)
    print("🚀 TRIÁŽNÍ AGENT - DEMO SERVER")
    print("="*80)
    print("\n✅ Server běží na: http://localhost:8000")
    print("📖 Dokumentace: http://localhost:8000/docs")
    print("👥 Pacienti: http://localhost:8000/api/patients")
    print("\n" + "="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)

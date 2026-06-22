"""
FASTAPI BACKEND

REST API + WebSocket pro real-time triáž
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Přidej backend do PATH
backend_path = str(Path(__file__).parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Importy našich modulů
from data.interface import TriageDataInterface
from agent.baseline import BaselineTriageSystem
from agent.coordinator import TriageCoordinatorAgent
from ml.predictor import EpidemicPredictor, PatientOutcomePredictor
from vision.pain_detection import VisionTriageAssistant
from ml.nlp_analyzer import MedicalRecordAnalyzer, SentimentAnalyzer
from api.external_services import WeatherService, EventsService
from ml.resource_optimizer import ResourceOptimizer

# FastAPI app
app = FastAPI(
    title="Triážní Agent API",
    description="AI-powered triage system pro urgentní příjem",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # V produkci omezit na frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globální instance
data_interface = TriageDataInterface(data_dir=str(Path(__file__).parent.parent.parent / "data" / "sandbox"))
baseline_system = BaselineTriageSystem()

# API klíč pro Claude (v produkci z environment)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "sk-ant-api03-AQ_Ab8RN6JVWSGwmB_s4yop_FESkf6BbWJL167kEbIQP_-BrzYdPg")
ai_agent = TriageCoordinatorAgent(api_key=ANTHROPIC_API_KEY)

# Pydantic modely
class TriageRequest(BaseModel):
    patient_id: str
    system: str = "agent"  # "baseline" nebo "agent"

class FeedbackRequest(BaseModel):
    patient_id: str
    ai_decision: Dict[str, Any]
    physician_decision: Dict[str, Any]
    notes: Optional[str] = None


# === ENDPOINTS ===

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "running",
        "service": "Triážní Agent API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/patients")
async def list_patients():
    """Seznam všech pacientů"""
    return {"patients": data_interface.patients["patients"]}

@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: str):
    """Detail pacienta"""
    for patient in data_interface.patients["patients"]:
        if patient["id"] == patient_id:
            return patient

    raise HTTPException(status_code=404, detail="Patient not found")

@app.post("/api/triage")
async def perform_triage(request: TriageRequest):
    """
    Provede triáž pacienta

    - **patient_id**: ID pacienta
    - **system**: "baseline" nebo "agent"
    """
    try:
        if request.system == "baseline":
            # Baseline systém
            presentation = data_interface.get_presentation(request.patient_id)
            decision = baseline_system.triage(request.patient_id, presentation)
        else:
            # AI Agent
            decision = ai_agent.triage(request.patient_id, data_interface)

        return {
            "success": True,
            "patient_id": request.patient_id,
            "system": request.system,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/epidemiology")
async def get_epidemiology(date: str = None):
    """Získá epidemiologickou situaci"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        data = data_interface.get_epidemiology(date)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/predictions/surge")
async def predict_surge():
    """Predikce náporu pacientů"""
    predictor = EpidemicPredictor()
    weather_service = WeatherService()
    events_service = EventsService()

    # Získej data
    today = datetime.now().strftime("%Y-%m-%d")
    epi_data = data_interface.get_epidemiology(today)
    weather = weather_service.get_current_weather()
    events = events_service.get_local_events("Plzeň", today)

    # Predikce
    surge = predictor.predict_patient_surge(
        epidemiology_data=epi_data,
        weather_data=weather,
        events=events
    )

    return surge

@app.get("/api/predictions/patient/{patient_id}")
async def predict_patient_outcome(patient_id: str):
    """Predikce vývoje stavu pacienta"""
    # Načti data
    patient = None
    for p in data_interface.patients["patients"]:
        if p["id"] == patient_id:
            patient = p
            break

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    predictor = PatientOutcomePredictor()

    # Predikuj riziko deteriorace
    risk = predictor.predict_deterioration_risk(
        vital_signs=patient["presentation"]["vital_signs"],
        medical_history=patient["medical_history"],
        age=patient["age"]
    )

    # Odhad délky pobytu
    los = predictor.estimate_length_of_stay(
        priority=patient.get("true_priority", 3),
        age=patient["age"],
        conditions=patient["medical_history"]["conditions"]
    )

    return {
        "patient_id": patient_id,
        "deterioration_risk": risk,
        "length_of_stay": los
    }

@app.get("/api/vision/assessment/{patient_id}")
async def vision_assessment(patient_id: str, consent: bool = False):
    """Vision-based assessment (vyžaduje GDPR souhlas)"""
    vision_assistant = VisionTriageAssistant()

    result = vision_assistant.comprehensive_vision_assessment(
        patient_id=patient_id,
        consent_verified=consent
    )

    return result

@app.get("/api/nlp/analyze/{patient_id}")
async def nlp_analysis(patient_id: str):
    """NLP analýza zdravotních záznamů"""
    # Načti pacienta
    patient = None
    for p in data_interface.patients["patients"]:
        if p["id"] == patient_id:
            patient = p
            break

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Analýza záznamů
    analyzer = MedicalRecordAnalyzer()
    history_analysis = analyzer.analyze_medical_history(patient["medical_history"])

    # Sentiment analýza
    sentiment_analyzer = SentimentAnalyzer()
    sentiment = sentiment_analyzer.analyze_patient_communication(
        chief_complaint=patient["presentation"]["chief_complaint"],
        symptoms=patient["presentation"]["symptoms"]
    )

    return {
        "patient_id": patient_id,
        "medical_history_analysis": history_analysis,
        "sentiment_analysis": sentiment
    }

@app.get("/api/resources/status")
async def resources_status():
    """Status zdrojů nemocnice"""
    # Načti data
    today = datetime.now().strftime("%Y-%m-%d")
    epi_data = data_interface.get_epidemiology(today)

    optimizer = ResourceOptimizer(epi_data)
    dashboard = optimizer.get_hospital_dashboard()

    return dashboard

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Feedback lékaře - learning loop

    AI rozhodnutí vs. skutečné rozhodnutí lékaře
    """
    # V produkci by ukládalo do DB pro trénink
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "patient_id": feedback.patient_id,
        "ai_decision": feedback.ai_decision,
        "physician_decision": feedback.physician_decision,
        "notes": feedback.notes,
        "agreement": feedback.ai_decision.get("priority") == feedback.physician_decision.get("priority")
    }

    # TODO: Save to database and retrain model

    return {
        "success": True,
        "feedback_id": f"FB-{datetime.now().timestamp()}",
        "message": "Feedback přijat. Systém se učí z vašeho rozhodnutí."
    }

@app.get("/api/weather")
async def get_weather():
    """Aktuální počasí a zdravotní dopad"""
    weather_service = WeatherService()
    weather = weather_service.get_current_weather()
    forecast = weather_service.get_health_forecast()

    return {
        "current_weather": weather,
        "health_forecast": forecast
    }

@app.get("/api/events")
async def get_events(date: str = None):
    """Lokální události"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    events_service = EventsService()
    events = events_service.get_local_events("Plzeň", date)
    impact = events_service.assess_event_impact(events)

    return {
        "date": date,
        "events": events,
        "impact_assessment": impact
    }


# === WEBSOCKET ===
# Pro real-time updates

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/triage")
async def websocket_triage(websocket: WebSocket):
    """
    WebSocket pro real-time triáž

    Klient pošle: {"action": "triage", "patient_id": "P001", "system": "agent"}
    Server vrací: progress updates + final decision
    """
    await manager.connect(websocket)
    try:
        while True:
            # Přijmi zprávu
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "triage":
                patient_id = data.get("patient_id")
                system = data.get("system", "agent")

                # Progress update
                await websocket.send_json({
                    "type": "progress",
                    "message": f"Zahajuji triáž pacienta {patient_id}..."
                })

                try:
                    if system == "baseline":
                        presentation = data_interface.get_presentation(patient_id)
                        decision = baseline_system.triage(patient_id, presentation)
                    else:
                        await websocket.send_json({
                            "type": "progress",
                            "message": "Získávám prezentaci pacienta..."
                        })

                        await websocket.send_json({
                            "type": "progress",
                            "message": "Analyzuji zdravotní záznamy..."
                        })

                        await websocket.send_json({
                            "type": "progress",
                            "message": "Konzultuji AI agent..."
                        })

                        decision = ai_agent.triage(patient_id, data_interface)

                    # Final decision
                    await websocket.send_json({
                        "type": "decision",
                        "patient_id": patient_id,
                        "system": system,
                        "decision": decision
                    })

                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })

            elif action == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("🚀 SPOUŠTÍM TRIÁŽNÍ AGENT API")
    print("="*80)
    print("\nDokumentace: http://localhost:8000/docs")
    print("Health check: http://localhost:8000/")
    print("\nWebSocket: ws://localhost:8000/ws/triage")
    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)

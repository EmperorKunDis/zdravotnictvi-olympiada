"""
EXTERNÍ API SLUŽBY

Integrace s vnějšími službami:
- Počasí (vliv na kardio případy)
- Lokální události (festivals → úrazy)
- Záchranná služba (pre-notifikace)
- Krizové plány

V produkci by volalo skutečná API.
Pro demo používá mock data s realistickým chováním.
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class WeatherService:
    """
    Služba pro získání počasí a zdravotních alertů
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        # V produkci: OpenWeatherMap, WeatherAPI, atd.

    def get_current_weather(self, location: str = "Plzeň") -> Dict[str, Any]:
        """
        Získá aktuální počasí

        V produkci by volalo:
        API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.api_key}"
        """
        # Mock data pro demo
        return {
            "location": location,
            "temperature": 32,
            "feels_like": 35,
            "humidity": 45,
            "conditions": "sunny",
            "weather_alert": {
                "type": "heat_wave",
                "level": "warning",
                "message": "Varování před vedry - teploty nad 30°C",
                "health_impact": "Zvýšené riziko dehydratace a kardiovaskulárních komplikací"
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_health_forecast(self, location: str = "Plzeň") -> Dict[str, Any]:
        """
        Predikce zdravotního dopadu počasí

        Args:
            location: Lokace

        Returns:
            Zdravotní prognóza
        """
        weather = self.get_current_weather(location)
        temp = weather["temperature"]

        health_risks = []
        surge_prediction = 1.0

        # Vedra
        if temp >= 30:
            health_risks.append({
                "condition": "Kardiovaskulární onemocnění",
                "risk_increase": "+20%",
                "vulnerable_groups": ["Senioři 65+", "Chronicky nemocní", "Děti"],
                "prevention": "Dostatečná hydratace, klimatizace"
            })
            surge_prediction = 1.2

        # Extrémní vedra
        if temp >= 35:
            health_risks.append({
                "condition": "Úpal, dehydratace",
                "risk_increase": "+50%",
                "vulnerable_groups": ["Všechny věkové skupiny"],
                "prevention": "Vyhýbat se pobytu venku, klimatizace"
            })
            surge_prediction = 1.5

        # Mráz
        if temp <= 0:
            health_risks.append({
                "condition": "Pády, hypotermie",
                "risk_increase": "+15%",
                "vulnerable_groups": ["Senioři", "Bezdomovci"],
                "prevention": "Opatrnost na ledě, teplé oblečení"
            })
            surge_prediction = 1.15

        return {
            "current_temperature": temp,
            "health_risks": health_risks,
            "expected_surge_multiplier": surge_prediction,
            "recommendation": self._get_weather_recommendation(temp),
            "forecast_confidence": "high"
        }

    def _get_weather_recommendation(self, temp: float) -> str:
        """Doporučení podle počasí"""
        if temp >= 35:
            return "⚠️ EXTRÉMNÍ VEDRA - Připravit extra kapacitu pro kardio případy"
        elif temp >= 30:
            return "☀️ VEDRA - Očekávat zvýšený přísun seniorů s dehydratací/kolapsem"
        elif temp <= -10:
            return "❄️ EXTRÉMNÍ MRÁZ - Riziko hypotermie a pádů"
        elif temp <= 0:
            return "🧊 MRÁZ - Zvýšená pozornost na pády"
        else:
            return "🌤️ Normální počasí - standardní provoz"


class EventsService:
    """
    Sleduje lokální události s dopadem na urgentní příjem
    """

    def __init__(self):
        # V produkci by mělo DB událostí nebo API (Eventbrite, lokální kalendáře)
        pass

    def get_local_events(
        self,
        location: str = "Plzeň",
        date: str = None
    ) -> List[Dict[str, Any]]:
        """
        Získá lokální události s potenciálním dopadem

        Args:
            location: Lokace
            date: Datum (YYYY-MM-DD)

        Returns:
            Seznam událostí
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Mock data
        events = [
            {
                "event_name": "Hudební festival Plzeň 2026",
                "date": "2026-06-21 - 2026-06-23",
                "type": "festival",
                "expected_attendance": 15000,
                "health_impact": {
                    "expected_cases": {
                        "úrazy": "+30 případů",
                        "intoxikace_alkohol": "+15 případů",
                        "dehydratace": "+20 případů",
                        "ublížení_na_zdraví": "+5 případů"
                    },
                    "surge_multiplier": 1.25,
                    "peak_hours": "22:00 - 04:00"
                },
                "recommendations": [
                    "Posílit noční směny",
                    "Připravit toxikologické vyšetření",
                    "Kontaktovat pořadatele pro medicínský stan"
                ]
            },
            {
                "event_name": "FC Viktoria Plzeň vs. Sparta (ligový zápas)",
                "date": "2026-06-22 19:00",
                "type": "sports",
                "expected_attendance": 12000,
                "health_impact": {
                    "expected_cases": {
                        "úrazy": "+10 případů",
                        "intoxikace": "+8 případů"
                    },
                    "surge_multiplier": 1.15,
                    "peak_hours": "21:00 - 23:00"
                },
                "recommendations": [
                    "Připravit traumatologii po zápase"
                ]
            }
        ]

        return [e for e in events if date in e["date"]]

    def assess_event_impact(
        self,
        events: List[Dict]
    ) -> Dict[str, Any]:
        """
        Posoudí celkový dopad událostí na urgentní příjem

        Args:
            events: Seznam událostí

        Returns:
            Celkové posouzení
        """
        if not events:
            return {
                "total_surge_multiplier": 1.0,
                "expected_additional_cases": 0,
                "recommendation": "Žádné významné události - standardní provoz"
            }

        total_multiplier = 1.0
        total_cases = 0

        for event in events:
            impact = event.get("health_impact", {})
            total_multiplier *= impact.get("surge_multiplier", 1.0)

            cases = impact.get("expected_cases", {})
            for case_type, count_str in cases.items():
                # Extrahuj číslo z "+30 případů"
                count = int(count_str.split("+")[1].split(" ")[0])
                total_cases += count

        return {
            "events_count": len(events),
            "total_surge_multiplier": round(total_multiplier, 2),
            "expected_additional_cases": total_cases,
            "recommendation": f"📅 {len(events)} událostí - očekávat +{total_cases} případů",
            "peak_hours": "21:00 - 04:00"
        }


class EmergencyServiceIntegration:
    """
    Integrace se záchrannou službou (RZP)

    Pre-notifikace od RZP o pacientech na cestě
    """

    def __init__(self):
        # V produkci by mělo WebSocket spojení s dispečinkem RZP
        pass

    def receive_pre_notification(
        self,
        ems_case_id: str
    ) -> Dict[str, Any]:
        """
        Příjem pre-notifikace od RZP

        V produkci:
        - Real-time WebSocket
        - Strukturovaná data od záchranky
        - ETA (estimated time of arrival)

        Args:
            ems_case_id: ID případu RZP

        Returns:
            Pre-notifikace
        """
        # Mock data
        return {
            "ems_case_id": ems_case_id,
            "priority": "CODE_RED",
            "chief_complaint": "CMP - pravostranná hemiparéza",
            "vital_signs": {
                "blood_pressure": "180/105",
                "heart_rate": 92,
                "respiratory_rate": 18,
                "oxygen_saturation": 95,
                "gcs": 14
            },
            "interventions_performed": [
                "IV přístup zajištěn",
                "Kyslík 4L/min",
                "Monitoring vitálních funkcí"
            ],
            "eta_minutes": 8,
            "crew_note": "71letý muž, náhle vznikla slabost pravé strany a porucha řeči před 45 minutami. Při vědomí, spolupracuje.",
            "recommended_preparation": [
                "Aktivovat CMP tým",
                "Připravit CT mozku",
                "Upozornit neurologa"
            ],
            "timestamp": datetime.now().isoformat()
        }

    def send_capacity_status(
        self,
        available_beds: int,
        estimated_wait_time: int
    ) -> Dict[str, Any]:
        """
        Pošle status kapacity zpět RZP

        Args:
            available_beds: Dostupná lůžka
            estimated_wait_time: Odhadovaná čekací doba (min)

        Returns:
            Potvrzení
        """
        return {
            "status": "SENT",
            "available_beds": available_beds,
            "estimated_wait_time": estimated_wait_time,
            "redirect_recommended": available_beds < 2,
            "alternative_facilities": [
                "Fakultní nemocnice Hradec Králové - 45 min",
                "Nemocnice Karlovy Vary - 60 min"
            ] if available_beds < 2 else [],
            "timestamp": datetime.now().isoformat()
        }


class CrisisManager:
    """
    Správa krizových plánů a hromadných neštěstí
    """

    def __init__(self):
        self.crisis_levels = {
            "GREEN": "Normální provoz",
            "YELLOW": "Zvýšená pohotovost",
            "ORANGE": "Krizový režim",
            "RED": "Hromadné neštěstí"
        }

    def activate_crisis_plan(
        self,
        crisis_type: str,
        estimated_casualties: int
    ) -> Dict[str, Any]:
        """
        Aktivuje krizový plán

        Args:
            crisis_type: Typ krize (mci, chemical, pandemic, atd.)
            estimated_casualties: Odhadovaný počet obětí

        Returns:
            Aktivovaný plán
        """
        # Určení úrovně
        if estimated_casualties >= 50:
            level = "RED"
        elif estimated_casualties >= 20:
            level = "ORANGE"
        elif estimated_casualties >= 10:
            level = "YELLOW"
        else:
            level = "GREEN"

        crisis_plans = {
            "mci": {  # Mass Casualty Incident
                "name": "Hromadné neštěstí",
                "actions": [
                    "Aktivovat vnější triážní tým",
                    "Zřídit dekontaminační stanoviště (pokud nutné)",
                    "Vyčistit emergency department - stabilní pacienty přeložit",
                    "Volat off-duty personál",
                    "Připravit operační sály",
                    "Kontaktovat krevní banku",
                    "Informovat management a PR"
                ]
            },
            "pandemic": {
                "name": "Pandemie",
                "actions": [
                    "Aktivovat infekční protokol",
                    "Zřídit separované prostory",
                    "OOP pro personál (FFP2/FFP3)",
                    "Omezit elektivní výkony",
                    "Posílit testovací kapacity"
                ]
            },
            "chemical": {
                "name": "Chemická havárie",
                "actions": [
                    "Aktivovat dekontaminační tým",
                    "Uzavřít ventilaci",
                    "Připravit antidota",
                    "Kontaktovat toxikologii",
                    "Separovat kontaminované pacienty"
                ]
            }
        }

        plan = crisis_plans.get(crisis_type, crisis_plans["mci"])

        return {
            "crisis_level": level,
            "crisis_type": crisis_type,
            "crisis_plan": plan["name"],
            "estimated_casualties": estimated_casualties,
            "actions_to_take": plan["actions"],
            "incident_commander": "Primář urgentního příjmu",
            "activation_time": datetime.now().isoformat(),
            "status": "ACTIVATED"
        }


# Demonstrace
if __name__ == "__main__":
    print("="*80)
    print("EXTERNÍ API SLUŽBY - DEMONSTRACE")
    print("="*80)

    # Test 1: Počasí
    print("\n1. WEATHER SERVICE")
    print("-" * 80)

    weather_service = WeatherService()
    weather = weather_service.get_current_weather()
    forecast = weather_service.get_health_forecast()

    print(f"📍 Lokace: {weather['location']}")
    print(f"🌡️  Teplota: {weather['temperature']}°C (pocitově {weather['feels_like']}°C)")
    print(f"\n⚠️  Alert: {weather['weather_alert']['type']}")
    print(f"   {weather['weather_alert']['message']}")
    print(f"   Zdravotní dopad: {weather['weather_alert']['health_impact']}")

    print(f"\n💡 Zdravotní prognóza:")
    print(f"   Násobek náporu: {forecast['expected_surge_multiplier']}x")
    print(f"   Rizika:")
    for risk in forecast['health_risks']:
        print(f"     - {risk['condition']}: {risk['risk_increase']}")
    print(f"\n   📋 {forecast['recommendation']}")

    # Test 2: Lokální události
    print("\n\n2. EVENTS SERVICE")
    print("-" * 80)

    events_service = EventsService()
    events = events_service.get_local_events("Plzeň", "2026-06-22")
    impact = events_service.assess_event_impact(events)

    print(f"📅 Nalezené události: {len(events)}")
    for event in events:
        print(f"\n   🎉 {event['event_name']}")
        print(f"      Účastníků: {event['expected_attendance']}")
        print(f"      Násobek: {event['health_impact']['surge_multiplier']}x")
        print(f"      Očekávané případy:")
        for case_type, count in event['health_impact']['expected_cases'].items():
            print(f"        - {case_type}: {count}")

    print(f"\n💡 Celkový dopad:")
    print(f"   Celkový násobek: {impact['total_surge_multiplier']}x")
    print(f"   Dodatečné případy: +{impact['expected_additional_cases']}")
    print(f"   {impact['recommendation']}")

    # Test 3: Pre-notifikace RZP
    print("\n\n3. EMERGENCY SERVICE INTEGRATION")
    print("-" * 80)

    ems_service = EmergencyServiceIntegration()
    notification = ems_service.receive_pre_notification("RZP-2026-12345")

    print(f"🚑 Pre-notifikace od RZP")
    print(f"   Case ID: {notification['ems_case_id']}")
    print(f"   Priorita: {notification['priority']}")
    print(f"   Stížnost: {notification['chief_complaint']}")
    print(f"   ETA: {notification['eta_minutes']} minut")
    print(f"\n   Vitální funkce:")
    print(f"     TK: {notification['vital_signs']['blood_pressure']}")
    print(f"     GCS: {notification['vital_signs']['gcs']}")
    print(f"\n   💡 Doporučená příprava:")
    for prep in notification['recommended_preparation']:
        print(f"     - {prep}")

    # Test 4: Krizový plán
    print("\n\n4. CRISIS MANAGER")
    print("-" * 80)

    crisis_manager = CrisisManager()
    crisis = crisis_manager.activate_crisis_plan("mci", estimated_casualties=35)

    print(f"🚨 KRIZOVÝ PLÁN AKTIVOVÁN")
    print(f"   Úroveň: {crisis['crisis_level']}")
    print(f"   Typ: {crisis['crisis_plan']}")
    print(f"   Odhadované oběti: {crisis['estimated_casualties']}")
    print(f"   Status: {crisis['status']}")
    print(f"\n   📋 Akce k provedení:")
    for i, action in enumerate(crisis['actions_to_take'], 1):
        print(f"     {i}. {action}")

    print("\n" + "="*80)
    print("Externí API služby funkční!")
    print("="*80)

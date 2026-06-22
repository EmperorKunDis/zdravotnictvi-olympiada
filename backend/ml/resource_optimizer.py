"""
OPTIMALIZACE ZDROJŮ

Alokace lůžek, specialistů a zdrojů podle priority a kapacity
"""

from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import json


class BedAllocator:
    """
    Optimální alokace lůžek podle priority pacientů a dostupnosti
    """

    def __init__(self, hospital_capacity: Dict):
        self.total_beds = hospital_capacity.get("total_beds", 450)
        self.available_beds = hospital_capacity.get("available_beds", 78)
        self.icu_beds = hospital_capacity.get("icu_beds", 32)
        self.available_icu_beds = hospital_capacity.get("available_icu_beds", 4)

    def allocate_bed(
        self,
        patient_priority: int,
        estimated_stay_hours: int,
        icu_required: bool = False
    ) -> Dict[str, Any]:
        """
        Alokuje lůžko pacientovi

        Args:
            patient_priority: Priorita 1-5
            estimated_stay_hours: Odhadovaná délka pobytu
            icu_required: Vyžaduje ICU

        Returns:
            Alokace lůžka
        """
        # ICU požadavek
        if icu_required:
            if self.available_icu_beds > 0:
                self.available_icu_beds -= 1
                return {
                    "allocated": True,
                    "bed_type": "ICU",
                    "bed_number": f"ICU-{32 - self.available_icu_beds}",
                    "estimated_discharge": self._calculate_discharge_time(estimated_stay_hours),
                    "note": "ICU lůžko alokováno"
                }
            else:
                return {
                    "allocated": False,
                    "bed_type": "ICU",
                    "reason": "Všechna ICU lůžka obsazena",
                    "alternatives": [
                        "Transfer do jiné nemocnice s volným ICU",
                        "Předčasný propuštění méně kritického pacienta z ICU"
                    ],
                    "action_required": "URGENT - Kontaktovat management"
                }

        # Standardní lůžko
        if self.available_beds > 0:
            # Priority pacienti mají přednost
            if patient_priority <= 2 or self.available_beds > 20:
                self.available_beds -= 1
                ward = self._assign_ward(patient_priority)

                return {
                    "allocated": True,
                    "bed_type": "STANDARD",
                    "ward": ward,
                    "bed_number": f"{ward}-{100 + (78 - self.available_beds)}",
                    "estimated_discharge": self._calculate_discharge_time(estimated_stay_hours),
                    "note": f"Lůžko alokováno na {ward}"
                }
            else:
                return {
                    "allocated": "WAITING_LIST",
                    "reason": f"Pouze {self.available_beds} lůžek - priorita {patient_priority} musí počkat",
                    "estimated_wait": "30-60 minut",
                    "note": "Observace na emergency department"
                }
        else:
            return {
                "allocated": False,
                "reason": "Žádná volná lůžka",
                "capacity_status": "CRITICAL",
                "alternatives": [
                    "Transfer do jiné nemocnice",
                    "Urychlené propouštění stabilních pacientů",
                    "Aktivovat krizový plán - dodatečná lůžka"
                ],
                "action_required": "IMMEDIATE"
            }

    def _assign_ward(self, priority: int) -> str:
        """Přiřadí oddělení podle priority"""
        if priority == 1:
            return "RESUSCITATION"
        elif priority == 2:
            return "ACUTE_CARE"
        elif priority == 3:
            return "GENERAL_WARD"
        else:
            return "OBSERVATION"

    def _calculate_discharge_time(self, hours: int) -> str:
        """Vypočítá předpokládaný čas propuštění"""
        discharge = datetime.now() + timedelta(hours=hours)
        return discharge.strftime("%Y-%m-%d %H:%M")

    def get_capacity_status(self) -> Dict[str, Any]:
        """Vrátí aktuální stav kapacity"""
        total_occupancy = ((self.total_beds - self.available_beds) / self.total_beds) * 100
        icu_occupancy = ((self.icu_beds - self.available_icu_beds) / self.icu_beds) * 100

        if total_occupancy >= 95 or icu_occupancy >= 90:
            status = "CRITICAL"
        elif total_occupancy >= 85 or icu_occupancy >= 75:
            status = "HIGH"
        elif total_occupancy >= 70:
            status = "MODERATE"
        else:
            status = "NORMAL"

        return {
            "status": status,
            "total_beds": self.total_beds,
            "available_beds": self.available_beds,
            "occupancy_rate": round(total_occupancy, 1),
            "icu_beds": self.icu_beds,
            "available_icu_beds": self.available_icu_beds,
            "icu_occupancy_rate": round(icu_occupancy, 1),
            "recommendation": self._get_capacity_recommendation(status)
        }

    def _get_capacity_recommendation(self, status: str) -> str:
        """Doporučení podle kapacity"""
        if status == "CRITICAL":
            return "🚨 KRITICKÁ KAPACITA - Aktivovat krizový plán, přesměrovat RZP"
        elif status == "HIGH":
            return "⚠️ VYSOKÁ ZAPLNĚNOST - Urychlit propouštění, připravit rezervní lůžka"
        elif status == "MODERATE":
            return "📊 STŘEDNÍ ZAPLNĚNOST - Monitorovat, plánovat propouštění"
        else:
            return "✅ NORMÁLNÍ KAPACITA"


class SpecialistScheduler:
    """
    Plánování a dostupnost specialistů
    """

    def __init__(self, specialist_availability: Dict):
        self.specialists = specialist_availability

    def find_available_specialist(
        self,
        specialty: str,
        urgency: str = "routine"
    ) -> Dict[str, Any]:
        """
        Najde dostupného specialistu

        Args:
            specialty: Specializace (cardiology, neurology, atd.)
            urgency: routine, urgent, immediate

        Returns:
            Dostupný specialista
        """
        specialist_data = self.specialists.get(specialty, {})

        if not specialist_data:
            return {
                "available": False,
                "specialty": specialty,
                "reason": "Specializace není dostupná",
                "alternative": "Konzultace telefonická nebo transfer"
            }

        is_available = specialist_data.get("available", False)
        on_call = specialist_data.get("on_call", "")
        response_time = specialist_data.get("response_time", "")

        if is_available or urgency == "immediate":
            return {
                "available": True,
                "specialty": specialty,
                "doctor": on_call,
                "response_time": response_time,
                "urgency": urgency,
                "contact_method": "Přímé přivolání" if urgency == "immediate" else "Telefonní konzultace možná",
                "note": f"{on_call} je dostupný za {response_time}"
            }
        else:
            return {
                "available": False,
                "specialty": specialty,
                "on_call": on_call,
                "response_time": response_time,
                "reason": "Specialista není na místě",
                "alternatives": [
                    "Telefonická konzultace",
                    "Externí specialista (prodloužený response time)",
                    "Transfer do specializovaného centra"
                ],
                "estimated_external_time": "45+ minut"
            }

    def get_all_specialists_status(self) -> Dict[str, Any]:
        """Vrátí status všech specialistů"""
        status_summary = {
            "available_count": 0,
            "unavailable_count": 0,
            "specialists": []
        }

        for specialty, data in self.specialists.items():
            is_available = data.get("available", False)

            status_summary["specialists"].append({
                "specialty": specialty,
                "available": is_available,
                "on_call": data.get("on_call", ""),
                "response_time": data.get("response_time", "")
            })

            if is_available:
                status_summary["available_count"] += 1
            else:
                status_summary["unavailable_count"] += 1

        return status_summary


class ResourceOptimizer:
    """
    Hlavní optimalizátor zdrojů
    Koordinuje lůžka, specialisty, vybavení
    """

    def __init__(self, hospital_data: Dict):
        capacity = hospital_data.get("hospital_capacity", {})
        specialists = hospital_data.get("specialist_availability", {})

        self.bed_allocator = BedAllocator(capacity)
        self.specialist_scheduler = SpecialistScheduler(specialists)

    def optimize_patient_care(
        self,
        patient_priority: int,
        required_specialty: Optional[str],
        estimated_stay_hours: int,
        icu_required: bool = False
    ) -> Dict[str, Any]:
        """
        Optimalizuje péči o pacienta - lůžko + specialista

        Args:
            patient_priority: Priorita pacienta
            required_specialty: Potřebná specializace
            estimated_stay_hours: Odhadovaný pobyt
            icu_required: Potřeba ICU

        Returns:
            Plán péče
        """
        # Alokace lůžka
        bed = self.bed_allocator.allocate_bed(
            patient_priority,
            estimated_stay_hours,
            icu_required
        )

        # Specialista pokud potřeba
        specialist = None
        if required_specialty:
            urgency = "immediate" if patient_priority <= 1 else "urgent" if patient_priority == 2 else "routine"
            specialist = self.specialist_scheduler.find_available_specialist(
                required_specialty,
                urgency
            )

        # Celkový plán
        care_plan = {
            "bed_allocation": bed,
            "specialist_allocation": specialist,
            "overall_status": "READY" if bed.get("allocated") == True else "DELAYED",
            "bottlenecks": [],
            "recommendations": []
        }

        # Identifikuj bottlenecks
        if not bed.get("allocated"):
            care_plan["bottlenecks"].append("Nedostatek lůžek")
            care_plan["recommendations"].append("Urychlit propouštění nebo transfer")

        if specialist and not specialist.get("available"):
            care_plan["bottlenecks"].append(f"Specialista {required_specialty} nedostupný")
            care_plan["recommendations"].append(specialist.get("alternatives", []))

        return care_plan

    def get_hospital_dashboard(self) -> Dict[str, Any]:
        """
        Kompletní přehled zdrojů nemocnice
        """
        capacity = self.bed_allocator.get_capacity_status()
        specialists = self.specialist_scheduler.get_all_specialists_status()

        # Celkový health score
        health_score = 100

        # Penalizace podle kapacity
        if capacity["status"] == "CRITICAL":
            health_score -= 40
        elif capacity["status"] == "HIGH":
            health_score -= 20
        elif capacity["status"] == "MODERATE":
            health_score -= 10

        # Penalizace podle specialistů
        if specialists["available_count"] < specialists["unavailable_count"]:
            health_score -= 15

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health_score": max(0, health_score),
            "capacity_status": capacity,
            "specialist_status": specialists,
            "alerts": self._generate_alerts(capacity, specialists),
            "recommendations": self._generate_dashboard_recommendations(capacity, specialists)
        }

    def _generate_alerts(self, capacity: Dict, specialists: Dict) -> List[str]:
        """Generuje alerty"""
        alerts = []

        if capacity["status"] == "CRITICAL":
            alerts.append("🚨 KRITICKÁ KAPACITA LŮŽEK")

        if capacity["available_icu_beds"] <= 2:
            alerts.append("⚠️ KRITICKÝ NEDOSTATEK ICU LŮŽEK")

        if specialists["unavailable_count"] > specialists["available_count"]:
            alerts.append("⚠️ VĚTŠINA SPECIALISTŮ NEDOSTUPNÁ")

        return alerts

    def _generate_dashboard_recommendations(self, capacity: Dict, specialists: Dict) -> List[str]:
        """Generuje doporučení"""
        recommendations = []

        if capacity["occupancy_rate"] > 85:
            recommendations.append("Urychlit propouštění stabilních pacientů")
            recommendations.append("Kontaktovat sociální služby pro post-acute care")

        if capacity["available_icu_beds"] <= 3:
            recommendations.append("Připravit krizový plán pro ICU přetížení")
            recommendations.append("Zvážit transfer kritických pacientů do jiných center")

        if specialists["unavailable_count"] > 3:
            recommendations.append("Aktivovat externí konzultační linky")

        return recommendations


# Demonstrace
if __name__ == "__main__":
    print("="*80)
    print("OPTIMALIZACE ZDROJŮ - DEMONSTRACE")
    print("="*80)

    # Mock data
    hospital_data = {
        "hospital_capacity": {
            "total_beds": 450,
            "available_beds": 78,
            "icu_beds": 32,
            "available_icu_beds": 4
        },
        "specialist_availability": {
            "cardiology": {"available": True, "on_call": "Dr. Novák", "response_time": "15 min"},
            "neurology": {"available": True, "on_call": "Dr. Svobodová", "response_time": "10 min"},
            "surgery": {"available": True, "on_call": "Dr. Černý", "response_time": "immediate"},
            "orthopedics": {"available": True, "on_call": "Dr. Malý", "response_time": "20 min"},
            "pulmonology": {"available": False, "on_call": "Dr. Horáková (external)", "response_time": "45 min"}
        }
    }

    optimizer = ResourceOptimizer(hospital_data)

    # Test 1: Optimalizace péče pro kritického pacienta
    print("\n1. OPTIMALIZACE PÉČE - KRITICKÝ PACIENT")
    print("-" * 80)

    care_plan = optimizer.optimize_patient_care(
        patient_priority=1,
        required_specialty="neurology",
        estimated_stay_hours=48,
        icu_required=True
    )

    print(f"Status: {care_plan['overall_status']}")
    print(f"\n🛏️  Lůžko:")
    print(f"   Alokováno: {care_plan['bed_allocation']['allocated']}")
    if care_plan['bed_allocation']['allocated']:
        print(f"   Typ: {care_plan['bed_allocation']['bed_type']}")
        print(f"   Číslo: {care_plan['bed_allocation']['bed_number']}")
        print(f"   Předpokládané propuštění: {care_plan['bed_allocation']['estimated_discharge']}")

    print(f"\n👨‍⚕️  Specialista:")
    spec = care_plan['specialist_allocation']
    print(f"   Dostupný: {spec['available']}")
    if spec['available']:
        print(f"   {spec['doctor']} ({spec['specialty']})")
        print(f"   Response time: {spec['response_time']}")

    if care_plan['bottlenecks']:
        print(f"\n⚠️  Bottlenecks:")
        for bn in care_plan['bottlenecks']:
            print(f"   - {bn}")

    # Test 2: Dashboard nemocnice
    print("\n\n2. HOSPITAL DASHBOARD")
    print("-" * 80)

    dashboard = optimizer.get_hospital_dashboard()

    print(f"⚕️  Overall Health Score: {dashboard['overall_health_score']}/100")

    print(f"\n📊 Kapacita:")
    cap = dashboard['capacity_status']
    print(f"   Status: {cap['status']}")
    print(f"   Lůžka: {cap['available_beds']}/{cap['total_beds']} ({cap['occupancy_rate']}% zaplněno)")
    print(f"   ICU: {cap['available_icu_beds']}/{cap['icu_beds']} ({cap['icu_occupancy_rate']}% zaplněno)")
    print(f"   💡 {cap['recommendation']}")

    print(f"\n👨‍⚕️  Specialisté:")
    spec_status = dashboard['specialist_status']
    print(f"   Dostupných: {spec_status['available_count']}")
    print(f"   Nedostupných: {spec_status['unavailable_count']}")
    for spec in spec_status['specialists']:
        status_icon = "✅" if spec['available'] else "❌"
        print(f"   {status_icon} {spec['specialty']}: {spec['on_call']} ({spec['response_time']})")

    if dashboard['alerts']:
        print(f"\n🚨 ALERTY:")
        for alert in dashboard['alerts']:
            print(f"   {alert}")

    if dashboard['recommendations']:
        print(f"\n💡 DOPORUČENÍ:")
        for rec in dashboard['recommendations']:
            print(f"   - {rec}")

    print("\n" + "="*80)
    print("Resource Optimizer funkční!")
    print("="*80)

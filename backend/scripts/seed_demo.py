"""
Comprehensive SIH Demo Dataset Seed Script
===========================================
Creates a realistic, interconnected coal mine governance dataset
for Smart India Hackathon demonstration.

ALL DATA IS FICTIONAL — DEMO/SIMULATED ONLY.

Usage:
    cd backend
    .\.venv\Scripts\python.exe scripts/seed_demo.py          # Seed fresh
    .\.venv\Scripts\python.exe scripts/seed_demo.py --reset   # Drop + Reseed
"""
import asyncio, sys, os, uuid, hashlib, json
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.base import Base
from app.models.hierarchy import Organization, Subsidiary, Region, Mine, Department
from app.models.user import User, Role
from app.models.compliance import ComplianceRequirement, ComplianceRecord, ComplianceStatus
from app.models.field import (
    Inspection, InspectionStatus,
    SafetyEvent, SafetyEventType, SafetyEventCategory, SafetyEventSeverity,
    CorrectiveAction, ActionStatus,
)
from app.models.workflow import Notification, EscalationRule, AuditLog
from app.models.analytics import RiskHistory, AnomalyEvent, RecurringIssue
from app.models.contractor import Contractor, Worker, AttendanceRecord
from app.models.operations import EnvironmentReading, ProductionRecord
from app.models.grievance import Grievance, GrievanceStatus
from app.models.settings import UserSettings
from app.core.security import hash_password
from app.config import get_settings
from app.database import engine

settings = get_settings()
DB_URL = settings.DATABASE_URL
TODAY = date.today()
NOW = datetime.now(timezone.utc)

def _dt(days_offset: int = 0, hours_offset: int = 0) -> datetime:
    return NOW + timedelta(days=days_offset, hours=hours_offset)

def _d(days_offset: int = 0) -> date:
    return TODAY + timedelta(days=days_offset)

# Deterministic audit hash chain
_prev_hash = "0" * 64
def _audit_hash(action, entity_type, entity_id, after_state):
    global _prev_hash
    payload = f"{_prev_hash}|{action}|{entity_type}|{entity_id}|{json.dumps(after_state, default=str)}"
    h = hashlib.sha256(payload.encode()).hexdigest()
    _prev_hash = h
    return h

async def seed_demo():
    reset = "--reset" in sys.argv
    print(f"Using database URL: {DB_URL}")

    if reset:
        print("[RESET] Dropping all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as s:
        # Check if already seeded
        from sqlalchemy import select
        existing_org = (await s.execute(select(Organization).where(Organization.name == "Eastern Coal Operations Ltd."))).scalar_one_or_none()
        if existing_org and not reset:
            print("[INFO] Demo data already exists (Eastern Coal Operations Ltd. found).")
            print("[INFO] Skipping seed process to avoid duplicates.")
            print("[INFO] Use --reset to drop and reseed data (Development only).")
            return

        # ================================================================
        # 1. ORGANIZATION HIERARCHY
        # ================================================================
        print("[1/12] Creating organization hierarchy...")
        org = Organization(name="Eastern Coal Operations Ltd.", description="[DEMO] Fictional coal mining subsidiary for SIH demonstration")
        s.add(org); await s.flush()

        sub = Subsidiary(organization_id=org.id, name="Eastern Coalfields Division")
        s.add(sub); await s.flush()

        region = Region(subsidiary_id=sub.id, name="Raniganj-Asansol Belt")
        s.add(region); await s.flush()

        mines_data = [
            ("Raniganj Central Mine", 23.6245, 87.1441, "Underground", "active"),
            ("Durgapur North Mine", 23.5204, 87.3119, "Open Cast", "active"),
            ("Asansol Open Cast Mine", 23.6889, 86.9661, "Open Cast", "active"),
        ]
        mines = []
        for name, lat, lon, mtype, status in mines_data:
            m = Mine(region_id=region.id, name=name, latitude=lat, longitude=lon, mine_type=mtype, status=status)
            s.add(m); await s.flush(); mines.append(m)

        depts_map = {}  # mine_id -> list of departments
        dept_names = ["Safety & Operations", "Environment", "Excavation", "Transport & Logistics"]
        for mine in mines:
            depts = []
            for dn in dept_names:
                d = Department(mine_id=mine.id, name=dn)
                s.add(d); await s.flush(); depts.append(d)
            depts_map[mine.id] = depts

        # ================================================================
        # 2. USERS / ROLES
        # ================================================================
        print("[2/12] Creating demo users...")
        users_spec = [
            ("admin@coalmine.gov.in", "admin123", "Rajesh Kumar (Admin)", Role.SYSTEM_ADMIN, None),
            ("corporate@coalmine.gov.in", "demo123", "Priya Sharma (Corporate)", Role.CORPORATE_MANAGER, None),
            ("manager.raniganj@coalmine.gov.in", "demo123", "Anil Verma (Mine Mgr)", Role.MINE_MANAGER, 0),
            ("manager.durgapur@coalmine.gov.in", "demo123", "Suresh Patel (Mine Mgr)", Role.MINE_MANAGER, 1),
            ("manager.asansol@coalmine.gov.in", "demo123", "Kavita Singh (Mine Mgr)", Role.MINE_MANAGER, 2),
            ("safety@coalmine.gov.in", "demo123", "Vikram Ghosh (Safety Officer)", Role.MINE_OFFICER, 0),
            ("inspector@coalmine.gov.in", "demo123", "Anita Roy (Inspector)", Role.FIELD_INSPECTOR, 0),
            ("env.officer@coalmine.gov.in", "demo123", "Deepak Mukherjee (Env. Officer)", Role.MINE_OFFICER, 1),
        ]
        users = {}
        for email, pw, name, role, mine_idx in users_spec:
            u = User(
                email=email, hashed_password=hash_password(pw),
                full_name=name, role=role, is_active=True,
                organization_id=org.id if mine_idx is None else None,
                mine_id=mines[mine_idx].id if mine_idx is not None else None,
            )
            s.add(u); await s.flush(); users[email] = u

        # Assign mine managers
        mines[0].manager_id = users["manager.raniganj@coalmine.gov.in"].id
        mines[1].manager_id = users["manager.durgapur@coalmine.gov.in"].id
        mines[2].manager_id = users["manager.asansol@coalmine.gov.in"].id
        await s.flush()

        # User settings for admin
        s.add(UserSettings(user_id=users["admin@coalmine.gov.in"].id, theme="system", language="en", default_mine_id=str(mines[0].id)))
        await s.flush()

        mgr = users["manager.raniganj@coalmine.gov.in"]
        safety_officer = users["safety@coalmine.gov.in"]
        inspector = users["inspector@coalmine.gov.in"]
        env_officer = users["env.officer@coalmine.gov.in"]

        # ================================================================
        # 3. INSPECTIONS (20 inspections across 3 mines)
        # ================================================================
        print("[3/12] Creating inspections...")
        inspection_templates = [
            # Mine 0 – Raniganj (10 inspections)
            (0, "ROUTINE", -30, InspectionStatus.CLOSED, "Routine pit inspection. All clear.", {"highwall_stable": True, "dust_controlled": True}),
            (0, "SAFETY_AUDIT", -21, InspectionStatus.VERIFIED, "Safety audit of Section B. Minor issues found.", {"ppe_compliance": True, "ventilation_adequate": False}),
            (0, "ENVIRONMENTAL", -14, InspectionStatus.SUBMITTED, "Environmental check — dust levels elevated.", {"dust_controlled": False, "water_quality_ok": True}),
            (0, "ROUTINE", -7, InspectionStatus.SUBMITTED, "Weekly routine check. Conveyor belt wear observed.", {"conveyor_ok": False, "signage_adequate": True}),
            (0, "SAFETY_AUDIT", -3, InspectionStatus.DRAFT, "Emergency exit audit — 2 exits blocked.", {"exit_1_clear": False, "exit_2_clear": False, "exit_3_clear": True}),
            (0, "ELECTRICAL", -1, InspectionStatus.SUBMITTED, "Electrical panel inspection. Loose wiring found.", {"panel_a_ok": False, "panel_b_ok": True}),
            (0, "ROUTINE", 0, InspectionStatus.DRAFT, "Today's routine inspection — in progress.", {}),
            # Mine 1 – Durgapur (7 inspections)
            (1, "ROUTINE", -25, InspectionStatus.CLOSED, "Monthly routine. PPE compliance at 92%.", {"ppe_compliance": True}),
            (1, "ENVIRONMENTAL", -18, InspectionStatus.VERIFIED, "Env. monitoring — noise levels within range.", {"noise_ok": True, "air_quality_ok": True}),
            (1, "SAFETY_AUDIT", -10, InspectionStatus.SUBMITTED, "Safety walk — inadequate barricading at Pit C.", {"barricading_ok": False}),
            (1, "ROUTINE", -5, InspectionStatus.SUBMITTED, "Haul road inspection. Road surface deteriorating.", {"road_surface_ok": False}),
            (1, "MACHINERY", -2, InspectionStatus.DRAFT, "HEMM maintenance inspection pending.", {}),
            # Mine 2 – Asansol (5 inspections)
            (2, "ROUTINE", -20, InspectionStatus.CLOSED, "Routine OC pit inspection completed.", {"slope_stability_ok": True}),
            (2, "ENVIRONMENTAL", -12, InspectionStatus.VERIFIED, "Rainwater runoff assessment done.", {"drainage_ok": True}),
            (2, "SAFETY_AUDIT", -4, InspectionStatus.SUBMITTED, "Safety audit — lighting inadequate in loading area.", {"lighting_ok": False}),
            (2, "BLASTING", -1, InspectionStatus.DRAFT, "Pre-blast survey — pending.", {}),
            # Overdue inspections
            (0, "DGMS_STATUTORY", -45, InspectionStatus.SUBMITTED, "[DEMO] DGMS statutory inspection — overdue for review.", {"statutory_check": False}),
            (1, "DGMS_STATUTORY", -40, InspectionStatus.DRAFT, "[DEMO] DGMS quarterly review — overdue.", {}),
            (2, "VENTILATION", -35, InspectionStatus.SUBMITTED, "[DEMO] Ventilation survey — pending verification.", {"ventilation_adequate": False}),
            (0, "ROUTINE", -50, InspectionStatus.CLOSED, "Historical routine — all clear at that time.", {"all_ok": True}),
        ]

        inspections = []
        for mi, itype, day_off, status, notes, checklist in inspection_templates:
            insp = Inspection(
                mine_id=mines[mi].id,
                inspector_id=inspector.id if mi == 0 else users[list(users.keys())[3 + mi]].id,
                type=itype, date=_dt(day_off), status=status,
                notes=notes, checklist_data=checklist,
            )
            s.add(insp); await s.flush(); inspections.append(insp)

        # ================================================================
        # 4. SAFETY EVENTS / NEAR MISSES (20 events)
        # ================================================================
        print("[4/12] Creating safety events...")
        safety_templates = [
            # CRITICAL (2)
            (0, SafetyEventType.INCIDENT, SafetyEventCategory.SAFETY, SafetyEventSeverity.CRITICAL,
             "Conveyor belt snapped during operation — workers evacuated from loading zone", "Conveyor 3, Section A", -2, 92, "CRITICAL"),
            (0, SafetyEventType.UNSAFE_CONDITION, SafetyEventCategory.SAFETY, SafetyEventSeverity.CRITICAL,
             "Unstable highwall with visible cracks — immediate exclusion zone established", "Highwall, Pit B North Face", -1, 88, "CRITICAL"),
            # HIGH (5)
            (0, SafetyEventType.NEAR_MISS, SafetyEventCategory.SAFETY, SafetyEventSeverity.HIGH,
             "Haul truck narrowly avoided collision with light vehicle at blind junction", "Junction 4, Pit B", -3, 75, "HIGH"),
            (1, SafetyEventType.UNSAFE_CONDITION, SafetyEventCategory.SAFETY, SafetyEventSeverity.HIGH,
             "Loose electrical cable dangling near worker walkway — shock hazard", "Walkway B, Panel Room", -5, 72, "HIGH"),
            (0, SafetyEventType.NEAR_MISS, SafetyEventCategory.OPERATIONS, SafetyEventSeverity.HIGH,
             "Excavator boom struck overhead power line — no injuries", "Section C, OB Dump", -8, 78, "HIGH"),
            (2, SafetyEventType.UNSAFE_CONDITION, SafetyEventCategory.SAFETY, SafetyEventSeverity.HIGH,
             "Emergency exit blocked by stored materials — fire escape compromised", "Loading Bay 2", -6, 70, "HIGH"),
            (1, SafetyEventType.INCIDENT, SafetyEventCategory.SAFETY, SafetyEventSeverity.HIGH,
             "Worker slipped on wet surface near pump house — minor injury", "Pump House Access Path", -4, 65, "HIGH"),
            # MEDIUM (7)
            (0, SafetyEventType.HAZARD_OBSERVATION, SafetyEventCategory.SAFETY, SafetyEventSeverity.MEDIUM,
             "Missing PPE observed — 3 workers without safety helmets", "Section A Entry Gate", -10, 45, "MEDIUM"),
            (1, SafetyEventType.HAZARD_OBSERVATION, SafetyEventCategory.ENVIRONMENT, SafetyEventSeverity.MEDIUM,
             "Water accumulation in pit floor exceeding safe limits", "Pit C Floor", -12, 50, "MEDIUM"),
            (2, SafetyEventType.UNSAFE_CONDITION, SafetyEventCategory.SAFETY, SafetyEventSeverity.MEDIUM,
             "Inadequate barricading around blasting zone", "Blast Zone 2", -9, 48, "MEDIUM"),
            (0, SafetyEventType.HAZARD_OBSERVATION, SafetyEventCategory.SAFETY, SafetyEventSeverity.MEDIUM,
             "Poor illumination in underground gallery — visibility below standard", "Gallery 7", -15, 42, "MEDIUM"),
            (1, SafetyEventType.UNSAFE_CONDITION, SafetyEventCategory.OPERATIONS, SafetyEventSeverity.MEDIUM,
             "Unstable material storage near haul road", "OB Dump Area", -11, 47, "MEDIUM"),
            (2, SafetyEventType.NEAR_MISS, SafetyEventCategory.SAFETY, SafetyEventSeverity.MEDIUM,
             "Unauthorized personnel entered restricted blasting area", "Blast Zone 1", -7, 52, "MEDIUM"),
            (0, SafetyEventType.HAZARD_OBSERVATION, SafetyEventCategory.SAFETY, SafetyEventSeverity.MEDIUM,
             "Inadequate safety signage at conveyor crossing", "Conveyor Crossing 2", -13, 40, "MEDIUM"),
            # LOW (6)
            (0, SafetyEventType.HAZARD_OBSERVATION, SafetyEventCategory.SAFETY, SafetyEventSeverity.LOW,
             "Minor oil spill near equipment parking — contained quickly", "Equipment Yard", -20, 18, "LOW"),
            (1, SafetyEventType.HAZARD_OBSERVATION, SafetyEventCategory.ENVIRONMENT, SafetyEventSeverity.LOW,
             "Dust levels slightly above normal during dry season", "Haul Road 3", -18, 22, "LOW"),
            (2, SafetyEventType.HAZARD_OBSERVATION, SafetyEventCategory.SAFETY, SafetyEventSeverity.LOW,
             "Fire extinguisher past inspection date in office block", "Admin Block", -25, 15, "LOW"),
            (0, SafetyEventType.HAZARD_OBSERVATION, SafetyEventCategory.OPERATIONS, SafetyEventSeverity.LOW,
             "Minor equipment vibration anomaly — logged for monitoring", "Crusher Unit 1", -22, 20, "LOW"),
            (1, SafetyEventType.HAZARD_OBSERVATION, SafetyEventCategory.SAFETY, SafetyEventSeverity.LOW,
             "First aid kit missing supplies — restocked", "Control Room", -16, 12, "LOW"),
            (2, SafetyEventType.HAZARD_OBSERVATION, SafetyEventCategory.ENVIRONMENT, SafetyEventSeverity.LOW,
             "Noise levels at boundary marginally above limit during blasting", "Boundary Wall East", -14, 25, "LOW"),
        ]

        safety_events = []
        for mi, etype, cat, sev, desc, loc, day_off, risk_score, risk_level in safety_templates:
            linked_insp = None
            # Link some events to inspections
            if len(safety_events) < 3 and len(inspections) > len(safety_events):
                linked_insp = inspections[len(safety_events)].id

            risk_factors = {
                "severity_weight": 0.3 if sev == SafetyEventSeverity.LOW else 0.5 if sev == SafetyEventSeverity.MEDIUM else 0.7 if sev == SafetyEventSeverity.HIGH else 0.9,
                "recurrence_factor": 1.2 if risk_score > 60 else 1.0,
                "overdue_actions_factor": 1.3 if risk_score > 70 else 1.0,
                "data_quality_score": 0.85,
                "anomaly_detected": risk_score > 75,
            }
            ev = SafetyEvent(
                mine_id=mines[mi].id, type=etype, category=cat, severity=sev,
                description=desc, location_details=loc,
                date=_dt(day_off), is_anonymous=(mi == 2),
                reporter_id=safety_officer.id if mi == 0 else users[list(users.keys())[3 + mi]].id,
                risk_score=risk_score, risk_level=risk_level, risk_factors=risk_factors,
                is_recurring=(risk_score > 60),
                inspection_id=linked_insp,
            )
            s.add(ev); await s.flush(); safety_events.append(ev)

        # ================================================================
        # 5. CORRECTIVE ACTIONS (25 actions)
        # ================================================================
        print("[5/12] Creating corrective actions...")
        ca_templates = [
            # From safety events
            (0, None, 0, "Immediately halt conveyor and perform full belt replacement", ActionStatus.IN_PROGRESS, -2, 3),
            (0, None, 1, "Install exclusion fencing and conduct geotechnical survey of highwall", ActionStatus.OPEN, -1, 5),
            (0, None, 2, "Install convex mirrors and speed breakers at Junction 4", ActionStatus.ASSIGNED, -3, 7),
            (1, None, 3, "Re-route electrical cable through conduit and add insulation", ActionStatus.IN_PROGRESS, -5, 4),
            (0, None, 4, "Install height barriers near overhead power lines", ActionStatus.OPEN, -8, 10),
            (2, None, 5, "Clear stored materials from emergency exit and install locks", ActionStatus.RESOLVED, -6, 2),
            (1, None, 6, "Install anti-slip matting and drainage near pump house", ActionStatus.IN_PROGRESS, -4, 5),
            (0, None, 7, "Enforce PPE compliance — issue warnings to defaulters", ActionStatus.CLOSED, -10, 3),
            (1, None, 8, "Deploy additional pumps for pit floor dewatering", ActionStatus.IN_PROGRESS, -12, 8),
            (2, None, 9, "Upgrade barricading to DGMS standards at blast zone", ActionStatus.ASSIGNED, -9, 6),
            (0, None, 10, "Install additional lighting in Gallery 7", ActionStatus.OPEN, -15, 10),
            (1, None, 11, "Relocate material storage away from haul road", ActionStatus.IN_PROGRESS, -11, 7),
            (2, None, 12, "Install biometric access control at blasting zones", ActionStatus.OPEN, -7, 14),
            (0, None, 13, "Install proper signage at all conveyor crossings", ActionStatus.ASSIGNED, -13, 5),
            # From inspections
            (0, 3, None, "Replace worn conveyor belt section identified in routine inspection", ActionStatus.IN_PROGRESS, -7, 5),
            (0, 4, None, "Clear and maintain emergency exits — re-inspect within 48 hours", ActionStatus.OPEN, -3, 2),
            (0, 5, None, "Tighten electrical panel wiring — schedule licensed electrician", ActionStatus.ASSIGNED, -1, 3),
            (1, 9, None, "Rebuild barricading at Pit C per DGMS guidelines", ActionStatus.IN_PROGRESS, -10, 8),
            (1, 10, None, "Grade and resurface haul road section", ActionStatus.OPEN, -5, 10),
            # Overdue corrective actions
            (0, None, 0, "Conduct root cause analysis of conveyor failure and submit report", ActionStatus.OPEN, -15, -5),  # overdue
            (1, None, 6, "Complete medical review for injured worker and file DGMS report", ActionStatus.ASSIGNED, -20, -8),  # overdue
            (0, 16, None, "Complete pending DGMS statutory review documentation", ActionStatus.OPEN, -30, -10),  # overdue
            (2, None, 5, "Conduct fire drill after emergency exit was cleared", ActionStatus.OPEN, -14, -3),  # overdue
            (0, None, 10, "Submit lighting improvement plan to DGMS for underground gallery", ActionStatus.ASSIGNED, -25, -7),  # overdue
            (1, None, 8, "Submit dewatering completion certificate to regional office", ActionStatus.OPEN, -18, -4),  # overdue
        ]

        corrective_actions = []
        for mi, insp_idx, ev_idx, desc, status, created_off, due_off in ca_templates:
            ca = CorrectiveAction(
                mine_id=mines[mi].id,
                source_inspection_id=inspections[insp_idx].id if insp_idx is not None else None,
                source_event_id=safety_events[ev_idx].id if ev_idx is not None else None,
                description=desc,
                assigned_to_user_id=mgr.id if mi == 0 else users[list(users.keys())[3 + mi]].id,
                due_date=_dt(due_off) if due_off > 0 else _dt(created_off + due_off),
                status=status,
            )
            s.add(ca); await s.flush(); corrective_actions.append(ca)

        # ================================================================
        # 6. COMPLIANCE REQUIREMENTS & RECORDS (15 requirements, 25 records)
        # ================================================================
        print("[6/12] Creating compliance data...")
        req_templates = [
            ("[DEMO] Monthly Air Quality Assessment", "Regular checking of particulate matter levels in mining areas.", "Environmental", "Monthly", "CIL Env Protocol 4.2"),
            ("[DEMO] Quarterly Equipment Safety Audit", "Audit of heavy earth moving machinery (HEMM) per DGMS circular.", "Safety", "Quarterly", "DGMS Circular 2020"),
            ("[DEMO] Weekly Highwall Stability Check", "Visual and instrumented check of highwall and bench stability.", "Safety", "Weekly", "DGMS Tech Circular 03/2019"),
            ("[DEMO] Monthly Ventilation Survey", "Underground ventilation survey as per CMR 1957 Reg 130.", "Safety", "Monthly", "CMR 1957 Reg 130"),
            ("[DEMO] Daily Blasting Register", "Maintain daily record of blasting operations and explosives usage.", "Statutory", "Daily", "CMR 1957 Reg 106"),
            ("[DEMO] Annual Electrical Installation Audit", "Comprehensive electrical safety audit per IE Rules.", "Safety", "Annual", "Indian Electricity Rules 1956"),
            ("[DEMO] Monthly Water Quality Monitoring", "Monitoring pH, TDS, heavy metals in mine discharge.", "Environmental", "Monthly", "MoEF&CC Guidelines"),
            ("[DEMO] Bi-Annual Emergency Preparedness Drill", "Mine rescue and emergency response drill.", "Safety", "Bi-Annual", "DGMS Circular on Emergency Preparedness"),
            ("[DEMO] Weekly Conveyor Belt Inspection", "Physical inspection of conveyor belt condition and alignment.", "Operational", "Weekly", "Mine Operations Manual Ch.12"),
            ("[DEMO] Monthly Contractor Safety Compliance", "Review contractor safety records and documentation.", "Workforce", "Monthly", "CIL Contractor Policy"),
            ("[DEMO] Quarterly Noise Level Assessment", "Ambient and occupational noise measurement.", "Environmental", "Quarterly", "OSHA/DGMS Noise Standards"),
            ("[DEMO] Monthly PPE Compliance Audit", "Verify all personnel use appropriate PPE.", "Safety", "Monthly", "CMR 1957 Reg 26"),
            ("[DEMO] Annual Land Reclamation Plan Review", "Assess mine closure and land rehabilitation progress.", "Environmental", "Annual", "MoEF&CC Land Reclamation Guidelines"),
            ("[DEMO] Weekly Dust Suppression Verification", "Verify dust suppression measures on haul roads and work areas.", "Environmental", "Weekly", "CPCB Air Quality Standards"),
            ("[DEMO] Monthly Statutory Returns Filing", "Timely filing of returns to DGMS and state authorities.", "Statutory", "Monthly", "Mines Act 1952 Sec 44"),
        ]

        requirements = []
        for title, desc, cat, freq, ref in req_templates:
            for mine in mines:
                req = ComplianceRequirement(
                    title=title, description=desc, category=cat,
                    frequency=freq, source_reference=ref,
                    applicable_mine_id=mine.id,
                )
                s.add(req); await s.flush(); requirements.append(req)

        # Create compliance records (mix of statuses)
        statuses_cycle = [
            ComplianceStatus.COMPLIANT, ComplianceStatus.COMPLIANT, ComplianceStatus.DUE_SOON,
            ComplianceStatus.OVERDUE, ComplianceStatus.COMPLIANT, ComplianceStatus.NON_COMPLIANT,
            ComplianceStatus.COMPLIANT, ComplianceStatus.DUE_SOON, ComplianceStatus.COMPLIANT,
            ComplianceStatus.COMPLIANT, ComplianceStatus.COMPLIANT, ComplianceStatus.AT_RISK,
            ComplianceStatus.COMPLIANT, ComplianceStatus.COMPLIANT, ComplianceStatus.OVERDUE,
        ]
        comp_records = []
        for i, req in enumerate(requirements[:30]):  # First 30 requirements (10 per mine)
            status = statuses_cycle[i % len(statuses_cycle)]
            due_offset = {
                ComplianceStatus.COMPLIANT: -5,
                ComplianceStatus.DUE_SOON: 3,
                ComplianceStatus.OVERDUE: -10,
                ComplianceStatus.NON_COMPLIANT: -15,
                ComplianceStatus.AT_RISK: 1,
            }[status]
            sub_date = _dt(-7) if status == ComplianceStatus.COMPLIANT else None
            dept_list = depts_map.get(req.applicable_mine_id, [])
            dept_id = dept_list[0].id if dept_list else None

            rec = ComplianceRecord(
                requirement_id=req.id,
                due_date=_d(due_offset),
                status=status,
                responsible_department_id=dept_id,
                responsible_officer_id=mgr.id,
                submission_date=sub_date,
            )
            s.add(rec); await s.flush(); comp_records.append(rec)

        # ================================================================
        # 7. ENVIRONMENTAL READINGS (18 readings)
        # ================================================================
        print("[7/12] Creating environmental data...")
        env_templates = [
            (0, "Dust (PM10)", 145.0, "µg/m³", True),   # slightly high
            (0, "Dust (PM10)", 95.0, "µg/m³", True),
            (0, "Noise", 82.0, "dB(A)", True),
            (0, "Air Quality (SO2)", 35.0, "µg/m³", True),
            (0, "Water Quality (pH)", 6.8, "pH", True),
            (0, "Temperature", 38.5, "°C", True),       # high
            (1, "Dust (PM10)", 180.0, "µg/m³", True),   # ALERT — above threshold
            (1, "Noise", 78.0, "dB(A)", True),
            (1, "Air Quality (SO2)", 22.0, "µg/m³", True),
            (1, "Water Quality (pH)", 7.2, "pH", True),
            (1, "Rainfall", 85.0, "mm", True),          # heavy
            (1, "Temperature", 34.2, "°C", True),
            (2, "Dust (PM10)", 110.0, "µg/m³", True),
            (2, "Noise", 88.0, "dB(A)", True),          # ALERT — above limit
            (2, "Air Quality (SO2)", 45.0, "µg/m³", True),  # elevated
            (2, "Water Quality (pH)", 5.5, "pH", True),     # acidic — alert
            (2, "Rainfall", 120.0, "mm", True),             # very heavy
            (2, "Temperature", 36.0, "°C", True),
        ]
        for mi, param, val, unit, sim in env_templates:
            s.add(EnvironmentReading(mine_id=mines[mi].id, parameter=param, value=val, unit=unit, is_simulated=sim))
        await s.flush()

        # ================================================================
        # 8. PRODUCTION RECORDS (9 records, 3 per mine)
        # ================================================================
        print("[8/12] Creating production records...")
        for mi, mine in enumerate(mines):
            targets = [5000, 4800, 5200]
            actuals = [4200, 4900, 4600]
            for j in range(3):
                dev = round((actuals[j] - targets[j]) / targets[j] * 100, 1)
                s.add(ProductionRecord(
                    mine_id=mine.id, date=_d(-j * 7),
                    target=targets[j], actual=actuals[j], deviation=dev,
                ))
        await s.flush()

        # ================================================================
        # 9. CONTRACTORS & WORKERS
        # ================================================================
        print("[9/12] Creating contractors, workers, attendance...")
        contractors_data = [
            (0, "Apex Drillers Pvt. Ltd.", "Excavation", 15),
            (0, "SafeBlast Solutions", "Blasting", 25),
            (1, "GreenMine Transport Co.", "Hauling", 10),
            (1, "TechDrill India", "Drilling", 20),
            (2, "Bharat Earth Movers", "Excavation", 12),
            (2, "Reliable Maintenance Corp.", "Equipment Maintenance", 8),
        ]
        contractors = []
        for mi, name, wtype, risk in contractors_data:
            c = Contractor(mine_id=mines[mi].id, name=name, work_type=wtype, risk_indicator=risk, active=True)
            s.add(c); await s.flush(); contractors.append(c)

        workers = []
        worker_names = [
            "Ramesh Yadav", "Sunil Das", "Mohan Mondal", "Amit Sarkar", "Bipin Oraon",
            "Ravi Tirkey", "Sanjay Mahato", "Gopal Murmu", "Ashok Hembram", "Pintu Shaw",
            "Manoj Besra", "Dilip Tudu",
        ]
        for i, wname in enumerate(worker_names):
            mine_idx = i % 3
            ctr = contractors[mine_idx * 2 + (i % 2)]
            w = Worker(mine_id=mines[mine_idx].id, contractor_id=ctr.id, name=wname,
                       training_metadata={"safety_induction": True, "last_training": str(_d(-30 - i * 5))})
            s.add(w); await s.flush(); workers.append(w)

        # Attendance records (last 3 days for each worker)
        for w in workers:
            for day_off in range(-2, 1):
                s.add(AttendanceRecord(
                    worker_id=w.id, timestamp=_dt(day_off, 6),
                    location_data="Mine Gate Biometric", verified=True, is_anomaly=False,
                ))
        await s.flush()

        # ================================================================
        # 10. GRIEVANCES (8 grievances)
        # ================================================================
        print("[10/12] Creating grievances...")
        grievance_data = [
            (0, "Safety concern — inadequate lighting in underground section", "Workers report poor visibility in Gallery 7 during night shift.", "Safety", GrievanceStatus.INVESTIGATING),
            (0, "Sanitation issue — no clean drinking water at Pit B", "Drinking water facility has been non-functional for 3 days.", "Infrastructure", GrievanceStatus.PENDING),
            (1, "Contractor concern — SafeBlast workers lack valid training certificates", "Multiple blasting crew members have expired certifications.", "Workforce", GrievanceStatus.INVESTIGATING),
            (1, "Environmental concern — excessive dust on haul roads", "Community members near Durgapur mine report respiratory issues.", "Environmental", GrievanceStatus.PENDING),
            (2, "Workplace infrastructure — broken safety railing", "Safety railing near loading bay damaged and not repaired.", "Infrastructure", GrievanceStatus.RESOLVED),
            (0, "Safety concern — night shift inadequate supervision", "Only 1 supervisor for 30 workers during night operations.", "Safety", GrievanceStatus.PENDING),
            (1, "Environmental concern — noise during residential hours", "Blasting conducted after permitted hours on 3 occasions.", "Environmental", GrievanceStatus.INVESTIGATING),
            (2, "Contractor concern — delayed wage payments", "Workers of Bharat Earth Movers report 2-month salary delay.", "Workforce", GrievanceStatus.PENDING),
        ]
        for mi, title, desc, cat, status in grievance_data:
            s.add(Grievance(
                mine_id=mines[mi].id, submitter_id=safety_officer.id,
                title=title, description=desc, category=cat, status=status,
                assigned_department_id=depts_map[mines[mi].id][0].id,
                ai_suggestions={},
            ))
        await s.flush()

        # ================================================================
        # 11. RISK HISTORY, ANOMALIES, RECURRING ISSUES
        # ================================================================
        print("[11/12] Creating risk history, anomalies, recurring issues...")
        for mi, mine in enumerate(mines):
            base_scores = [35, 42, 55, 62, 48, 70, 65, 58, 75, 45]
            for i, score in enumerate(base_scores):
                s.add(RiskHistory(
                    mine_id=mine.id, score=score + mi * 3,
                    factors={"safety_events": score // 10, "overdue_actions": (score - 30) // 15, "compliance_gap": max(0, score - 50) // 10},
                    evaluated_at=_dt(-30 + i * 3),
                ))

        # Anomaly events
        s.add(AnomalyEvent(mine_id=mines[0].id, what_was_abnormal="Dust PM10 spike to 145 µg/m³",
                           baseline_reference="Normal: 80-100 µg/m³", observed_value="145 µg/m³",
                           anomaly_signal="ENVIRONMENTAL_SPIKE", timestamp=_dt(-2)))
        s.add(AnomalyEvent(mine_id=mines[1].id, what_was_abnormal="3 safety events in 48 hours",
                           baseline_reference="Avg: 1 event per week", observed_value="3 events in 2 days",
                           anomaly_signal="FREQUENCY_SPIKE", timestamp=_dt(-4)))
        s.add(AnomalyEvent(mine_id=mines[2].id, what_was_abnormal="Water pH dropped to 5.5",
                           baseline_reference="Normal: 6.5-8.0", observed_value="5.5 pH",
                           anomaly_signal="ENVIRONMENTAL_THRESHOLD_BREACH", timestamp=_dt(-1)))
        await s.flush()

        # Recurring issues
        ev_ids_m0 = [str(e.id) for e in safety_events if e.mine_id == mines[0].id][:3]
        ev_ids_m1 = [str(e.id) for e in safety_events if e.mine_id == mines[1].id][:2]
        s.add(RecurringIssue(mine_id=mines[0].id, recurrence_count=3, time_window_days=30,
                             location_details="Section A / Conveyor area", issue_category="Equipment Failure",
                             related_record_ids=ev_ids_m0, recurrence_signal="CONVEYOR_FAILURE_CLUSTER"))
        s.add(RecurringIssue(mine_id=mines[1].id, recurrence_count=2, time_window_days=14,
                             location_details="Pit C Area", issue_category="Barricading",
                             related_record_ids=ev_ids_m1, recurrence_signal="BARRICADING_DEFICIENCY"))
        await s.flush()

        # ================================================================
        # 12. NOTIFICATIONS & AUDIT TRAIL
        # ================================================================
        print("[12/12] Creating notifications and audit trail...")
        notif_templates = [
            (mgr.id, "🔴 CRITICAL: Conveyor Belt Failure", "A critical incident — conveyor belt snapped at Section A. Immediate corrective action required.", "CRITICAL_FINDING", "SafetyEvent", safety_events[0].id),
            (mgr.id, "🔴 CRITICAL: Highwall Instability", "Unstable highwall detected at Pit B North Face. Exclusion zone established.", "CRITICAL_FINDING", "SafetyEvent", safety_events[1].id),
            (mgr.id, "⚠️ Inspection Overdue", "DGMS statutory inspection is 45 days overdue for Raniganj Central Mine.", "DEADLINE_APPROACHING", "Inspection", inspections[16].id),
            (mgr.id, "⚠️ Corrective Action Overdue", "Root cause analysis for conveyor failure is 5 days past due date.", "DEADLINE_APPROACHING", "CorrectiveAction", corrective_actions[19].id),
            (safety_officer.id, "📋 New Near Miss Report", "Haul truck near-miss at Junction 4. Please review and assign corrective actions.", "NEW_SUBMISSION", "SafetyEvent", safety_events[2].id),
            (env_officer.id, "🌡️ Environmental Alert", "Dust PM10 levels at Durgapur mine reached 180 µg/m³ — above 150 µg/m³ threshold.", "THRESHOLD_EXCEEDED", "EnvironmentReading", None),
            (mgr.id, "📊 Compliance Review Required", "Monthly air quality assessment is due in 3 days for Raniganj Central Mine.", "DEADLINE_APPROACHING", "ComplianceRecord", comp_records[2].id if len(comp_records) > 2 else None),
            (users["manager.durgapur@coalmine.gov.in"].id, "⚠️ Worker Injury Report", "Worker slipped near pump house. Medical review and DGMS report required.", "CRITICAL_FINDING", "SafetyEvent", safety_events[6].id),
        ]
        for uid, title, msg, ntype, etype, eid in notif_templates:
            s.add(Notification(
                user_id=uid, title=title, message=msg,
                notification_type=ntype, entity_type=etype,
                entity_id=eid, is_read=False,
            ))
        await s.flush()

        # Escalation rules
        s.add(EscalationRule(entity_type="CorrectiveAction", condition="SEVERITY=CRITICAL", delay_hours=48, escalate_to_role=Role.REGIONAL_MANAGER.value))
        s.add(EscalationRule(entity_type="SafetyEvent", condition="SEVERITY=CRITICAL", delay_hours=24, escalate_to_role=Role.CORPORATE_MANAGER.value))
        await s.flush()

        # Audit trail (interconnected chain)
        audit_entries = [
            (mgr, "CREATE", "SafetyEvent", safety_events[0].id, None, {"type": "INCIDENT", "severity": "CRITICAL", "description": "Conveyor belt snapped"}),
            (mgr, "RISK_EVALUATE", "SafetyEvent", safety_events[0].id, None, {"risk_score": 92, "risk_level": "CRITICAL"}),
            (inspector, "CREATE", "Inspection", inspections[3].id, None, {"type": "ROUTINE", "status": "SUBMITTED"}),
            (inspector, "UPDATE", "Inspection", inspections[3].id, {"status": "DRAFT"}, {"status": "SUBMITTED", "notes": "Conveyor belt wear observed"}),
            (mgr, "CREATE", "CorrectiveAction", corrective_actions[0].id, None, {"description": "Halt conveyor and replace belt", "status": "IN_PROGRESS"}),
            (safety_officer, "CREATE", "SafetyEvent", safety_events[2].id, None, {"type": "NEAR_MISS", "severity": "HIGH"}),
            (mgr, "RISK_EVALUATE", "SafetyEvent", safety_events[2].id, None, {"risk_score": 75, "risk_level": "HIGH"}),
            (mgr, "CREATE", "CorrectiveAction", corrective_actions[2].id, None, {"description": "Install mirrors at Junction 4", "status": "ASSIGNED"}),
            (mgr, "UPDATE", "ComplianceRecord", comp_records[0].id if comp_records else uuid.uuid4(), {"status": "DUE_SOON"}, {"status": "COMPLIANT", "submission_date": str(NOW)}),
            (inspector, "CREATE", "Inspection", inspections[4].id, None, {"type": "SAFETY_AUDIT", "status": "DRAFT", "notes": "Emergency exit audit"}),
            (mgr, "ESCALATE", "CorrectiveAction", corrective_actions[19].id, None, {"reason": "Overdue by 5 days", "escalated_to": "regional_manager"}),
            (safety_officer, "UPDATE", "SafetyEvent", safety_events[5].id, {"status": "OPEN"}, {"status": "RESOLVED", "corrective_action": str(corrective_actions[5].id)}),
        ]
        global _prev_hash
        _prev_hash = "0" * 64
        for user, action, etype, eid, before, after in audit_entries:
            h = _audit_hash(action, etype, eid, after)
            s.add(AuditLog(
                user_id=user.id, role=user.role.value, action=action,
                entity_type=etype, entity_id=eid,
                before_state=before, after_state=after,
                previous_hash=_prev_hash, hash_signature=h,
            ))
        await s.flush()

        await s.commit()

    print("\n" + "=" * 60)
    print("[OK] DEMO DATASET SEEDED SUCCESSFULLY")
    print("=" * 60)
    print(f"  Organization:       1 (Eastern Coal Operations Ltd.)")
    print(f"  Subsidiary:         1 (Eastern Coalfields Division)")
    print(f"  Region:             1 (Raniganj-Asansol Belt)")
    print(f"  Mines:              3")
    print(f"  Departments:        {len(dept_names) * 3}")
    print(f"  Users:              {len(users)}")
    print(f"  Inspections:        {len(inspections)}")
    print(f"  Safety Events:      {len(safety_events)}")
    print(f"  Corrective Actions: {len(corrective_actions)}")
    print(f"  Compliance Reqs:    {len(requirements)}")
    print(f"  Compliance Records: {len(comp_records)}")
    print(f"  Env. Readings:      {len(env_templates)}")
    print(f"  Contractors:        {len(contractors)}")
    print(f"  Workers:            {len(workers)}")
    print(f"  Grievances:         {len(grievance_data)}")
    print(f"  Notifications:      {len(notif_templates)}")
    print(f"  Audit Logs:         {len(audit_entries)}")
    print(f"  Risk History:       30")
    print(f"  Anomaly Events:     3")
    print(f"  Recurring Issues:   2")
    print("=" * 60)
    print("\nDEMO ACCOUNTS:")
    print("  admin@coalmine.gov.in          / admin123  (System Admin)")
    print("  manager.raniganj@coalmine.gov.in / demo123 (Mine Manager)")
    print("  safety@coalmine.gov.in          / demo123  (Safety Officer)")
    print("  inspector@coalmine.gov.in       / demo123  (Inspector)")
    print("  env.officer@coalmine.gov.in     / demo123  (Env. Officer)")
    print("  corporate@coalmine.gov.in       / demo123  (Corporate Mgr)")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(seed_demo())

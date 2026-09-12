import asyncio
import os
import sys

# Add backend dir to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, async_sessionmaker
from app.models.hierarchy import Organization, Subsidiary, Region, Mine, Department
from app.models.user import User, Role
from app.core.security import hash_password

from app.models.compliance import ComplianceRequirement, ComplianceRecord, ComplianceStatus
from datetime import date, timedelta, datetime

async def seed_data():
    # Ensure tables exist
    from app.models.base import Base
    import app.models
    from app.models.analytics import AnomalyEvent, RecurringIssue
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_sessionmaker(engine, class_=AsyncSession)() as session:
        # Create hierarchy
        org = Organization(name="Coal India Ltd", description="State-owned coal mining corporate")
        session.add(org)
        await session.flush()
        
        sub = Subsidiary(organization_id=org.id, name="Eastern Coalfields")
        session.add(sub)
        await session.flush()
        
        region = Region(subsidiary_id=sub.id, name="Raniganj Region")
        session.add(region)
        await session.flush()
        
        mine = Mine(region_id=region.id, name="Mine Alpha", latitude=23.6, longitude=86.9, status="active", mine_type="Open Cast")
        session.add(mine)
        await session.flush()
        
        dept = Department(mine_id=mine.id, name="Safety & Operations")
        session.add(dept)
        await session.flush()

        # Create Users
        admin_user = User(
            email="admin@coalmine.gov.in",
            hashed_password=hash_password("admin123"),
            full_name="System Admin",
            role=Role.SYSTEM_ADMIN,
        )
        session.add(admin_user)
        
        manager_user = User(
            email="manager.alpha@coalmine.gov.in",
            hashed_password=hash_password("manager123"),
            full_name="Alpha Manager",
            role=Role.MINE_MANAGER,
            mine_id=mine.id
        )
        session.add(manager_user)
        await session.flush()

        mine.manager_id = manager_user.id
        session.add(mine)
        await session.flush()

        # Phase 3: Compliance Data
        req1 = ComplianceRequirement(
            title="[DEMO] Monthly Air Quality Assessment",
            description="Regular checking of particulate matter in open cast sectors.",
            category="Environmental",
            frequency="Monthly",
            source_reference="CIL Env Protocol 4.2",
            applicable_mine_id=mine.id
        )
        req2 = ComplianceRequirement(
            title="[DEMO] Quarterly Equipment Safety Audit",
            description="Audit of heavy earth moving machinery (HEMM).",
            category="Safety",
            frequency="Quarterly",
            source_reference="DGMS Circular 2020",
            applicable_mine_id=mine.id
        )
        session.add_all([req1, req2])
        await session.flush()

        # Records
        today = date.today()
        rec1 = ComplianceRecord(
            requirement_id=req1.id,
            due_date=today + timedelta(days=5),
            status=ComplianceStatus.DUE_SOON,
            responsible_department_id=dept.id,
            responsible_officer_id=manager_user.id
        )
        rec2 = ComplianceRecord(
            requirement_id=req2.id,
            due_date=today - timedelta(days=2),
            status=ComplianceStatus.OVERDUE,
            responsible_department_id=dept.id,
            responsible_officer_id=manager_user.id
        )
        rec3 = ComplianceRecord(
            requirement_id=req1.id,
            due_date=today - timedelta(days=25),
            status=ComplianceStatus.COMPLIANT,
            responsible_department_id=dept.id,
            responsible_officer_id=manager_user.id,
            submission_date=datetime.now()
        )
        session.add_all([rec1, rec2, rec3])
        
        from app.models.field import SafetyEvent, SafetyEventType, SafetyEventSeverity, CorrectiveAction, ActionStatus, Inspection, InspectionStatus
        
        # Add UserSettings for demo
        from app.models.settings import UserSettings
        u_settings = UserSettings(user_id=admin_user.id, theme='system', language='en', default_mine_id=str(mine.id))
        session.add(u_settings)
        await session.flush()
        
        # Add Inspection
        insp1 = Inspection(
            mine_id=mine.id,
            inspector_id=manager_user.id,
            type="ROUTINE",
            date=datetime.now(),
            status=InspectionStatus.SUBMITTED,
            notes="Routine inspection of Pit B highwall.",
            checklist_data={"highwall_stable": True, "dust_controlled": False}
        )
        session.add(insp1)
        await session.flush()

        # Add a Near Miss (Finding)
        nm1 = SafetyEvent(
            mine_id=mine.id,
            type=SafetyEventType.NEAR_MISS,
            severity=SafetyEventSeverity.HIGH,
            description="Haul truck almost collided with light vehicle at junction 4.",
            location_details="Junction 4, Pit B",
            date=datetime.now(),
            is_anonymous=True,
            reporter_id=manager_user.id,
            inspection_id=insp1.id # Linked as a finding
        )
        
        # Add an Incident
        inc1 = SafetyEvent(
            mine_id=mine.id,
            type=SafetyEventType.INCIDENT,
            severity=SafetyEventSeverity.CRITICAL,
            description="Conveyor belt tear causing spillage.",
            location_details="Conveyor 2",
            date=datetime.now() - timedelta(days=1),
            is_anonymous=False,
            reporter_id=manager_user.id
        )
        session.add_all([nm1, inc1])
        await session.flush()
        
        # Add Corrective Action
        ca1 = CorrectiveAction(
            mine_id=mine.id,
            source_event_id=inc1.id,
            description="Repair conveyor belt and inspect idlers.",
            assigned_to_user_id=manager_user.id,
            due_date=datetime.now() + timedelta(days=2),
            status=ActionStatus.OPEN
        )
        session.add(ca1)
        
        from app.models.workflow import EscalationRule, Notification
        from app.core.audit import log_audit_event
        
        # Add Escalation Rules
        er1 = EscalationRule(
            entity_type="CorrectiveAction",
            condition="SEVERITY=CRITICAL",
            delay_hours=48,
            escalate_to_role=Role.REGIONAL_MANAGER
        )
        session.add(er1)
        
        # Add Notification
        notif = Notification(
            user_id=manager_user.id,
            title="New Incident Reported",
            message="A critical incident (Conveyor belt tear) was reported.",
            notification_type="CRITICAL_FINDING",
            entity_type="SafetyEvent",
            entity_id=inc1.id,
            is_read=False
        )
        session.add(notif)
        await session.flush()
        
        # --- Phase 9: Secondary Modules Seed Data ---
        from app.models.contractor import Contractor, Worker
        from app.models.operations import EnvironmentReading, ProductionRecord
        
        contractor = Contractor(
            mine_id=mine.id,
            name="Apex Drillers LLC",
            work_type="Excavation",
            risk_indicator=15,
            active=True
        )
        session.add(contractor)
        await session.flush()
        
        env = EnvironmentReading(
            mine_id=mine.id,
            parameter="Dust",
            value=160.5,
            unit="ug/m3",
            is_simulated=True
        )
        session.add(env)
        
        prod = ProductionRecord(
            mine_id=mine.id,
            date=date.today(),
            target=5000.0,
            actual=4200.0,
            deviation=-16.0
        )
        session.add(prod)
        await session.flush()
        
        # Add Tamper-Evident Audit Log
        await log_audit_event(
            db=session,
            user=manager_user,
            action="CREATE",
            entity_type="CorrectiveAction",
            entity_id=ca1.id,
            before_state=None,
            after_state={"status": ca1.status.value, "assigned_to": str(manager_user.id)}
        )
        
        await session.commit()
        print("Seed data successfully created.")

if __name__ == "__main__":
    asyncio.run(seed_data())

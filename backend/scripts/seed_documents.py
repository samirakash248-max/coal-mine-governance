import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Ensure the app module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine
from app.models.hierarchy import Mine
from app.models.user import User
from app.models.document import Document, DocumentStatus

async def seed_documents():
    async with AsyncSession(engine) as s:
        # Get an existing Mine to attach documents to
        mine = (await s.execute(select(Mine).limit(1))).scalar_one_or_none()
        if not mine:
            print("No mines found. Please run seed_demo.py first.")
            return

        # Get an existing User to act as the owner
        user = (await s.execute(select(User).limit(1))).scalar_one_or_none()
        
        NOW = datetime.now(timezone.utc)
        
        demo_documents_data = [
            {
                "title": "DGMS Approval for Deep Hole Blasting",
                "document_number": "DGMS/RB/2026/104",
                "category": "Statutory Permissions",
                "issue_date": NOW - timedelta(days=120),
                "expiry_date": NOW + timedelta(days=245),
                "file_path": "/mock-storage/dgms_blasting_approval.pdf",
                "status": DocumentStatus.VERIFIED
            },
            {
                "title": "MoEF Environmental Clearance Certificate",
                "document_number": "EC-MOEF-8821",
                "category": "Environmental",
                "issue_date": NOW - timedelta(days=300),
                "expiry_date": NOW + timedelta(days=1500),
                "file_path": "/mock-storage/moef_clearance.pdf",
                "status": DocumentStatus.VERIFIED
            },
            {
                "title": "Standard Operating Procedure: Heavy Machinery",
                "document_number": "SOP-HM-003",
                "category": "Safety Policies",
                "issue_date": NOW - timedelta(days=40),
                "expiry_date": None,
                "file_path": "/mock-storage/sop_machinery.pdf",
                "status": DocumentStatus.VERIFIED
            },
            {
                "title": "Q3 Audit Trail - Contractor Vehicles",
                "document_number": "AUD-Q3-99",
                "category": "Audit Reports",
                "issue_date": NOW - timedelta(days=15),
                "expiry_date": None,
                "file_path": "/mock-storage/q3_audit.pdf",
                "status": DocumentStatus.PENDING_VERIFICATION
            }
        ]

        inserted_count = 0
        skipped_count = 0

        for doc_data in demo_documents_data:
            doc_number = doc_data["document_number"]
            # Check if this document_number already exists
            existing = (await s.execute(select(Document).where(Document.document_number == doc_number))).scalar_one_or_none()
            
            if existing:
                print(f"Skipping existing document: {doc_number}")
                skipped_count += 1
            else:
                new_doc = Document(
                    mine_id=mine.id,
                    owner_id=user.id if user else None,
                    **doc_data
                )
                s.add(new_doc)
                inserted_count += 1
                print(f"Inserting document: {doc_number}")

        if inserted_count > 0:
            await s.commit()
            
        print(f"\n--- Seeding Complete ---")
        print(f"Inserted: {inserted_count}")
        print(f"Skipped:  {skipped_count}")

        # Verification step
        all_docs = (await s.execute(select(Document))).scalars().all()
        print(f"\n--- Verification ---")
        print(f"Total documents in database: {len(all_docs)}")
        for d in all_docs:
            print(f" - [{d.document_number}] {d.title} (Status: {d.status.value})")

if __name__ == "__main__":
    asyncio.run(seed_documents())

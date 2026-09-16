Write-Host "Starting Database Migration..."
alembic upgrade head
Write-Host "Seeding Demo Data..."
python scripts/seed_demo.py
Write-Host "Done!"

#!/bin/bash
set -e
echo "Starting Database Migration..."
alembic upgrade head
echo "Seeding Demo Data..."
python scripts/seed_demo.py
echo "Done!"

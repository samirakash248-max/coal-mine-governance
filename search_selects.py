import glob
import re

for filepath in glob.glob("backend/app/api/v1/*.py"):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Just print out files that have 'select('
    if "select(" in content:
        print(f"\n--- {filepath} ---")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "select(" in line:
                print(f"L{i+1}: {line.strip()}")
                

import re

filepath = "backend/tests/test_isolation.py"
with open(filepath, 'r') as f:
    content = f.read()

# Fix the fixture by committing user first
old_fixture = """    db_session.add_all([org, sub, reg, mine_a, mine_b, user_a, insp_b, event_b])
    await db_session.commit()"""

new_fixture = """    db_session.add_all([org, sub, reg, mine_a, mine_b, user_a])
    await db_session.flush()
    
    insp_b.inspector_id = user_a.id
    db_session.add_all([insp_b, event_b])
    await db_session.commit()"""

content = content.replace(old_fixture, new_fixture)
with open(filepath, 'w') as f:
    f.write(content)

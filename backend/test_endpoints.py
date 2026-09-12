import httpx, time
base = "http://127.0.0.1:8002/api/v1"

# Login
t0 = time.time()
r = httpx.post(f"{base}/auth/login", data={"username": "admin@coalmine.gov.in", "password": "admin123"})
print(f"Login: {time.time()-t0:.3f}s  status={r.status_code}")
token = r.json()["access_token"]
h = {"Authorization": f"Bearer {token}"}

# Dashboard
t0 = time.time()
r = httpx.get(f"{base}/dashboard/summary", headers=h)
print(f"Dashboard: {time.time()-t0:.3f}s  status={r.status_code}")
d = r.json()
print(f"  mines={d['total_mines']}  compliance={d['compliance_percentage']}%  overdue={d['overdue_count']}")
print(f"  near_misses={d['open_near_misses_count']}  incidents={d['incidents_count']}  critical={d['critical_findings_count']}")
print(f"  overdue_actions={d['overdue_actions_count']}  high_risk={d['high_critical_risk_cases']}")

# Inspections
t0 = time.time()
r = httpx.get(f"{base}/inspections/", headers=h, timeout=10)
print(f"Inspections: {time.time()-t0:.3f}s  status={r.status_code}  count={len(r.json())}")

# Safety events
t0 = time.time()
r = httpx.get(f"{base}/field/events", headers=h, timeout=10)
print(f"Safety Events: {time.time()-t0:.3f}s  status={r.status_code}  count={len(r.json())}")

# Corrective actions
t0 = time.time()
r = httpx.get(f"{base}/field/actions", headers=h, timeout=10)
print(f"Corrective Actions: {time.time()-t0:.3f}s  status={r.status_code}  count={len(r.json())}")

# Compliance
t0 = time.time()
r = httpx.get(f"{base}/compliance/records", headers=h, timeout=10)
print(f"Compliance: {time.time()-t0:.3f}s  status={r.status_code}  count={len(r.json())}")

# Copilot domain test (OUT-OF-DOMAIN)
t0 = time.time()
r = httpx.post(f"{base}/copilot/chat", json={"message": "What is the capital of France?", "history": []}, headers=h, timeout=10)
ans = r.json().get("answer", "N/A")
print(f"Domain Guard (reject): {time.time()-t0:.3f}s  answer={ans[:100]}")

# Copilot domain test (IN-DOMAIN)
t0 = time.time()
r = httpx.post(f"{base}/copilot/chat", json={"message": "How do I report a near miss?", "history": []}, headers=h, timeout=10)
ans = r.json().get("answer", "N/A")
print(f"In-domain: {time.time()-t0:.3f}s  answer={ans[:100]}")

# Health
t0 = time.time()
r = httpx.get(f"{base}/health", timeout=10)
hj = r.json()
print(f"Health: {time.time()-t0:.3f}s  status={r.status_code}  ai={hj['providers']['ai']['configured_provider']}")

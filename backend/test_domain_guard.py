import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        print("Logging in...")
        base_url = "http://127.0.0.1:8002/api/v1"
        try:
            r = await client.post(f"{base_url}/auth/login", data={"username": "admin@coalmine.gov.in", "password": "admin123"})
            token = r.json()["access_token"]
        except Exception as e:
            print("Failed to login:", e)
            return

        headers = {"Authorization": f"Bearer {token}"}
        
        test_cases = [
            ("What is the capital of France?", "OUT-OF-DOMAIN"),
            ("Who is the Prime Minister of India?", "OUT-OF-DOMAIN"),
            ("Tell me a joke.", "OUT-OF-DOMAIN"),
            ("Explain quantum mechanics.", "OUT-OF-DOMAIN"),
            ("Write a Python game.", "OUT-OF-DOMAIN"),
            ("Who won yesterday's cricket match?", "OUT-OF-DOMAIN"),
            ("What does Regulation 106 require?", "IN-DOMAIN"),
            ("How do I report a near miss?", "IN-DOMAIN")
        ]
        
        for msg, expected in test_cases:
            print(f"\n[Q] {msg}")
            try:
                # The frontend sends a JSON with {"message": msg} to /copilot/chat
                r2 = await client.post(f"{base_url}/copilot/chat", json={"message": msg, "history": []}, headers=headers, timeout=10)
                ans = r2.json().get("answer", str(r2.text))
                print(f"[A] {ans[:200]}")
            except Exception as e:
                print(f"[E] Error connecting or timing out: {e}")

asyncio.run(main())

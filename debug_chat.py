# debug_chat.py
# Run this to debug chat issues
# python debug_chat.py

import requests
import json

print("=" * 50)
print("AURA-X Chat Debug Tool")
print("=" * 50)

# Step 1: Check Flask
print("\n1. Checking Flask server...")
try:
    r = requests.get("http://localhost:5000/api/health", timeout=5)
    print(f"   ✅ Flask running - Status: {r.status_code}")
    data = r.json()
    print(f"   App: {data.get('app')}")
except Exception as e:
    print(f"   ❌ Flask NOT running: {e}")
    print("   → Run: python app.py")
    exit()

# Step 2: Check LM Studio
print("\n2. Checking LM Studio...")
try:
    r = requests.get("http://localhost:1234/v1/models", timeout=5)
    if r.status_code == 200:
        models = r.json().get("data", [])
        print(f"   ✅ LM Studio running")
        if models:
            for m in models:
                print(f"   📦 Model: {m.get('id')}")
        else:
            print("   ⚠️ No model loaded in LM Studio!")
    else:
        print(f"   ❌ LM Studio error: {r.status_code}")
except Exception as e:
    print(f"   ❌ LM Studio NOT running: {e}")
    print("   → Open LM Studio and start the server")
    exit()

# Step 3: Test chat API
print("\n3. Testing chat API...")
try:
    payload = {
        "message": "Say hello in one short sentence",
        "session_id": "debug_test"
    }
    r = requests.post(
        "http://localhost:5000/api/chat",
        json=payload,
        timeout=60
    )
    data = r.json()
    print(f"   Status: {r.status_code}")
    print(f"   Response status: {data.get('status')}")

    if data.get("status") == "success":
        response = data.get("data", {}).get("response", "")
        print(f"   ✅ Chat working!")
        print(f"   AURA says: {response[:100]}")
    else:
        print(f"   ❌ Chat failed: {data.get('message')}")

except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 4: Check .env
print("\n4. Checking configuration...")
try:
    import os
    from dotenv import load_dotenv
    load_dotenv()

    url = os.getenv("LM_STUDIO_BASE_URL", "NOT SET")
    model = os.getenv("LM_STUDIO_MODEL", "NOT SET")
    print(f"   LM Studio URL: {url}")
    print(f"   Model name: {model}")

    if model == "NOT SET" or model == "your-model-name-here":
        print("   ⚠️ Model name not set in .env file!")
        print("   → Update LM_STUDIO_MODEL in .env")
    else:
        print("   ✅ Config looks good")
except Exception as e:
    print(f"   ❌ Config error: {e}")

print("\n" + "=" * 50)
print("Debug complete!")
print("=" * 50)
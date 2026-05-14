import requests, json, datetime, os, sys
from pathlib import Path

KEY      = "b6a1de31-dc9a-47cf-850d-fd602d9209ec"
OUT      = Path("output")
OUT.mkdir(exist_ok=True)

print("=== LAUNCHWISE PIPELINE START ===")
print("Time:", datetime.datetime.now().isoformat())

# STEP 1 — GET TOKEN
print("\n--- Step 1: Getting token ---")
try:
    r = requests.get(
        "https://eservice.ura.gov.sg/uraDataService/insertNewToken/v1",
        headers={"AccessKey: "b6a1de31-dc9a-47cf-850d-fd602d9209ec"},
        timeout=30
    )
    print("Status:", r.status_code)
    print("Body:", r.text[:500])
except Exception as e:
    print("ERROR:", e)
    sys.exit(1)

# STEP 2 — PARSE TOKEN
try:
    token = r.json()["Result"]
    print("Token:", token[:15], "...")
except Exception as e:
    print("Could not parse token:", e)
    print("Full response:", r.text)
    sys.exit(1)

# STEP 3 — FETCH DATA
print("\n--- Step 2: Fetching projects ---")
try:
    r2 = requests.get(
        "https://www.ura.gov.sg/uraDataService/invokeUraDS?service=PMI_Resi_Developer_Sales",
        headers={"AccessKey": KEY, "Token": token},
        timeout=30
    )
    print("Status:", r2.status_code)
    print("Body preview:", r2.text[:300])
except Exception as e:
    print("ERROR:", e)
    sys.exit(1)

# STEP 4 — SAVE
try:
    data = r2.json()
    print("URA Status:", data.get("Status"))
    projects = data.get("Result", [])
    print("Total projects:", len(projects))
    with open(OUT/"projects.json","w") as f:
        json.dump({"total": len(projects), "projects": projects}, f, indent=2)
    print("SAVED: output/projects.json")
except Exception as e:
    print("Parse/save error:", e)
    print("Raw:", r2.text[:500])

print("=== DONE ===")

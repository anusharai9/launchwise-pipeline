import requests
import json
import datetime
import sys
from pathlib import Path

ACCESS_KEY = "b6a1de31-dc9a-47cf-850d-fd602d9209ec"
OUT = Path("output")
OUT.mkdir(exist_ok=True)
REGION = {}
for i in [1,2,3,4,5,6,7,8,9,10,11]:
    REGION[str(i)] = "CCR"
for i in [12,13,14,15,20,21]:
    REGION[str(i)] = "RCR"
for i in [16,17,18,19,22,23,24,25,26,27,28]:
    REGION[str(i)] = "OCR"

print("=== PIPELINE START ===")
print("Getting token...")
resp = requests.get(
    "https://eservice.ura.gov.sg/uraDataService/insertNewToken/v1",
    headers={"AccessKey": ACCESS_KEY},
    timeout=30
)
print("Status:", resp.status_code)
print("Body:", resp.text[:300])
if resp.status_code == 200:
    token = resp.json()["Result"]
    print("Token OK:", token[:15])
    resp2 = requests.get(
        "https://eservice.ura.gov.sg/uraDataService/invokeUraDS?service=PMI_Resi_Developer_Sales",
        headers={"AccessKey": ACCESS_KEY, "Token": token},
        timeout=30
    )
    print("Data status:", resp2.status_code)
    print("Data preview:", resp2.text[:300])
    data = resp2.json()
    projects = data.get("Result", [])
    print("Projects:", len(projects))
    with open(OUT / "projects.json", "w") as f:
        json.dump({"total": len(projects), "projects": projects}, f, indent=2)
    print("SAVED")
else:
    print("Token failed")
    sys.exit(1)

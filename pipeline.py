import requests, json, datetime, os
from pathlib import Path

KEY = os.environ.get("URA_ACCESS_KEY", "b6a1de31-dc9a-47cf-850d-fd602d9209ec")
TOKEN_URL = "https://eservice.ura.gov.sg/uraDataService/insertNewToken/v1"
URA_BASE  = "https://eservice.ura.gov.sg/uraDataService/invokeUraDS"
HEADERS   = {"AccessKey": KEY}

REGION = {
    **{str(i): "CCR" for i in [1,2,3,4,5,6,7,8,9,10,11]},
    **{str(i): "RCR" for i in [12,13,14,15,20,21]},
    **{str(i): "OCR" for i in [16,17,18,19,22,23,24,25,26,27,28]},
}

def get_token():
    r = requests.get(
        TOKEN_URL,
        headers={"AccessKey": KEY},
        timeout=20
    )
    print("Token status:", r.status_code)
    print("Token raw:", r.text[:300])
    if r.status_code != 200:
        raise Exception(f"Token endpoint returned {r.status_code}")
    d = r.json()
    assert d["Status"] == "Success", f"Token failed: {d}"
    print("Token OK:", d["Result"][:12], "...")
    return d["Result"]

def fetch_projects(token):
    h = {**HEADERS, "Token": token}
    r = requests.get(f"{URA_BASE}?service=PMI_Resi_Developer_Sales", headers=h, timeout=30)
    print("Sales status:", r.status_code)
    d = r.json()
    assert d["Status"] == "Success", f"Sales failed: {d.get('Message')}"
    raw = d.get("Result", [])
    print(f"Raw projects from URA: {len(raw)}")
    rows = []
    for p in raw:
        sales = p.get("developerSales", [])
        if not sales:
            continue
        latest = sorted(sales, key=lambda x: x.get("refPeriod","0000"), reverse=True)[0]
        total  = int(latest.get("launchedToDate") or 0)
        if total < 30:
            continue
        sold   = int(latest.get("soldToDate") or 0)
        avail  = int(latest.get("unitsAvail") or 0)
        med    = float(latest.get("medianPrice") or 0)
        high   = float(latest.get("highestPrice") or 0)
        low    = float(latest.get("lowestPrice") or 0)
        dist   = str(p.get("district","")).strip()
        pct    = round(sold / total * 100, 1) if total else 0
        status = ("Fully Sold" if avail == 0 and sold > 0
                  else "Almost Sold" if pct >= 80
                  else "Available")
        rows.append({
            "project_name":    p.get("project","").strip().upper(),
            "developer":       p.get("developer","").strip(),
            "street":          p.get("street","").strip(),
            "district":        dist,
            "region":          REGION.get(dist, "OCR"),
            "total_units":     total,
            "units_sold":      sold,
            "units_available": avail,
            "pct_sold":        pct,
            "median_psf":      med,
            "highest_psf":     high,
            "lowest_psf":      low,
            "launch_status":   status,
            "last_updated":    datetime.date.today().isoformat(),
            "source":          "URA PMI Developer Sales",
        })
    return rows

def run():
    print("=== LAUNCHWISE PIPELINE START ===")
    print("Time:", datetime.datetime.now().isoformat())
    token = get_token()
    rows  = fetch_projects(token)
    print(f"Qualifying projects (30+ units): {len(rows)}")
    out = {
        "generated": datetime.datetime.now().isoformat(),
        "total":     len(rows),
        "projects":  rows,
    }
    Path("output").mkdir(exist_ok=True)
    with open("output/projects.json", "w") as f:
        json.dump(out, f, indent=2)
    import csv
    with open("output/projects.csv", "w", newline="", encoding="utf-8-sig") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
    print(f"Available:   {sum(1 for r in rows if r['launch_status']=='Available')}")
    print(f"Almost sold: {sum(1 for r in rows if r['launch_status']=='Almost Sold')}")
    print(f"Fully sold:  {sum(1 for r in rows if r['launch_status']=='Fully Sold')}")
    print("Output saved: output/projects.json + output/projects.csv")
    print("=== PIPELINE COMPLETE ===")

if __name__ == "__main__":
    run()
  

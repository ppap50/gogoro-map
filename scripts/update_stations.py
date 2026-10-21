"""Download the Gogoro station list and save a compact copy as stations.json."""
import json
import urllib.request

URLS = ["https://webapi.gogoro.com/api/vm/list", "https://wapi.gogoro.com/tw/api/vm/list"]


def pick(value):
    """Multilingual fields are JSON strings like {"List":[{"Value":..,"Lang":"zh-TW"}]}."""
    if not isinstance(value, str) or not value.strip().startswith("{"):
        return value or ""
    items = json.loads(value).get("List", [])
    zh = [i for i in items if "zh" in i.get("Lang", "")]
    return (zh or items or [{}])[0].get("Value", "")


def fetch():
    for url in URLS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                try:
                    return json.loads(raw)["data"]
                except Exception:
                    print(f"::warning::{url} unexpected body: {raw[:300]!r}")
                    raise
        except Exception as e:
            body = getattr(e, "read", lambda: b"")()[:200]
            print(f"::warning::{url} failed: {e!r} {body!r}")
    raise SystemExit("all sources failed")


stations = []
for d in fetch():
    if not d.get("Latitude") or not d.get("Longitude"):
        continue
    stations.append({
        "id": d.get("Id"),
        "name": pick(d.get("LocName")),
        "address": pick(d.get("Address")),
        "City": pick(d.get("City")),
        "District": pick(d.get("District")),
        "lat": round(float(d["Latitude"]), 6),
        "lng": round(float(d["Longitude"]), 6),
        "availableTime": pick(d.get("AvailableTime")),
    })

if len(stations) < 100:
    raise SystemExit(f"only {len(stations)} stations, not saving")
with open("stations.json", "w", encoding="utf-8") as f:
    json.dump({"data": stations}, f, ensure_ascii=False, separators=(",", ":"))
print(f"saved {len(stations)} stations")

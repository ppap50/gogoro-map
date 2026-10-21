"""Download the Gogoro station list and save a compact copy as stations.json."""
import json
import urllib.request

URL = "https://official-site-pro.gogoroapp.com/PartnerService/Gogoro/GetVmList?offset=0&pageSize=10000"


def pick(value):
    """Names and addresses come as {"zh-TW": ..., "en-US": ...}."""
    if isinstance(value, dict):
        return value.get("zh-TW") or next(iter(value.values()), "")
    return value or ""


def hours(byte_str):
    if not byte_str:
        return ""
    return "24 小時營業" if set(byte_str.upper()) == {"F"} else "非 24 小時,請注意營業時間"


req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0", "Origin": "https://www.gogoro.com"})
with urllib.request.urlopen(req, timeout=120) as r:
    data = json.load(r)["Data"]

stations = []
for d in data:
    if not d.get("Latitude") or not d.get("Longitude") or d.get("State") not in (1, None):
        continue
    stations.append({
        "id": d.get("Id"),
        "name": pick(d.get("LocName")),
        "address": pick(d.get("Address")),
        "lat": round(float(d["Latitude"]), 6),
        "lng": round(float(d["Longitude"]), 6),
        "availableTime": hours(d.get("AvailableTimeByte")),
    })

if len(stations) < 1000:
    raise SystemExit(f"only {len(stations)} stations, not saving")
with open("stations.json", "w", encoding="utf-8") as f:
    json.dump({"data": stations}, f, ensure_ascii=False, separators=(",", ":"))
print(f"saved {len(stations)} stations")

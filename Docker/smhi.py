#!/usr/bin/env python3
"""
SMHI snow1g prognos → InfluxDB line protocol
===========================================

- En rad per parameter och tidssteg
- parameter=... (human-readable namn) som tag
- unit=... som separat tag
- value=... som fält

Körning:
    python3 smhi_snow1g_to_influx.py --lon 16 --lat 58
"""

import requests
import argparse
import sys
from datetime import datetime
import re

test = False
URL = "http://192.168.0.73:8086"

def write_influxdb(out):
    """
    Skriver data till InfluxDB eller skriver ut den om test_is_set är True.
    Använder den globala variabeln test_is_set.
    """
    if test:
        print(f"{out}")
    else:
        # Korrekt sätt att göra ett POST-anrop till InfluxDB
        # Vi använder f-strängar för att inkludera URL-parametrar i anropet
        try:
            r = requests.post(f"{URL}/write?db=smhi", data=out, timeout=10)
            r.raise_for_status() # Kasta ett fel för dåliga statuskoder (4xx eller 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Error posting to InfluxDB: {e}", file=sys.stderr)


def sanitize_tag(value: str) -> str:
    """Gör strängar säkra för InfluxDB tags"""
    if not value:
        return "unknown"
    v = str(value).strip()
    v = v.replace(" ", "_").replace(",", "_").replace("=", "_").replace("/", "_").replace("%", "p")
    v = re.sub(r'[^a-zA-Z0-9_.-]', '_', v)
    v = re.sub(r'__+', '_', v).strip('_')
    return v


def load_parameters():
    """Hämtar parameter.json och mappar på 'name' (det som faktiskt används i data.json)"""
    url = "https://opendata-download-metfcst.smhi.se/api/category/snow1g/version/1/parameter.json"
    try:
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        data = r.json()

        mapping = {}
        for p in data.get("parameter", []):
            name = p.get("name")
            if not name:
                continue
            mapping[name] = {
                "name": name,
                "unit": p.get("unit", ""),
                "shortName": p.get("shortName", "")
            }
        print(f"✅ Hämtade {len(mapping)} parametrar med enheter från SMHI", file=sys.stderr)
        return mapping

    except Exception as e:
        print(f"⚠️  Kunde inte hämta parameter.json: {e}", file=sys.stderr)
        return {}


def main():
    parser = argparse.ArgumentParser(description="SMHI snow1g → InfluxDB line protocol")
    parser.add_argument("--lon", type=float, required=True, help="Longitud (t.ex. 16.0)")
    parser.add_argument("--lat", type=float, required=True, help="Latitud (t.ex. 58.0)")
    parser.add_argument("--measurement", default="smhi", help="Measurement-namn (default: smhi)")
    parser.add_argument("--skip-missing", action="store_true", default=True, help="Skippa 9999-värden")
    parser.add_argument("--test", action="store_true", default=False, help="Pring till stdout for debug")
    args = parser.parse_args()

    global test
    test = args.test

    param_mapping = load_parameters()

    # Hämta prognosdata
    data_url = (
        f"https://opendata-download-metfcst.smhi.se/api/category/snow1g"
        f"/version/1/geotype/point/lon/{args.lon}/lat/{args.lat}/data.json"
    )

    try:
        r = requests.get(data_url, timeout=15)
        r.raise_for_status()
        forecast = r.json()
    except requests.RequestException as e:
        print(f"❌ Fel vid hämtning av data: {e}", file=sys.stderr)
        sys.exit(1)

    measurement = args.measurement

    for ts in forecast.get("timeSeries", []):
        time_str = ts.get("time")
        if not time_str:
            continue

        try:
            dt_str = time_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(dt_str)
            timestamp_ns = int(dt.timestamp() * 1000000000)
        except Exception:
            continue

        line = ""

        for param_name, value in ts.get("data", {}).items():
            if value is None or (args.skip_missing and value == 9999):
                continue

            # Hämta info från parameter.json (nu matchar det perfekt)
            info = param_mapping.get(param_name, {})
            unit = info.get("unit", "")

            # Bygg tags
            tags = [
                #f"lon={args.lon}",
                #f"lat={args.lat}",
                #f"parameter={sanitize_tag(param_name)}"
                f"{sanitize_tag(param_name)}"
            ]
            if unit:
                #tags.append(f"unit={sanitize_tag(unit)}")
                u = f"unit={sanitize_tag(unit)}"
                if u:
                    tags.append(u)

            tag_string = ",".join(tags)

            # Formatera värde
            if isinstance(value, bool):
                val_str = str(value).lower()
            elif isinstance(value, int):
                val_str = f"{value}i"
            elif isinstance(value, float):
                val_str = str(value)
            else:
                val_str = f'"{value}"'

            line += f"{tag_string} value={val_str} {timestamp_ns}\n"

        write_influxdb(line)


if __name__ == "__main__":
    test = False
    main()


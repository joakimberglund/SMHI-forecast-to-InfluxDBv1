import sys
import requests
import time
from calendar import timegm # Behövs för att konvertera tiden korrekt

# --- Konfiguration ---
# **Byt ut denna URL mot din InfluxDB-adress**
URL = "http://influxdb:8086"
# ---------------------

# Initiera variabeln i det globala scopet
test_is_set = False

if len(sys.argv) < 3:
    print("Usage: python coords.py <lat> <long> [test]", file=sys.stderr)
    sys.exit(1)

# Parse latitude and longitude (first two args)
try:
    # OBS: ordningen i SMHI-URL:en är: .../lon/{long}/{lat}/data.json
    # Så vi parsade inmatningsargumenten i ordningen <lat> <long>
    lat = float(sys.argv[1])
    long = float(sys.argv[2])
except ValueError:
    print("Error: lat and long must be valid numbers.", file=sys.stderr)
    sys.exit(1)

# Check if in test mode or not
# Enklare sätt att kontrollera det tredje argumentet
if len(sys.argv) > 3 and sys.argv[3] == 'test':
    test_is_set = True

def write_influxdb(out):
    """
    Skriver data till InfluxDB eller skriver ut den om test_is_set är True.
    Använder den globala variabeln test_is_set.
    """
    if test_is_set:
        print(f"{out}")
    else:
        # Korrekt sätt att göra ett POST-anrop till InfluxDB
        # Vi använder f-strängar för att inkludera URL-parametrar i anropet
        try:
            r = requests.post(f"{URL}/write?db=smhi", data=out, timeout=10)
            r.raise_for_status() # Kasta ett fel för dåliga statuskoder (4xx eller 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Error posting to InfluxDB: {e}", file=sys.stderr)


# Fetch forecast from SMHI
# Använd f-strängar för att korrekt bygga URL:en
smhi_url = f"http://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{long}/lat/{lat}/data.json"

try:
    r = requests.get(smhi_url, timeout=10)
    r.raise_for_status() # Kontrollera att anropet lyckades
    data = r.json()
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from SMHI: {e}", file=sys.stderr)
    sys.exit(1)

# Loopa igenom tidsserierna och skicka data
for nr in data["timeSeries"]:
    ltime = nr["validTime"]

    # Konvertera SMHI:s tid (UTC) till Unix epoch-tid i sekunder
    utc_time = time.strptime(ltime, "%Y-%m-%dT%H:%M:%SZ")
    epoch_time_s = timegm(utc_time)

    # InfluxDB kräver nanosekunder. Vi konverterar från sekunder genom att lägga till nollor.
    # epoch_time + '000000000' skapar en sträng som representerar nanosekunder.
    epoch_time_ns = str(epoch_time_s) + "000000000"

    for param in nr["parameters"]:
        # Skapa InfluxDB line protocol-strängen
        # Format: <measurement>,<tag_key>=<tag_value> field=<value> <timestamp>
        line_protocol = f"{param['name']},unit={param['unit']} value={param['values'][0]} {epoch_time_ns}"

        write_influxdb(line_protocol)



import os
import requests
from datetime import datetime, timezone

OWM_KEY   = os.environ["OWM_API_KEY"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

# Koordinaten statt Stadtname (genauer)
LAT, LON = 46.948, 7.4474  # Bern

def hole_wetterdaten():
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": LAT, "lon": LON,
        "appid": OWM_KEY,
        "units": "metric",
        "lang": "de",
        "exclude": "minutely,current,alerts",  # nur daily + hourly
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def erstelle_nachricht(daten):
    heute = daten["daily"][0]
    stunden = daten["hourly"][:24]  # nächste 24h

    temp_min = heute["temp"]["min"]
    temp_max = heute["temp"]["max"]
    beschreibung = heute["weather"][0]["description"].capitalize()
    regen_chance = int(heute.get("pop", 0) * 100)

    # Stunden mit Regen > 30% Wahrscheinlichkeit
    regen_zeiten = []
    for h in stunden:
        if h.get("pop", 0) >= 0.3:
            uhrzeit = datetime.fromtimestamp(h["dt"], tz=timezone.utc).strftime("%H:%M")
            regen_zeiten.append(uhrzeit)

    msg = f"🌤 *Wetter heute in Bern*\n"
    msg += f"🌡 {temp_min:.0f}°C – {temp_max:.0f}°C\n"
    msg += f"🌧 Regenwahrscheinlichkeit: {regen_chance}%\n"

    if regen_zeiten:
        msg += f"⏰ Regen möglich um: {', '.join(regen_zeiten[:4])} Uhr\n"
    else:
        msg += "☀️ Kein nennenswerter Regen erwartet\n"

    msg += f"📋 {beschreibung}"
    return msg

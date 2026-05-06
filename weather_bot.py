import os
import requests
from datetime import datetime, timezone, timedelta

OWM_KEY   = os.environ["OWM_API_KEY"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

LAT, LON = 46.948, 7.4474  # Bern
SCHWEIZ_OFFSET = timedelta(hours=2)  # MESZ (Sommer), im Winter timedelta(hours=1)

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni",
          "Juli", "August", "September", "Oktober", "November", "Dezember"]

def hole_wetterdaten():
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": LAT, "lon": LON,
        "appid": OWM_KEY,
        "units": "metric",
        "lang": "de",
        "exclude": "minutely,current,alerts",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def unix_zu_lokalzeit(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc) + SCHWEIZ_OFFSET

def hole_weather_overview():
    url = "https://api.openweathermap.org/data/3.0/onecall/overview"
    params = {
        "lat": LAT, "lon": LON,
        "appid": OWM_KEY,
        "units": "metric",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()["weather_overview"]


def erstelle_nachricht(daten):
    heute = daten["daily"][0]
    stunden = daten["hourly"][:24]

    # Datum
    jetzt = unix_zu_lokalzeit(heute["dt"])
    wochentag = WOCHENTAGE[jetzt.weekday()]
    datum_str = f"{wochentag}, {jetzt.day}. {MONATE[jetzt.month - 1]}"

    # Temperaturen
    temp_min = heute["temp"]["min"]
    temp_max = heute["temp"]["max"]
    beschreibung = heute["weather"][0]["description"].capitalize()
    regen_chance = int(heute.get("pop", 0) * 100)

    # Regen in mm
    regen_mm = heute.get("rain", 0)

    # Sonnenauf- und -untergang
    aufgang  = unix_zu_lokalzeit(heute["sunrise"]).strftime("%H:%M")
    untergang = unix_zu_lokalzeit(heute["sunset"]).strftime("%H:%M")

    # Stunden mit Regen > 30%
    regen_zeiten = []
    for h in stunden:
        if h.get("pop", 0) >= 0.3:
            uhrzeit = unix_zu_lokalzeit(h["dt"]).strftime("%H:%M")
            regen_zeiten.append(uhrzeit)

    msg = f"🌤 *Wetter {datum_str} in Bern*\n"
    msg += f"🌡 {temp_min:.0f}°C – {temp_max:.0f}°C\n"
    msg += f"🌧 Regenwahrscheinlichkeit: {regen_chance}%\n"

    if regen_mm > 0:
        msg += f"💧 Erwartete Regenmenge: {regen_mm:.1f} mm\n"
    else:
        msg += f"💧 Keine Regenmenge erwartet\n"

    if regen_zeiten:
        msg += f"⏰ Regen möglich um: {', '.join(regen_zeiten[:4])} Uhr\n"
    else:
        msg += "☀️ Kein nennenswerter Regen erwartet\n"

    msg += f"🌅 Sonnenaufgang: {aufgang} Uhr\n"
    msg += f"🌇 Sonnenuntergang: {untergang} Uhr\n"
    msg += f"📋 {beschreibung}"
    msg += f"\n💬 _{overview}_"
    return msg

def sende_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()

if __name__ == "__main__":
    daten = hole_wetterdaten()
    overview = hole_weather_overview()
    nachricht = erstelle_nachricht(daten)
    sende_telegram(nachricht)
    print("Nachricht gesendet:", nachricht)

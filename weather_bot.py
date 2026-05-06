import os
import requests
from datetime import datetime, timezone, timedelta

OWM_KEY   = os.environ["OWM_API_KEY"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

LAT, LON = 46.948, 7.4474  # Bern, Switzerland
SWISS_OFFSET = timedelta(hours=2)  # CEST (summer), use hours=1 for CET (winter)

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

def fetch_weather():
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": LAT, "lon": LON,
        "appid": OWM_KEY,
        "units": "metric",
        "lang": "en",
        "exclude": "minutely,current,alerts",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def unix_to_local(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc) + SWISS_OFFSET

def build_message(data):
    today = data["daily"][0]
    hours = data["hourly"][:24]

    # Date
    now = unix_to_local(today["dt"])
    weekday = WEEKDAYS[now.weekday()]
    date_str = f"{weekday}, {MONTHS[now.month - 1]} {now.day}"

    # Temperature
    temp_min = today["temp"]["min"]
    temp_max = today["temp"]["max"]
    description = today["weather"][0]["description"].capitalize()
    rain_chance = int(today.get("pop", 0) * 100)

    # Rain in mm
    rain_mm = today.get("rain", 0)

    # Sunrise / sunset
    sunrise = unix_to_local(today["sunrise"]).strftime("%H:%M")
    sunset  = unix_to_local(today["sunset"]).strftime("%H:%M")

    # Hours with rain probability > 30%
    rain_times = []
    for h in hours:
        if h.get("pop", 0) >= 0.3:
            time = unix_to_local(h["dt"]).strftime("%H:%M")
            rain_times.append(time)

    msg = f"🌤 *Weather {date_str} — Bern*\n"
    msg += f"🌡 {temp_min:.0f}°C – {temp_max:.0f}°C\n"
    msg += f"🌧 Rain probability: {rain_chance}%\n"

    if rain_mm > 0:
        msg += f"💧 Expected rainfall: {rain_mm:.1f} mm\n"
    else:
        msg += f"💧 No rainfall expected\n"

    if rain_times:
        msg += f"⏰ Rain possible at: {', '.join(rain_times[:4])}\n"
    else:
        msg += "☀️ No significant rain expected\n"

    msg += f"🌅 Sunrise: {sunrise}\n"
    msg += f"🌇 Sunset: {sunset}\n"
    msg += f"📋 {description}"
    return msg

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()

if __name__ == "__main__":
    data = fetch_weather()
    message = build_message(data)
    send_telegram(message)
    print("Message sent:", message)

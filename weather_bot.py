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

def group_rain_times(hours):
    """Groups consecutive rainy hours into ranges, single hours stay as-is."""
    rainy = [h for h in hours if h.get("pop", 0) >= 0.3]
    if not rainy:
        return []

    groups = []
    current_group = [rainy[0]]

    for h in rainy[1:]:
        prev_dt = unix_to_local(current_group[-1]["dt"])
        curr_dt = unix_to_local(h["dt"])
        # Hours are consecutive if exactly 1 hour apart
        if (curr_dt - prev_dt) == timedelta(hours=1):
            current_group.append(h)
        else:
            groups.append(current_group)
            current_group = [h]
    groups.append(current_group)

    result = []
    for group in groups:
        start = unix_to_local(group[0]["dt"]).strftime("%H:%M")
        if len(group) == 1:
            result.append(start)
        else:
            end = unix_to_local(group[-1]["dt"]).strftime("%H:%M")
            result.append(f"{start} – {end}")

    return result

def build_message(data):
    today = data["daily"][0]

    # Only hours belonging to today (local date)
    today_date = (datetime.now(timezone.utc) + SWISS_OFFSET).date()
    hours = [h for h in data["hourly"] if unix_to_local(h["dt"]).date() == today_date]

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

    # Grouped rain times
    rain_groups = group_rain_times(hours)

    msg = f"🌤 *Weather {date_str} — Bern*\n"
    msg += f"🌡 {temp_min:.0f}°C – {temp_max:.0f}°C\n"
    msg += f"🌧 Rain probability: {rain_chance}%\n"

    if rain_mm > 0:
        msg += f"💧 Expected rainfall: {rain_mm:.1f} mm\n"
    else:
        msg += f"💧 No rainfall expected\n"

    if rain_groups:
        msg += f"⏰ Rain possible at: {', '.join(rain_groups)}\n"
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

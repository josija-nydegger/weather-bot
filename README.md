# 🌤 Wetter-Bot

Ein automatischer Telegram-Bot der täglich um 05:30 Uhr (Schweizer Sommerzeit) eine Wettervorhersage für Bern sendet.

## Features

- Tagestemperatur (Min/Max)
- Regenwahrscheinlichkeit und erwartete Regenmenge
- Uhrzeiten mit Regen (>30% Wahrscheinlichkeit)
- Sonnenauf- und -untergang
- Automatischer Versand via Telegram

## Technologien

- **Python 3.12**
- **OpenWeatherMap One Call API 3.0** — Wetterdaten
- **Telegram Bot API** — Nachrichtenversand
- **GitHub Actions** — tägliche Ausführung per Cron

## Einrichtung

### 1. Voraussetzungen

- OpenWeatherMap-Konto mit One Call API 3.0 Abonnement
- Telegram Bot (via [@BotFather](https://t.me/BotFather) erstellen)

### 2. GitHub Secrets setzen

Im Repository unter **Settings → Secrets and variables → Actions** drei Secrets anlegen:

| Secret | Beschreibung |
|---|---|
| `OWM_API_KEY` | OpenWeatherMap API-Key |
| `TELEGRAM_BOT_TOKEN` | Token von BotFather |
| `CHAT_ID` | Deine Telegram Chat-ID |

### 3. Standort anpassen

In `weather_bot.py` die Koordinaten auf deinen Standort setzen:

```python
LAT, LON = 46.948, 7.4474  # Bern
```

## Ausführung

Der Bot läuft automatisch täglich um 03:30 UTC (05:30 MESZ). Manuell starten:

**GitHub → Actions → Wetter-Bot → Run workflow**

## Beispiel-Nachricht

```
🌤 Wetter Dienstag, 6. Mai in Bern
🌡 11°C – 18°C
🌧 Regenwahrscheinlichkeit: 40%
💧 Erwartete Regenmenge: 2.3 mm
⏰ Regen möglich um: 14:00, 17:00 Uhr
🌅 Sonnenaufgang: 06:12 Uhr
🌇 Sonnenuntergang: 20:48 Uhr
📋 Leicht bewölkt
```

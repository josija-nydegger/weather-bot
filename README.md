# 🌤 Weather Bot

An automated Telegram bot that sends a daily weather forecast for Bern, Switzerland every morning at 05:30 (Central European Summer Time).

## Features

- Daily temperature (min/max)
- Rain probability and expected rainfall in mm
- Hours with rain likely (>30% probability)
- Sunrise and sunset times
- Fully automated via GitHub Actions

## Tech Stack

- **Python 3.12**
- **OpenWeatherMap One Call API 3.0** — weather data
- **Telegram Bot API** — message delivery
- **GitHub Actions** — daily cron execution

## Cost

This bot uses the [OpenWeatherMap One Call API 3.0](https://openweathermap.org/api/one-call-3) which includes **1,000 free API calls per day**. This bot makes 1 call per day, so it runs completely free of charge.

Note: A credit card is required to subscribe to One Call API 3.0, but you will not be charged as long as you stay within the free tier. It is recommended to set your daily call limit to 1,000 in your OpenWeatherMap account to avoid any accidental charges.

## Setup

### 1. Prerequisites

- OpenWeatherMap account with an active [One Call API 3.0](https://openweathermap.org/api/one-call-3) subscription
- Telegram Bot created via [@BotFather](https://t.me/BotFather)
- Your Telegram Chat ID (send `/start` to your bot, then call `https://api.telegram.org/bot<TOKEN>/getUpdates`)

### 2. Fork or clone this repository

```bash
git clone https://github.com/josija-nydegger/weather-bot.git
```

### 3. Set GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|---|---|
| `OWM_API_KEY` | Your OpenWeatherMap API key |
| `TELEGRAM_BOT_TOKEN` | Token from BotFather |
| `CHAT_ID` | Your Telegram chat ID |

### 4. Adjust location

In `weather_bot.py`, set your coordinates:

```python
LAT, LON = 46.948, 7.4474  # Bern, Switzerland
```

### 5. Adjust timezone

The default offset is CEST (UTC+2). In winter, change to CET (UTC+1):

```python
SWISS_OFFSET = timedelta(hours=1)  # CET (winter)
```

And update the cron schedule in `.github/workflows/weather.yml` accordingly:

```yaml
cron: "30 4 * * *"   # 05:30 CET (UTC+1)
```

## Running manually

Go to **Actions → Weather Bot → Run workflow** to trigger the bot instantly without waiting for the scheduled run.

## Example message
```
🌤 Weather Tuesday, May 6 — Bern
🌡 11°C – 18°C
🌧 Rain probability: 40%
💧 Expected rainfall: 2.3 mm
⏰ Rain possible at: 14:00, 17:00
🌅 Sunrise: 06:12
🌇 Sunset: 20:48
📋 Partly cloudy
```

## License

MIT

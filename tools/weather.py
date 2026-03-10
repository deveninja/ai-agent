"""
weather.py

Fetches a multi-day weather forecast for a geographic location using
the Open-Meteo free forecast API (no API key required).
"""

import requests

def get_weather(latitude, longitude):
  """
  Retrieve a 5-day weather forecast for the given coordinates.

  Calls the Open-Meteo /v1/forecast endpoint and returns daily
  maximum/minimum temperatures (°C) and precipitation probability
  for the next 5 days.

  Args:
    latitude  (float): Geographic latitude of the target location.
    longitude (float): Geographic longitude of the target location.

  Returns:
    list[dict]: A list of up to 5 daily forecast dictionaries, each
    containing:
      - "date"        (str):   ISO date string (YYYY-MM-DD).
      - "temp_max"    (float): Maximum temperature in °C.
      - "temp_min"    (float): Minimum temperature in °C.
      - "rain_chance" (int):   Precipitation probability (0–100 %).
  """
  url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}"
    f"&longitude={longitude}"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
    "&timezone=auto"
  )

  r = requests.get(url)
  data = r.json()

  forecast = []

  for i in range(len(data["daily"]["time"])):

    forecast.append({
      "date": data["daily"]["time"][i],
      "temp_max": data["daily"]["temperature_2m_max"][i],
      "temp_min": data["daily"]["temperature_2m_min"][i],
      "rain_chance": data["daily"]["precipitation_probability_max"][i]
    })

  return forecast[:5]  # 5 day forecast
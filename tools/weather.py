import requests

def get_weather(latitude, longitude):
  # """
  # Demo weather tool.
  # In production this would call a real API.
  # """

  # return {
  #   "city": city,
  #   "temperature": "30°C",
  #   "condition": "Sunny"
  # }

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
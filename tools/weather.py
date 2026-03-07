def get_weather(city: str):
  """
  Demo weather tool.
  In production this would call a real API.
  """

  return {
    "city": city,
    "temperature": "30°C",
    "condition": "Sunny"
  }
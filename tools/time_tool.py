from datetime import datetime

def get_time(city: str):
  """
  Returns the current time.
  """

  return {
    "city": city,
    "time": datetime.now().strftime("%H:%M:%S")
  }
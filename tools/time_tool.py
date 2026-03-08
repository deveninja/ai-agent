import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_time(timezone: str):
  # """
  # Returns the current time.
  # """

  # return {
  #   "city": city,
  #   "time": datetime.now().strftime("%H:%M:%S")
  # }

  print(f"Getting time for timezone: {timezone}")
  r = requests.get(
    "http://api.timezonedb.com/v2.1/get-time-zone",
    params={
      "key": os.getenv("TIMEZONEDB_API_KEY"),
      "format": "json",
      "by": "zone",
      "zone": timezone
    }
  ).json()

  return {
      "time": r["formatted"],
      "timezone": r["zoneName"]
  }
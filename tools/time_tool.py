"""
time_tool.py

Retrieves the current local time for a given IANA timezone string
by calling the TimeZoneDB REST API.
"""

import requests
import os

def get_time(timezone: str):
  """
  Fetch the current time for an IANA timezone via the TimeZoneDB API.

  Args:
    timezone (str): A valid IANA timezone identifier
                    (e.g. "Asia/Manila", "America/New_York").

  Returns:
    dict: A dictionary with the following keys:
      - "time"     (str): Formatted datetime string returned by the API.
      - "timezone" (str): The confirmed IANA timezone name.
  """
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
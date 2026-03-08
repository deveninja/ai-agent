import requests
import os

def geocode_location(location):

  geo = requests.get(
    "https://geocoding-api.open-meteo.com/v1/search",
    params={
      "name": location,
      "count": 1
    }
  ).json()

  place = geo["results"][0]

  lat = place["latitude"]
  lon = place["longitude"]

  tz = requests.get(
    "http://api.timezonedb.com/v2.1/get-time-zone",
    params={
      "key": os.getenv("TIMEZONEDB_API_KEY"),
      "format": "json",
      "by": "position",
      "lat": lat,
      "lng": lon
    }
  ).json()

  return {
    "latitude": lat,
    "longitude": lon,
    "timezone": tz["zoneName"]
  }

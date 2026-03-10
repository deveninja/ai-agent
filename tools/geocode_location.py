"""
geocode_location.py

Resolves a human-readable place name into geographic coordinates
(latitude/longitude) and its IANA timezone string by combining the
Open-Meteo Geocoding API with the TimeZoneDB REST API.
"""

import requests
import os

def geocode_location(location):
  """
  Convert a location name to its coordinates and timezone.

  First queries the Open-Meteo Geocoding API to obtain latitude and
  longitude for the given place name, then queries the TimeZoneDB API
  to resolve the IANA timezone for those coordinates.

  Args:
    location (str): A city or place name (e.g. "Tokyo", "New York").

  Returns:
    dict: A dictionary with the following keys:
      - "latitude"  (float): Geographic latitude.
      - "longitude" (float): Geographic longitude.
      - "timezone"  (str):   IANA timezone identifier (e.g. "Asia/Tokyo").
  """

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

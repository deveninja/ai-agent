from tools.geocode_location import geocode_location
from tools.weather import get_weather
from tools.time_tool import get_time

tool_registry = {
  "geocode_location": geocode_location,
  "get_weather": get_weather,
  "get_time": get_time
}
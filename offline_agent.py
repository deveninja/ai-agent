def decide_tool(question: str):
  """
  Simple rule-based AI fallback
  """

  question = question.lower()

  city = extract_city(question)

  if "weather" in question:
    return {
      "tool_name": "geocode_location",
      "parameters": {"location": city},
      "next_tool": "get_weather"
    }

  if "time" in question:
    return {
      "tool_name": "geocode_location",
      "parameters": {"location": city},
      "next_tool": "get_time"
    }

  return None

def extract_city(question: str):
  """
  Very simple city extractor
  """

  words = question.split()

  for i, word in enumerate(words):
    if word == "in" and i + 1 < len(words):
      return words[i + 1].capitalize()

  return "Manila"
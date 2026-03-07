def decide_tool(question: str):
  """
  Simple rule-based AI fallback
  """

  question = question.lower()

  if "weather" in question:
    return {
      "tool_name": "get_weather",
      "parameters": {"city": extract_city(question)}
    }

  if "time" in question:
    return {
      "tool_name": "get_time",
      "parameters": {"city": extract_city(question)}
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
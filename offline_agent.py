import re

MEMORY = {
  "last_city": None
}

STOP_WORDS = {
  "weather", "time", "in", "what", "is", "the",
  "today", "now", "please",
  "today",
  "tomorrow",
  "yesterday"
}

def decide_tool(question: str):
  """
  Simple rule-based AI fallback
  """

  question = question.lower()
  city = extract_city(question)

  if not city and MEMORY["last_city"]:
    city = MEMORY["last_city"]

  if city:
    MEMORY["last_city"] = city

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
  
  if any(word in question for word in ["who is", "find", "user", "employee"]):
    
    name = extract_name(question)
    name = " ".join(name.split()[:2])
    return {
      "tool_name": "get_user",
      "parameters": {"name": name},
      "next_tool": None
    }

  return None

def extract_city(question: str):
  """
  Very simple city extractor
  """

  words = question.split()

  # case 1: "weather in tokyo"
  for i, word in enumerate(words):
    if word == "in" and i + 1 < len(words):
      city = " ".join(words[i + 1:])
      city = re.sub(r"[^\w\s]", "", city)
      return city.title()

  # case 2: "tokyo weather" or "weather tokyo"
  for word in words:

    word = re.sub(r"[^\w\s]", "", word)

    if word and word not in STOP_WORDS:
      return word.title()

  return None

def extract_name(question: str):
  """
  Extract name after 'who is'
  """

  q = question.lower()

  if "who is" in q:
    name = q.split("who is")[-1].strip()

    # remove punctuation like ?, ., !
    name = re.sub(r"[^\w\s]", "", name)

    return name.title()

  return None
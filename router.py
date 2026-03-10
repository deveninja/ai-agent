import json

with open("config/tools.json") as f:
  tools = json.load(f)

KEYWORDS = []
EXTRA_KEYWORDS = ["weather", "time", "who", "employee", "user"]

for tool in tools:
  KEYWORDS.append(tool["name"].lower())

  if "description" in tool:
    KEYWORDS.extend(tool["description"].lower().split())


def allow_request(question: str):

  q = question.lower()

  for word in EXTRA_KEYWORDS:
    if word in q:
      return True

  for word in KEYWORDS:
    if word in q:
      return True

  return False

def route_tool(question: str):

  q = question.lower()

  if "weather" in q:
    return "weather"

  if "time" in q:
    return "time"

  if any(word in q for word in ["who is", "employee", "user"]):
    return "user"

  return None
import json

with open("config/tools.json") as f:
  tools = json.load(f)

KEYWORDS = []

for tool in tools:
  KEYWORDS.append(tool["name"].lower())

  if "description" in tool:
    KEYWORDS.extend(tool["description"].lower().split())


def allow_request(question: str):

  q = question.lower()

  for word in KEYWORDS:
    if word in q:
      return True

  return False
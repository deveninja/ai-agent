import json
import requests
import os
from router import allow_request

from dotenv import load_dotenv
from openai import OpenAI

from offline_agent import decide_tool

load_dotenv()

USE_OFFLINE = False

try:
  client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except:
  USE_OFFLINE = True


with open("config/tools.json") as f:
  tools = json.load(f)


def call_tool(tool_name, arguments):

  result = requests.post(
    "http://127.0.0.1:8000/tool",
    json={
      "tool_name": tool_name,
      "parameters": arguments
    }
  )

  if result.status_code != 200:
    return f"Tool server error: {result.status_code}"

  try:
    data = result.json()
    return data["result"]
  except Exception:
    return f"Invalid response from tool server: {result.text}"


def ask_agent(question):

  global USE_OFFLINE

  # ROUTER CHECK
  if not allow_request(question):
    return "This agent only supports questions related to its tools."

  if not USE_OFFLINE:

    try:

      messages = [{"role": "user", "content": question}]

      while True:

        response = client.chat.completions.create(
          model="gpt-4o-mini",
          messages=messages,
          tools=[{"type": "function", "function": tool} for tool in tools],
        )

        message = response.choices[0].message

        # If AI wants to call a tool
        if message.tool_calls:

          tool_call = message.tool_calls[0]

          tool_name = tool_call.function.name
          arguments = json.loads(tool_call.function.arguments)

          print("AI selected tool:", tool_name)

          result = call_tool(tool_name, arguments)

          # add tool call to conversation
          messages.append(message)

          messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
          })

        else:
          return message.content

    except Exception as e:
      print("⚠️ OpenAI failed, switching to offline mode")
      USE_OFFLINE = True


  # Offline fallback
  decision = decide_tool(question)

  if decision:

    print("Offline AI selected tool:", decision["tool_name"])

    location_result = call_tool(
      decision["tool_name"],
      decision["parameters"]
    )

    if not isinstance(location_result, dict):
      return f"Tool error: {location_result}"

    # chain next tool
    if decision["next_tool"] == "get_weather":

      return call_tool(
        "get_weather",
        {
          "latitude": location_result["latitude"],
          "longitude": location_result["longitude"]
        }
      )

    if decision["next_tool"] == "get_time":

      return call_tool(
        "get_time",
        {
          "timezone": location_result["timezone"]
        }
      )

  return "Offline AI could not determine the tool."


if __name__ == "__main__":

  while True:

    question = input("\nAsk something: ")

    result = ask_agent(question)

    print("Result:", result)
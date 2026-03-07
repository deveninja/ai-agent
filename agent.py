import json
import requests
import os

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

    return result.json()


def ask_agent(question):

  global USE_OFFLINE

  if not USE_OFFLINE:

    try:

      response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
        tools=[{"type": "function", "function": tool} for tool in tools],
      )

      message = response.choices[0].message

      if message.tool_calls:

        tool_call = message.tool_calls[0]

        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print("AI selected tool:", tool_name)

        return call_tool(tool_name, arguments)

      return message.content

    except Exception as e:
      print("⚠️ OpenAI failed, switching to offline mode")
      USE_OFFLINE = True

  # Offline fallback
  decision = decide_tool(question)

  if decision:

    print("Offline AI selected tool:", decision["tool_name"])

    return call_tool(
      decision["tool_name"],
      decision["parameters"]
    )

  return "Offline AI could not determine the tool."


if __name__ == "__main__":

  while True:

    question = input("\nAsk something: ")

    result = ask_agent(question)

    print("Result:", result)
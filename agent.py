"""
AI MCP Agent

Core responsibilities:

1. Understand user queries
2. Route simple queries directly to tools
3. Use Ollama for reasoning when needed
4. Maintain short-term conversational memory
5. Execute external tools through a tool server
"""

import json
import requests
import ollama

from tools.nlp_parser import parse_query
from router import route_tool
from tools.knowledge_search import search_knowledge
from tools.memory import save_memory, search_memory

# ---------------------------------------------------------
# GLOBAL CONFIGURATION
# ---------------------------------------------------------

CONVERSATION = []

AGENT_MEMORY = {
    "last_city": None
}

MAX_HISTORY = 12
MAX_TOOL_STEPS = 5


# ---------------------------------------------------------
# LOAD TOOL DEFINITIONS
# ---------------------------------------------------------

with open("config/tools.json") as f:
    tools = json.load(f)


# ---------------------------------------------------------
# TOOL EXECUTION
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# FAST TOOL ROUTER
# ---------------------------------------------------------

def run_router_tools(intent, parsed):

    if intent == "weather":

        location = parsed.get("city") or AGENT_MEMORY["last_city"]

        if not location:
          return "Please specify a city."

        geo = call_tool("geocode_location", {"location": location})

        if isinstance(geo, str):
            return geo

        weather = call_tool(
            "get_weather",
            {
                "latitude": geo["latitude"],
                "longitude": geo["longitude"]
            }
        )

        return weather


    elif intent == "time":

        location = parsed.get("city") or AGENT_MEMORY["last_city"]

        if not location:
          return "I don't know which city you mean. Please specify a location."

        geo = call_tool("geocode_location", {"location": location})

        if isinstance(geo, str):
            return geo

        time_data = call_tool(
            "get_time",
            {
                "timezone": geo["timezone"]
            }
        )

        return time_data


    elif intent == "user":

        name = parsed.get("name")

        user_data = call_tool(
            "get_user",
            {
                "name": name
            }
        )

        return user_data
  
    elif intent == "knowledge":

        query = parsed.get("query")

        knowledge_data = search_knowledge(query)

        return knowledge_data
    
    elif intent == "unknown":
      return None

    return None


# ---------------------------------------------------------
# MAIN AGENT
# ---------------------------------------------------------

def ask_agent(question):

    global CONVERSATION

    # -----------------------------------------------------
    # STEP 1: PARSE QUERY
    # -----------------------------------------------------

    parsed = parse_query(question)

    print("Parsed query:", parsed)

    context_words = [
      "there",
      "that city",
      "same place",
      "over there",
      "that place",
      "in that city",
      "in the same place"
    ]

    if not parsed.get("city"):
      q_lower = question.lower()

      if any(word in q_lower for word in context_words) and AGENT_MEMORY["last_city"]:
        parsed["city"] = AGENT_MEMORY["last_city"]

    if parsed.get("city"):
        AGENT_MEMORY["last_city"] = parsed["city"]

    intent = parsed.get("intent")


    # -----------------------------------------------------
    # STEP 2: FAST ROUTER
    # -----------------------------------------------------

    router_result = run_router_tools(intent, parsed)

    if router_result is not None:
        return router_result


    # -----------------------------------------------------
    # STEP 3: INIT CONVERSATION
    # -----------------------------------------------------

    if not CONVERSATION:
        CONVERSATION.append({
            "role": "system",
            "content": """
              You are an AI assistant that can use tools.

              If tool results are provided, use them to answer the user naturally.
              Do not output raw JSON unless asked.
            """
        })


    CONVERSATION.append({
        "role": "user",
        "content": question
    })


    # -----------------------------------------------------
    # STEP 4: TRIM HISTORY
    # -----------------------------------------------------

    if len(CONVERSATION) > MAX_HISTORY:
        del CONVERSATION[1:-MAX_HISTORY]


    # -----------------------------------------------------
    # STEP 5: MEMORY CONTEXT
    # -----------------------------------------------------

    memory = search_memory(question)

    print("MEMORY RESULT:", memory)

    memory_text = "\n".join(memory)

    memory_message = {
        "role": "system",
        "content": f"""
          Agent memory:

          Last known city: {AGENT_MEMORY["last_city"]}

          Relevant past conversation:
          {memory_text}
        """
    }

    # -------------------------------------
    # BUILD MESSAGE CONTEXT
    # -------------------------------------

    messages = [CONVERSATION[0]] + [memory_message] + CONVERSATION[1:]



    # -----------------------------------------------------
    # STEP 5.5: KNOWLEDGE SEARCH (RAG)
    # -----------------------------------------------------

    knowledge = search_knowledge(question)

    print("KNOWLEDGE RESULT:", knowledge)

    if knowledge:

        context = "\n\n".join(knowledge)

        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant that answers questions using provided knowledge."
                },
                {
                    "role": "user",
                    "content": f"""
                      Use the knowledge below to answer the question.

                      Knowledge:
                      {context}

                      Question:
                      {question}

                      Answer clearly and concisely.
                    """
                }
            ]
        )

        # SAFELY read response
        message = response.get("message", {})
        answer = message.get("content")

        # fallback protection
        if not answer or answer.strip() == "":
            answer = f"""
              Based on the available knowledge:

              {context}
            """

        # save to conversation memory
        CONVERSATION.append({
            "role": "assistant",
            "content": answer
        })

        save_memory(f"User: {question}")
        save_memory(f"Assistant: {answer}")

        return answer


    # -----------------------------------------------------
    # STEP 6: LLM TOOL LOOP
    # -----------------------------------------------------

    ollama_tools = [
        {
            "type": "function",
            "function": tool
        }
        for tool in tools
    ]


    last_tool_call = None

    for step in range(MAX_TOOL_STEPS):

        response = ollama.chat(
            model="llama3.2",
            messages=messages,
            tools=ollama_tools
        )

        message = response["message"]

        print("AI response:", message)

        # -----------------------------
        # TOOL REQUEST
        # -----------------------------
        if "tool_calls" in message:

            tool_call = message["tool_calls"][0]

            tool_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            if isinstance(arguments, str):
                arguments = json.loads(arguments)

            tool_signature = f"{tool_name}:{arguments}"

            # STOP if tool repeats
            if tool_signature == last_tool_call:
                print("⚠️ Duplicate tool call detected. Stopping.")
                return "⚠️ Tool loop detected."

            last_tool_call = tool_signature

            print("AI selected tool:", tool_name)

            result = call_tool(tool_name, arguments)

            # Safety check — prevents infinite loops if tool returns empty data
            if not result:
                print("⚠️ Tool returned no data.")
                return "⚠️ Tool returned no data."
            
            # Save city in memory when geocode tool runs
            if tool_name == "geocode_location" and "location" in arguments:
                AGENT_MEMORY["last_city"] = arguments["location"]

            tool_message = {
                "role": "tool",
                "tool_name": tool_name,
                "content": json.dumps(result)
            }

            CONVERSATION.append(message)
            CONVERSATION.append(tool_message)

            # rebuild messages instead of mutating it
            messages = [CONVERSATION[0]] + [memory_message] + CONVERSATION[1:]

            continue

        # -----------------------------
        # FINAL ANSWER
        # -----------------------------
        CONVERSATION.append(message)

        answer = message["content"]

        save_memory(f"User: {question}")
        save_memory(f"Assistant: {answer}")

        return answer

    return "⚠️ Tool loop exceeded."


# ---------------------------------------------------------
# CLI TEST MODE
# ---------------------------------------------------------

if __name__ == "__main__":

    while True:

        question = input("\nAsk something: ")

        result = ask_agent(question)

        print("Result:", result)
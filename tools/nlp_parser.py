"""
nlp_parser.py

Parses free-text user queries into structured intent objects.
Uses a fast rule-based parser for common intents (weather, time, user
lookup) and falls back to an Ollama LLM (llama3.2) for anything that
does not match a known pattern.
"""

import json
import ollama
import re


def parse_query(text):
    """
    Detect the intent and extract entities from a natural-language query.

    First applies lightweight keyword rules for the intents "weather",
    "time", and "user".  If none match, the query is sent to the
    llama3.2 LLM via Ollama which returns structured JSON.  The raw
    JSON is parsed and returned; malformed responses are handled with
    a regex fallback.

    Args:
        text (str): The raw query string from the user.

    Returns:
        dict: A dictionary with the following keys:
            - "intent" (str):  One of "weather", "time", "user", "unknown".
            - "city"   (str|None): Extracted city name, or None.
            - "name"   (str|None): Extracted person name, or None.
            - "date"   (str|None): Extracted date string, or None.
    """

    text_lower = text.lower()

    # --------------------------------
    # FAST RULE PARSER (very fast)
    # --------------------------------

    # WEATHER
    if any(word in text_lower for word in ["weather", "forecast", "temperature", "rain"]):

        city = extract_city(text)

        return {
            "intent": "weather",
            "city": city,
            "name": None,
            "date": None
        }

    # TIME
    if "time" in text_lower:

        city = extract_city(text)

        return {
            "intent": "time",
            "city": city,
            "name": None,
            "date": None
        }

    # USER LOOKUP
    if any(word in text_lower for word in ["user", "employee", "staff"]):

        name = extract_name(text)

        return {
            "intent": "user",
            "city": None,
            "name": name,
            "date": None
        }

    # --------------------------------
    # LLM FALLBACK
    # --------------------------------

    prompt = f"""
        You extract structured data from user queries.

        Return ONLY valid JSON.

        Fields:
        intent
        city
        name
        date

        Allowed intents:
        weather
        time
        user
        unknown

        Intent definitions:

        weather
        Questions about weather or forecasts.

        time
        Questions about current time in a place.

        user
        Looking up information about a specific person.

        unknown
        Anything that does not match the above.

        Important rules:

        - Only use intent "user" if the query is asking about a PERSON.
        - Company names, products, or organizations are NOT users.
        - If unsure, return "unknown".

        Examples:

        Query: weather in Tokyo
        Output:
        {{"intent":"weather","city":"Tokyo","name":null,"date":null}}

        Query: what time is it in Manila
        Output:
        {{"intent":"time","city":"Manila","name":null,"date":null}}

        Query: show user John
        Output:
        {{"intent":"user","city":null,"name":"John","date":null}}

        Query: what services does Virtual Workers offer
        Output:
        {{"intent":"unknown","city":null,"name":null,"date":null}}

        Query: {text}
    """

    response = ollama.chat(
        model="llama3.2",
        format="json",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response["message"]["content"]

    print("Parsed text:", content)

    try:
        return json.loads(content)

    except:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group(0))

    return {"intent": "unknown", "city": None, "name": None, "date": None}

def extract_city(text):
    """
    Extract a city name following the word "in" from a query string.

    Uses a simple regex pattern to capture the text that comes after
    "in " (e.g. "weather in Tokyo" → "Tokyo").

    Args:
        text (str): The raw query string.

    Returns:
        str | None: The extracted city name, or None if not found.
    """

    match = re.search(r"in ([A-Za-z ]+)", text)

    if match:
        return match.group(1).strip()

    return None

def extract_name(text):
    """
    Extract a person's name from a query string.

    Assumes the name is the last word(s) of the query.  Returns the
    final token when the query contains at least two words.

    Args:
        text (str): The raw query string.

    Returns:
        str | None: The extracted name token, or None if the query is
        a single word.
    """

    words = text.split()

    if len(words) >= 2:
        return words[-1]

    return None
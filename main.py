from fastapi import FastAPI
from registry import tool_registry
from schemas.tool_request import ToolRequest

app = FastAPI(title="MCP Tool Server")


@app.get("/")
def root():
  return {"message": "MCP Tool Server Running"}


@app.post("/tool")
def run_tool(request: ToolRequest):

  print(f"Tool called: {request.tool_name}")
  print(f"Parameters: {request.parameters}")

  tool_function = tool_registry.get(request.tool_name)

  if not tool_function:
    return {"error": "Tool not found"}

  result = tool_function(**request.parameters)

  return {"result": result}

@app.get("/tools")
def list_tools():

  tools = []

  for name, func in tool_registry.items():

    tools.append({
      "name": name,
      "description": func.__doc__
    })

  return {"tools": tools}
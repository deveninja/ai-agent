from fastapi import FastAPI
from registry import tool_registry
from schemas.tool_request import ToolRequest

app = FastAPI(title="MCP Tool Server")


@app.get("/")
def root():
  return {"message": "MCP Tool Server Running"}


@app.post("/tool")
def run_tool(request: ToolRequest):

  tool_function = tool_registry.get(request.tool_name)

  if not tool_function:
    return {"error": "Tool not found"}

  result = tool_function(**request.parameters)

  return {"result": result}

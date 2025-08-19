"""
Routers package for the Python Playground API.

Exports submodules:
- auth: Authentication endpoints
- snippets: Snippet CRUD endpoints
- run: Code execution endpoint
- history: Execution history endpoints
"""
# PUBLIC_INTERFACE
def describe() -> str:
    """Return a short description of available routers."""
    return "Routers: auth, snippets, run, history"

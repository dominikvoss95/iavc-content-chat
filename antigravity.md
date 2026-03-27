# Antigravity.md

+ Keep track of all changes and updates to the project
+ Keep changelog
+ Keep track of all dependencies and versions
+ Build a log view for all changes and prompts to the model

## Changelog
- Initialize `src/` and `tests/` structure for the Python LangGraph project
- Create `src/state.py` containing `IAVCGraphState` and typed dicts
- Create `src/nodes.py` containing individual node responsibilities
- Create `src/graph.py` wiring nodes for ingestion and querying
- Create `src/main.py` entrypoint serving FastAPI routes
- Added unit tests in `tests/test_nodes.py` which are passing correctly
- Created baseline `requirements.txt` and `README.md`
- Completed MVP stage as defined in `specs.md`
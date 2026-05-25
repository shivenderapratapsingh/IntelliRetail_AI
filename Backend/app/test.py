from app.models.state import AgentState

from app.graphs.graph_builder import workflow


query = """
Which category has lowest sales
and forecast future demand?
"""

initial_state = AgentState(
    user_query=query
)

result = workflow.invoke(initial_state)

print(result)
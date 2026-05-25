from app.models.state import AgentState

from app.graphs.graph_builder import workflow


query = """
Using internal retail documents and current market trends, suggest how the business can improve customer retention.
"""

initial_state = AgentState(
    user_query=query
)

result = workflow.invoke(initial_state)

print(result)
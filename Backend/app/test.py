from app.models.state import AgentState

from app.graphs.graph_builder import (
    workflow
)


state = AgentState(
    user_query="What is the refund policy?"
)


result = workflow.invoke(state)


print("\n================ GRAPH RESULT ================\n")

print(f"Query: {result['user_query']}")

print(f"Route: {result['route']}")

print(f"\nAnswer:\n{result['final_answer']}")
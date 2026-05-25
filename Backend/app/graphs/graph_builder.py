from langgraph.graph import (
    StateGraph,
    START,
    END
)

from app.models.state import AgentState

from app.agents.supervisor_agent import (
    supervisor_agent
)


#intialize graph

builder = StateGraph(AgentState)


#add nodes

builder.add_node(
    "supervisor",
    supervisor_agent
)


#graph flow

builder.add_edge(
    START,
    "supervisor"
)

builder.add_edge(
    "supervisor",
    END
)


#compile graph

workflow = builder.compile()
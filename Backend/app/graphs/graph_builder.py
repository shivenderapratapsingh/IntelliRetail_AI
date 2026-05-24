from langgraph.graph import StateGraph

from app.models.state import AgentState

from app.agents.supervisor_agent import (
    supervisor_agent
)

from app.agents.analyst_agent import (
    analyst_agent
)

from app.agents.forecast_agent import (
    forecast_agent
)

from app.agents.anomaly_agent import (
    anomaly_agent
)

from app.agents.document_agent import (
    document_agent
)


# =========================================================
# INITIALIZE GRAPH
# =========================================================

graph = StateGraph(AgentState)


# =========================================================
# ADD NODES
# =========================================================

graph.add_node(
    "supervisor",
    supervisor_agent
)

graph.add_node(
    "analyst",
    analyst_agent
)

graph.add_node(
    "forecast",
    forecast_agent
)

graph.add_node(
    "anomaly",
    anomaly_agent
)

graph.add_node(
    "document",
    document_agent
)


# =========================================================
# ROUTING FUNCTION
# =========================================================

def route_decision(state: AgentState):

    return state.route


# =========================================================
# CONDITIONAL ROUTING
# =========================================================

graph.add_conditional_edges(

    "supervisor",

    route_decision,

    {

        "analyst": "analyst",

        "forecast": "forecast",

        "anomaly": "anomaly",

        "document": "document"
    }
)


# =========================================================
# ENTRY POINT
# =========================================================

graph.set_entry_point("supervisor")


# =========================================================
# FINISH POINTS
# =========================================================

graph.set_finish_point("analyst")

graph.set_finish_point("forecast")

graph.set_finish_point("anomaly")

graph.set_finish_point("document")


# =========================================================
# COMPILE WORKFLOW
# =========================================================

workflow = graph.compile()
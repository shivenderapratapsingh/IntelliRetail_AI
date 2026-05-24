from langchain_openai import AzureChatOpenAI

from app.agents.analyst_agent import analyst_agent
from app.agents.forecast_agent import forecast_agent
from app.agents.anomaly_agent import anomaly_agent
from app.agents.document_agent import document_agent

from app.models.state import AgentState

from app.memory.conversation_memory import (
    save_conversation,
    get_recent_conversations
)

from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION
)


# =========================================================
# INITIALIZE LLM
# =========================================================

llm = AzureChatOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    api_version=AZURE_OPENAI_API_VERSION,
    temperature=0
)


# =========================================================
# ROUTER
# =========================================================

def classify_query(
    state: AgentState,
    conversation_history: str
):

    prompt = f"""
    You are an AI supervisor agent.

    Your task is to classify the user query into ONE category.

    Conversation History:
    {conversation_history}

    Categories:

    1. analyst
       - sales
       - revenue
       - profit
       - KPIs
       - SQL analytics
       - regions
       - categories
       - retail metrics

    2. forecast
       - forecasting
       - future prediction
       - future sales
       - next month sales

    3. anomaly
       - anomalies
       - unusual activity
       - fraud
       - abnormal behavior

    4. document
       - PDF questions
       - policies
       - knowledge base
       - documentation

    5. reject
       - unrelated questions
       - general chat
       - weather
       - politics

    Return ONLY one word:
    analyst
    forecast
    anomaly
    document
    reject

    Current User Query:
    {state.user_query}
    """

    response = llm.invoke(prompt)

    return response.content.strip().lower()


# =========================================================
# SUPERVISOR AGENT
# =========================================================

def supervisor_agent(state: AgentState):

    # =====================================================
    # LOAD RECENT MEMORY
    # =====================================================

    memory_result = get_recent_conversations(limit=3)

    conversation_history = ""

    if memory_result["success"]:

        conversations = memory_result["conversations"]

        for convo in conversations:

            conversation_history += f"""
            User: {convo['user_query']}
            Assistant: {convo['final_answer']}
            """

    # =====================================================
    # CLASSIFY QUERY
    # =====================================================

    route = classify_query(
        state,
        conversation_history
    )

    # =====================================================
    # STORE ROUTE
    # =====================================================

    state.route = route

    print("\nROUTE:\n")
    print(route)

    # =====================================================
    # ROUTING
    # =====================================================

    if route == "analyst":

        updated_state = analyst_agent(state)

    elif route == "forecast":

        updated_state = forecast_agent(state)

    elif route == "anomaly":

        updated_state = anomaly_agent(state)

    elif route == "document":

        updated_state = document_agent(state)

    else:

        state.success = False

        state.error = (
            "Query is unrelated to IntelliRetail AI system."
        )

        updated_state = state

    # =====================================================
    # SAVE CONVERSATION
    # =====================================================

    save_conversation(updated_state)

    return updated_state
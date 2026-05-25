from langchain_openai import AzureChatOpenAI

from app.agents.analyst_agent import analyst_agent
from app.agents.forecast_agent import forecast_agent
from app.agents.anomaly_agent import anomaly_agent
from app.agents.document_agent import document_agent
from app.agents.market_agent import market_agent

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
    You are an AI orchestration supervisor.

    Your task is to identify ALL agents required
    to answer the user query.

    Available agents:

    1. analyst
       - sales
       - revenue
       - SQL analytics
       - KPIs
       - profit
       - retail metrics

    2. forecast
       - future sales
       - prediction
       - demand forecasting

    3. anomaly
       - fraud
       - anomalies
       - abnormal behavior

    4. document
       - policies
       - SOPs
       - PDF knowledge base

    5. market
       - trending products
       - competitors
       - retail trends
       - market demand
       - popular products
       - industry insights

    Rules:
    - Return ALL relevant agents.
    - Multiple agents are allowed.
    - Return comma-separated values only.
    - Do NOT explain.

    Examples:
    analyst
    analyst,forecast
    analyst,anomaly
    document
    market
    analyst,market
    forecast,market

    Conversation History:
    {conversation_history}

    Current User Query:
    {state.user_query}
    """

    response = llm.invoke(prompt)

    routes = response.content.strip().lower()

    return [
        route.strip()
        for route in routes.split(",")
    ]


#super visor agent

def supervisor_agent(state: AgentState):

    try:

        #Load recent memory

        memory_result = get_recent_conversations(limit=3)

        conversation_history = ""

        if memory_result["success"]:

            conversations = memory_result["conversations"]

            for convo in conversations:

                conversation_history += f"""
                User: {convo['user_query']}
                Assistant: {convo['final_answer']}
                """

        #classigy_query

        routes = classify_query(
            state,
            conversation_history
        )

        #store routes

        state.routes = routes

        print("\nROUTES:\n")
        print(routes)

        #Multi agent orchestrate
        if "analyst" in routes:

            state = analyst_agent(state)

        if "forecast" in routes:

            state.forecast_input is None

        if "anomaly" in routes:

            state = anomaly_agent(state)

        if "document" in routes:

            state = document_agent(state)

        if "market" in routes:

            state = market_agent(state)

        #Here what we are doing is synthesize complete result 

        synthesis_prompt = f"""
        You are an enterprise retail AI assistant.

        Combine all available agent outputs into
        ONE final professional response.

        
  

        User Query:
        {state.user_query}

        SQL Result:
        {state.sql_result}

        Forecast Prediction:
        {state.prediction}

        Anomaly Status:
        {state.anomaly_status}

        Document Context:
        {state.retrieved_documents}

        Market Insights:
        {state.market_insights}

        Existing Partial Answer:
        {state.final_answer}

        Rules:
        - Combine insights clearly
        - Keep response concise
        - Use professional business language
        - Do NOT hallucinate
        - Only use available information
        """

        final_response = llm.invoke(
            synthesis_prompt
        )

        state.final_answer = (
            final_response.content
        )
        #save conversation

        save_conversation(state)

        return state

    except Exception as e:

        state.success = False

        state.error = str(e)

        return state
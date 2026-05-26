from langchain_openai import AzureChatOpenAI

from app.agents.analyst_agent import analyst_agent
from app.agents.document_agent import document_agent
from app.agents.market_agent import market_agent

from app.models.state import AgentState

from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION
)




llm = AzureChatOpenAI(

    api_key=AZURE_OPENAI_API_KEY,

    azure_endpoint=AZURE_OPENAI_ENDPOINT,

    azure_deployment=AZURE_OPENAI_DEPLOYMENT,

    api_version=AZURE_OPENAI_API_VERSION,

    temperature=0
)




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
       - profit
       - retail metrics

    2. document
       - policies
       - SOPs
       - PDF knowledge base

    3. market
       - trending products
       - competitors
       - retail trends
       - market demand
       - popular products
       - industry insights

    4. forecast
       - future sales
       - prediction
       - demand forecasting

    5. anomaly
       - fraud
       - anomalies
       - abnormal behavior

    6. general
       - greetings
       - help
       - capabilities
       - casual conversation
       - introduction
       - what can you do

    Rules:
    - Return ALL relevant agents.
    - Multiple agents are allowed.
    - Return comma-separated values only.
    - Do NOT explain.
    - If query is conversational return: general

    Examples:
    analyst
    analyst,market
    document
    market
    general
    forecast
    anomaly

    Conversation History:
    {conversation_history}

    Current User Query:
    {state.user_query}
    """

    response = llm.invoke(prompt)

    routes = response.content.strip().lower()

    cleaned_routes = [

        route.strip()

        for route in routes.split(",")

        if route.strip() not in ["", "none", "null"]
    ]

    return cleaned_routes




def supervisor_agent(state: AgentState):

    try:

        # =================================================
        # SESSION CHAT HISTORY
        # =================================================

        conversation_history = ""

        if state.chat_history:

            for message in state.chat_history:

                role = message.get(
                    "role",
                    ""
                )

                content = message.get(
                    "content",
                    ""
                )

                conversation_history += f"""
                {role}: {content}
                """



        routes = classify_query(
            state,
            conversation_history
        )

        state.routes = routes

        print("\nROUTES:\n")

        print(routes)



        if "general" in routes:

            state.final_answer = """
            Hello! I can help you with:

            • Retail sales analytics
            • Business KPI insights
            • SQL-based business analysis
            • Market trend analysis
            • Retail document Q&A
            • Product performance analysis
            • Revenue and profit insights

            You can ask questions like:

            - Which category has highest sales?
            - Show low-performing products
            - Analyze regional profit trends
            - Which segment is most profitable?
            - What are current retail market trends?
            - Answer questions from uploaded retail documents
            """

            return state



        if "forecast" in routes:

            state.final_answer = """
            Forecasting requires structured business data.

            Please use the dedicated forecasting endpoint:

            POST /forecast

            Required JSON fields:

            - Quantity
            - Profit
            - Returns
            - Order_Year
            - Order_Month
            - Order_Day
            - Profit_Margin
            - Shipping_Days
            """

            return state



        if "anomaly" in routes:

            state.final_answer = """
                Anomaly detection requires structured transaction data.

                Please use the dedicated anomaly endpoint:

                POST /anomaly

                Provide business transaction features
                in JSON format for anomaly analysis.
            """

            return state



        if "analyst" in routes:

            state = analyst_agent(state)



        if "document" in routes:

            state = document_agent(state)



        if "market" in routes:

            state = market_agent(state)



        #Final Synthesis

        synthesis_prompt = f"""
        You are an enterprise retail AI assistant.

        Combine all available agent outputs into
        ONE final professional response.

        User Query:
        {state.user_query}

        SQL Result:
        {state.sql_result}

        Document Context:
        {state.retrieved_documents}

        Market Insights:
        {state.market_insights}

        Existing Partial Answer:
        {state.final_answer}

        Instructions:

        1. Use ONLY available information.
        2. Do NOT hallucinate.
        3. Keep response concise.
        4. Use professional business language.
        5. Focus on actionable insights.
        6. Never mention SQL queries
           or technical implementation.
        """

        final_response = llm.invoke(
            synthesis_prompt
        )

        state.final_answer = (
            final_response.content
        )

        return state

    except Exception as e:

        state.success = False

        state.error = str(e)

        return state
from langchain_openai import AzureChatOpenAI

from app.models.state import AgentState

from app.services.azure_ml_service import (
    forecast_sales
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
# FORECAST AGENT
# =========================================================

def forecast_agent(state: AgentState):

    try:

        # =================================================
        # SAMPLE INPUT DATA
        # =================================================

        input_data = {
            "Quantity": 8,
            "Profit": 250.75,
            "Returns": 0,
            "Order_Year": 2025,
            "Order_Month": 11,
            "Order_Day": 15,
            "Profit_Margin": 22.5,
            "Shipping_Days": 2
        }

        # =================================================
        # CALL FORECAST SERVICE
        # =================================================

        result = forecast_sales(input_data)

        # =================================================
        # HANDLE ERRORS
        # =================================================

        if result["status"] == "error":

            state.success = False

            state.error = result["message"]

            return state

        prediction = result["predicted_sales"]

        # =================================================
        # STORE PREDICTION
        # =================================================

        state.prediction = prediction

        # =================================================
        # BUSINESS EXPLANATION
        # =================================================

        prompt = f"""
        You are a retail forecasting analyst.

        User Query:
        {state.user_query}

        Predicted Sales:
        {prediction}

        Explain the forecast in simple business language.

        Keep response concise and professional.
        """

        response = llm.invoke(prompt)

        state.final_answer = response.content

        return state

    except Exception as e:

        state.success = False

        state.error = str(e)

        return state
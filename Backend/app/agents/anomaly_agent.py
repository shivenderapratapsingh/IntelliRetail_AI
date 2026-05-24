import joblib
import pandas as pd

from langchain_openai import AzureChatOpenAI

from app.models.state import AgentState

from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
    ANOMALY_MODEL_PATH,
    SCALER_PATH
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
# LOAD MODEL + SCALER
# =========================================================

model = joblib.load(ANOMALY_MODEL_PATH)

scaler = joblib.load(SCALER_PATH)


# =========================================================
# ANOMALY AGENT
# =========================================================

def anomaly_agent(state: AgentState):

    try:

        # =================================================
        # SAMPLE INPUT
        # =================================================

        input_data = pd.DataFrame([{
            "Sales": 10000,
            "Profit": -5000,
            "Quantity": 1,
            "Profit_Margin": -50,
            "Shipping_Days": 15
        }])

        # =================================================
        # SCALE DATA
        # =================================================

        scaled_data = scaler.transform(input_data)

        # =================================================
        # PREDICT
        # =================================================

        prediction = model.predict(scaled_data)[0]

        # =================================================
        # INTERPRET RESULT
        # =================================================

        if prediction == -1:

            anomaly_status = "Anomaly Detected"

        else:

            anomaly_status = "Normal Transaction"

        # =================================================
        # STORE IN STATE
        # =================================================

        state.anomaly_status = anomaly_status

        # =================================================
        # BUSINESS EXPLANATION
        # =================================================

        prompt = f"""
        You are a retail anomaly detection analyst.

        User Query:
        {state.user_query}

        Detection Result:
        {anomaly_status}

        Transaction Data:
        {input_data.to_dict(orient='records')}

        Explain the anomaly result in simple business language.

        Keep response concise and professional.
        """

        response = llm.invoke(prompt)

        state.final_answer = response.content

        return state

    except Exception as e:

        state.success = False

        state.error = str(e)

        return state
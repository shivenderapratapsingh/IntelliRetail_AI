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




llm = AzureChatOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    api_version=AZURE_OPENAI_API_VERSION,
    temperature=0
)



def forecast_agent(state: AgentState):

    try:
        #Here is input data
        input_data = state.forecast_input

        #Here is forcast service

        result = forecast_sales(input_data)


        if result["status"] == "error":

            state.success = False

            state.error = result["message"]

            return state

        prediction = result["predicted_sales"]

        #Prediction

        state.prediction = prediction



        prompt = f"""
        You are a retail forecasting analyst.

        User Query:
        {state.user_query}

        Predicted Sales Value:
        {round(prediction, 2)}

        Your task:
        - Explain the predicted sales value in simple business language.
        - Keep the response concise and professional.
        - Do NOT mention units unless explicitly provided.
        - Focus on business impact and retail insight.
        """

        response = llm.invoke(prompt)



        state.final_answer = response.content



        state.success = True

        return state

    except Exception as e:

        state.success = False

        state.error = str(e)

        return state
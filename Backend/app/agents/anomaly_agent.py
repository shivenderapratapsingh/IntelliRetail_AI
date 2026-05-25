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

from app.core.logger import logger


#llm

llm = AzureChatOpenAI(

    api_key=AZURE_OPENAI_API_KEY,

    azure_endpoint=AZURE_OPENAI_ENDPOINT,

    azure_deployment=AZURE_OPENAI_DEPLOYMENT,

    api_version=AZURE_OPENAI_API_VERSION,

    temperature=0
)


#Here i am doing two things first using scaler to give equal weightage to each column value and then fee
#vale to model

model = joblib.load(
    ANOMALY_MODEL_PATH
)

scaler = joblib.load(
    SCALER_PATH
)

#Anomaly agent

def anomaly_agent(
    state: AgentState
):

    try:

        logger.info(
            "Anomaly agent started"
        )


        #Validate input means checking if input is correct or not

        if not state.anomaly_input:

            logger.warning(
                "No anomaly input provided"
            )

            state.success = False

            state.error = (
                "Anomaly input data is required"
            )

            return state

        #Here what we are doing is that we create dataframe the input user feed so model generate correct result 

        input_data = pd.DataFrame([
            state.anomaly_input
        ])

        logger.info(
            f"Input Data: {input_data.to_dict(orient='records')}"
        )


        #Scale data 

        scaled_data = scaler.transform(
            input_data
        )

        logger.info(
            "Data scaling completed"
        )

        #Here we are predicting result

        prediction = model.predict(
            scaled_data
        )[0]

        logger.info(
            f"Prediction Result: {prediction}"
        )

        #Here we interpreting resutl

        if prediction == -1:

            anomaly_status = (
                "Anomaly Detected"
            )

        else:

            anomaly_status = (
                "Normal Transaction"
            )

        #Store status

        state.anomaly_status = (
            anomaly_status
        )

        logger.info(
            f"Anomaly Status: {anomaly_status}"
        )

        #Here we are entering prompt

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

        response = llm.invoke(
            prompt
        )

        #Here we are storing final result
        state.final_answer = (
            response.content
        )


        state.success = True

        logger.info(
            "Anomaly agent completed successfully"
        )

        return state

    except Exception as e:

        logger.error(
            f"Anomaly agent failed: {str(e)}"
        )

        state.success = False

        state.error = str(e)

        return state
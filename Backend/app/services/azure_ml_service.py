import requests

from dotenv import load_dotenv
import os
from app.core.logger import logger

load_dotenv()

AZURE_ML_API_KEY=os.getenv("AZURE_ML_API_KEY")
AZURE_ML_ENDPOINT=os.getenv("AZURE_ML_ENDPOINT")


def forecast_sales(data: dict):

    try:

        logger.info("Preparing Azure ML request")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AZURE_ML_API_KEY}"
        }

        payload = {
            "Inputs": {
                "input1": [data]
            },
            "GlobalParameters": {}
        }

        logger.info(f"Payload: {payload}")

        response = requests.post(
            AZURE_ML_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=30
        )

        logger.info(
            f"Azure ML Response Status: {response.status_code}"
        )

        response.raise_for_status()

        result = response.json()

        logger.info(f"Azure ML Response: {result}")

        prediction = result["Results"][
            "WebServiceOutput0"
        ][0]["Scored Labels"]

        logger.info(
            f"Predicted Sales: {prediction}"
        )

        return {
            "predicted_sales": prediction,
            "status": "success"
        }

    except requests.exceptions.RequestException as e:

        logger.error(
            f"Azure ML Request Failed: {str(e)}"
        )

        return {
            "status": "error",
            "message": str(e)
        }

    except Exception as e:

        logger.error(
            f"Unexpected Error: {str(e)}"
        )

        return {
            "status": "error",
            "message": str(e)
        }
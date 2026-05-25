from fastapi import APIRouter

from app.models.state import AgentState

from app.agents.forecast_agent import (
    forecast_agent
)

from app.agents.anomaly_agent import (
    anomaly_agent
)

from app.models.ml_schema import (
    ForecastRequest,
    AnomalyRequest
)

from app.core.logger import logger




router = APIRouter()


#forecast end point

@router.post("/ml-expert/forecast")

def forecast_endpoint(
    payload: ForecastRequest
):

    try:

        logger.info(
            "Forecast endpoint called"
        )

        logger.info(
            f"Forecast payload: {payload.dict()}"
        )

        # =================================================
        # CREATE STATE
        # =================================================

        state = AgentState(

            user_query="Forecast sales",

            forecast_input={

                "Quantity": payload.quantity,

                "Profit": payload.profit,

                "Returns": payload.returns,

                "Order_Year": payload.order_year,

                "Order_Month": payload.order_month,

                "Order_Day": payload.order_day,

                "Profit_Margin": payload.profit_margin,

                "Shipping_Days": payload.shipping_days
            }


        )

        #here forecast agent run

        result = forecast_agent(state)

        logger.info(
            "Forecast prediction completed"
        )

        logger.info(
            f"Prediction: {result.prediction}"
        )

        return {

            "success": result.success,

            "prediction": result.prediction,

            "answer": result.final_answer
        }

    except Exception as e:

        logger.error(
            f"Forecast endpoint failed: {str(e)}"
        )

        return {

            "success": False,

            "error": str(e)
        }


#anomaly endpoint

@router.post("/ml-expert/anomaly")

def anomaly_endpoint(
    payload: AnomalyRequest
):

    try:

        logger.info(
            "Anomaly endpoint called"
        )

        logger.info(
            f"Anomaly payload: {payload.dict()}"
        )

        #state

        state = AgentState(

            user_query="Detect anomalies",

            anomaly_input={

                "Sales": payload.sales,

                "Profit": payload.profit,

                "Quantity": payload.quantity,

                "Profit_Margin": payload.profit_margin,

                "Shipping_Days": payload.shipping_days}
        )

        #run anomaly agent 

        result = anomaly_agent(state)

        logger.info(
            "Anomaly detection completed"
        )

        logger.info(
            f"Anomaly Status: {result.anomaly_status}"
        )

        return {

            "success": result.success,

            "anomaly_status": result.anomaly_status,

            "answer": result.final_answer
        }

    except Exception as e:

        logger.error(
            f"Anomaly endpoint failed: {str(e)}"
        )

        return {

            "success": False,

            "error": str(e)
        }
from fastapi import APIRouter

from app.models.state import AgentState

from app.graphs.graph_builder import (
    workflow
)

from app.models.agent_schema import (
    AgentRequest
)

from app.core.logger import logger


#Router

router = APIRouter()




@router.post("/data-analyst/chat")

def agent_chat(
    payload: AgentRequest
):

    try:

        logger.info(
            "Agent interaction endpoint called"
        )

        logger.info(
            f"User Query: {payload.query}"
        )
        
        #State query

        state = AgentState(
            user_query=payload.query
        )

        #run langgraph workflow

        result = workflow.invoke(state)

        logger.info(
            "Workflow execution completed"
        )

        logger.info(
            f"Routes used: {result['routes']}"
        )

        return {

            "success": result["success"],

            "routes": result["routes"],

            "answer": result["final_answer"]
        }

    except Exception as e:

        logger.error(
            f"Agent endpoint failed: {str(e)}"
        )

        return {

            "success": False,

            "error": str(e)
        }
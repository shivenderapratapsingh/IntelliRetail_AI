from fastapi import APIRouter

from app.models.state import AgentState

from app.agents.document_agent import (
    document_agent
)

from app.models.document_schema import (
    DocumentRequest
)

from app.core.logger import logger



router = APIRouter()


#document search endpoint

@router.post("/document-assistant/search")

def document_search(
    payload: DocumentRequest
):

    try:

        logger.info(
            "Document search endpoint called"
        )

        logger.info(
            f"Query: {payload.query}"
        )

        #Create state

        state = AgentState(

            user_query=payload.query
        )

        #run document agent

        result = document_agent(state)

        logger.info(
            "Document retrieval completed"
        )

        return {

            "success": result.success,

            "answer": result.final_answer,

            "sources": [

                doc["source"]

                for doc in (
                    result.retrieved_documents or []
                )
            ]
        }

    except Exception as e:

        logger.error(
            f"Document endpoint failure: {str(e)}"
        )

        return {

            "success": False,

            "error": str(e)
        }
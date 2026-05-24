from langchain_openai import AzureChatOpenAI

from app.models.state import AgentState

from app.rag.retrieval import retrieve_documents

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
# DOCUMENT AGENT
# =========================================================

def document_agent(state: AgentState):

    try:

        # =================================================
        # RETRIEVE RELEVANT DOCUMENTS
        # =================================================

        retrieval_result = retrieve_documents(
            query=state.user_query,
            k=3
        )

        # =================================================
        # HANDLE ERRORS
        # =================================================

        if not retrieval_result["success"]:

            state.success = False

            state.error = retrieval_result["error"]

            return state

        documents = retrieval_result["results"]

        # =================================================
        # STORE RETRIEVED DOCS
        # =================================================

        state.retrieved_documents = documents

        # =================================================
        # BUILD CONTEXT
        # =================================================

        context = "\n\n".join([
            doc["content"]
            for doc in documents
        ])

        # =================================================
        # PROMPT
        # =================================================

        prompt = f"""
        You are a Retail Knowledge Assistant.

        Answer ONLY using the provided context.

        If answer is not present in context,
        say:
        "I could not find this information in the knowledge base."

        CONTEXT:
        {context}

        USER QUESTION:
        {state.user_query}
        """

        # =================================================
        # LLM RESPONSE
        # =================================================

        response = llm.invoke(prompt)

        state.final_answer = response.content

        return state

    except Exception as e:

        state.success = False

        state.error = str(e)

        return state
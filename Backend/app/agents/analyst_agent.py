from langchain_openai import AzureChatOpenAI
from app.models.state import AgentState
from app.tools.sql_tool import run_sql_tool

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
# ANALYST AGENT
# =========================================================

def analyst_agent(state: AgentState):

    try:

        # RUN SQL TOOL
        sql_result = run_sql_tool(state.user_query)

        # HANDLE ERRORS
        if not sql_result["success"]:

            state.success = False
            state.error = sql_result["error"]

            return state

        # EXTRACT DATA
        generated_sql = sql_result["generated_sql"]

        data = sql_result["data"]

        state.generated_sql = generated_sql

        state.sql_result = data

        # PROMPT
        prompt = f"""
        ...
        """

        response = llm.invoke(prompt)

        state.final_answer = response.content
        state.agent_name = "analyst_agent"

        return state


    except Exception as e:

        state.success = False

        state.error = str(e)

        return state
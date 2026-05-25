from langchain_openai import AzureChatOpenAI
from app.models.state import AgentState
from app.tools.sql_tool import run_sql_tool

from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION
)


#intialize llm

llm = AzureChatOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    api_version=AZURE_OPENAI_API_VERSION,
    temperature=0
)


#analyst agent

def analyst_agent(state: AgentState):

    try:

        # run sql tooool
        sql_result = run_sql_tool(state.user_query)

        if not sql_result["success"]:

            state.success = False
            state.error = sql_result["error"]

            return state

        # doing extraction of data
        generated_sql = sql_result["generated_sql"]

        data = sql_result["data"]

        state.generated_sql = generated_sql

        state.sql_result = data

        #Here we going to enter prompt
        prompt = f"""
        You are a retail business analyst.

        User Question:
        {state.user_query}

        Generated SQL:
        {generated_sql}

        SQL Result:
        {data}

        Explain the result in concise business language.

        Keep response professional and easy to understand.
        """

        response = llm.invoke(prompt)

        state.final_answer = response.content
        # state.agent_name = "analyst_agent" #Just for checking purpose

        return state


    except Exception as e:

        state.success = False

        state.error = str(e)

        return state
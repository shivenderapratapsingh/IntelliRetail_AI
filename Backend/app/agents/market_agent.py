from langchain_openai import AzureChatOpenAI

from tavily import TavilyClient

from app.models.state import AgentState

from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
    TAVILY_API_KEY
)




llm = AzureChatOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    api_version=AZURE_OPENAI_API_VERSION,
    temperature=0
)



tavily_client = TavilyClient(
    api_key=TAVILY_API_KEY
)


#market agent

def market_agent(state: AgentState):

    try:

        #This is going to use upto date things

        tavily_response = tavily_client.search(

            query=state.user_query,

            search_depth="advanced",

            max_results=5
        )

        results = tavily_response.get(
            "results",
            []
        )
        print("It is from tavily--------------------------------")
        print(results)
        print("It is from tavily--------------------------------")



        market_context = "\n\n".join([

            result.get("content", "")

            for result in results
        ])


        state.market_insights = results



        prompt = f"""
        You are a retail market intelligence expert.

        Analyze the following market research data
        and provide strategic business insights.

        User Query:
        {state.user_query}

        Market Research Data:
        {market_context}

        Rules:
        - Keep response concise
        - Focus on retail strategy
        - Mention trends clearly
        - Mention competitor insights if available
        - Do NOT hallucinate
        - ONLY use provided information
        """

        response = llm.invoke(prompt)

        state.final_answer = response.content

        return state

    except Exception as e:

        state.success = False

        state.error = str(e)

        return state
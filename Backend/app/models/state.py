from typing import Optional, List, Dict

from pydantic import BaseModel,Field


class AgentState(BaseModel):

    #user input

    user_query: str

    #routing

    routes: list[str] = Field(default_factory=list)

    #sql agent

    generated_sql: Optional[str] = None

    sql_result: Optional[List[Dict]] = None

    #forecast

    prediction: Optional[float] = None

    #Anomaly

    anomaly_status: Optional[str] = None

    #market insights we add

    market_insights: Optional[list] = None

    #document agent

    retrieved_documents: Optional[List[Dict]] = None


    #structured input

    forecast_input: Optional[dict] = None

    anomaly_input: Optional[dict] = None

    #final response

    final_answer: Optional[str] = None

    #meta deta

    success: bool = True

    error: Optional[str] = None
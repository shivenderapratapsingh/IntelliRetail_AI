from typing import Optional, List, Dict

from pydantic import BaseModel, Field


class AgentState(BaseModel):



    user_query: str



    chat_history: Optional[List[Dict]] = None



    routes: list[str] = Field(default_factory=list)



    generated_sql: Optional[str] = None

    sql_result: Optional[List[Dict]] = None



    prediction: Optional[float] = None



    anomaly_status: Optional[str] = None



    market_insights: Optional[list] = None



    retrieved_documents: Optional[List[Dict]] = None



    forecast_input: Optional[dict] = None

    anomaly_input: Optional[dict] = None



    final_answer: Optional[str] = None



    success: bool = True

    error: Optional[str] = None
from typing import Optional, List, Dict

from pydantic import BaseModel


class AgentState(BaseModel):

    # =====================================================
    # USER INPUT
    # =====================================================

    user_query: str

    # =====================================================
    # ROUTING
    # =====================================================

    route: Optional[str] = None

    # =====================================================
    # SQL AGENT
    # =====================================================

    generated_sql: Optional[str] = None

    sql_result: Optional[List[Dict]] = None

    # =====================================================
    # FORECAST
    # =====================================================

    prediction: Optional[float] = None

    # =====================================================
    # ANOMALY
    # =====================================================

    anomaly_status: Optional[str] = None

    # =====================================================
    # DOCUMENT AGENT
    # =====================================================

    retrieved_documents: Optional[List[Dict]] = None

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    final_answer: Optional[str] = None

    # =====================================================
    # METADATA
    # =====================================================

    success: bool = True

    error: Optional[str] = None
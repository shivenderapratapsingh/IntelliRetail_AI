from fastapi import FastAPI
import os
from app.api.routes.ml_routes import (
    router as ml_router
)

from app.api.routes.documents_routes import (
    router as document_router
)
from app.api.routes.agent_routes import (
    router as agent_router
)

from app.api.routes.ingestion_routes import (
    router as ingestion_router
)

from app.Monitoring.telemetry import (
    setup_telemetry
    
)

from app.core.config import (
    LANGCHAIN_API_KEY,
    LANGCHAIN_PROJECT
)

#It is for azure analytics


# setup_telemetry()

#Langsmith it is for agent meteric

os.environ["LANGCHAIN_TRACING_V2"] = "true"

os.environ["LANGCHAIN_API_KEY"] = (
    LANGCHAIN_API_KEY
)

os.environ["LANGCHAIN_PROJECT"] = (
    LANGCHAIN_PROJECT
)
app = FastAPI(

    title="IntelliRetail AI",

    description="""
    Enterprise Retail Intelligence Platform

    Features:
    - ML Forecasting
    - Anomaly Detection
    - RAG Document Search
    - Multi-Agent AI Orchestration
    - Market Intelligence
    """,

    version="1.0.0"
)


#Register routes

app.include_router(
    ml_router
)

app.include_router(
    document_router
)

app.include_router(
    agent_router
)


app.include_router(
    ingestion_router
)

#This to check api running or not

@app.get("/")

def root():

    return {

        "message": "IntelliRetail AI API Running",

        "status": "success"
    }
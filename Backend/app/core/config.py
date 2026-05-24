import os

from dotenv import load_dotenv

load_dotenv()


# =========================================================
# AZURE OPENAI
# =========================================================

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")


# =========================================================
# EMBEDDING MODEL
# =========================================================

AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
)


# =========================================================
# AZURE AI SEARCH
# =========================================================

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")

AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")

AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")


# =========================================================
# AZURE ML
# =========================================================

AZURE_ML_ENDPOINT = os.getenv("AZURE_ML_ENDPOINT")

AZURE_ML_API_KEY = os.getenv("AZURE_ML_API_KEY")


# =========================================================
# MONGODB
# =========================================================

MONGODB_URI = os.getenv("MONGODB_URI")

MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")


# =========================================================
# LOCAL FILES
# =========================================================

PARQUET_FILE_PATH = "data/cleaned_data.parquet"

ANOMALY_MODEL_PATH = "app/ml/artifacts/anomaly_model.pkl"

SCALER_PATH = "app/ml/artifacts/anomaly_scaler.pkl"

FORECAST_MODEL_PATH = "app/ml/artifacts/forecast_model.pkl"

#Mogodb connection

MONGODB_URI = os.getenv("MONGODB_URI")

MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")
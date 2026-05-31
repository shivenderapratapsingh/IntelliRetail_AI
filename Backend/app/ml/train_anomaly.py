import os
import joblib
import pandas as pd

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.core.logger import logger




load_dotenv()




CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

CONTAINER_NAME = os.getenv(
    "CONTAINER_NAME"
)

BLOB_NAME = os.getenv(
    "BLOB_NAME"
)

LOCAL_DATA_PATH = os.getenv(
    "LOCAL_DATA_PATH"
)

MODEL_PATH = os.getenv(
    "ANOMALY_MODEL_PATH"
)


#Here what i am doing is downloading data from blob

try:

    logger.info(
        "Connecting to Azure Blob Storage..."
    )

    blob_service_client = BlobServiceClient.from_connection_string(
        CONNECTION_STRING
    )

    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME,
        blob=BLOB_NAME
    )

    logger.info(
        "Downloading cleaned dataset..."
    )

    with open(LOCAL_DATA_PATH, "wb") as file:

        download_stream = blob_client.download_blob()

        file.write(download_stream.readall())

    logger.info(
        "Dataset downloaded successfully!"
    )

except Exception as e:

    logger.error(
        f"Blob download failed: {e}"
    )

    raise


#load that dataset which we downloaded

try:

    logger.info(
        "Loading dataset..."
    )

    df = pd.read_parquet(LOCAL_DATA_PATH)

    logger.info(
        f"Dataset loaded successfully | Shape: {df.shape}"
    )

except Exception as e:

    logger.error(
        f"Dataset loading failed: {e}"
    )

    raise


#feature selection

FEATURE_COLUMNS = [
    "Sales",
    "Profit",
    "Quantity",
    "Profit_Margin",
    "Shipping_Days"
]

logger.info(
    f"Selected Features: {FEATURE_COLUMNS}"
)

X = df[FEATURE_COLUMNS]


#handling missing values

logger.info(
    "Handling missing values..."
)

X = X.fillna(0)


#applying feature scaling

logger.info(
    "Applying feature scaling..."
)

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

logger.info(
    "Feature scaling completed!"
)


#Train isolation model

logger.info(
    "Training Isolation Forest model..."
)

model = IsolationForest(
    n_estimators=200,
    contamination=0.07,
    random_state=42
)

model.fit(X_scaled)

logger.info(
    "Model training completed successfully!"
)


#Generate prediciton

logger.info(
    "Generating anomaly predictions..."
)

predictions = model.predict(X_scaled)

"""
1  = Normal
-1 = Anomaly
"""

df["Anomaly_Prediction"] = predictions

df["Anomaly_Label"] = df[
    "Anomaly_Prediction"
].map(
    {
        1: "Normal",
        -1: "Anomaly"
    }
)

logger.info(
    "Predictions generated successfully!"
)


#Evaluation
logger.info(
    "Evaluating anomaly results..."
)

normal_count = len(
    df[df["Anomaly_Label"] == "Normal"]
)

anomaly_count = len(
    df[df["Anomaly_Label"] == "Anomaly"]
)

logger.info(
    f"Normal Records: {normal_count}"
)

logger.info(
    f"Anomaly Records: {anomaly_count}"
)


#sample anomalies

logger.info(
    "Displaying sample anomalies..."
)

sample_anomalies = df[
    df["Anomaly_Label"] == "Anomaly"
][
    FEATURE_COLUMNS + ["Anomaly_Label"]
].head(10)

print("\n================ SAMPLE ANOMALIES ================\n")

print(sample_anomalies)


from sklearn.metrics import classification_report


#synthesis 

df["GroundTruth"] = (

    (df["Profit"] < -500) |

    (df["Profit_Margin"] < -50) |

    (
        (df["Sales"] > 3000) &
        (df["Profit"] < 0)
    ) |

    (df["Shipping_Days"] > 10)

).astype(int)

#convert model prediction

df["Predicted"] = (
    df["Anomaly_Prediction"] == -1
).astype(int)


#evaluation report

report = classification_report(
    df["GroundTruth"],
    df["Predicted"]
)

print("\n================ EVALUATION REPORT ================\n")

print(report)

logger.info(
    "Evaluation completed successfully!"
)


#save model

logger.info(
    "Saving anomaly model..."
)

joblib.dump(
    model,
    MODEL_PATH
)

logger.info(
    f"Model saved successfully at: {MODEL_PATH}"
)


#save scaler

SCALER_PATH = (
    "app/ml/artifacts/anomaly_scaler.pkl"
)

joblib.dump(
    scaler,
    SCALER_PATH
)

logger.info(
    f"Scaler saved successfully at: {SCALER_PATH}"
)



#save ouput csv

OUTPUT_PATH = "anomaly_output.csv"

df.to_csv(
    OUTPUT_PATH,
    index=False
)

logger.info(
    f"Anomaly results saved at: {OUTPUT_PATH}"
)


#final summary

logger.info(
    "Anomaly detection pipeline completed successfully!"
)

print("\n==============================================")

print("ANOMALY DETECTION PIPELINE COMPLETED")

print("==============================================\n")

print(f"Dataset Shape       : {df.shape}")

print(f"Features Used       : {FEATURE_COLUMNS}")

print(f"Model Saved At      : {MODEL_PATH}")

print(f"Scaler Saved At     : {SCALER_PATH}")

print(f"Output CSV Saved At : {OUTPUT_PATH}")

print("\nPipeline executed successfully!\n")
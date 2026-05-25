import os
import logging

from azure.monitor.opentelemetry import (
    configure_azure_monitor
)

from app.core.config import (
    APPLICATIONINSIGHTS_CONNECTION_STRING
)


#logger

logger = logging.getLogger(
    "IntelliRetailAI-Telemetry"
)


#setting telemetry

def setup_telemetry():

    #connection string

    connection_string =APPLICATIONINSIGHTS_CONNECTION_STRING

    #check connection strring

    if not connection_string:

        logger.warning(
            "Telemetry disabled: No connection string found."
        )

        return

    #configure azuremonitor

    try:

        configure_azure_monitor(

            connection_string=connection_string
        )

        logger.info(
            "Azure Monitor Telemetry Enabled Successfully"
        )

    except Exception as e:

        logger.error(
            f"Telemetry initialization failed: {str(e)}"
        )
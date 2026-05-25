from fastapi import (
    APIRouter,
    UploadFile,
    File
)

import os

from app.services.document_ingestion_service import (
    ingest_documents
)

router = APIRouter()


@router.post("/data-ingestion/upload-documents")

async def upload_documents(

    file: UploadFile = File(...)

):

    try:

        upload_dir = "uploaded_docs"

        os.makedirs(
            upload_dir,
            exist_ok=True
        )

        file_path = os.path.join(
            upload_dir,
            file.filename
        )

        with open(file_path, "wb") as f:

            content = await file.read()

            f.write(content)

        result = ingest_documents(
            [file_path]
        )

        return result

    except Exception as e:

        return {

            "success": False,

            "message": str(e)
        }
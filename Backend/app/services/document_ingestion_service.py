import os
from dotenv import load_dotenv

load_dotenv(override=True)

#docment loader adn splitter
from langchain_community.document_loaders import (
    PyPDFLoader
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

#azure embedding and vector spaxe

from langchain_openai import (
    AzureOpenAIEmbeddings
)

from langchain_community.vectorstores import (
    AzureSearch
)

#config

from app.core.config import (

    AZURE_OPENAI_ENDPOINT,

    AZURE_OPENAI_API_KEY,

    AZURE_OPENAI_API_VERSION,

    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,

    AZURE_SEARCH_ENDPOINT,

    AZURE_SEARCH_KEY,

    AZURE_SEARCH_INDEX
)

#logger

from app.core.logger import logger




def ingest_documents(
    file_paths: list[str]
):

    try:

        logger.info(
            "Starting document ingestion"
        )


        #initalize embeddings

        logger.info(
            "Initializing Azure OpenAI embeddings"
        )

        embeddings = AzureOpenAIEmbeddings(

            azure_endpoint=AZURE_OPENAI_ENDPOINT,

            api_key=AZURE_OPENAI_API_KEY,

            azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,

            openai_api_version=AZURE_OPENAI_API_VERSION
        )

        logger.info(
            "Embeddings initialized successfully"
        )


        #initaialize azure ai search

        logger.info(
            "Initializing Azure AI Search"
        )

        vector_store = AzureSearch(

            azure_search_endpoint=AZURE_SEARCH_ENDPOINT,

            azure_search_key=AZURE_SEARCH_KEY,

            index_name=AZURE_SEARCH_INDEX,

            embedding_function=embeddings.embed_query
        )

        logger.info(
            "Azure AI Search initialized successfully"
        )


        #validate files

        if not file_paths:

            logger.warning(
                "No PDF files received"
            )

            return {

                "success": False,

                "message": "No files provided"
            }

        logger.info(
            f"Received {len(file_paths)} PDF files"
        )

        all_splits = []

        #process each pdf

        for pdf_path in file_paths:

            try:

                file_name = os.path.basename(
                    pdf_path
                )

                logger.info(
                    f"Processing PDF: {file_name}"
                )


                #load pdf

                loader = PyPDFLoader(
                    pdf_path
                )

                raw_docs = loader.load()

                logger.info(
                    f"Loaded {len(raw_docs)} pages"
                )

                #chunking

                text_splitter = (
                    RecursiveCharacterTextSplitter(

                        chunk_size=1000,

                        chunk_overlap=200
                    )
                )

                splits = (
                    text_splitter.split_documents(
                        raw_docs
                    )
                )



                #add source metadata

                for split in splits:

                    split.metadata["source"] = (
                        file_name
                    )

                logger.info(
                    f"Created {len(splits)} chunks"
                )

                all_splits.extend(splits)

            except Exception as e:

                logger.error(
                    f"Failed processing {pdf_path}: {str(e)}"
                )



        #upload to azure ai search

        if all_splits:

            try:

                logger.info(
                    f"Uploading {len(all_splits)} chunks"
                )

                vector_store.add_documents(
                    documents=all_splits
                )

                logger.info(
                    "Document indexing completed"
                )

                return {

                    "success": True,

                    "message": "Documents indexed successfully"
                }

            except Exception as e:

                logger.error(
                    f"Upload failed: {str(e)}"
                )

                return {

                    "success": False,

                    "message": str(e)
                }

            finally:

                vector_store = None

        else:

            logger.warning(
                "No documents were processed"
            )

            return {

                "success": False,

                "message": "No documents processed"
            }

    except Exception as e:

        logger.error(
            f"Document ingestion failed: {str(e)}"
        )

        return {

            "success": False,

            "message": str(e)
        }
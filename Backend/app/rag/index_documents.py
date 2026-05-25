import os
import glob
from dotenv import load_dotenv

load_dotenv(override=True)

# Document Loaders and Splitters
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Azure Vector Store & Embeddings
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch

# Import your existing config variables
from app.core.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_KEY,
    AZURE_SEARCH_INDEX
)

def index_docs():



    #pdf folder path

    data_folder = r"D:\INTELLIRETAIL_AI\Backend\data\document"

    print(f"Looking for PDFs inside: {data_folder}")

    #Intialize embeddings

    try:

        print("Initializing Azure OpenAI Embeddings...")

        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            openai_api_version=AZURE_OPENAI_API_VERSION,
        )

        print("Embeddings initialized successfully")

    except Exception as e:
        print(f"Embeddings initialization failed: {e}")
        return

    #Intialize azure search

    try:

        print("Initializing Azure AI Search......")

        vector_store = AzureSearch(
            azure_search_endpoint=AZURE_SEARCH_ENDPOINT,
            azure_search_key=AZURE_SEARCH_KEY,
            index_name=AZURE_SEARCH_INDEX,
            embedding_function=embeddings.embed_query
        )

        print("Azure AI Search initialized successfully")

    except Exception as e:
        print(f"Azure Search initialization failed: {e}")
        return


    #Find pdf files

    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in {data_folder}")
        return

    print(f"Found {len(pdf_files)} PDFs")

    all_splits = []

    #process each pdf

    for pdf_path in pdf_files:

        try:

            file_name = os.path.basename(pdf_path)

            print(f"Processing: {file_name}")

            loader = PyPDFLoader(pdf_path)

            raw_docs = loader.load()

            print(f"Loaded {len(raw_docs)} pages")

            #chunking

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )

            splits = text_splitter.split_documents(raw_docs)

            # we adding some meta data
            for split in splits:
                split.metadata["source"] = file_name

            print(f"Created {len(splits)} chunks")

            all_splits.extend(splits)

        except Exception as e:
            print(f"Failed to process {pdf_path}: {e}")



    #uploading to azure search

    if all_splits:

        try:

            print(f"Uploading {len(all_splits)} chunks...")

            vector_store.add_documents(documents=all_splits)

            print("DOCUMENT INDEXING COMPLETED")

        except Exception as e:
            print(f"Failed to upload documents: {e}")

        finally:

            vector_store = None

    else:
        print("No documents were processed")


if __name__ == "__main__":

    try:
        index_docs()

    except Exception as e:
        print(f"Application failed: {e}")
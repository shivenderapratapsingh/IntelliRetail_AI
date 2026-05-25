from langchain_openai import AzureOpenAIEmbeddings

from langchain_community.vectorstores import AzureSearch

from app.core.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_KEY,
    AZURE_SEARCH_INDEX
)




print("Initializing embeddings...")

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    openai_api_version=AZURE_OPENAI_API_VERSION
)

print("Embeddings initialized")


#Intializing vector store

print("Connecting to Azure AI Search...")

vector_store = AzureSearch(
    azure_search_endpoint=AZURE_SEARCH_ENDPOINT,
    azure_search_key=AZURE_SEARCH_KEY,
    index_name=AZURE_SEARCH_INDEX,
    embedding_function=embeddings.embed_query
)

print("Azure AI Search connected")


#retrieve document

def retrieve_documents(query: str, k: int = 3):

    try:

        print(f"\nSearching for: {query}")

        results = vector_store.similarity_search(
            query=query,
            k=k
        )

        retrieved_chunks = []

        for doc in results:

            retrieved_chunks.append({
                "content": doc.page_content,
                "source": doc.metadata.get(
                    "source",
                    "Unknown"
                )
            })

        return {
            "success": True,
            "query": query,
            "results": retrieved_chunks
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }
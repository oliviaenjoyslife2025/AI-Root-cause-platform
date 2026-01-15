import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document

# Mock data for RAG (similar to technical wikis)
WIKI_DATA = [
    "Error: Redis connection timeout. Solution: Check security groups and increase connection pool size.",
    "Issue: 500 Internal Server Error in payment-service. Root Cause: Downstream database lock. Solution: Kill long-running queries.",
    "Metric: High latency in streaming-node. Possible cause: CPU throttling on EKS nodes. Solution: Adjust HPA (Horizontal Pod Autoscaler) limits."
]

class RAGPipeline:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_db = None
        self._initialize_db()

    def _initialize_db(self):
        # Initialize in-memory ChromaDB for demonstration
        documents = [Document(page_content=text) for text in WIKI_DATA]
        self.vector_db = Chroma.from_documents(
            documents=documents, 
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )

    def query(self, query_text: str):
        results = self.vector_db.similarity_search(query_text, k=1)
        return results[0].page_content if results else "No historical solution found."

rag_pipeline = RAGPipeline()

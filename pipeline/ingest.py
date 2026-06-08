"""Document ingestion pipeline with semantic chunking."""
import os
from typing import List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from google.cloud import bigquery

class EnterpriseIngestionPipeline:
    def __init__(self, project_id: str, namespace: str):
        self.project_id = project_id
        self.namespace = namespace
        self.embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
        self.bq = bigquery.Client(project=project_id)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=512, chunk_overlap=77,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def ingest_document(self, content: str, metadata: dict) -> int:
        chunks = self.splitter.split_text(content)
        embeddings = self.embeddings.embed_documents(chunks)
        rows = [
            {"namespace": self.namespace, "chunk_id": f"{metadata["id"]}_{i}",
             "content": chunk, "embedding": emb, "metadata": str(metadata)}
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
        ]
        self.bq.insert_rows_json(f"{self.project_id}.rag_store.chunks", rows)
        return len(chunks)

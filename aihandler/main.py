import faiss
import numpy as np
import json
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

class RAGIndex:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.faiss_index = None
        self.documents = []
        self.load_data()

    def load_data(self):
        """Load and index documents at startup"""
        try:
            from django.db import connection

            # Check if table exists
            with connection.cursor() as cursor:
                if os.getenv("DEVELOPMENT_MODE") == "False":
                    cursor.execute(
                        "SELECT tablename FROM pg_catalog.pg_tables WHERE tablename = 'aihandler_product';"
                    )
                    table_exists = cursor.fetchone()
                else:
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='aihandler_product';"
                    )
                    table_exists = cursor.fetchone()

            if not table_exists:
                print("Table 'aihandler_product' does not exist. Skipping data load.")
                return

            # Import models only if table exists
            from .models import Product
            from .serializers import ProductSerializer

            product = Product.objects.all()
            if not product.exists():
                print("No products found in the database.")
                return
                
            if Product is None:
                return  #
            product = Product.objects.all()
            if not product.exists():
                return
            product_serializer = ProductSerializer(product, many=True).data

            document_texts = [json.dumps(i) for i in product_serializer]
            self.documents = [Document(page_content=text) for text in document_texts]

            # Create FAISS index
            doc_embeddings = self.embeddings.embed_documents(document_texts)
            embedding_dim = len(doc_embeddings[0])
            self.faiss_index = faiss.IndexFlatL2(embedding_dim)

            # Add embeddings to FAISS index
            self.faiss_index.add(np.array(doc_embeddings).astype("float32"))
        except Exception as e:
            raise Exception(f"Error loading data: {e}")

    def retrieve_documents(self, query, k=2):
        """Retrieve relevant documents"""
        try:
            if not self.faiss_index:
                return []

            query_embedding = self.embeddings.embed_query(query)
            query_embedding = np.array(query_embedding).reshape(1, -1).astype("float32")

            distances, indices = self.faiss_index.search(query_embedding, k)
            return [self.documents[i].page_content for i in indices[0] if i != -1]
        except Exception as e:
            raise Exception(f"Error retrieving documents: {e}")

# Create a global instance to be used throughout the app
rag_index = RAGIndex()
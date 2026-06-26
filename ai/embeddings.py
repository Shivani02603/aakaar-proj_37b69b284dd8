import os
from typing import List
import openai

# Constants
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

class EmbeddingClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for a single text input.
        """
        client = openai.OpenAI(api_key=self.api_key)
        response = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of text inputs.
        """
        client = openai.OpenAI(api_key=self.api_key)
        response = client.embeddings.create(input=texts, model=EMBEDDING_MODEL)
        return [item.embedding for item in response.data]

# Module-level function for embedding
def get_embedding(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a batch of text inputs using the pinned model.
    """
    client = EmbeddingClient()
    return client.embed_batch(texts)
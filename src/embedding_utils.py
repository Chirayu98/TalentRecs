from sentence_transformers import SentenceTransformer

# Load embedding model once globally
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    """
    Generate an embedding vector for the input text using the loaded model.
    """
    return model.encode(text)

import time

print("Importing...")
t0 = time.time()
from fastembed import TextEmbedding
print(f"Import took {time.time() - t0:.2f}s")

print("Creating embedder...")
t1 = time.time()
embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
print(f"Embedder creation took {time.time() - t1:.2f}s")

print("Embedding 8 short texts...")
texts = ["This is a test sentence about machine learning."] * 8
t2 = time.time()
embeddings = list(embedder.embed(texts))
print(f"Embedding took {time.time() - t2:.2f}s")

print("Embedding again (same process)...")
t3 = time.time()
embeddings2 = list(embedder.embed(texts))
print(f"Second embedding took {time.time() - t3:.2f}s")
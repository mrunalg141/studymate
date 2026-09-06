import time
from fastembed import TextEmbedding

print('Loading model...')
t0 = time.time()
embedder = TextEmbedding(model_name='BAAI/bge-small-en-v1.5')
print(f'Load took {time.time()-t0:.2f}s')

# Simulate a realistic 150-word chunk, repeated 21 times (like your real PDF)
sample_chunk = ' '.join(['machine learning deep neural networks'] * 30)  # ~150 words
texts = [sample_chunk] * 21

print('Embedding 21 realistic chunks...')
t1 = time.time()
embeddings = list(embedder.embed(texts))
print(f'Embedding took {time.time()-t1:.2f}s')

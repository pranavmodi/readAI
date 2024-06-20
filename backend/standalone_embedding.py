import logging
import time
import psutil
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import gc
import sys
import json
import os


def log_memory_usage(stage=""):
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logging.info(f"{stage} - Memory usage: {memory_info.rss / 1024 ** 2:.2f} MB")
    sys.stdout.flush()

def create_embeddings(texts, model_name, batch_size=1):
    print("printing the text ", texts)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        if i % 10 == 0:
            logging.info(f"Embeddings generated for {i}")
            sys.stdout.flush()

        start_time = time.time()
        try:
            inputs = tokenizer(batch_texts, return_tensors='pt', truncation=True, padding=True)
            
            try:
                outputs = model(**inputs)
            except Exception as e:
                logging.error(f"Error during model forward pass for text chunk {i + 1}: {e}")
                sys.stdout.flush()
                continue
            
            embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
            embeddings.extend(embedding)

            # Clear cache and garbage collect
            del inputs
            del outputs
            gc.collect()
            torch.cuda.empty_cache()

        except Exception as e:
            logging.error(f"Error processing text chunk {i + 1}: {e}")
            sys.stdout.flush()
            continue  # Skip the problematic chunk and proceed with the next one

    return np.vstack(embeddings) if embeddings else np.array([])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    texts = json.loads(sys.argv[1])
    model_name = sys.argv[2]
    batch_size = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    embeddings = create_embeddings(texts, model_name, batch_size)
    np.save('embeddings.npy', embeddings)
    logging.info(f"Embeddings shape: {embeddings.shape}")
    sys.stdout.flush()

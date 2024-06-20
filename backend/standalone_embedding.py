# standalone_embedding.py

import logging
import time
import psutil
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import gc
import os

def log_memory_usage(stage=""):
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logging.info(f"{stage} - Memory usage: {memory_info.rss / 1024 ** 2:.2f} MB")

def create_embeddings(texts, model_name, batch_size=1):
    logging.info("in standalone create embeddings!!")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        logging.info(f"Processing text chunk {i + 1}/{len(texts)}: {batch_texts[0][:100]}...")  # Log the first 100 characters of the first text in batch
        start_time = time.time()
        try:
            inputs = tokenizer(batch_texts, return_tensors='pt', truncation=True, padding=True)
            logging.info(f"Tokenized text chunk {i + 1}/{len(texts)}: {inputs['input_ids'].shape}")
            
            log_memory_usage(f"After tokenizing chunk {i + 1}")
            
            logging.info("Before model forward pass")
            sys.stdout.flush()
            try:
                outputs = model(**inputs)
                logging.info("After model forward pass")
                sys.stdout.flush()
            except Exception as e:
                logging.error(f"Error during model forward pass for text chunk {i + 1}: {e}")
                sys.stdout.flush()
                continue
            
            log_memory_usage(f"After model forward pass for chunk {i + 1}")

            embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
            embeddings.extend(embedding)
            logging.info(f"Successfully processed text chunk {i + 1}/{len(texts)} in {time.time() - start_time:.2f} seconds")
            sys.stdout.flush()
            
            log_memory_usage(f"After processing chunk {i + 1}")

            # Clear cache and garbage collect
            del inputs
            del outputs
            gc.collect()
            torch.cuda.empty_cache()

        except Exception as e:
            logging.error(f"Error processing text chunk {i + 1}: {e}")
            continue  # Skip the problematic chunk and proceed with the next one

    return np.vstack(embeddings) if embeddings else np.array([])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    import sys
    import json

    texts = json.loads(sys.argv[1])
    model_name = sys.argv[2]
    batch_size = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    embeddings = create_embeddings(texts, model_name, batch_size)
    np.save('embeddings.npy', embeddings)
    logging.info(f"Embeddings shape: {embeddings.shape}")

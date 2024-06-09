import os
import json
import logging
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_embeddings(input_filename, output_filename, model_name='all-MiniLM-L6-v2'):
    logging.info(f'Processing file: {input_filename}')
    
    model = SentenceTransformer(model_name)
    
    with open(input_filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    texts = []
    for line in lines:
        data = json.loads(line)
        if 'body' in data:
            texts.append(data['body'])
        elif 'title' in data:
            texts.append(data['title'])
    
    if not texts:
        logging.warning(f'No texts found in file: {input_filename}')
        return
    
    try:
        embeddings = model.encode(texts, show_progress_bar=True)
    except Exception as e:
        logging.error(f'Error generating embeddings for file: {input_filename}, error: {str(e)}')
        return
    
    with open(output_filename, 'w', encoding='utf-8') as file:
        for i, line in enumerate(lines):
            data = json.loads(line)
            data['embedding'] = embeddings[i].tolist()
            file.write(json.dumps(data) + '\n')
    
    logging.info(f'Embeddings saved to {output_filename}')

def run_vector_embed():
    os.makedirs('embed', exist_ok=True)
    
    input_directory = 'input'
    for filename in os.listdir(input_directory):
        if filename.endswith('.txt'):
            input_filepath = os.path.join(input_directory, filename)
            output_filepath = os.path.join('embed', f'{filename.split(".")[0]}_embeddings.txt')
            generate_embeddings(input_filepath, output_filepath)

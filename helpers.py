import os
import shutil
import numpy as np

def clear_directory(directory):
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        os.makedirs(directory)

def load_all_embeddings(embed_dir):
    embeddings = []
    for file in os.listdir(embed_dir):
        if file.endswith(".txt"):
            with open(os.path.join(embed_dir, file), 'r') as f:
                for line in f:
                    embeddings.append(np.fromstring(line.strip(), sep=' '))
    return np.vstack(embeddings)

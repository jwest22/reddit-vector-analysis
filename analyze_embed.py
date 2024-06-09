import os
import json
import numpy as np
import faiss
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from datetime import datetime

def load_embeddings(input_filename):
    with open(input_filename, 'r', encoding='utf-8') as file:
        data = [json.loads(line) for line in file]
    texts = [d['body'] if 'body' in d else d['title'] for d in data]
    embeddings = np.array([d['embedding'] for d in data])
    return texts, embeddings

def cluster_embeddings(embeddings, n_clusters=10, analyze_all_together=False):
    if analyze_all_together:
        labels = np.zeros(len(embeddings))
    else:
        n_clusters = min(n_clusters, len(embeddings))
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(embeddings)
        labels = kmeans.labels_
    return labels.astype(int)

def analyze_clusters(texts, labels, n_top_terms=10):
    labels = labels.astype(int)
    cluster_texts = {i: [] for i in range(max(labels) + 1)}
    for text, label in zip(texts, labels):
        cluster_texts[label].append(text)
    
    vectorizer = CountVectorizer(stop_words='english')
    cluster_top_terms = {}
    
    for label, texts in cluster_texts.items():
        X = vectorizer.fit_transform(texts)
        freqs = zip(vectorizer.get_feature_names_out(), X.sum(axis=0).tolist()[0])
        top_terms = sorted(freqs, key=lambda x: -x[1])[:n_top_terms]
        cluster_top_terms[label] = top_terms
    
    return cluster_top_terms

def run_vector_analysis(n_top_terms):
    os.makedirs('output', exist_ok=True)

    embed_directory = 'embed'
    all_texts = []
    all_embeddings = []

    for filename in os.listdir(embed_directory):
        if filename.endswith('.txt'):
            input_filepath = os.path.join(embed_directory, filename)
            texts, embeddings = load_embeddings(input_filepath)
            all_texts.extend(texts)
            all_embeddings.append(embeddings)
            
            default_n_clusters = 10
            analyze_all_together = True

            labels = cluster_embeddings(embeddings, default_n_clusters, analyze_all_together)

            top_terms = analyze_clusters(texts, labels, n_top_terms)

            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            output_filename = f'output/{filename.split(".")[0]}_analysis_{timestamp}.txt'
            with open(output_filename, 'w', encoding='utf-8') as output_file:
                for cluster, terms in top_terms.items():
                    output_file.write(f"Cluster {cluster}:\n")
                    for term, freq in terms:
                        output_file.write(f"{term}: {freq}\n")
                    output_file.write("\n")

            print(f"Analysis saved to {output_filename}")

    all_embeddings = np.vstack(all_embeddings)
    
    d = all_embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    
    index.add(all_embeddings)

    faiss_index_file = 'output/faiss_index.bin'
    faiss.write_index(index, faiss_index_file)
    print(f"FAISS index saved to {faiss_index_file}")

    return index, all_texts

def search_faiss_index(index, query_embedding, top_k=5):
    D, I = index.search(query_embedding, top_k)
    return I, D

import os
import shutil
from sentence_transformers import SentenceTransformer
from get_comments import run_comment_retrieval
from vector_embed import run_vector_embed
from analyze_embed import run_vector_analysis, search_faiss_index

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

if __name__ == "__main__":
    directories_to_clear = ['input', 'embed', 'output']
    for directory in directories_to_clear:
        clear_directory(directory)

    hours = 24
    subreddit = 'dataengineering'
    run_comment_retrieval(subreddit, hours)
    
    run_vector_embed()
    
    n_top_terms=100
    index, texts = run_vector_analysis(n_top_terms)
    
    model_name = 'all-MiniLM-L6-v2'
    model = SentenceTransformer(model_name)
    query_text = input("Enter Query: ")
    query_embedding = model.encode([query_text])
    top_k = 5
    I, D = search_faiss_index(index, query_embedding, top_k)
    print("Top results:")
    for i in range(top_k):
        print(f"Text: {texts[I[0][i]]}, Distance: {D[0][i]}")

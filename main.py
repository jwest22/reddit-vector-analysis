import os
from datetime import datetime
from sentence_transformers import SentenceTransformer
from get_comments import run_comment_retrieval
from vector_embed import run_vector_embed
from analyze_embed import run_vector_analysis, search_faiss_index, load_faiss_index
from helpers import clear_directory, load_all_embeddings

HOURS = 24
SUBREDDIT = 'dataengineering'
TOP_N_TERMS = 100
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
TOP_K_MATCHES = 5

if __name__ == "__main__":
    reprocess_choice = input("Do you want to reprocess posts and comments? (yes/no): ").strip().lower()
    if reprocess_choice == 'yes':
        directories_to_clear = ['input', 'embed', 'output']
        for directory in directories_to_clear:
            clear_directory(directory)

        run_comment_retrieval(SUBREDDIT, HOURS)
        run_vector_embed()
        index, texts = run_vector_analysis(TOP_N_TERMS)
    else:
        if os.listdir('embed') and os.path.exists('output/faiss_index.bin'):
            index = load_faiss_index('output/faiss_index.bin')
            texts = load_all_embeddings('embed')
            index, texts = run_vector_analysis(TOP_N_TERMS)
        else:
            print("No existing embeddings or FAISS index found. Please reprocess the data.")
            exit()

    model = SentenceTransformer(EMBEDDING_MODEL)
    query_text = input("Enter Query: ")
    query_embedding = model.encode([query_text])
    
    if index and texts:
        I, D = search_faiss_index(index, query_embedding, TOP_K_MATCHES)
        print("Top results:")
        
        results = []
        for i in range(TOP_K_MATCHES):
            result = f"Text: {texts[I[0][i]]}, Distance: {D[0][i]}"
            results.append(result)
            print(result)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join('output', f'search_results_{timestamp}.txt')
        with open(output_file, 'w') as f:
            for result in results:
                f.write(result + '\n')
                
        print(f"Results saved to {output_file}")
    else:
        print("No embeddings available for search. Please reprocess the data.")

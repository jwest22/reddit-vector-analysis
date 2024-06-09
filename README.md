# Reddit Data Retrieval, Embedding, and Analysis

This project retrieves recent posts and comments from a specified subreddit, generates embeddings using Sentence Transformers, clusters the embeddings, and allows for similarity search using FAISS.

## Table of Contents
- [Installation](#installation)
- [Overview](#overview)
- [Usage](#usage)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/username/repo-name.git
    cd repo-name
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Overview

The script will:

* Clear the contents of the input, embed, and output directories.
* Retrieve recent posts and comments from the specified subreddit for a specified lookback window (hours).
* Generate embeddings for the retrieved comments and posts.
* Cluster the embeddings and perform analysis (for n_top_terms)
* Save the analysis to the output directory.
* Prompt for a text query and perform a similarity search using FAISS and return similar posts/comments (top_k).

## Usage

Update the variables in `main.py` as desired:
* hours = 24
* subreddit = 'dataengineering'
* n_top_terms=100
* top_k = 5

To run the entire process, simply execute the main script:

```bash
python main.py
```

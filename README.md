# D&D Knowledge Base API

## Description

This project provides a FastAPI-based API for performing semantic searches on a pre-built knowledge base containing Dungeons & Dragons (5th Edition and other sources) information. It uses Sentence Transformers for generating embeddings and Faiss for efficient vector similarity searching, allowing users to query the knowledge base with natural language questions.

The knowledge base index (`index.faiss` and `index.pkl`) must be generated separately (e.g., using a script like `faissmaker.py`) using the `sentence-transformers/all-MiniLM-L6-v2` model.

## Features

* Semantic search over D&D documents (monsters, spells, rules, etc.).
* FastAPI backend providing a RESTful interface.
* Retrieves relevant text chunks along with metadata (source, type, original JSON data where applicable).
* Includes basic health check endpoint.
* Automated tests using `pytest`.

## Technology Stack

* **API Framework:** FastAPI
* **Web Server:** Uvicorn
* **Embeddings:** Sentence Transformers (`sentence-transformers/all-MiniLM-L6-v2`)
* **Vector Search:** Faiss (`faiss-cpu`)
* **Data Handling:** LangChain Core, LangChain Community (for loading pickled Docstore/Documents)
* **Testing:** Pytest

## Prerequisites

* Python 3.11+
* Pip (Python package installer)
* Access to the pre-built Faiss index files:
    * `faiss_index/index.faiss`
    * `faiss_index/index.pkl` (containing the LangChain Docstore and ID map)

## Setup and Installation

1.  **Clone/Setup Project:** Ensure you have the project files in a local directory.
2.  **Create Virtual Environment:** It's highly recommended to use a virtual environment.
    ```bash
    python -m venv .venv
    source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
    ```
3.  **Install Dependencies:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
4.  **Place Index Files:** Ensure the pre-built `index.faiss` and `index.pkl` files are located inside a subdirectory named `faiss_index` within the project root:
    ```
    your-project-root/
    ├── faiss_index/
    │   ├── index.faiss
    │   └── index.pkl
    ├── main.py
    ├── requirements.txt
    └── ... (other files)
    ```

## Running the API (Development)

To run the API locally with auto-reload enabled for development:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
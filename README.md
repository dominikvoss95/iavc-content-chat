# IAVC World Content Chat Agent

An intelligent AI chat agent that crawls, indexes, and answers user questions based on content from [IAVC World](https://www.iavcworld.de). The system runs **100% locally** using Ollama and SQLite-vec.

## ✨ Features
- **Local RAG:** Uses Ollama (`phi3`) and HuggingFace Embeddings locally. No API keys required.
- **Intelligent Parsing:** Extracts clean article text, metadata (title, author/company), and publication dates.
- **Auto-Crawler:** A robust script to automatically discover and ingest article lists from the website.
- **Chat Widget:** A drop-in JavaScript widget for any website (e.g., WordPress integration).
- **Persistent Memory:** Stores knowledge in a local SQLite vector database (`iavc_knowledge.db`).

## 🚀 Installation

1. **Prerequisites:**
   - Install [Ollama](https://ollama.com/).
   - Pull the model: `ollama pull phi3`.

2. **Repository Setup:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 🛠 Usage

### 1. Start the Backend
```bash
python -m src.main
```
The server starts at `http://localhost:8000`.

### 2. Ingest Content (Crawler)
In a separate terminal:
```bash
python scripts/auto_crawler.py
```
This scans the homepage and AI categories to populate the database.

### 3. Deploy the Widget
- **Local Testing:** Open `http://localhost:8000/public/index.html` in your browser.
- **Production:** Host the backend and embed the `<script>` tag from `public/index.html` into your site footer.

## 📁 Project Structure
- `src/`: Core logic, LangGraph nodes, and database management.
- `scripts/`: Utility scripts like the Auto-Crawler.
- `public/`: Static assets for the frontend and chat widget.
- `tests/`: Unit tests for graph logic and validation.

---
*Developed for the IAVC World project.*

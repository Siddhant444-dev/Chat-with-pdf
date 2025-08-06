# RAG System for Document Processing and Question Answering

A comprehensive Retrieval-Augmented Generation (RAG) system built with FastAPI, Pinecone, and OpenAI for processing insurance policy documents and answering questions about them.

## Features

- **Document Processing**: Supports PDF, DOCX, and TXT files
- **Vector Storage**: Uses Pinecone for efficient similarity search
- **LLM Integration**: OpenAI GPT models for intelligent responses
- **RESTful API**: FastAPI-based API with proper authentication
- **Scalable Architecture**: Modular design for easy extension

## Tech Stack

- **Backend**: FastAPI
- **Vector Database**: Pinecone
- **LLM**: OpenAI GPT-3.5-turbo
- **Embeddings**: Sentence Transformers
- **Document Processing**: PyPDF2, python-docx
- **Deployment**: Heroku-ready

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd rag-system
```

2. **Create and activate conda environment**:
```bash
conda create -n rag-system python=3.11 -y
conda activate rag-system
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp env_example.txt .env
# Edit .env with your API keys
```

## Configuration

Create a `.env` file with the following variables:

```env
# Vector Database (Pinecone)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=your-pinecone-environment
PINECONE_INDEX_NAME=rag-system

# LLM Settings
OPENAI_API_KEY=your-openai-api-key

# Optional: Perplexity API
PERPLEXITY_API_KEY=your-perplexity-api-key
```

## Usage

### Running the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Main Endpoint: `/hackrx/run`

**POST** `/hackrx/run`

Process a document and answer questions about it.

**Headers**:
```
Authorization: Bearer <api_key>
Content-Type: application/json
```

**Request Body**:
```json
{
    "documents": "https://example.com/policy.pdf",
    "questions": [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?",
        "Does this policy cover maternity expenses?"
    ]
}
```

**Response**:
```json
{
    "answers": [
        "A grace period of thirty days is provided for premium payment...",
        "There is a waiting period of thirty-six months...",
        "Yes, the policy covers maternity expenses..."
    ]
}
```

#### Health Check: `/health`

**GET** `/health`

Check system health and component status.

**Response**:
```json
{
    "status": "healthy",
    "components": {
        "vector_store_available": true,
        "llm_client_available": true,
        "document_processor_available": true
    }
}
```

### Example Usage

```python
import requests

# API endpoint
url = "http://localhost:8000/hackrx/run"

# Request data
data = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?"
    ]
}

# Headers
headers = {
    "Authorization": "Bearer your-api-key",
    "Content-Type": "application/json"
}

# Make request
response = requests.post(url, json=data, headers=headers)
print(response.json())
```

## Architecture

### Components

1. **Document Processor** (`rag_system/utils/document_processor.py`)
   - Downloads documents from URLs
   - Extracts text from PDF, DOCX, and TXT files
   - Chunks text for vector storage

2. **Vector Store** (`rag_system/utils/vector_store.py`)
   - Manages Pinecone vector database
   - Creates embeddings using Sentence Transformers
   - Handles similarity search

3. **LLM Client** (`rag_system/utils/llm_client.py`)
   - Interfaces with OpenAI API
   - Generates responses based on retrieved context
   - Supports structured and simple responses

4. **RAG System** (`rag_system/models/rag_system.py`)
   - Orchestrates all components
   - Handles document processing and question answering
   - Provides system status monitoring

5. **FastAPI Application** (`rag_system/app/main.py`)
   - RESTful API endpoints
   - Authentication and error handling
   - Request/response validation

### Flow

1. **Document Processing**:
   - Download document from URL
   - Extract text based on file type
   - Chunk text into smaller pieces
   - Create embeddings for each chunk
   - Store in Pinecone vector database

2. **Question Answering**:
   - Create embedding for the question
   - Search for similar chunks in vector database
   - Retrieve top-k most relevant chunks
   - Generate answer using LLM with retrieved context

## Deployment

### Heroku Deployment

1. **Create Heroku app**:
```bash
heroku create your-app-name
```

2. **Set environment variables**:
```bash
heroku config:set PINECONE_API_KEY=your-key
heroku config:set PINECONE_ENVIRONMENT=your-env
heroku config:set OPENAI_API_KEY=your-key
```

3. **Deploy**:
```bash
git push heroku main
```

### Docker Deployment

1. **Build image**:
```bash
docker build -t rag-system .
```

2. **Run container**:
```bash
docker run -p 8000:8000 rag-system
```

## Evaluation Parameters

The system is designed to meet the following evaluation criteria:

- **Accuracy**: Precise query understanding and clause matching
- **Token Efficiency**: Optimized LLM token usage
- **Latency**: Fast response times (< 30 seconds)
- **Reusability**: Modular code design
- **Explainability**: Clear decision reasoning with clause traceability

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub. 
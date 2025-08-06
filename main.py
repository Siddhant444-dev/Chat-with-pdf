import uvicorn
import logging
import os
from rag_system.app.main import app
from rag_system.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use PORT env var if set (Azure), fallback to 8000 locally
    uvicorn.run(
        "rag_system.app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

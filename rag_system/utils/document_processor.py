import os
import requests
import tempfile
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
from docx import Document
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles processing of various document types for RAG system"""
    
    def __init__(self, supported_types: List[str] = None):
        self.supported_types = supported_types or [".pdf", ".docx", ".doc", ".txt"]
    
    def download_document(self, url: str) -> bytes:
        """Download document from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading document from {url}: {e}")
            raise
    
    def extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX content"""
        try:
            doc = Document(BytesIO(content))
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise
    
    def extract_text_from_txt(self, content: bytes) -> str:
        """Extract text from TXT content"""
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            return content.decode('latin-1')
    
    def process_document(self, url: str) -> Dict[str, Any]:
        """Process document from URL and return extracted text and metadata"""
        try:
            # Download document
            content = self.download_document(url)
            
            # Determine file type from URL
            file_extension = Path(url.split('?')[0]).suffix.lower()
            
            if file_extension not in self.supported_types:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Extract text based on file type
            if file_extension == ".pdf":
                text = self.extract_text_from_pdf(content)
            elif file_extension == ".docx":
                text = self.extract_text_from_docx(content)
            elif file_extension == ".txt":
                text = self.extract_text_from_txt(content)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            return {
                "text": text,
                "file_type": file_extension,
                "url": url,
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error processing document from {url}: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this is not the first chunk, include some overlap
            if start > 0:
                start = start - overlap
            
            chunk = text[start:end]
            chunks.append(chunk)
            
            start = end
        
        return chunks 
#!/usr/bin/env python3
"""
Demo script for the RAG System
This script demonstrates how to use the RAG system with sample data
"""

import requests
import json
import time
from typing import Dict, Any

def demo_rag_system():
    """Demo the RAG system with sample data"""
    
    # API endpoint (assuming running locally)
    base_url = "http://localhost:8000"
    
    # Sample request data (using the exact format from the requirements)
    sample_request = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?",
            "What is the waiting period for cataract surgery?",
            "Are the medical expenses for an organ donor covered under this policy?",
            "What is the No Claim Discount (NCD) offered in this policy?",
            "Is there a benefit for preventive health check-ups?",
            "How does the policy define a 'Hospital'?",
            "What is the extent of coverage for AYUSH treatments?",
            "Are there any sub-limits on room rent and ICU charges for Plan A?"
        ]
    }
    
    # Headers with Bearer token
    headers = {
        "Authorization": "Bearer demo-api-key",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("🚀 RAG System Demo")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✓ Health check passed: {health_data['status']}")
            print(f"  Components: {json.dumps(health_data['components'], indent=2)}")
        else:
            print(f"✗ Health check failed: {health_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Health check error: {e}")
    
    # Test 2: Main RAG Endpoint
    print("\n2. Testing Main RAG Endpoint...")
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/hackrx/run",
            json=sample_request,
            headers=headers,
            timeout=60  # 60 seconds timeout
        )
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ RAG request successful! ({processing_time:.2f}s)")
            print(f"  Number of answers: {len(result['answers'])}")
            
            # Display answers
            for i, answer in enumerate(result['answers'], 1):
                print(f"\n  Q{i}: {sample_request['questions'][i-1]}")
                print(f"  A{i}: {answer[:200]}{'...' if len(answer) > 200 else ''}")
                
        else:
            print(f"✗ RAG request failed: {response.status_code}")
            print(f"  Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ RAG request error: {e}")
    
    print("\n" + "=" * 50)
    print("Demo completed!")

def demo_without_server():
    """Demo the RAG system components without running the server"""
    
    print("🔧 RAG System Component Demo")
    print("=" * 50)
    
    try:
        from rag_system.models.rag_system import RAGSystem
        from rag_system.utils.document_processor import DocumentProcessor
        
        # Test document processor
        print("\n1. Testing Document Processor...")
        processor = DocumentProcessor()
        
        # Test text chunking
        sample_text = "This is a sample insurance policy document. " * 100
        chunks = processor.chunk_text(sample_text, chunk_size=200, overlap=50)
        print(f"✓ Created {len(chunks)} text chunks")
        
        # Test RAG system initialization
        print("\n2. Testing RAG System Initialization...")
        rag_system = RAGSystem()
        status = rag_system.get_system_status()
        print(f"✓ RAG system initialized")
        print(f"  Vector store available: {status.get('vector_store_available', False)}")
        print(f"  LLM client available: {status.get('llm_client_available', False)}")
        print(f"  Document processor available: {status.get('document_processor_available', False)}")
        
        print("\n" + "=" * 50)
        print("Component demo completed!")
        
    except Exception as e:
        print(f"✗ Component demo error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--components":
        demo_without_server()
    else:
        demo_rag_system() 
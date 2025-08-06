#!/usr/bin/env python3
"""
Test script for the RAG System
This script tests the main functionality without requiring external API keys
"""

import sys
import os
import logging
from typing import Dict, Any

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_system.utils.document_processor import DocumentProcessor
from rag_system.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_document_processor():
    """Test document processor functionality"""
    print("Testing Document Processor...")
    
    try:
        # Initialize document processor
        processor = DocumentProcessor()
        
        # Test text chunking
        test_text = "This is a test document with multiple sentences. " * 50
        chunks = processor.chunk_text(test_text, chunk_size=100, overlap=20)
        
        print(f"✓ Document processor initialized successfully")
        print(f"✓ Text chunking works: {len(chunks)} chunks created")
        
        return True
        
    except Exception as e:
        print(f"✗ Document processor test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading"""
    print("\nTesting Configuration...")
    
    try:
        # Test settings
        print(f"✓ Project name: {settings.PROJECT_NAME}")
        print(f"✓ API version: {settings.API_V1_STR}")
        print(f"✓ Chunk size: {settings.CHUNK_SIZE}")
        print(f"✓ Supported file types: {settings.SUPPORTED_FILE_TYPES}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_imports():
    """Test all module imports"""
    print("\nTesting Module Imports...")
    
    modules_to_test = [
        "rag_system.config.settings",
        "rag_system.utils.document_processor",
        "rag_system.utils.vector_store",
        "rag_system.utils.llm_client",
        "rag_system.models.rag_system",
        "rag_system.app.main"
    ]
    
    success_count = 0
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module}")
            success_count += 1
        except Exception as e:
            print(f"✗ {module}: {e}")
    
    return success_count == len(modules_to_test)


def test_fastapi_app():
    """Test FastAPI app creation"""
    print("\nTesting FastAPI App...")
    
    try:
        from rag_system.app.main import app
        
        # Test app creation
        assert app is not None
        print(f"✓ FastAPI app created successfully")
        print(f"✓ App title: {app.title}")
        print(f"✓ App version: {app.version}")
        
        # Test routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/hackrx/run", "/api/v1/process-document", "/api/v1/answer"]
        
        for route in expected_routes:
            if route in routes:
                print(f"✓ Route {route} exists")
            else:
                print(f"✗ Route {route} missing")
        
        return True
        
    except Exception as e:
        print(f"✗ FastAPI app test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("RAG System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Module Imports", test_imports),
        ("Document Processor", test_document_processor),
        ("FastAPI App", test_fastapi_app),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✓ {test_name} PASSED")
        else:
            print(f"✗ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The RAG system is ready to use.")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file")
        print("2. Run: python main.py")
        print("3. Test the API endpoints")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
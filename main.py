#!/usr/bin/env python3
"""
Finance Chat Application - Main Entry Point
A FastAPI-based application for AI-powered finance document analysis.
"""

import uvicorn
import os
from dotenv import load_dotenv

def main():
    """Main entry point for the Finance Chat Application"""
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_env_vars = ["GROQ_API_KEY", "OPENAI_API_KEY"]
    has_api_key = any(os.getenv(var) for var in required_env_vars)
    
    if not has_api_key:
        print("⚠️  Warning: No API key found!")
        print("Please set either GROQ_API_KEY or OPENAI_API_KEY in your .env file")
        print("Example .env file:")
        print("GROQ_API_KEY=your_groq_api_key_here")
        print("# OR")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        return
    
    print("🚀 Starting Finance Chat Application...")
    print("📊 Features:")
    print("   • PDF Upload & Processing")
    print("   • AI-Powered Document Q&A")
    print("   • Document Summarization")
    print("   • Vector Storage with Qdrant")
    print()
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print()
    
    # Start the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()

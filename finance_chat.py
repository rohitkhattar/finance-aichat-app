#!/usr/bin/env python3
"""
Finance Chat Client
A simple client to interact with the Finance Chat API
"""

import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

class FinanceChatClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        
    def upload_pdf(self, file_path: str):
        """Upload a PDF file to the server"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                return None
                
            if not file_path.suffix.lower() == '.pdf':
                print("❌ Only PDF files are supported")
                return None
            
            print(f"📤 Uploading {file_path.name}...")
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/pdf')}
                response = requests.post(f"{self.base_url}/upload_pdf", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Upload successful!")
                print(f"   Collection: {result.get('collection_name')}")
                print(f"   Status: {result.get('status')}")
                return result.get('collection_name')
            else:
                print(f"❌ Upload failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed. Make sure the server is running at http://localhost:8000")
            return None
        except Exception as e:
            print(f"❌ Upload error: {str(e)}")
            return None
    
    def send_chat_message(self, collection_name: str, message: str):
        """Send a chat message to the finance chatbot"""
        try:
            print(f"💬 Asking: {message}")
            print("🤔 Processing...")
            
            params = {
                "collection_name": collection_name,
                "message": message
            }
            response = requests.post(f"{self.base_url}/fin_chat", params=params)

            if response.status_code == 200:
                result = response.json()
                print("✅ Response received!")
                print(f"🤖 Answer: {result.get('response', 'No response')}")
                return result
            else:
                print(f"❌ Chat failed with status {response.status_code}")
                error_msg = response.json().get('error', response.text) if response.headers.get('content-type') == 'application/json' else response.text
                print(f"   Error: {error_msg}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed. Make sure the server is running at http://localhost:8000")
            return None
        except Exception as e:
            print(f"❌ Chat error: {str(e)}")
            return None
    
    def list_collections(self):
        """List all available collections"""
        try:
            response = requests.get(f"{self.base_url}/collections")
            if response.status_code == 200:
                result = response.json()
                collections = result.get('collections', [])
                print(f"📚 Available collections ({len(collections)}):")
                for i, collection in enumerate(collections, 1):
                    print(f"   {i}. {collection}")
                return collections
            else:
                print(f"❌ Failed to list collections: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error listing collections: {str(e)}")
            return []
    
    def get_collection_info(self, collection_name: str):
        """Get information about a collection"""
        try:
            response = requests.get(f"{self.base_url}/collection/{collection_name}/info")
            if response.status_code == 200:
                result = response.json()
                print(f"📊 Collection Info: {collection_name}")
                print(f"   Vectors: {result.get('vectors_count', 0)}")
                print(f"   Indexed: {result.get('indexed_vectors_count', 0)}")
                return result
            else:
                print(f"❌ Collection not found: {collection_name}")
                return None
        except Exception as e:
            print(f"❌ Error getting collection info: {str(e)}")
            return None

def interactive_mode():
    """Interactive chat mode"""
    client = FinanceChatClient()
    
    print("🏦 Finance Chat Interactive Mode")
    print("=" * 40)
    
    # List available collections
    collections = client.list_collections()
    
    if not collections:
        print("\n📁 No collections found. Please upload a PDF first.")
        return
    
    # Select collection
    while True:
        try:
            choice = input(f"\nSelect collection (1-{len(collections)}) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                return
            
            idx = int(choice) - 1
            if 0 <= idx < len(collections):
                selected_collection = collections[idx]
                break
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Please enter a number")
    
    print(f"\n✅ Selected collection: {selected_collection}")
    client.get_collection_info(selected_collection)
    
    # Chat loop
    print("\n💬 Chat Mode (type 'quit' to exit, 'summary' for document summary)")
    print("-" * 50)
    
    while True:
        try:
            message = input("\n🗣️  You: ").strip()
            if message.lower() in ['quit', 'exit', 'q']:
                break
            if not message:
                continue
                
            client.send_chat_message(selected_collection, message)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Command line mode
        if sys.argv[1] == "upload" and len(sys.argv) > 2:
            client = FinanceChatClient()
            client.upload_pdf(sys.argv[2])
        elif sys.argv[1] == "chat" and len(sys.argv) > 3:
            client = FinanceChatClient()
            collection_name = sys.argv[2]
            message = " ".join(sys.argv[3:])
            client.send_chat_message(collection_name, message)
        elif sys.argv[1] == "list":
            client = FinanceChatClient()
            client.list_collections()
        else:
            print("Usage:")
            print("  python finance_chat.py upload <pdf_file>")
            print("  python finance_chat.py chat <collection_name> <message>")
            print("  python finance_chat.py list")
            print("  python finance_chat.py  # Interactive mode")
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()

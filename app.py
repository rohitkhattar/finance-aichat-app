import os
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import tempfile

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.tools import Tool
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_community.vectorstores import Qdrant
from pathlib import Path

app = FastAPI(title="Finance Chat Application", description="AI-powered finance document analysis")
load_dotenv()

# ----------------------------------------
# 🔧 Configuration
# ----------------------------------------

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
embedder = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

# Initialize Qdrant in-memory client
qdrant_client = QdrantClient(":memory:")

# Global storage for in-memory collections
in_memory_collections = {}

# ----------------------------------------
# 🧠 In-Memory Qdrant Functions
# ----------------------------------------

def create_or_refresh_store(collection_name: str, file_bytes: bytes, filename: str):
    """Create or refresh Qdrant in-memory store with new document"""
    try:
        # Save bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file_path = tmp_file.name

        # Load document using PyPDFLoader (more reliable)
        loader = PyPDFLoader(tmp_file_path)
        docs = loader.load()
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        # Split documents
        chunks = RecursiveCharacterTextSplitter(
            chunk_size=800, 
            chunk_overlap=200
        ).split_documents(docs)

        # Delete collection if it exists
        try:
            qdrant_client.delete_collection(collection_name=collection_name)
        except:
            pass  # Collection doesn't exist, which is fine

        # Create collection with proper vector configuration
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)  # BGE model dimension
        )

        # Create Qdrant vectorstore
        store = Qdrant(
            client=qdrant_client,
            collection_name=collection_name,
            embeddings=embedder
        )
        
        # Add documents to the store
        store.add_documents(chunks)
        
        # Store reference for later access
        in_memory_collections[collection_name] = {
            "store": store,
            "doc_count": len(chunks),
            "filename": filename
        }
        
        return store
        
    except Exception as e:
        raise Exception(f"Failed to create/refresh store: {str(e)}")

def load_qdrant_store(collection_name: str):
    """Load existing Qdrant in-memory collection"""
    try:
        if collection_name not in in_memory_collections:
            # Check if collection exists in client
            collections = [c.name for c in qdrant_client.get_collections().collections]
            if collection_name not in collections:
                raise ValueError(f"Collection '{collection_name}' not found. Available collections: {list(in_memory_collections.keys())}")
            
            # Recreate store reference if it exists in client but not in our dict
            store = Qdrant(
                client=qdrant_client,
                collection_name=collection_name,
                embeddings=embedder
            )
            in_memory_collections[collection_name] = {"store": store}
        
        return in_memory_collections[collection_name]["store"]
    except Exception as e:
        raise Exception(f"Failed to load in-memory collection: {str(e)}")

def list_collections():
    """List all available in-memory collections"""
    return list(in_memory_collections.keys())

def get_collection_info(collection_name: str):
    """Get information about a specific collection"""
    if collection_name not in in_memory_collections:
        return None
    
    collection_data = in_memory_collections[collection_name]
    try:
        # Get collection info from Qdrant client
        collection_info = qdrant_client.get_collection(collection_name)
        return {
            "collection_name": collection_name,
            "vectors_count": collection_info.vectors_count,
            "doc_count": collection_data.get("doc_count", 0),
            "filename": collection_data.get("filename", "unknown"),
            "status": "ready"
        }
    except:
        return {
            "collection_name": collection_name,
            "vectors_count": 0,
            "doc_count": collection_data.get("doc_count", 0),
            "filename": collection_data.get("filename", "unknown"),
            "status": "error"
        }

# ----------------------------------------
# 🛠️ Tools & LLM
# ----------------------------------------

def get_llm():
    """Get configured LLM (Groq or OpenAI)"""
    try:
        if os.getenv("GROQ_API_KEY"):
            return ChatGroq(model="llama3-8b-8192", groq_api_key=os.getenv("GROQ_API_KEY"))
        elif os.getenv("OPENAI_API_KEY"):
            return ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))
        else:
            raise ValueError("No API key found. Please set GROQ_API_KEY or OPENAI_API_KEY")
    except Exception as e:
        raise Exception(f"Failed to initialize LLM: {str(e)}")

def create_pdf_qa_tool(store, name="PDF_QA"):
    """Create PDF Q&A tool"""
    try:
        chain = RetrievalQA.from_chain_type(
            llm=get_llm(),
            retriever=store.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )
        
        def qa_func(query: str) -> str:
            try:
                result = chain.invoke({"query": query})
                return result.get("result", "No answer found")
            except Exception as e:
                return f"Error processing query: {str(e)}"
        
        return Tool(name=name, func=qa_func, description="Answer questions from the PDF document.")
    except Exception as e:
        raise Exception(f"Failed to create PDF QA tool: {str(e)}")

def create_summary_tool(store, name="PDF_Summary"):
    """Create PDF summary tool"""
    try:
        prompt = PromptTemplate.from_template(
            "Summarize the following financial document content in a clear and concise manner:\n\n{content}\n\nSummary:"
        )
        chain = LLMChain(llm=get_llm(), prompt=prompt)

        def summarize(query: str) -> str:
            try:
                # Get relevant documents for summary
                docs = store.as_retriever(search_kwargs={"k": 5}).get_relevant_documents("summary overview content")
                if not docs:
                    return "No content available for summary"
                
                full_text = "\n\n".join(d.page_content for d in docs[:3])  # Limit content
                result = chain.run({"content": full_text})
                return result
            except Exception as e:
                return f"Error generating summary: {str(e)}"

        return Tool(name=name, func=summarize, description="Generate a summary of the PDF document.")
    except Exception as e:
        raise Exception(f"Failed to create summary tool: {str(e)}")

# ----------------------------------------
# 🧠 Enhanced Agent
# ----------------------------------------

def build_agent(pdf_tool, summary_tool):
    """Build intelligent routing agent"""
    def agent_logic(message: str) -> str:
        try:
            message_lower = message.lower()
            
            # Route based on keywords
            summary_keywords = ["summary", "summarize", "overview", "general", "what is this about"]
            
            if any(keyword in message_lower for keyword in summary_keywords):
                return summary_tool.run(message)
            else:
                return pdf_tool.run(message)
                
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    return agent_logic

# ----------------------------------------
# 🚀 FastAPI Endpoints
# ----------------------------------------

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Finance Chat Application", 
        "status": "running",
        "storage_type": "Qdrant In-Memory",
        "collections_count": len(in_memory_collections),
        "endpoints": {
            "upload": "/upload_pdf",
            "chat": "/fin_chat",
            "collections": "/collections"
        }
    }

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload PDF and create vector store"""
    try:
        if not file.filename.endswith('.pdf'):
            return JSONResponse(status_code=400, content={"error": "Only PDF files are supported"})
        
        file_bytes = await file.read()
        collection_name = file.filename.replace(".pdf", "").lower().replace(" ", "_")
        
        # Create store
        store = create_or_refresh_store(collection_name, file_bytes, file.filename)
        
        return {
            "status": "success", 
            "message": "PDF uploaded and processed successfully",
            "collection_name": collection_name,
            "filename": file.filename,
            "storage_type": "Qdrant In-Memory",
            "doc_count": in_memory_collections[collection_name]["doc_count"]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Upload failed: {str(e)}"})

@app.post("/fin_chat")
async def fin_chat(collection_name: str = Query(..., description="Collection name"), 
                  message: str = Query(..., description="Chat message")):
    """Chat with the finance document"""
    try:
        # Load store
        store = load_qdrant_store(collection_name)
        
        # Create tools
        pdf_tool = create_pdf_qa_tool(store)
        summary_tool = create_summary_tool(store)
        
        # Build agent
        agent = build_agent(pdf_tool, summary_tool)
        
        # Get response
        response = agent(message)
        
        return {
            "status": "success",
            "collection_name": collection_name,
            "message": message,
            "response": response,
            "storage_type": "Qdrant In-Memory"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "error": str(e),
            "message": "Failed to process chat request"
        })

@app.get("/collections")
async def list_collections_endpoint():
    """List all available collections"""
    try:
        collections = list_collections()
        return {
            "status": "success",
            "collections": collections,
            "count": len(collections),
            "storage_type": "Qdrant In-Memory"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to list collections: {str(e)}"})

@app.get("/collection/{collection_name}/info")
def get_collection_info_endpoint(collection_name: str):
    """Get information about a specific collection"""
    try:
        info = get_collection_info(collection_name)
        if info is None:
            return JSONResponse(status_code=404, content={"error": f"Collection '{collection_name}' not found"})
        
        return {
            "status": "success",
            "storage_type": "Qdrant In-Memory",
            **info
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to get collection info: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
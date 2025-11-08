"""Optional Streamlit UI for the RAG system."""
import streamlit as st
import requests
import os
from datetime import datetime

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="RAG Document Q&A",
    page_icon="📚",
    layout="wide"
)

# Title
st.title("📚 RAG Document Q&A System")
st.markdown("Upload documents and ask questions to get AI-powered answers with source citations.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    top_k = st.slider("Number of sources", min_value=1, max_value=10, value=5)
    min_score = st.slider("Minimum similarity", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
    
    st.divider()
    
    st.header("📊 System Stats")
    try:
        response = requests.get(f"{API_URL}/api/v1/admin/stats")
        if response.status_code == 200:
            stats = response.json()
            st.metric("Documents", stats["total_documents"])
            st.metric("Chunks", stats["total_chunks"])
            st.metric("Queries", stats["total_queries"])
        else:
            st.error("Failed to load stats")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Tabs
tab1, tab2, tab3 = st.tabs(["💬 Ask Questions", "📤 Upload Documents", "📜 History"])

# Tab 1: Ask Questions
with tab1:
    st.header("Ask a Question")
    
    query = st.text_area(
        "Enter your question:",
        placeholder="What are the main findings in the document?",
        height=100
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        ask_button = st.button("🔍 Ask", type="primary")
    
    if ask_button and query:
        with st.spinner("Searching and generating answer..."):
            try:
                response = requests.post(
                    f"{API_URL}/api/v1/query",
                    json={
                        "query": query,
                        "top_k": top_k,
                        "min_score": min_score,
                        "include_sources": True
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Display answer
                    st.success("Answer:")
                    st.markdown(f"**{data['answer']}**")
                    
                    # Display metadata
                    st.caption(f"⏱️ Processing time: {data['processing_time']:.2f}s | "
                             f"📄 Retrieved: {data['retrieved_count']} chunks")
                    
                    # Display sources
                    if data['sources']:
                        st.divider()
                        st.subheader("📑 Sources")
                        
                        for i, source in enumerate(data['sources'], 1):
                            with st.expander(
                                f"Source {i}: {source['document']} "
                                f"(Score: {source['score']:.3f})"
                            ):
                                st.text(source['chunk_text'])
                                st.caption(
                                    f"Chunk #{source['chunk_index']} | "
                                    f"Chars: {source['start_char']}-{source['end_char']}"
                                )
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Request failed: {str(e)}")

# Tab 2: Upload Documents
with tab2:
    st.header("Upload Documents")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'doc', 'txt', 'md'],
        help="Supported formats: PDF, DOCX, TXT, MD"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([1, 5])
        with col1:
            upload_button = st.button("📤 Upload", type="primary")
        
        if upload_button:
            with st.spinner("Uploading and processing document..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    response = requests.post(f"{API_URL}/api/v1/upload", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ {data['message']}")
                        st.json(data)
                    else:
                        st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")
    
    # List documents
    st.divider()
    st.subheader("📚 Uploaded Documents")
    
    try:
        response = requests.get(f"{API_URL}/api/v1/documents")
        if response.status_code == 200:
            data = response.json()
            
            if data['documents']:
                for doc in data['documents']:
                    with st.expander(f"📄 {doc['filename']} ({doc['status']})"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Type:** {doc['file_type']}")
                            st.write(f"**Size:** {doc['file_size']} bytes")
                            st.write(f"**Chunks:** {doc['total_chunks']}")
                            st.write(f"**Uploaded:** {doc['upload_date']}")
                        
                        with col2:
                            if st.button("🗑️ Delete", key=f"del_{doc['id']}"):
                                try:
                                    del_response = requests.delete(
                                        f"{API_URL}/api/v1/documents/{doc['id']}"
                                    )
                                    if del_response.status_code == 200:
                                        st.success("Deleted!")
                                        st.rerun()
                                    else:
                                        st.error("Delete failed")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
            else:
                st.info("No documents uploaded yet")
        else:
            st.error("Failed to load documents")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Tab 3: History
with tab3:
    st.header("Query History")
    
    try:
        response = requests.get(f"{API_URL}/api/v1/queries?limit=20")
        if response.status_code == 200:
            data = response.json()
            
            if data['queries']:
                for query in data['queries']:
                    with st.expander(
                        f"❓ {query['query_text'][:80]}... | "
                        f"{query['timestamp']}"
                    ):
                        st.write(f"**Query:** {query['query_text']}")
                        if query['response']:
                            st.write(f"**Answer:** {query['response']}")
                        if query['processing_time']:
                            st.caption(f"⏱️ {query['processing_time']:.2f}s")
            else:
                st.info("No queries yet")
        else:
            st.error("Failed to load history")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Footer
st.divider()
st.caption("Built with ❤️ using FastAPI, FAISS, and Streamlit")

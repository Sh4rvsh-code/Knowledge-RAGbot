"""
Streamlit RAG Bot - Standalone deployment version
This app integrates the RAG system directly without requiring a separate FastAPI backend.
"""
import streamlit as st
import os
import sys
from pathlib import Path
import tempfile
from datetime import datetime
import traceback

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import RAG components
try:
    from app.config import Settings
    from app.core.ingestion.extractors import ExtractorFactory
    from app.core.ingestion.chunker import RecursiveChunker
    from app.core.ingestion.embedder import get_embedder
    from app.core.ingestion.indexer import get_index_manager
    from app.core.retrieval.retriever import SemanticRetriever
    from app.core.llm.orchestrator import LLMOrchestrator
    from app.core.llm.remote_llm import get_llm
    from app.models.database import DatabaseManager, Document, Chunk
    from sqlalchemy.orm import Session
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title="RAG Document Q&A Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.settings = None
    st.session_state.db_manager = None
    st.session_state.embedder = None
    st.session_state.index_manager = None
    st.session_state.retriever = None
    st.session_state.orchestrator = None
    st.session_state.query_history = []

def initialize_system():
    """Initialize the RAG system components."""
    try:
        # Load settings (use st.secrets if available, otherwise env vars)
        if hasattr(st, 'secrets') and len(st.secrets) > 0:
            # Override settings with Streamlit secrets
            os.environ['LLM_PROVIDER'] = st.secrets.get('LLM_PROVIDER', 'gemini')
            os.environ['GEMINI_API_KEY'] = st.secrets.get('GEMINI_API_KEY', '')
            os.environ['GEMINI_MODEL'] = st.secrets.get('GEMINI_MODEL', 'gemini-1.5-flash')
            os.environ['DATABASE_URL'] = st.secrets.get('DATABASE_URL', 'sqlite:///./data/rag.db')
            os.environ['EMBEDDING_MODEL'] = st.secrets.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            os.environ['CHUNK_SIZE'] = str(st.secrets.get('CHUNK_SIZE', '512'))
            os.environ['CHUNK_OVERLAP'] = str(st.secrets.get('CHUNK_OVERLAP', '50'))
            os.environ['TOP_K_RESULTS'] = str(st.secrets.get('TOP_K_RESULTS', '5'))
            os.environ['SIMILARITY_THRESHOLD'] = str(st.secrets.get('SIMILARITY_THRESHOLD', '0.7'))
        
        settings = Settings()
        
        # Create necessary directories
        os.makedirs(settings.upload_dir, exist_ok=True)
        os.makedirs(settings.data_dir, exist_ok=True)
        os.makedirs(settings.index_dir, exist_ok=True)
        
        # Initialize database
        db_manager = DatabaseManager(settings.database_url)
        db_manager.create_tables()
        
        # Initialize embedder
        embedder = get_embedder()
        
        # Initialize index manager (384 dimensions for all-MiniLM-L6-v2)
        index_manager = get_index_manager(dimension=384)
        
        # Initialize retriever (it will use global embedder, index_manager, db_manager)
        retriever = SemanticRetriever(
            top_k=settings.top_k_results,
            similarity_threshold=settings.similarity_threshold
        )
        
        # Initialize LLM
        llm = get_llm()
        orchestrator = LLMOrchestrator(llm)
        
        return {
            'settings': settings,
            'db_manager': db_manager,
            'embedder': embedder,
            'index_manager': index_manager,
            'retriever': retriever,
            'orchestrator': orchestrator
        }
    except Exception as e:
        st.error(f"Failed to initialize system: {e}")
        st.error(traceback.format_exc())
        return None

def process_document(uploaded_file, components):
    """Process an uploaded document."""
    try:
        settings = components['settings']
        db_manager = components['db_manager']
        embedder = components['embedder']
        index_manager = components['index_manager']
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name
        
        # Extract text using ExtractorFactory instance
        extractor_factory = ExtractorFactory()
        extractor = extractor_factory.get_extractor(tmp_path)
        extraction_result = extractor.extract(tmp_path)
        
        # Generate a temporary doc_id (will be replaced with actual DB id)
        import uuid
        temp_doc_id = str(uuid.uuid4())
        
        # Chunk text
        chunker = RecursiveChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        chunks = chunker.chunk(
            text=extraction_result.text,
            doc_id=temp_doc_id,
            metadata=extraction_result.metadata
        )
        
        # Generate embeddings
        embeddings = embedder.embed_chunks([c.chunk_text for c in chunks])
        st.info(f"✅ Generated {len(embeddings)} embeddings")
        
        # Prepare metadata for FAISS
        metadata_list = [
            {
                'doc_id': temp_doc_id,
                'chunk_index': i,
                'chunk_text': chunk.chunk_text[:200],  # Store preview
                'start_char': chunk.start_char,
                'end_char': chunk.end_char,
                **chunk.metadata
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Add to FAISS index
        faiss_ids = index_manager.add_vectors(embeddings, metadata_list)
        st.info(f"✅ Added {len(faiss_ids)} vectors to FAISS index")
        
        # Save to database
        import json
        st.info("💾 Saving to database...")
        with db_manager.get_session() as session:
            doc = Document(
                id=temp_doc_id,  # Use the UUID we generated earlier
                filename=uploaded_file.name,
                file_type=Path(uploaded_file.name).suffix[1:],
                file_size=uploaded_file.size,
                status='completed',
                total_chunks=len(chunks),
                doc_metadata=json.dumps(extraction_result.metadata)
            )
            session.add(doc)
            session.flush()
            
            # Add chunks
            for i, (chunk, faiss_id) in enumerate(zip(chunks, faiss_ids)):
                db_chunk = Chunk(
                    doc_id=doc.id,
                    chunk_index=i,
                    chunk_text=chunk.chunk_text,
                    start_char=chunk.start_char,
                    end_char=chunk.end_char,
                    faiss_id=faiss_id,
                    chunk_metadata=json.dumps(chunk.metadata)
                )
                session.add(db_chunk)
            
            session.commit()
            st.info(f"✅ Saved document and {len(chunks)} chunks to database")
            
            # Store doc_id before session closes
            doc_id = doc.id
        
        # Save index
        index_manager.save_index()
        st.info("✅ FAISS index saved to disk")
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return {
            'success': True,
            'doc_id': doc_id,
            'filename': uploaded_file.name,
            'chunks': len(chunks)
        }
    
    except Exception as e:
        st.error(f"❌ Error processing document: {e}")
        st.error(f"**Traceback:**")
        st.code(traceback.format_exc())
        return {'success': False, 'error': str(e)}

def answer_question(query, top_k, min_score, components):
    """Answer a question using RAG."""
    try:
        retriever = components['retriever']
        orchestrator = components['orchestrator']
        index_manager = components['index_manager']
        
        # Check if index has vectors
        if not index_manager.index or index_manager.index.ntotal == 0:
            return {
                'success': False,
                'error': 'No documents in the index. Please upload documents first.',
                'sources': [],
                'retrieved_count': 0
            }
        
        # Retrieve relevant chunks
        start_time = datetime.now()
        results = retriever.search(query, top_k=top_k, min_score=min_score)
        
        # If no results found, provide helpful message
        if len(results) == 0:
            return {
                'success': False,
                'error': f'No relevant chunks found with similarity >= {min_score:.2f}. Try lowering the threshold.',
                'sources': [],
                'retrieved_count': 0,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
        
        # Generate answer (pass results directly, orchestrator will build context)
        answer = orchestrator.answer_question(query, results)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': True,
            'answer': answer,
            'sources': results,
            'processing_time': processing_time,
            'retrieved_count': len(results)
        }
    
    except Exception as e:
        st.error(f"Error answering question: {e}")
        st.error(traceback.format_exc())
        return {'success': False, 'error': str(e)}

def get_documents(components):
    """Get all documents from database."""
    try:
        db_manager = components['db_manager']
        with db_manager.get_session() as session:
            docs = session.query(Document).order_by(Document.upload_date.desc()).all()
            return [
                {
                    'id': doc.id,
                    'filename': doc.filename,
                    'file_type': doc.file_type,
                    'file_size': doc.file_size,
                    'upload_date': doc.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': doc.status,
                    'total_chunks': doc.total_chunks
                }
                for doc in docs
            ]
    except Exception as e:
        st.error(f"Error fetching documents: {e}")
        return []

def delete_document(doc_id, components):
    """Delete a document and its chunks."""
    try:
        db_manager = components['db_manager']
        index_manager = components['index_manager']
        
        with db_manager.get_session() as session:
            # Get chunks to remove from index
            doc = session.query(Document).filter(Document.id == doc_id).first()
            if doc:
                chunks = session.query(Chunk).filter(Chunk.doc_id == doc_id).all()
                faiss_ids = [c.faiss_id for c in chunks]
                
                # Delete from database (use doc_id, not document_id)
                session.query(Chunk).filter(Chunk.doc_id == doc_id).delete()
                session.query(Document).filter(Document.id == doc_id).delete()
                session.commit()
                
                # Rebuild index without these chunks
                index_manager.delete_by_doc_id(doc_id)
                index_manager.save_index()
                
                return True
        return False
    except Exception as e:
        st.error(f"Error deleting document: {e}")
        return False

# Main App
def main():
    # Header
    st.title("🤖 RAG Document Q&A Bot")
    st.markdown("Upload documents and ask questions to get AI-powered answers with source citations.")
    
    # Initialize system
    if not st.session_state.initialized:
        with st.spinner("🚀 Initializing RAG system..."):
            components = initialize_system()
            if components:
                st.session_state.components = components
                st.session_state.initialized = True
                st.success("✅ System initialized successfully!")
            else:
                st.error("❌ Failed to initialize system. Please check your configuration.")
                st.stop()
    
    components = st.session_state.components
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key input (if not set in env)
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            st.warning("⚠️ No API key detected!")
            api_provider = st.selectbox("LLM Provider", ["OpenAI", "Anthropic"])
            api_key = st.text_input("API Key", type="password")
            
            if api_key:
                if api_provider == "OpenAI":
                    os.environ["OPENAI_API_KEY"] = api_key
                else:
                    os.environ["ANTHROPIC_API_KEY"] = api_key
                st.success("✅ API key set!")
        
        top_k = st.slider("Number of sources", min_value=1, max_value=10, value=5)
        min_score = st.slider("Minimum similarity", min_value=0.0, max_value=1.0, value=0.3, step=0.05, 
                             help="Lower threshold = more results. Try 0.3 for better retrieval.")
        
        st.divider()
        
        st.header("📊 System Stats")
        docs = get_documents(components)
        total_chunks = sum(d['total_chunks'] for d in docs)
        
        # Get FAISS stats
        index_manager = components['index_manager']
        faiss_count = index_manager.index.ntotal if index_manager.index else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Documents", len(docs))
            st.metric("Chunks in DB", total_chunks)
        with col2:
            st.metric("Vectors in FAISS", faiss_count)
            st.metric("Queries", len(st.session_state.query_history))
        
        # Warning if mismatch
        if total_chunks > 0 and faiss_count == 0:
            st.warning("⚠️ Chunks in DB but no vectors in FAISS! Try re-uploading documents.")
        elif total_chunks != faiss_count:
            st.info(f"ℹ️ DB chunks ({total_chunks}) ≠ FAISS vectors ({faiss_count})")
        
        st.divider()
        
        if st.button("🔄 Refresh Stats"):
            st.rerun()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 Ask Questions", "📤 Upload Documents", "📜 History"])
    
    # Tab 1: Ask Questions
    with tab1:
        st.header("Ask a Question")
        
        # Check if documents are available
        docs = get_documents(components)
        if not docs:
            st.warning("⚠️ No documents uploaded yet! Please upload documents first.")
        
        query = st.text_area(
            "Enter your question:",
            placeholder="What are the main findings in the document?",
            height=100
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            ask_button = st.button("🔍 Ask", type="primary", disabled=not docs)
        
        if ask_button and query:
            with st.spinner("🔍 Searching and generating answer..."):
                result = answer_question(query, top_k, min_score, components)
                
                if result['success']:
                    # Store in history
                    st.session_state.query_history.append({
                        'query': query,
                        'answer': result['answer'],
                        'timestamp': datetime.now(),
                        'processing_time': result['processing_time']
                    })
                    
                    # Display answer
                    st.success("Answer:")
                    st.markdown(f"**{result['answer']}**")
                    
                    # Display metadata
                    st.caption(f"⏱️ Processing time: {result['processing_time']:.2f}s | "
                             f"📄 Retrieved: {result['retrieved_count']} chunks")
                    
                    # Display sources
                    if result['sources']:
                        st.divider()
                        st.subheader("📑 Sources")
                        
                        for i, source in enumerate(result['sources'], 1):
                            with st.expander(
                                f"Source {i}: {source.get('filename', 'Unknown')} "
                                f"(Score: {source.get('score', 0):.3f})"
                            ):
                                st.text(source.get('chunk_text', 'No text available'))
                                st.caption(
                                    f"Chunk #{source.get('chunk_index', 0)} | "
                                    f"Chars: {source.get('start_char', 0)}-{source.get('end_char', 0)}"
                                )
                else:
                    # Display error message
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                    if result.get('retrieved_count', 0) == 0:
                        st.info(f"💡 Tip: Try lowering the similarity threshold below {min_score:.2f} using the slider in the sidebar.")
    
    # Tab 2: Upload Documents
    with tab2:
        st.header("Upload Documents")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'doc', 'txt', 'md'],
            help="Supported formats: PDF, DOCX, TXT, MD (Max 50MB)"
        )
        
        if uploaded_file:
            st.info(f"📄 Selected: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
            
            col1, col2 = st.columns([1, 5])
            with col1:
                upload_button = st.button("📤 Upload", type="primary")
            
            if upload_button:
                with st.spinner("📤 Uploading and processing document..."):
                    result = process_document(uploaded_file, components)
                    
                    if result['success']:
                        st.success(f"✅ Successfully processed {result['filename']} ({result['chunks']} chunks)")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to process document: {result.get('error', 'Unknown error')}")
        
        # List documents
        st.divider()
        st.subheader("📚 Uploaded Documents")
        
        docs = get_documents(components)
        
        if docs:
            for doc in docs:
                with st.expander(f"📄 {doc['filename']} ({doc['status']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Type:** {doc['file_type']}")
                        st.write(f"**Size:** {doc['file_size'] / 1024:.1f} KB")
                        st.write(f"**Chunks:** {doc['total_chunks']}")
                        st.write(f"**Uploaded:** {doc['upload_date']}")
                    
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{doc['id']}"):
                            if delete_document(doc['id'], components):
                                st.success("Deleted!")
                                st.rerun()
                            else:
                                st.error("Delete failed")
        else:
            st.info("No documents uploaded yet")
    
    # Tab 3: History
    with tab3:
        st.header("Query History")
        
        if st.session_state.query_history:
            for i, item in enumerate(reversed(st.session_state.query_history), 1):
                with st.expander(
                    f"❓ {item['query'][:80]}... | "
                    f"{item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
                ):
                    st.write(f"**Query:** {item['query']}")
                    st.write(f"**Answer:** {item['answer']}")
                    st.caption(f"⏱️ {item['processing_time']:.2f}s")
        else:
            st.info("No queries yet")
    
    # Footer
    st.divider()
    st.caption("Built with ❤️ using FastAPI, FAISS, Sentence Transformers, and Streamlit")

if __name__ == "__main__":
    main()

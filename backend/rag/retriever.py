"""
RAG Retriever with ChromaDB for domain-specific content retrieval.
Provides semantic search over pre-loaded reference documents.
"""

from typing import Optional, List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
import uuid
from datetime import datetime

from config import settings
from models.schemas import RAGResult
from services.llm import get_llm_service


class RAGRetriever:
    """
    RAG Retriever for domain-specific content retrieval.
    
    Uses ChromaDB to store and retrieve reference documents
    that provide context for storyboard generation.
    """
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None
    ):
        """
        Initialize the RAG Retriever.
        
        Args:
            persist_directory: ChromaDB persistence directory
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = persist_directory or settings.chromadb_persist_dir
        self.collection_name = collection_name or settings.chromadb_rag_collection
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self._llm_service = None
        self._initialized = False
    
    @property
    def llm_service(self):
        """Lazy load LLM service."""
        if self._llm_service is None:
            self._llm_service = get_llm_service()
        return self._llm_service
    
    async def initialize_domain_content(self) -> None:
        """
        Initialize the RAG collection with domain-specific reference content.
        This should be called once during application startup.
        """
        if self._initialized:
            return
        
        # Check if collection already has documents
        count = self.collection.count()
        if count > 0:
            self._initialized = True
            return
        
        # Domain-specific reference content
        domain_content = self._get_domain_reference_content()
        
        for domain, documents in domain_content.items():
            for doc in documents:
                await self.add_document(
                    content=doc["content"],
                    domain=domain,
                    source=doc.get("source", f"{domain}_reference"),
                    metadata=doc.get("metadata", {})
                )
        
        self._initialized = True
    
    def _get_domain_reference_content(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get pre-defined domain reference content."""
        return {
            "product_demo": [
                {
                    "content": "Product demos should open with the problem statement, then introduce the solution. Use close-up shots for UI details and wide shots for context. Maintain a professional yet approachable tone.",
                    "source": "product_demo_guide",
                    "metadata": {"category": "structure"}
                },
                {
                    "content": "Effective product demos use the AIDA framework: Attention (hook), Interest (problem), Desire (solution benefits), Action (call to action). Each scene should flow naturally to the next.",
                    "source": "marketing_framework",
                    "metadata": {"category": "framework"}
                },
                {
                    "content": "For software demos, use screen recordings with smooth transitions. Highlight key features with subtle animations or callouts. Keep scenes under 10 seconds for engagement.",
                    "source": "software_demo_tips",
                    "metadata": {"category": "technical"}
                }
            ],
            "education": [
                {
                    "content": "Educational content should follow the 'Tell-Show-Do' methodology. First explain the concept, then demonstrate it visually, finally show practical application.",
                    "source": "education_methodology",
                    "metadata": {"category": "pedagogy"}
                },
                {
                    "content": "Use visual metaphors and analogies to explain complex concepts. Break information into digestible chunks. Include recap scenes every 3-4 scenes.",
                    "source": "instructional_design",
                    "metadata": {"category": "design"}
                },
                {
                    "content": "Educational videos benefit from consistent visual language: same colors for same concepts, recurring characters or icons, and clear visual hierarchy.",
                    "source": "visual_learning",
                    "metadata": {"category": "visual"}
                }
            ],
            "medical": [
                {
                    "content": "Medical content requires accuracy and sensitivity. Use anatomically correct visualizations. Include disclaimers where appropriate. Avoid graphic content unless necessary.",
                    "source": "medical_guidelines",
                    "metadata": {"category": "compliance"}
                },
                {
                    "content": "Patient education videos should use simple language (6th-grade reading level). Show procedures step-by-step. Include recovery expectations and when to seek help.",
                    "source": "patient_education",
                    "metadata": {"category": "communication"}
                },
                {
                    "content": "Healthcare marketing must balance professionalism with empathy. Show diverse patients. Focus on outcomes and quality of life improvements.",
                    "source": "healthcare_marketing",
                    "metadata": {"category": "marketing"}
                }
            ],
            "marketing": [
                {
                    "content": "Marketing storyboards should establish brand identity in the first 3 seconds. Use consistent color palette and typography. Create emotional connection before presenting product.",
                    "source": "brand_guidelines",
                    "metadata": {"category": "branding"}
                },
                {
                    "content": "Effective marketing videos use storytelling: relatable protagonist, conflict/problem, resolution through product/service, transformation/success.",
                    "source": "storytelling_marketing",
                    "metadata": {"category": "narrative"}
                },
                {
                    "content": "Social media marketing requires vertical formats (9:16), bold text overlays, and hooks in the first 2 seconds. Optimize for sound-off viewing.",
                    "source": "social_media_guide",
                    "metadata": {"category": "platform"}
                }
            ],
            "film_style": [
                {
                    "content": "Cinematic storytelling uses the three-act structure: Setup (25%), Confrontation (50%), Resolution (25%). Each act has specific pacing and emotional beats.",
                    "source": "screenplay_structure",
                    "metadata": {"category": "structure"}
                },
                {
                    "content": "Camera movements convey emotion: dolly in for intensity, dolly out for isolation, tracking shots for journey, static shots for stability or tension.",
                    "source": "cinematography_guide",
                    "metadata": {"category": "camera"}
                },
                {
                    "content": "Lighting creates mood: high-key for comedy/romance, low-key for drama/thriller, motivated lighting for realism, stylized for artistic effect.",
                    "source": "lighting_guide",
                    "metadata": {"category": "lighting"}
                }
            ],
            "gaming": [
                {
                    "content": "Game trailers should showcase gameplay variety, key mechanics, and progression systems. Use fast cuts for action, slower pacing for story beats.",
                    "source": "game_trailer_guide",
                    "metadata": {"category": "trailer"}
                },
                {
                    "content": "Gaming content benefits from dynamic camera angles: over-shoulder for immersion, wide shots for scale, dramatic angles for boss encounters.",
                    "source": "game_cinematics",
                    "metadata": {"category": "camera"}
                },
                {
                    "content": "Game storyboards should indicate interactivity: UI elements, player choices, branching paths. Use consistent iconography for player actions.",
                    "source": "interactive_design",
                    "metadata": {"category": "interactivity"}
                }
            ]
        }
    
    async def add_document(
        self,
        content: str,
        domain: str,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a document to the RAG collection.
        
        Args:
            content: Document content
            domain: Domain category
            source: Source URL or reference
            metadata: Additional metadata
            
        Returns:
            str: Document ID
        """
        doc_id = str(uuid.uuid4())
        
        # Get embedding
        embedding = await self.llm_service.get_embedding(content)
        
        # Prepare metadata
        doc_metadata = {
            "domain": domain,
            "source": source or "unknown",
            "created_at": datetime.utcnow().isoformat(),
            **(metadata or {})
        }
        
        # Add to ChromaDB
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding] if embedding else None,
            documents=[content],
            metadatas=[doc_metadata]
        )
        
        return doc_id
    
    async def search(
        self,
        query: str,
        domain: Optional[str] = None,
        n_results: int = 5
    ) -> List[RAGResult]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            domain: Optional domain filter
            n_results: Number of results to return
            
        Returns:
            List[RAGResult]: Matching documents with relevance scores
        """
        # Build where clause
        where_clause = None
        if domain:
            where_clause = {"domain": domain}
        
        # Get query embedding
        query_embedding = await self.llm_service.get_embedding(query)
        
        if not query_embedding:
            # Fall back to text search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )
        else:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause
            )
        
        # Convert to RAGResult objects
        rag_results = []
        if results and results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                content = results['documents'][0][i] if results['documents'] else ""
                distance = results['distances'][0][i] if results.get('distances') else 0
                
                # Convert distance to relevance score
                relevance_score = 1 - distance if distance else 1.0
                
                rag_results.append(RAGResult(
                    content=content,
                    source=metadata.get('source'),
                    relevance_score=relevance_score,
                    metadata=metadata
                ))
        
        return rag_results
    
    async def search_with_context(
        self,
        query: str,
        domain: str,
        context: str,
        n_results: int = 3
    ) -> List[RAGResult]:
        """
        Search with additional context for better results.
        
        Args:
            query: Search query
            domain: Domain filter
            context: Additional context to enhance search
            n_results: Number of results
            
        Returns:
            List[RAGResult]: Matching documents
        """
        # Combine query with context for better semantic matching
        enhanced_query = f"{query}\n\nContext: {context}"
        return await self.search(enhanced_query, domain, n_results)
    
    async def get_domain_documents(self, domain: str) -> List[RAGResult]:
        """
        Get all documents for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List[RAGResult]: All domain documents
        """
        results = self.collection.get(
            where={"domain": domain}
        )
        
        rag_results = []
        if results and results['ids']:
            for i, doc_id in enumerate(results['ids']):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                content = results['documents'][i] if results['documents'] else ""
                
                rag_results.append(RAGResult(
                    content=content,
                    source=metadata.get('source'),
                    relevance_score=1.0,
                    metadata=metadata
                ))
        
        return rag_results
    
    def get_document_count(self, domain: Optional[str] = None) -> int:
        """
        Get the number of documents in the collection.
        
        Args:
            domain: Optional domain filter
            
        Returns:
            int: Document count
        """
        if domain:
            results = self.collection.get(where={"domain": domain})
            return len(results['ids']) if results and results['ids'] else 0
        return self.collection.count()


# Singleton instance
_rag_service: Optional[RAGRetriever] = None


def get_rag_service() -> RAGRetriever:
    """
    Get the RAG service singleton instance.
    
    Returns:
        RAGRetriever: The RAG service instance
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGRetriever()
    return _rag_service


"""
Direct chat service for normal (non-multi-agent) responses.
Provides simple LLM-based chat without agent orchestration.
Can auto-detect domain from user query for context-aware responses.
"""

from typing import AsyncGenerator, Optional, Dict, Any
from services.llm import get_llm_service


# Domain detection patterns (imported logic from PreAct)
DOMAIN_PATTERNS = {
    "healthcare": ["medical", "health", "clinical", "patient", "hospital", "doctor", "nurse", "diagnosis", "treatment", "pharma", "drug"],
    "finance": ["finance", "banking", "investment", "stock", "trading", "loan", "credit", "insurance", "accounting", "budget", "revenue"],
    "hr": ["hr", "human resources", "employee", "hiring", "recruitment", "onboarding", "payroll", "benefits", "performance review", "talent"],
    "cloud": ["cloud", "aws", "azure", "gcp", "kubernetes", "docker", "devops", "infrastructure", "serverless", "microservices"],
    "software": ["software", "development", "programming", "code", "api", "database", "testing", "agile", "scrum", "deployment"],
    "sales": ["sales", "crm", "lead", "pipeline", "prospect", "deal", "quota", "revenue", "customer", "conversion"],
    "education": ["education", "learning", "teaching", "course", "curriculum", "student", "training", "tutorial", "lesson", "classroom"],
    "marketing": ["marketing", "campaign", "brand", "advertising", "social media", "seo", "content", "promotion", "audience", "engagement"],
    "legal": ["legal", "law", "contract", "compliance", "regulation", "litigation", "attorney", "court", "rights", "policy"],
    "manufacturing": ["manufacturing", "production", "factory", "assembly", "quality control", "supply chain", "inventory", "lean", "six sigma"],
}


class DirectChatService:
    """
    Direct chat service for normal chatbot responses.
    
    This provides a simpler alternative to the multi-agent pipeline,
    generating responses in a single LLM call without the
    preAct → ReAct → ReFlect orchestration.
    
    Features:
    - Auto-detect domain from user query
    - Context-aware responses based on detected domain
    - Normal chatbot mode (no storyboard generation by default)
    """
    
    SYSTEM_PROMPT = """You are ThinkerLLM, an intelligent AI assistant.

You help users with their questions by:
1. Understanding their request clearly
2. Providing accurate, helpful responses
3. Being conversational and helpful
4. Using markdown formatting for code blocks, lists, and headers

Be helpful, accurate, and conversational. Respond naturally like a knowledgeable assistant.
Do NOT format responses as storyboards or structured product demos unless explicitly asked.
Just answer the user's question directly and helpfully."""
    
    STORYBOARD_SYSTEM_PROMPT = """You are a professional storyboard creator. Generate detailed, production-ready storyboards ONLY when the user explicitly asks for a storyboard.

Your storyboards should include:
1. A compelling title
2. Overall visual style and tone
3. Detailed scene breakdowns with:
   - Scene number and title
   - Visual description
   - Camera directions
   - Dialogue (if applicable)
   - Sound/music notes
   - Duration estimate

Be creative, specific, and professional."""

    def __init__(self):
        """Initialize the direct chat service."""
        self._llm = None
    
    @property
    def llm(self):
        """Lazy load LLM service."""
        if self._llm is None:
            self._llm = get_llm_service()
        return self._llm
    
    def detect_domain(self, query: str) -> str:
        """
        Auto-detect domain from user query.
        
        Args:
            query: User query
            
        Returns:
            str: Detected domain or 'general'
        """
        query_lower = query.lower()
        domain_scores = {}
        
        for domain, keywords in DOMAIN_PATTERNS.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        
        return "general"
    
    def is_storyboard_request(self, query: str) -> bool:
        """
        Check if the user is asking for a storyboard.
        
        Args:
            query: User query
            
        Returns:
            bool: True if storyboard is requested
        """
        storyboard_keywords = [
            "storyboard", "video script", "scene breakdown", 
            "create scenes", "video production", "animation script",
            "visual story", "scene by scene"
        ]
        query_lower = query.lower()
        return any(kw in query_lower for kw in storyboard_keywords)
    
    def build_prompt(self, query: str, domain: Optional[str] = None, mode: str = "chat") -> str:
        """
        Build the prompt for direct chat or storyboard generation.
        
        Args:
            query: User query
            domain: Domain type (optional, will auto-detect if not provided)
            mode: "chat" for normal chat, "storyboard" for storyboard generation
            
        Returns:
            str: Formatted prompt
        """
        # Auto-detect domain if not provided
        if not domain or domain == "auto":
            domain = self.detect_domain(query)
        
        if mode == "storyboard":
            return self._build_storyboard_prompt(domain, query)
        else:
            return self._build_chat_prompt(domain, query)
    
    def _build_chat_prompt(self, domain: str, query: str) -> str:
        """Build prompt for normal chat mode - simple and direct."""
        return f"""{query}

---
Respond naturally and helpfully. Use markdown formatting for code blocks and structure if needed."""
    
    def _build_storyboard_prompt(self, domain: str, query: str) -> str:
        """Build prompt for storyboard generation mode - only when explicitly requested."""
        return f"""## STORYBOARD REQUEST

**User Request:** {query}

## YOUR TASK

Generate a complete storyboard with 5-7 scenes. For each scene include:
- Scene number and title
- Detailed visual description (2-3 sentences)
- Camera direction
- Dialogue (if any)
- Sound/music notes
- Estimated duration in seconds

Format your response as a well-structured storyboard document."""
    
    async def generate(
        self,
        query: str,
        domain: Optional[str] = None,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Generate a response using direct LLM call.
        Auto-detects domain and mode (chat vs storyboard).
        
        Args:
            query: User query
            domain: Domain type (optional, will auto-detect)
            stream: Whether to stream the response
            
        Yields:
            str: Response chunks
        """
        # Auto-detect domain if not provided
        detected_domain = domain if domain and domain != "auto" else self.detect_domain(query)
        
        # Determine mode based on query
        mode = "storyboard" if self.is_storyboard_request(query) else "chat"
        system_prompt = self.STORYBOARD_SYSTEM_PROMPT if mode == "storyboard" else self.SYSTEM_PROMPT
        
        prompt = self.build_prompt(query, detected_domain, mode)
        
        if stream:
            async for chunk in self.llm.generate_stream(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7
            ):
                yield chunk
        else:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            yield response
    
    async def generate_full(
        self, 
        query: str, 
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete response without streaming.
        Auto-detects domain and mode.
        
        Args:
            query: User query
            domain: Domain type (optional, will auto-detect)
            
        Returns:
            Dict containing response and metadata
        """
        # Auto-detect domain if not provided
        detected_domain = domain if domain and domain != "auto" else self.detect_domain(query)
        
        # Determine mode based on query
        mode = "storyboard" if self.is_storyboard_request(query) else "chat"
        system_prompt = self.STORYBOARD_SYSTEM_PROMPT if mode == "storyboard" else self.SYSTEM_PROMPT
        
        prompt = self.build_prompt(query, detected_domain, mode)
        
        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        return {
            "response": response,
            "detected_domain": detected_domain,
            "mode": mode,
            "is_storyboard": mode == "storyboard"
        }


# Singleton instance
_direct_chat_service: Optional[DirectChatService] = None


def get_direct_chat_service() -> DirectChatService:
    """Get the direct chat service singleton."""
    global _direct_chat_service
    if _direct_chat_service is None:
        _direct_chat_service = DirectChatService()
    return _direct_chat_service


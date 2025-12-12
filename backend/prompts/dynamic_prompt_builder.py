"""
Dynamic prompt builder that creates contextual prompts using LLM enhancement.
Combines static templates with dynamic LLM-generated context adaptations.
"""

from typing import Dict, Any, Optional, List
import json
import os
from pathlib import Path

from config import settings


class DynamicPromptBuilder:
    """
    Dynamic prompt builder for creating agent prompts.
    
    Features:
    - Loads base templates from JSON
    - Dynamically adapts prompts based on query context
    - Merges RAG results and memory context
    - Can use LLM to enhance prompts for specific scenarios
    """
    
    def __init__(self, templates_path: Optional[str] = None):
        """
        Initialize the dynamic prompt builder.
        
        Args:
            templates_path: Path to domain templates JSON file
        """
        self.templates_path = templates_path or settings.domain_templates_path
        self._templates: Optional[Dict[str, Dict[str, str]]] = None
        self._llm_service = None
    
    @property
    def templates(self) -> Dict[str, Dict[str, str]]:
        """
        Lazy load domain templates.
        
        Returns:
            Dict[str, Dict[str, str]]: Domain templates
        """
        if self._templates is None:
            self._templates = self._load_templates()
        return self._templates
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Load domain templates from JSON file.
        
        Returns:
            Dict[str, Dict[str, str]]: Loaded templates
        """
        paths_to_try = [
            self.templates_path,
            os.path.join(os.path.dirname(__file__), "domain_templates.json"),
            os.path.join(os.path.dirname(__file__), "..", "prompts", "domain_templates.json"),
        ]
        
        for path in paths_to_try:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                continue
        
        return self._get_default_templates()
    
    def _get_default_templates(self) -> Dict[str, Dict[str, str]]:
        """Get default templates if file is not available."""
        return {
            "default": {
                "planning_rules": "Create a clear, structured storyboard with logical scene progression.",
                "camera_rules": "Use appropriate camera angles and movements for each scene.",
                "tone_guidelines": "Maintain a professional and engaging tone throughout.",
                "visual_style": "Clean, modern visual style with consistent aesthetics."
            }
        }
    
    def get_domain_template(self, domain: str) -> Dict[str, str]:
        """
        Get template for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Dict[str, str]: Domain template or default
        """
        return self.templates.get(domain, self.templates.get("default", {}))
    
    def get_available_domains(self) -> list:
        """
        Get list of available domains.
        
        Returns:
            list: Available domain names
        """
        return [d for d in self.templates.keys() if d != "default"]
    
    def build_context(
        self,
        domain: str,
        query: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build complete context for prompt generation.
        
        Args:
            domain: Domain name
            query: User query
            additional_context: Optional additional context
            
        Returns:
            Dict[str, Any]: Complete context dictionary
        """
        template = self.get_domain_template(domain)
        
        # Analyze query to extract key elements
        query_analysis = self._analyze_query(query)
        
        context = {
            "domain": domain,
            "query": query,
            "query_type": query_analysis.get("type", "general"),
            "key_elements": query_analysis.get("elements", []),
            "planning_rules": template.get("planning_rules", ""),
            "camera_rules": template.get("camera_rules", ""),
            "tone_guidelines": template.get("tone_guidelines", ""),
            "visual_style": template.get("visual_style", ""),
        }
        
        if additional_context:
            context.update(additional_context)
        
        return context
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze query to extract key elements for dynamic adaptation.
        
        Args:
            query: User query
            
        Returns:
            Dict[str, Any]: Query analysis results
        """
        query_lower = query.lower()
        
        # Determine query type
        query_type = "general"
        if any(word in query_lower for word in ["demo", "showcase", "feature", "product"]):
            query_type = "product_showcase"
        elif any(word in query_lower for word in ["explain", "teach", "learn", "understand"]):
            query_type = "educational"
        elif any(word in query_lower for word in ["trailer", "cinematic", "film", "movie"]):
            query_type = "cinematic"
        elif any(word in query_lower for word in ["ad", "commercial", "promote", "marketing"]):
            query_type = "promotional"
        elif any(word in query_lower for word in ["game", "gameplay", "player"]):
            query_type = "gaming"
        
        # Extract key elements
        elements = []
        
        # Look for duration hints
        if "short" in query_lower or "brief" in query_lower:
            elements.append("short_format")
        elif "long" in query_lower or "detailed" in query_lower:
            elements.append("long_format")
        
        # Look for audience hints
        if any(word in query_lower for word in ["children", "kids", "young"]):
            elements.append("young_audience")
        elif any(word in query_lower for word in ["professional", "business", "corporate"]):
            elements.append("professional_audience")
        
        # Look for style hints
        if any(word in query_lower for word in ["fun", "playful", "exciting"]):
            elements.append("energetic_style")
        elif any(word in query_lower for word in ["serious", "formal", "professional"]):
            elements.append("formal_style")
        
        return {
            "type": query_type,
            "elements": elements
        }
    
    def format_domain_guidelines(self, domain: str) -> str:
        """
        Format domain guidelines as a readable string.
        
        Args:
            domain: Domain name
            
        Returns:
            str: Formatted guidelines
        """
        template = self.get_domain_template(domain)
        
        sections = []
        
        if template.get("planning_rules"):
            sections.append(f"**Planning Rules:**\n{template['planning_rules']}")
        
        if template.get("camera_rules"):
            sections.append(f"**Camera Rules:**\n{template['camera_rules']}")
        
        if template.get("tone_guidelines"):
            sections.append(f"**Tone Guidelines:**\n{template['tone_guidelines']}")
        
        if template.get("visual_style"):
            sections.append(f"**Visual Style:**\n{template['visual_style']}")
        
        return "\n\n".join(sections)
    
    def build_adaptive_prompt(
        self,
        domain: str,
        query: str,
        agent_type: str,
        context_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build an adaptive prompt that adjusts based on query analysis.
        
        Args:
            domain: Domain name
            query: User query
            agent_type: Type of agent (preact, react, reflect)
            context_data: Additional context data
            
        Returns:
            str: Dynamically adapted prompt
        """
        base_context = self.build_context(domain, query, context_data)
        query_type = base_context.get("query_type", "general")
        elements = base_context.get("key_elements", [])
        
        # Get base template
        template = self.get_domain_template(domain)
        
        # Build adaptive sections based on query analysis
        adaptive_sections = []
        
        # Adapt planning rules based on query type
        if query_type == "product_showcase":
            adaptive_sections.append(
                "Focus on feature highlights and user benefits. "
                "Structure scenes around key product capabilities."
            )
        elif query_type == "educational":
            adaptive_sections.append(
                "Use progressive complexity, starting simple. "
                "Include visual metaphors and recap moments."
            )
        elif query_type == "cinematic":
            adaptive_sections.append(
                "Employ dramatic pacing and emotional beats. "
                "Use cinematic techniques like establishing shots and reveals."
            )
        elif query_type == "promotional":
            adaptive_sections.append(
                "Lead with emotional hook, follow with value proposition. "
                "End with clear call-to-action."
            )
        
        # Adapt based on elements
        if "short_format" in elements:
            adaptive_sections.append(
                "Keep scenes concise (3-5 seconds each). "
                "Prioritize impact over detail."
            )
        elif "long_format" in elements:
            adaptive_sections.append(
                "Allow scenes to breathe (8-15 seconds each). "
                "Include transitional moments and detailed descriptions."
            )
        
        if "young_audience" in elements:
            adaptive_sections.append(
                "Use bright colors and simple language. "
                "Include engaging, dynamic visuals."
            )
        elif "professional_audience" in elements:
            adaptive_sections.append(
                "Maintain sophisticated visual language. "
                "Focus on efficiency and clarity."
            )
        
        # Combine with base guidelines
        dynamic_guidelines = "\n".join(adaptive_sections) if adaptive_sections else ""
        
        return {
            "base_guidelines": self.format_domain_guidelines(domain),
            "adaptive_guidelines": dynamic_guidelines,
            "query_type": query_type,
            "detected_elements": elements,
            "context": base_context
        }
    
    def merge_with_rag_context(
        self,
        base_context: Dict[str, Any],
        rag_results: list
    ) -> Dict[str, Any]:
        """
        Merge base context with RAG retrieval results.
        
        Args:
            base_context: Base context dictionary
            rag_results: List of RAG results
            
        Returns:
            Dict[str, Any]: Merged context
        """
        if not rag_results:
            return base_context
        
        # Format RAG results with relevance scoring
        rag_content = "\n\n".join([
            f"**Source:** {r.source or 'Unknown'} (Relevance: {r.relevance_score:.2f})\n{r.content}"
            for r in rag_results
        ])
        
        merged = base_context.copy()
        merged["rag_context"] = rag_content
        merged["has_rag_context"] = True
        
        return merged
    
    def merge_with_memory_context(
        self,
        base_context: Dict[str, Any],
        memory_entries: list
    ) -> Dict[str, Any]:
        """
        Merge base context with memory entries.
        
        Args:
            base_context: Base context dictionary
            memory_entries: List of memory entries
            
        Returns:
            Dict[str, Any]: Merged context
        """
        if not memory_entries:
            return base_context
        
        # Group by type
        grouped: Dict[str, list] = {}
        for entry in memory_entries:
            mem_type = entry.memory_type
            if mem_type not in grouped:
                grouped[mem_type] = []
            grouped[mem_type].append(entry.content)
        
        # Format memory content
        memory_sections = []
        for mem_type, contents in grouped.items():
            memory_sections.append(f"**{mem_type.upper()}:**")
            for content in contents:
                memory_sections.append(f"- {content}")
        
        merged = base_context.copy()
        merged["memory_context"] = "\n".join(memory_sections)
        merged["has_memory_context"] = True
        merged["memory_types"] = list(grouped.keys())
        
        return merged
    
    async def enhance_prompt_with_llm(
        self,
        domain: str,
        query: str,
        base_prompt: str
    ) -> str:
        """
        Use LLM to enhance and adapt the prompt for specific scenarios.
        This makes prompts truly dynamic by leveraging AI understanding.
        
        Args:
            domain: Domain name
            query: User query
            base_prompt: Base prompt to enhance
            
        Returns:
            str: Enhanced prompt
        """
        if self._llm_service is None:
            from services.llm import get_llm_service
            self._llm_service = get_llm_service()
        
        enhancement_prompt = f"""Given this storyboard request, suggest specific adaptations to the guidelines:

Domain: {domain}
User Request: {query}

Current Guidelines:
{base_prompt[:500]}...

Provide 2-3 specific, actionable adaptations that would improve the storyboard for this particular request. Keep each adaptation to 1-2 sentences."""

        try:
            enhancement = await self._llm_service.generate(
                prompt=enhancement_prompt,
                temperature=0.7,
                max_tokens=300
            )
            return f"{base_prompt}\n\n## DYNAMIC ADAPTATIONS\n{enhancement}"
        except Exception:
            # If LLM enhancement fails, return base prompt
            return base_prompt


# Singleton instance
_prompt_builder: Optional[DynamicPromptBuilder] = None


def get_prompt_builder() -> DynamicPromptBuilder:
    """
    Get the dynamic prompt builder singleton.
    
    Returns:
        DynamicPromptBuilder: The prompt builder instance
    """
    global _prompt_builder
    if _prompt_builder is None:
        _prompt_builder = DynamicPromptBuilder()
    return _prompt_builder

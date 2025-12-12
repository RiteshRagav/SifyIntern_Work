"""
PreAct Agent - Pre-Action Reasoning ("Think Before Acting")

PreAct creates a structured reasoning plan BEFORE producing any output.
Pattern: Plan → Execute → Answer

This is the THINKER component of ThinkerLLM - adding thinking capacity to non-thinking LLMs.
Like Cursor's Plan Mode, PreAct:
1. Understands the task
2. Detects the domain dynamically
3. Breaks it down into logical steps
4. Identifies requirements and constraints
5. Creates a clear execution plan with domain-specific keys
6. Includes required skills (e.g., Instructional Designer)

Use cases:
- Dynamic template generation
- Code generation
- Summaries
- Data classification
- Writing tasks
- Business logic execution
"""

from typing import AsyncGenerator, Optional, Dict, Any, List
import json
import re
import uuid
from datetime import datetime

from .base import BaseAgent, AgentContext
from models.schemas import AgentEvent, AgentName, AgentEventType, MasterPlan
from config import settings


# Domain detection patterns and keywords
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

# Domain-specific skill sets (Instructional Designer is ALWAYS included)
DOMAIN_SKILLS = {
    "healthcare": ["Clinical Trainer", "Medical Writer", "Patient Educator", "Compliance Specialist"],
    "finance": ["Financial Analyst", "Risk Assessor", "Compliance Officer", "Investment Advisor"],
    "hr": ["Talent Developer", "Policy Writer", "Employee Relations Specialist", "Compensation Analyst"],
    "cloud": ["Solutions Architect", "DevOps Engineer", "Security Specialist", "Cost Optimizer"],
    "software": ["Technical Writer", "Code Reviewer", "Architecture Designer", "QA Specialist"],
    "sales": ["Sales Trainer", "CRM Specialist", "Negotiation Coach", "Pipeline Analyst"],
    "education": ["Curriculum Designer", "Assessment Developer", "Learning Technologist", "Subject Expert"],
    "marketing": ["Content Strategist", "Brand Manager", "Analytics Expert", "Campaign Designer"],
    "legal": ["Legal Writer", "Contract Analyst", "Compliance Trainer", "Policy Developer"],
    "manufacturing": ["Process Engineer", "Quality Trainer", "Safety Specialist", "Lean Consultant"],
    "default": ["Content Creator", "Process Designer", "Quality Analyst", "Documentation Specialist"],
}

# Domain-specific capability keys (unique per domain, no duplication)
DOMAIN_CAPABILITIES = {
    "healthcare": ["clinical_protocols", "patient_safety_guidelines", "hipaa_compliance", "medical_terminology"],
    "finance": ["risk_assessment_framework", "regulatory_compliance", "financial_modeling", "audit_procedures"],
    "hr": ["policy_framework", "employee_lifecycle", "performance_metrics", "benefits_administration"],
    "cloud": ["infrastructure_patterns", "security_protocols", "cost_optimization", "disaster_recovery"],
    "software": ["development_standards", "code_quality_metrics", "api_documentation", "testing_frameworks"],
    "sales": ["sales_methodology", "pipeline_management", "objection_handling", "closing_techniques"],
    "education": ["learning_objectives", "assessment_criteria", "engagement_strategies", "progression_paths"],
    "marketing": ["brand_guidelines", "content_strategy", "audience_targeting", "campaign_metrics"],
    "legal": ["contract_templates", "compliance_checklist", "risk_mitigation", "regulatory_mapping"],
    "manufacturing": ["process_workflows", "quality_standards", "safety_protocols", "efficiency_metrics"],
    "default": ["content_structure", "quality_guidelines", "process_flow", "output_standards"],
}


class ReasoningStep:
    """A single step in the reasoning plan."""
    
    def __init__(
        self,
        step_number: int,
        title: str,
        description: str,
        expected_output: str,
        dependencies: List[int] = None
    ):
        self.step_number = step_number
        self.title = title
        self.description = description
        self.expected_output = expected_output
        self.dependencies = dependencies or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "title": self.title,
            "description": self.description,
            "expected_output": self.expected_output,
            "dependencies": self.dependencies
        }


class ClarificationQuestion:
    """A clarification question for the user to refine the plan."""
    
    def __init__(
        self,
        id: str,
        question: str,
        question_type: str = "boolean",  # "boolean", "choice", "text"
        options: List[str] = None,
        default: str = None
    ):
        self.id = id
        self.question = question
        self.question_type = question_type
        self.options = options or []
        self.default = default
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "type": self.question_type,
            "options": self.options,
            "default": self.default
        }


class ReasoningPlan:
    """A structured reasoning plan created by PreAct."""
    
    def __init__(
        self,
        title: str,
        task_understanding: str,
        approach: str,
        steps: List[ReasoningStep],
        constraints: List[str],
        success_criteria: List[str],
        estimated_complexity: str,
        detected_domain: str = "default",
        domain_skills: List[str] = None,
        domain_capabilities: List[str] = None,
        template_id: str = None,
        clarification_questions: List[ClarificationQuestion] = None,
        chat_history: List[Dict] = None
    ):
        self.title = title
        self.task_understanding = task_understanding
        self.approach = approach
        self.steps = steps
        self.constraints = constraints
        self.success_criteria = success_criteria
        self.estimated_complexity = estimated_complexity
        # Domain-specific fields for dynamic template generation
        self.detected_domain = detected_domain
        self.domain_skills = domain_skills or ["Instructional Designer"]
        self.domain_capabilities = domain_capabilities or []
        self.template_id = template_id or str(uuid.uuid4())
        self.created_at = datetime.utcnow().isoformat()
        # Chat/refinement fields
        self.clarification_questions = clarification_questions or []
        self.chat_history = chat_history or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "task_understanding": self.task_understanding,
            "approach": self.approach,
            "steps": [s.to_dict() for s in self.steps],
            "constraints": self.constraints,
            "success_criteria": self.success_criteria,
            "estimated_complexity": self.estimated_complexity,
            # Domain-specific metadata for template generation
            "detected_domain": self.detected_domain,
            "domain_skills": self.domain_skills,
            "domain_capabilities": self.domain_capabilities,
            "template_id": self.template_id,
            "created_at": self.created_at,
            # Chat/refinement fields
            "clarification_questions": [q.to_dict() for q in self.clarification_questions],
            "chat_history": self.chat_history,
            "metadata": {
                "generated_by": "thinker-llm-preact",
                "includes_instructional_designer": "Instructional Designer" in self.domain_skills
            }
        }


class PreActAgent(BaseAgent):
    """
    PreAct Agent - Pre-Action Reasoning (THE THINKER)
    
    "Think Before Acting" - Like Cursor's Plan Mode
    
    Creates a structured reasoning plan BEFORE producing output:
    1. Detect the domain from user query (dynamic domain detection)
    2. Understand what the user wants
    3. Break the task into logical steps
    4. Identify constraints and requirements
    5. Generate domain-specific skills (always includes Instructional Designer)
    6. Generate unique capability keys per domain
    7. Plan the approach
    8. Present plan for execution by ReAct
    
    This is the THINKER component - adding thinking capacity to non-thinking LLMs.
    """
    
    SYSTEM_PROMPT = """You are PreAct, the THINKER component of ThinkerLLM.

Your role is to add structured thinking capacity to any request. You always THINK BEFORE ACTING.

Before answering any request, you:
1. DETECT the domain from the user's query
2. CREATE a structured reasoning plan
3. IDENTIFY domain-specific skills needed (always include "Instructional Designer")
4. DEFINE unique capability keys for the domain
5. BREAK DOWN the task into logical steps
6. ASK clarifying questions to optimize the plan

Your plan should enable:
- Clear understanding of the request
- Domain-specific template generation
- Step-by-step execution by ReAct agent
- Validation by ReFlect agent

Output your reasoning plan in this JSON format:
{
    "title": "Brief title for this task",
    "detected_domain": "The domain detected from the query (e.g., healthcare, finance, hr, cloud, software, sales, education, marketing, legal, manufacturing)",
    "task_understanding": "What the user is asking for, in your own words",
    "approach": "High-level description of how you'll tackle this",
    "domain_skills": ["Instructional Designer", "...other domain-specific skills..."],
    "domain_capabilities": ["unique_key_1", "unique_key_2", "...domain-specific capability keys..."],
    "steps": [
        {
            "step_number": 1,
            "title": "Step title",
            "description": "What you'll do in this step",
            "expected_output": "What this step produces",
            "dependencies": []
        }
    ],
    "constraints": ["Any limitations or rules to follow"],
    "success_criteria": ["How we'll know the task is complete"],
    "estimated_complexity": "simple/moderate/complex",
    "clarification_questions": [
        {
            "id": "q1",
            "question": "A specific question to clarify requirements",
            "type": "choice",
            "options": ["Option A", "Option B", "Option C"],
            "default": "Option A"
        },
        {
            "id": "q2", 
            "question": "Another clarifying question",
            "type": "boolean",
            "default": "yes"
        }
    ]
}

IMPORTANT RULES:
1. "Instructional Designer" MUST be in domain_skills for ALL domains
2. domain_capabilities must be UNIQUE keys specific to the detected domain
3. Each step should be actionable and produce measurable output
4. Include at least 3-5 steps for proper reasoning chain
5. ALWAYS include 2-3 clarification_questions to help refine the plan
   - Questions should be specific and relevant to the task
   - Use "choice" type for multiple options, "boolean" for yes/no, "text" for open-ended
   - Provide sensible defaults

Be specific and thorough. This plan guides the entire generation process."""

    @property
    def name(self) -> AgentName:
        return AgentName.PREACT
    
    def _detect_domain(self, query: str) -> str:
        """
        Detect the domain from user query using keyword matching.
        Returns the most relevant domain based on keyword frequency.
        """
        query_lower = query.lower()
        domain_scores = {}
        
        for domain, keywords in DOMAIN_PATTERNS.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            # Return domain with highest score
            return max(domain_scores, key=domain_scores.get)
        
        return "default"
    
    def _get_domain_skills(self, domain: str) -> List[str]:
        """
        Get skills for a domain. Always includes 'Instructional Designer'.
        """
        base_skills = DOMAIN_SKILLS.get(domain, DOMAIN_SKILLS["default"])
        skills = ["Instructional Designer"] + base_skills
        return list(dict.fromkeys(skills))  # Remove duplicates while preserving order
    
    def _get_domain_capabilities(self, domain: str) -> List[str]:
        """
        Get unique capability keys for a domain.
        """
        return DOMAIN_CAPABILITIES.get(domain, DOMAIN_CAPABILITIES["default"])
    
    async def run(self, context: AgentContext) -> AsyncGenerator[AgentEvent, None]:
        """
        Execute PreAct reasoning - create a thinking plan before acting.
        Like Cursor's Plan Mode - THINK before executing.
        """
        yield self.create_event(
            AgentEventType.STATUS,
            "🧠 PreAct: Analyzing your request (Think Before Acting)..."
        )
        
        # Step 1: Detect domain from query
        detected_domain = self._detect_domain(context.query)
        domain_skills = self._get_domain_skills(detected_domain)
        domain_capabilities = self._get_domain_capabilities(detected_domain)
        
        yield self.create_event(
            AgentEventType.THOUGHT,
            f"🎯 Domain Detection:\n"
            f"• Detected Domain: {detected_domain}\n"
            f"• Skills: {', '.join(domain_skills[:3])}...\n"
            f"• Capabilities: {', '.join(domain_capabilities[:3])}..."
        )
        
        # Store detected domain in context
        context.metadata["detected_domain"] = detected_domain
        context.metadata["domain_skills"] = domain_skills
        context.metadata["domain_capabilities"] = domain_capabilities
        
        # Use detected domain if context.domain is generic
        effective_domain = detected_domain if context.domain in ["default", "general", ""] else context.domain
        
        yield self.create_event(
            AgentEventType.THOUGHT,
            f"Reading request: \"{context.query}\"\nEffective Domain: {effective_domain}"
        )
        
        # Step 2: Gather any relevant context
        domain_context = ""
        try:
            rag_results = await self.rag.search(
                query=context.query,
                domain=effective_domain,
                n_results=3
            )
            if rag_results:
                domain_context = "\n".join([f"• {r.content[:200]}" for r in rag_results])
                yield self.create_event(
                    AgentEventType.RAG_RESULT,
                    f"Found relevant context:\n{domain_context[:400]}...",
                    {"sources": [r.source for r in rag_results]}
                )
        except Exception as e:
            yield self.create_event(
                AgentEventType.THOUGHT,
                f"Proceeding without additional context: {str(e)[:100]}"
            )
        
        # Step 3: Generate the reasoning plan with domain-specific info
        yield self.create_event(
            AgentEventType.THOUGHT,
            f"Creating structured plan for {effective_domain} domain..."
        )
        
        planning_prompt = self._build_planning_prompt(
            context, 
            domain_context,
            detected_domain=detected_domain,
            domain_skills=domain_skills,
            domain_capabilities=domain_capabilities
        )
        
        full_response = ""
        async for chunk in self.llm.generate_stream(
            prompt=planning_prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.7
        ):
            full_response += chunk
            if len(full_response) % 200 == 0:
                yield self.create_event(
                    AgentEventType.THOUGHT,
                    f"Planning... ({len(full_response)} chars)"
                )
        
        # Step 4: Parse the plan
        yield self.create_event(
            AgentEventType.THOUGHT,
            "Organizing my reasoning plan..."
        )
        
        reasoning_plan = self._parse_reasoning_plan(full_response, context)
        
        # Store in context
        context.metadata["reasoning_plan"] = reasoning_plan.to_dict()
        
        # Step 5: Emit the structured plan
        yield self.create_event(
            AgentEventType.THOUGHT,
            f"📋 Task Understanding:\n{reasoning_plan.task_understanding}"
        )
        
        yield self.create_event(
            AgentEventType.THOUGHT,
            f"🎯 Approach:\n{reasoning_plan.approach}"
        )
        
        # Emit each step
        for step in reasoning_plan.steps:
            yield self.create_event(
                AgentEventType.ACTION,
                f"Step {step.step_number}: {step.title}",
                {
                    "step": step.to_dict(),
                    "event_type": "plan_step"
                }
            )
        
        # Emit constraints
        if reasoning_plan.constraints:
            yield self.create_event(
                AgentEventType.THOUGHT,
                "⚠️ Constraints:\n" + "\n".join([f"• {c}" for c in reasoning_plan.constraints])
            )
        
        # Emit success criteria
        if reasoning_plan.success_criteria:
            yield self.create_event(
                AgentEventType.THOUGHT,
                "✅ Success Criteria:\n" + "\n".join([f"• {c}" for c in reasoning_plan.success_criteria])
            )
        
        # Generate Mermaid diagram
        mermaid = self._generate_mermaid(reasoning_plan)
        
        # Create the complete plan event
        plan_summary = self._format_plan_summary(reasoning_plan)
        
        yield self.create_event(
            AgentEventType.PLAN,
            plan_summary,
            {
                "reasoning_plan": reasoning_plan.to_dict(),
                "mermaid_diagram": mermaid,
                "step_count": len(reasoning_plan.steps),
                "complexity": reasoning_plan.estimated_complexity,
                "requires_approval": True,
                "detected_domain": reasoning_plan.detected_domain,
                "domain_skills": reasoning_plan.domain_skills,
                "domain_capabilities": reasoning_plan.domain_capabilities,
                "template_id": reasoning_plan.template_id,
                "includes_instructional_designer": "Instructional Designer" in reasoning_plan.domain_skills
            }
        )
        
        # Create MasterPlan for compatibility
        context.master_plan = MasterPlan(
            title=reasoning_plan.title,
            domain=context.domain,
            total_scenes=len(reasoning_plan.steps),
            world_setting=reasoning_plan.task_understanding,
            characters=[],
            visual_style=reasoning_plan.approach,
            camera_rules=", ".join(reasoning_plan.constraints),
            tone=reasoning_plan.estimated_complexity,
            scene_outline=[f"Step {s.step_number}: {s.title}" for s in reasoning_plan.steps]
        )
        
        # Save to memory
        await self.tme.add_memory(
            session_id=context.session_id,
            content=f"Plan: {reasoning_plan.title} - {reasoning_plan.approach}",
            memory_type="plan",
            tags=["preact", "reasoning", context.domain]
        )
        
        yield self.create_event(
            AgentEventType.MEMORY_UPDATE,
            "Saved reasoning plan to memory",
            {"memory_type": "plan"}
        )
        
        yield self.create_event(
            AgentEventType.COMPLETE,
            f"✅ Reasoning plan ready!\n\n"
            f"🎯 Domain: {reasoning_plan.detected_domain}\n"
            f"📋 {len(reasoning_plan.steps)} steps planned\n"
            f"👥 {len(reasoning_plan.domain_skills)} skills (Instructional Designer: ✅)\n"
            f"🔧 {len(reasoning_plan.domain_capabilities)} capability keys\n"
            f"⚡ Complexity: {reasoning_plan.estimated_complexity}\n\n"
            f"ReAct will now execute this plan. ReFlect will validate.",
            {
                "requires_approval": True,
                "step_count": len(reasoning_plan.steps),
                "complexity": reasoning_plan.estimated_complexity,
                "detected_domain": reasoning_plan.detected_domain,
                "template_id": reasoning_plan.template_id,
                "skills_count": len(reasoning_plan.domain_skills),
                "capabilities_count": len(reasoning_plan.domain_capabilities)
            }
        )
    
    async def refine_plan(
        self,
        context: AgentContext,
        original_plan: Dict[str, Any],
        user_responses: Dict[str, Any],
        chat_message: str = "",
        chat_history: List[Dict] = None
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Refine an existing plan based on user feedback and clarification responses.
        
        Args:
            context: Agent context with session info
            original_plan: The original reasoning plan dict
            user_responses: User's responses to clarification questions
            chat_message: Additional user message for refinement
            chat_history: Previous chat messages for context
        """
        chat_history = chat_history or []
        
        yield self.create_event(
            AgentEventType.STATUS,
            "🔄 Refining plan based on your feedback..."
        )
        
        # Build refinement prompt
        refinement_prompt = self._build_refinement_prompt(
            context, original_plan, user_responses, chat_message, chat_history
        )
        
        yield self.create_event(
            AgentEventType.THOUGHT,
            f"Processing your feedback:\n"
            f"• Clarification responses: {len(user_responses)}\n"
            f"• Additional instructions: {len(chat_message)} chars\n"
            f"• Chat history: {len(chat_history)} messages"
        )
        
        # Generate refined plan
        full_response = ""
        async for chunk in self.llm.generate_stream(
            prompt=refinement_prompt,
            system_prompt=self.REFINE_SYSTEM_PROMPT,
            temperature=0.7
        ):
            full_response += chunk
        
        # Parse the refined plan
        reasoning_plan = self._parse_reasoning_plan(full_response, context)
        
        # Add chat message to history
        if chat_message:
            reasoning_plan.chat_history = chat_history + [
                {"role": "user", "content": chat_message},
                {"role": "assistant", "content": f"Updated plan: {reasoning_plan.title}"}
            ]
        else:
            reasoning_plan.chat_history = chat_history
        
        # Store in context
        context.metadata["reasoning_plan"] = reasoning_plan.to_dict()
        
        # Generate Mermaid diagram
        mermaid = self._generate_mermaid(reasoning_plan)
        
        # Emit the refined plan
        plan_summary = self._format_plan_summary(reasoning_plan)
        
        yield self.create_event(
            AgentEventType.PLAN,
            plan_summary,
            {
                "reasoning_plan": reasoning_plan.to_dict(),
                "mermaid_diagram": mermaid,
                "step_count": len(reasoning_plan.steps),
                "complexity": reasoning_plan.estimated_complexity,
                "requires_approval": True,
                "detected_domain": reasoning_plan.detected_domain,
                "is_refined": True,
                "refinement_context": {
                    "user_responses": user_responses,
                    "chat_message": chat_message
                }
            }
        )
        
        yield self.create_event(
            AgentEventType.COMPLETE,
            f"✅ Plan refined!\n\n"
            f"📋 {len(reasoning_plan.steps)} steps\n"
            f"🔄 Updated based on your feedback",
            {
                "is_refined": True,
                "step_count": len(reasoning_plan.steps)
            }
        )
    
    REFINE_SYSTEM_PROMPT = """You are PreAct, the THINKER component of ThinkerLLM.

You are REFINING an existing plan based on user feedback. Your job is to:
1. Incorporate the user's clarification responses
2. Adjust the plan based on their additional instructions
3. Keep the same JSON structure
4. Update steps, approach, and constraints as needed

Output the REFINED plan in the same JSON format as before. Make sure to:
- Address all user feedback
- Keep clarification_questions that are still relevant
- Update task_understanding if the user provided more context
- Adjust steps to match the refined requirements"""
    
    def _build_refinement_prompt(
        self,
        context: AgentContext,
        original_plan: Dict[str, Any],
        user_responses: Dict[str, Any],
        chat_message: str,
        chat_history: List[Dict]
    ) -> str:
        """Build prompt for plan refinement."""
        # Format user responses
        responses_text = ""
        for q_id, response in user_responses.items():
            responses_text += f"- {q_id}: {response}\n"
        
        # Format chat history
        history_text = ""
        for msg in chat_history[-5:]:  # Last 5 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_text += f"{role.title()}: {content}\n"
        
        return f"""## ORIGINAL PLAN
{json.dumps(original_plan, indent=2)}

## USER CLARIFICATION RESPONSES
{responses_text if responses_text else "No responses provided"}

## ADDITIONAL USER INSTRUCTIONS
{chat_message if chat_message else "No additional instructions"}

## CHAT HISTORY
{history_text if history_text else "No previous chat"}

## YOUR TASK
Refine the plan above based on the user's feedback. Output the complete refined plan in JSON format.

Key changes to incorporate:
- Adjust approach based on user preferences
- Update steps to match clarified requirements
- Keep the plan actionable and specific
- Generate new clarification questions if needed"""
    
    def _build_planning_prompt(
        self, 
        context: AgentContext, 
        domain_context: str,
        detected_domain: str = "default",
        domain_skills: List[str] = None,
        domain_capabilities: List[str] = None
    ) -> str:
        """Build the prompt for generating the reasoning plan with domain-specific info."""
        domain_skills = domain_skills or ["Instructional Designer"]
        domain_capabilities = domain_capabilities or []
        
        return f"""## USER REQUEST

**Domain:** {context.domain}
**Detected Domain:** {detected_domain}
**Request:** {context.query}

## DOMAIN-SPECIFIC INFORMATION

**Suggested Skills (include these in your plan):**
{json.dumps(domain_skills, indent=2)}

**Suggested Capability Keys (use as reference for unique keys):**
{json.dumps(domain_capabilities, indent=2)}

## RELEVANT CONTEXT
{domain_context if domain_context else "No additional context available."}

## YOUR TASK

Create a structured reasoning plan for how you will fulfill this request.

CRITICAL REQUIREMENTS:
1. "Instructional Designer" MUST be in your domain_skills list
2. Generate UNIQUE capability keys specific to {detected_domain} domain
3. Each step must produce actionable output for ReAct agent

Think carefully about:
1. What exactly is the user asking for?
2. What domain-specific skills are needed?
3. What unique capability keys should this domain have?
4. What are the logical steps to accomplish this?
5. What constraints or requirements should you follow?
6. What does success look like?

Break the task into clear, actionable steps. Each step should:
- Have a clear purpose
- Produce a specific output
- Build on previous steps if needed
- Be executable by the ReAct agent

This plan will guide:
- ReAct agent for execution
- ReFlect agent for validation
- TME for storage

Create your reasoning plan in the JSON format specified."""
    
    def _parse_reasoning_plan(self, response: str, context: AgentContext) -> ReasoningPlan:
        """Parse the LLM response into a ReasoningPlan with domain-specific fields."""
        # Get domain info from context metadata
        detected_domain = context.metadata.get("detected_domain", "default")
        default_skills = context.metadata.get("domain_skills", ["Instructional Designer"])
        default_capabilities = context.metadata.get("domain_capabilities", [])
        
        # Try to extract JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        
        if json_match:
            try:
                plan_data = json.loads(json_match.group())
                
                steps = []
                for i, step_data in enumerate(plan_data.get("steps", [])):
                    steps.append(ReasoningStep(
                        step_number=step_data.get("step_number", i + 1),
                        title=step_data.get("title", f"Step {i + 1}"),
                        description=step_data.get("description", ""),
                        expected_output=step_data.get("expected_output", ""),
                        dependencies=step_data.get("dependencies", [])
                    ))
                
                # Extract domain-specific fields from LLM response or use defaults
                domain_skills = plan_data.get("domain_skills", default_skills)
                # Ensure Instructional Designer is always included
                if "Instructional Designer" not in domain_skills:
                    domain_skills = ["Instructional Designer"] + domain_skills
                
                domain_capabilities = plan_data.get("domain_capabilities", default_capabilities)
                
                # Parse clarification questions
                clarification_questions = []
                for q_data in plan_data.get("clarification_questions", []):
                    clarification_questions.append(ClarificationQuestion(
                        id=q_data.get("id", f"q{len(clarification_questions)+1}"),
                        question=q_data.get("question", ""),
                        question_type=q_data.get("type", "boolean"),
                        options=q_data.get("options", []),
                        default=q_data.get("default")
                    ))
                
                # Generate default questions if none provided
                if not clarification_questions:
                    clarification_questions = self._generate_default_questions(context, detected_domain)
                
                return ReasoningPlan(
                    title=plan_data.get("title", f"{context.domain} Task"),
                    task_understanding=plan_data.get("task_understanding", context.query),
                    approach=plan_data.get("approach", "Step-by-step execution"),
                    steps=steps,
                    constraints=plan_data.get("constraints", []),
                    success_criteria=plan_data.get("success_criteria", []),
                    estimated_complexity=plan_data.get("estimated_complexity", "moderate"),
                    detected_domain=plan_data.get("detected_domain", detected_domain),
                    domain_skills=domain_skills,
                    domain_capabilities=domain_capabilities,
                    clarification_questions=clarification_questions
                )
            except json.JSONDecodeError:
                pass
        
        # Fallback: Create a default plan
        return self._create_default_plan(context, response)
    
    def _generate_default_questions(self, context: AgentContext, domain: str) -> List[ClarificationQuestion]:
        """Generate default clarification questions based on domain and query."""
        questions = []
        
        # Skill level question (common for most domains)
        questions.append(ClarificationQuestion(
            id="q_skill_level",
            question="What is the target skill level for this content?",
            question_type="choice",
            options=["Beginner", "Intermediate", "Advanced", "Mixed"],
            default="Intermediate"
        ))
        
        # Domain-specific questions
        if domain == "education" or "course" in context.query.lower():
            questions.append(ClarificationQuestion(
                id="q_content_type",
                question="What type of content delivery do you prefer?",
                question_type="choice",
                options=["Theory-focused", "Hands-on projects", "Mixed approach", "Case studies"],
                default="Mixed approach"
            ))
            questions.append(ClarificationQuestion(
                id="q_include_exercises",
                question="Should I include practice exercises and quizzes?",
                question_type="boolean",
                default="yes"
            ))
        elif domain == "software":
            questions.append(ClarificationQuestion(
                id="q_code_examples",
                question="Should I include detailed code examples?",
                question_type="boolean",
                default="yes"
            ))
            questions.append(ClarificationQuestion(
                id="q_deployment",
                question="Should deployment/production considerations be covered?",
                question_type="boolean",
                default="yes"
            ))
        else:
            questions.append(ClarificationQuestion(
                id="q_detail_level",
                question="What level of detail do you need?",
                question_type="choice",
                options=["High-level overview", "Detailed breakdown", "Comprehensive deep-dive"],
                default="Detailed breakdown"
            ))
            questions.append(ClarificationQuestion(
                id="q_examples",
                question="Should I include practical examples?",
                question_type="boolean",
                default="yes"
            ))
        
        return questions
    
    def _create_default_plan(self, context: AgentContext, raw_response: str) -> ReasoningPlan:
        """Create a default plan when parsing fails, including domain-specific fields."""
        # Get domain info from context metadata
        detected_domain = context.metadata.get("detected_domain", "default")
        domain_skills = context.metadata.get("domain_skills", self._get_domain_skills(detected_domain))
        domain_capabilities = context.metadata.get("domain_capabilities", self._get_domain_capabilities(detected_domain))
        
        # Ensure Instructional Designer is always included
        if "Instructional Designer" not in domain_skills:
            domain_skills = ["Instructional Designer"] + domain_skills
        
        # Try to extract steps from the response
        steps = []
        step_patterns = [
            r"(?:Step\s*)?(\d+)[.:\s]+(.+?)(?=(?:Step\s*)?\d+[.:]|$)",
            r"(\d+)\)\s*(.+?)(?=\d+\)|$)"
        ]
        
        for pattern in step_patterns:
            matches = re.findall(pattern, raw_response, re.IGNORECASE | re.DOTALL)
            if matches:
                for num, content in matches[:8]:
                    steps.append(ReasoningStep(
                        step_number=int(num),
                        title=content.strip()[:50],
                        description=content.strip(),
                        expected_output="Completed step output",
                        dependencies=[]
                    ))
                break
        
        # If no steps found, create domain-aware default steps
        if not steps:
            steps = [
                ReasoningStep(
                    step_number=1,
                    title="Analyze request and domain context",
                    description=f"Analyze: {context.query} in {detected_domain} domain",
                    expected_output="Clear understanding of requirements and domain context",
                    dependencies=[]
                ),
                ReasoningStep(
                    step_number=2,
                    title="Identify domain-specific skills",
                    description=f"Identify required skills including: {', '.join(domain_skills[:3])}",
                    expected_output="List of applicable skills for this domain",
                    dependencies=[1]
                ),
                ReasoningStep(
                    step_number=3,
                    title="Generate domain capabilities",
                    description=f"Generate unique capability keys: {', '.join(domain_capabilities[:3])}",
                    expected_output="Domain-specific capability structure",
                    dependencies=[2]
                ),
                ReasoningStep(
                    step_number=4,
                    title="Create instructional templates",
                    description="Generate instructional content using Instructional Designer skill",
                    expected_output="Domain-specific instructional templates",
                    dependencies=[3]
                ),
                ReasoningStep(
                    step_number=5,
                    title="Compile and validate",
                    description="Compile all components into final template structure",
                    expected_output="Complete domain template ready for validation",
                    dependencies=[4]
                )
            ]
        
        return ReasoningPlan(
            title=f"{detected_domain.replace('_', ' ').title()} Template Generation",
            task_understanding=context.query,
            approach=f"Systematic {detected_domain} domain template generation with Instructional Designer skill",
            steps=steps,
            constraints=[
                "Instructional Designer skill must be included",
                "All capability keys must be unique to this domain",
                "Follow domain-specific best practices",
                "Ensure accuracy and relevance"
            ],
            success_criteria=[
                "Request fully addressed",
                "Instructional Designer skill present",
                "All capability keys are unique",
                "Output follows required schema"
            ],
            estimated_complexity="moderate",
            detected_domain=detected_domain,
            domain_skills=domain_skills,
            domain_capabilities=domain_capabilities
        )
    
    def _generate_mermaid(self, plan: ReasoningPlan) -> str:
        """Generate a Mermaid diagram from the reasoning plan."""
        diagram = f"""graph TD
    subgraph Plan["📋 {plan.title}"]
        UNDERSTAND["🤔 Understanding<br/>{plan.task_understanding[:30]}..."]
"""
        
        # Add step nodes
        prev_node = "UNDERSTAND"
        for step in plan.steps:
            node_id = f"STEP{step.step_number}"
            label = f"{step.step_number}. {step.title[:25]}..."
            diagram += f'        {node_id}["{label}"]\n'
            
            if step.dependencies:
                for dep in step.dependencies:
                    diagram += f'        STEP{dep} --> {node_id}\n'
            else:
                diagram += f'        {prev_node} --> {node_id}\n'
            
            prev_node = node_id
        
        diagram += f"""        {prev_node} --> OUTPUT["✅ Final Output"]
    end
    
    style Plan fill:#f0f9ff
    style UNDERSTAND fill:#dbeafe
    style OUTPUT fill:#dcfce7
"""
        
        return diagram
    
    def _format_plan_summary(self, plan: ReasoningPlan) -> str:
        """Format the plan as a readable summary with domain-specific info."""
        summary = f"""# 🧠 Reasoning Plan: {plan.title}

## 🎯 Detected Domain
**Domain:** {plan.detected_domain}
**Template ID:** {plan.template_id}

## 📋 My Understanding
{plan.task_understanding}

## 🎯 My Approach
{plan.approach}

## 👥 Domain Skills
"""
        for skill in plan.domain_skills:
            marker = "⭐" if skill == "Instructional Designer" else "•"
            summary += f"{marker} {skill}\n"
        
        summary += "\n## 🔧 Domain Capabilities\n"
        for cap in plan.domain_capabilities:
            summary += f"• `{cap}`\n"
        
        summary += "\n## 📝 Execution Steps\n"
        
        for step in plan.steps:
            deps = f" (depends on: {', '.join(map(str, step.dependencies))})" if step.dependencies else ""
            summary += f"""
### Step {step.step_number}: {step.title}{deps}
{step.description}
**Expected output:** {step.expected_output}
"""
        
        if plan.constraints:
            summary += "\n## ⚠️ Constraints\n"
            for c in plan.constraints:
                summary += f"- {c}\n"
        
        if plan.success_criteria:
            summary += "\n## ✅ Success Criteria\n"
            for c in plan.success_criteria:
                summary += f"- {c}\n"
        
        summary += f"\n## ⚡ Complexity: {plan.estimated_complexity.upper()}\n"
        summary += f"\n## 📊 Metadata\n"
        summary += f"- Created: {plan.created_at}\n"
        summary += f"- Instructional Designer: {'✅ Included' if 'Instructional Designer' in plan.domain_skills else '❌ Missing'}\n"
        
        return summary

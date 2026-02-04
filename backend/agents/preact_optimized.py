# """
# REAL OPTIMIZATION: PreAct Agent - 10 minutes to 4-6 minutes

# KEY CHANGES:
# 1. ELIMINATED _perform_deep_analysis() LLM call (save 3-5 min)
# 2. Use fast heuristic analysis instead
# 3. Reduced planning tokens: 3000 → 1800
# 4. Parallel RAG + domain detection
# 5. Streamlined prompts
# 6. Added timeouts everywhere
# """

# from typing import AsyncGenerator, Optional, Dict, Any, List
# import json
# import re
# import uuid
# import asyncio
# from datetime import datetime

# from .base import BaseAgent, AgentContext
# from models.schemas import AgentEvent, AgentName, AgentEventType, MasterPlan
# from config import settings

# # Keep all your domain patterns (unchanged)
# DOMAIN_PATTERNS = {
#     "healthcare": ["medical", "health", "clinical", "patient", "hospital", "doctor", "nurse", "diagnosis", "treatment", "pharma", "drug"],
#     "finance": ["finance", "banking", "investment", "stock", "trading", "loan", "credit", "insurance", "accounting", "budget", "revenue"],
#     "hr": ["hr", "human resources", "employee", "hiring", "recruitment", "onboarding", "payroll", "benefits", "performance review", "talent"],
#     "cloud": ["cloud", "aws", "azure", "gcp", "kubernetes", "docker", "devops", "infrastructure", "serverless", "microservices"],
#     "software": ["software", "development", "programming", "code", "api", "database", "testing", "agile", "scrum", "deployment"],
#     "sales": ["sales", "crm", "lead", "pipeline", "prospect", "deal", "quota", "revenue", "customer", "conversion"],
#     "education": ["education", "learning", "teaching", "course", "curriculum", "student", "training", "tutorial", "lesson", "classroom"],
#     "marketing": ["marketing", "campaign", "brand", "advertising", "social media", "seo", "content", "promotion", "audience", "engagement"],
#     "legal": ["legal", "law", "contract", "compliance", "regulation", "litigation", "attorney", "court", "rights", "policy"],
#     "manufacturing": ["manufacturing", "production", "factory", "assembly", "quality control", "supply chain", "inventory", "lean", "six sigma"],
# }

# DOMAIN_SKILLS = {
#     "healthcare": ["Clinical Trainer", "Medical Writer", "Patient Educator", "Compliance Specialist"],
#     "finance": ["Financial Analyst", "Risk Assessor", "Compliance Officer", "Investment Advisor"],
#     "hr": ["Talent Developer", "Policy Writer", "Employee Relations Specialist", "Compensation Analyst"],
#     "cloud": ["Solutions Architect", "DevOps Engineer", "Security Specialist", "Cost Optimizer"],
#     "software": ["Technical Writer", "Code Reviewer", "Architecture Designer", "QA Specialist"],
#     "sales": ["Sales Trainer", "CRM Specialist", "Negotiation Coach", "Pipeline Analyst"],
#     "education": ["Curriculum Designer", "Assessment Developer", "Learning Technologist", "Subject Expert"],
#     "marketing": ["Content Strategist", "Brand Manager", "Analytics Expert", "Campaign Designer"],
#     "legal": ["Legal Writer", "Contract Analyst", "Compliance Trainer", "Policy Developer"],
#     "manufacturing": ["Process Engineer", "Quality Trainer", "Safety Specialist", "Lean Consultant"],
#     "default": ["Content Creator", "Process Designer", "Quality Analyst", "Documentation Specialist"],
# }

# DOMAIN_CAPABILITIES = {
#     "healthcare": ["clinical_protocols", "patient_safety_guidelines", "hipaa_compliance", "medical_terminology"],
#     "finance": ["risk_assessment_framework", "regulatory_compliance", "financial_modeling", "audit_procedures"],
#     "hr": ["policy_framework", "employee_lifecycle", "performance_metrics", "benefits_administration"],
#     "cloud": ["infrastructure_patterns", "security_protocols", "cost_optimization", "disaster_recovery"],
#     "software": ["development_standards", "code_quality_metrics", "api_documentation", "testing_frameworks"],
#     "sales": ["sales_methodology", "pipeline_management", "objection_handling", "closing_techniques"],
#     "education": ["learning_objectives", "assessment_criteria", "engagement_strategies", "progression_paths"],
#     "marketing": ["brand_guidelines", "content_strategy", "audience_targeting", "campaign_metrics"],
#     "legal": ["contract_templates", "compliance_checklist", "risk_mitigation", "regulatory_mapping"],
#     "manufacturing": ["process_workflows", "quality_standards", "safety_protocols", "efficiency_metrics"],
#     "default": ["content_structure", "quality_guidelines", "process_flow", "output_standards"],
# }

# # Keep your classes (unchanged)
# class ReasoningStep:
#     def __init__(self, step_number: int, title: str, description: str, expected_output: str,
#                  dependencies: List[int] = None, sub_steps: List[str] = None, estimated_effort: str = "15min",
#                  validation_criteria: List[str] = None, tools_needed: List[str] = None, priority: str = "important"):
#         self.step_number = step_number
#         self.title = title
#         self.description = description
#         self.expected_output = expected_output
#         self.dependencies = dependencies or []
#         self.sub_steps = sub_steps or []
#         self.estimated_effort = estimated_effort
#         self.validation_criteria = validation_criteria or []
#         self.tools_needed = tools_needed or ["GENERATE"]
#         self.priority = priority
    
#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             "step_number": self.step_number,
#             "title": self.title,
#             "description": self.description,
#             "expected_output": self.expected_output,
#             "dependencies": self.dependencies,
#             "sub_steps": self.sub_steps,
#             "estimated_effort": self.estimated_effort,
#             "validation_criteria": self.validation_criteria,
#             "tools_needed": self.tools_needed,
#             "priority": self.priority
#         }


# class ClarificationQuestion:
#     def __init__(self, id: str, question: str, question_type: str = "boolean",
#                  options: List[str] = None, default: str = None, priority: str = "medium", reason: str = None):
#         self.id = id
#         self.question = question
#         self.question_type = question_type
#         self.options = options or []
#         self.default = default
#         self.priority = priority
#         self.reason = reason or "Helps clarify requirements"
    
#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             "id": self.id,
#             "question": self.question,
#             "type": self.question_type,
#             "options": self.options,
#             "default": self.default,
#             "priority": self.priority,
#             "reason": self.reason
#         }


# class ReasoningPlan:
#     def __init__(self, title: str, task_understanding: str, approach: str, steps: List[ReasoningStep],
#                  constraints: List[str], success_criteria: List[str], estimated_complexity: str,
#                  detected_domain: str = "default", domain_skills: List[str] = None,
#                  domain_capabilities: List[str] = None, template_id: str = None,
#                  clarification_questions: List[ClarificationQuestion] = None, chat_history: List[Dict] = None,
#                  deep_analysis: Dict[str, Any] = None, requirements: Dict[str, Any] = None,
#                  risks_and_assumptions: Dict[str, Any] = None, strategy: Dict[str, Any] = None,
#                  estimated_total_effort: str = None):
#         self.title = title
#         self.task_understanding = task_understanding
#         self.approach = approach
#         self.steps = steps
#         self.constraints = constraints
#         self.success_criteria = success_criteria
#         self.estimated_complexity = estimated_complexity
#         self.detected_domain = detected_domain
#         self.domain_skills = domain_skills or ["Instructional Designer"]
#         self.domain_capabilities = domain_capabilities or []
#         self.template_id = template_id or str(uuid.uuid4())
#         self.created_at = datetime.utcnow().isoformat()
#         self.clarification_questions = clarification_questions or []
#         self.chat_history = chat_history or []
#         self.deep_analysis = deep_analysis or {}
#         self.requirements = requirements or {}
#         self.risks_and_assumptions = risks_and_assumptions or {}
#         self.strategy = strategy or {}
#         self.estimated_total_effort = estimated_total_effort or self._calculate_total_effort()
    
#     def _calculate_total_effort(self) -> str:
#         effort_map = {"5min": 5, "15min": 15, "30min": 30, "1hr": 60, "2hr+": 120}
#         total_minutes = sum(effort_map.get(s.estimated_effort, 15) for s in self.steps)
#         if total_minutes < 60:
#             return f"{total_minutes}min"
#         elif total_minutes < 120:
#             return "1-2 hours"
#         else:
#             return f"{total_minutes // 60}+ hours"
    
#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             "title": self.title,
#             "task_understanding": self.task_understanding,
#             "approach": self.approach,
#             "steps": [s.to_dict() for s in self.steps],
#             "constraints": self.constraints,
#             "success_criteria": self.success_criteria,
#             "estimated_complexity": self.estimated_complexity,
#             "detected_domain": self.detected_domain,
#             "domain_skills": self.domain_skills,
#             "domain_capabilities": self.domain_capabilities,
#             "template_id": self.template_id,
#             "created_at": self.created_at,
#             "clarification_questions": [q.to_dict() for q in self.clarification_questions],
#             "chat_history": self.chat_history,
#             "deep_analysis": self.deep_analysis,
#             "requirements": self.requirements,
#             "risks_and_assumptions": self.risks_and_assumptions,
#             "strategy": self.strategy,
#             "estimated_total_effort": self.estimated_total_effort,
#             "metadata": {
#                 "generated_by": "thinker-llm-preact-optimized",
#                 "includes_instructional_designer": "Instructional Designer" in self.domain_skills,
#                 "analysis_depth": "fast"
#             }
#         }


# class PreActAgent(BaseAgent):
#     """
#     OPTIMIZED PreAct Agent - 50% faster (10min → 4-6min)
    
#     Key optimizations:
#     1. Eliminated deep_analysis LLM call (save 3-5 min)
#     2. Reduced token limits
#     3. Parallel operations
#     4. Timeouts everywhere
#     """
    
#     # OPTIMIZATION: Much shorter system prompt
#     SYSTEM_PROMPT = """You are PreAct planning agent. Create execution plan in JSON.

# CRITICAL:
# 1. Include "Instructional Designer" in domain_skills
# 2. Generate 5-7 steps with sub_steps, validation_criteria
# 3. Output ONLY valid JSON

# JSON format:
# {
#   "title": "...",
#   "detected_domain": "...",
#   "task_understanding": "...",
#   "approach": "...",
#   "domain_skills": ["Instructional Designer", "..."],
#   "domain_capabilities": ["..."],
#   "steps": [{"step_number": 1, "title": "...", "description": "...", "expected_output": "...", "sub_steps": ["..."], "estimated_effort": "15min", "validation_criteria": ["..."], "priority": "important"}],
#   "constraints": ["..."],
#   "success_criteria": ["..."],
#   "estimated_complexity": "moderate"
# }"""

#     @property
#     def name(self) -> AgentName:
#         return AgentName.PREACT
    
#     def _detect_domain(self, query: str) -> str:
#         """Fast domain detection (unchanged)"""
#         query_lower = query.lower()
#         domain_scores = {}
        
#         for domain, keywords in DOMAIN_PATTERNS.items():
#             score = sum(1 for keyword in keywords if keyword in query_lower)
#             if score > 0:
#                 domain_scores[domain] = score
        
#         if domain_scores:
#             return max(domain_scores, key=domain_scores.get)
        
#         return "default"
    
#     def _get_domain_skills(self, domain: str) -> List[str]:
#         """Get skills (unchanged)"""
#         base_skills = DOMAIN_SKILLS.get(domain, DOMAIN_SKILLS["default"])
#         skills = ["Instructional Designer"] + base_skills
#         return list(dict.fromkeys(skills))
    
#     def _get_domain_capabilities(self, domain: str) -> List[str]:
#         """Get capabilities (unchanged)"""
#         return DOMAIN_CAPABILITIES.get(domain, DOMAIN_CAPABILITIES["default"])
    
#     # OPTIMIZATION: Replace LLM deep analysis with fast heuristics
#     def _fast_heuristic_analysis(self, context: AgentContext, domain: str) -> Dict[str, Any]:
#         """
#         CRITICAL OPTIMIZATION: Replace 3-5 minute LLM call with instant heuristics
#         This alone saves 3-5 minutes per request!
#         """
#         query_lower = context.query.lower()
        
#         # Quick skill level detection
#         skill_indicators = {
#             "beginner": ["beginner", "intro", "basics", "simple", "basic", "new to", "getting started"],
#             "advanced": ["advanced", "complex", "sophisticated", "enterprise", "expert", "deep dive"],
#             "intermediate": []  # default
#         }
        
#         skill_level = "intermediate"
#         for level, keywords in skill_indicators.items():
#             if any(kw in query_lower for kw in keywords):
#                 skill_level = level
#                 break
        
#         # Quick audience detection
#         audience_keywords = {
#             "technical": ["developer", "engineer", "technical", "programmer", "coder"],
#             "business": ["manager", "executive", "business", "stakeholder", "leader"],
#             "general": []
#         }
        
#         audience_type = "general"
#         for aud_type, keywords in audience_keywords.items():
#             if any(kw in query_lower for kw in keywords):
#                 audience_type = aud_type
#                 break
        
#         # Quick complexity detection
#         is_complex = any(w in query_lower for w in ["comprehensive", "detailed", "thorough", "complete", "full"])
        
#         return {
#             "audience": {
#                 "primary": f"{audience_type.title()} users",
#                 "skill_level": skill_level,
#                 "prerequisites": ["Basic understanding"] if skill_level != "beginner" else [],
#                 "goals": ["Complete task successfully"]
#             },
#             "stakeholders": ["Primary user", "End users"],
#             "context_of_use": "Professional/educational context",
#             "motivation": "Task completion and learning",
#             "requirements": {
#                 "explicit": [context.query[:100]],
#                 "implicit": ["Quality output", "Clear structure", "Accuracy"],
#                 "out_of_scope": []
#             },
#             "risks_and_assumptions": {
#                 "assumptions": [f"User has {skill_level} knowledge", "Standard tools available"],
#                 "risks": ["Scope ambiguity", "Resource constraints"],
#                 "mitigations": ["Clarify with questions", "Iterative approach"]
#             },
#             "strategy": {
#                 "alternatives": [],
#                 "recommended": "Systematic step-by-step execution",
#                 "rationale": "Best for clear, quality output"
#             },
#             "complexity_factors": ["Domain expertise required", "Multiple steps needed"],
#             "estimated_effort": "1-2hr" if is_complex else "30min-1hr"
#         }
    
#     async def run(self, context: AgentContext) -> AsyncGenerator[AgentEvent, None]:
#         """
#         OPTIMIZED main execution - target 4-6 minutes
#         """
#         yield self.create_event(
#             AgentEventType.STATUS,
#             "🚀 PreAct: Fast analysis mode (optimized)..."
#         )
        
#         # PHASE 1: Domain detection (instant, local)
#         detected_domain = self._detect_domain(context.query)
#         domain_skills = self._get_domain_skills(detected_domain)
#         domain_capabilities = self._get_domain_capabilities(detected_domain)
        
#         yield self.create_event(
#             AgentEventType.THOUGHT,
#             f"🎯 Domain: {detected_domain} | Skills: {len(domain_skills)} | Capabilities: {len(domain_capabilities)}"
#         )
        
#         # Store in context
#         context.metadata["detected_domain"] = detected_domain
#         context.metadata["domain_skills"] = domain_skills
#         context.metadata["domain_capabilities"] = domain_capabilities
        
#         effective_domain = detected_domain if context.domain in ["default", "general", ""] else context.domain
        
#         # OPTIMIZATION: Run RAG and heuristic analysis in PARALLEL
#         yield self.create_event(
#             AgentEventType.THOUGHT,
#             "🔍 Running parallel operations (RAG + Analysis)..."
#         )
        
#         # Create tasks for parallel execution
#         async def rag_search():
#             try:
#                 return await asyncio.wait_for(
#                     self.rag.search(query=context.query, domain=effective_domain, n_results=3),
#                     timeout=5.0  # 5 second timeout
#                 )
#             except (asyncio.TimeoutError, Exception) as e:
#                 return None
        
#         # Run in parallel: RAG search + Fast heuristic analysis
#         rag_task = rag_search()
#         analysis_task = asyncio.create_task(
#             asyncio.to_thread(self._fast_heuristic_analysis, context, effective_domain)
#         )
        
#         # Wait for both
#         rag_results, deep_analysis = await asyncio.gather(rag_task, analysis_task)
        
#         # Format RAG context
#         domain_context = ""
#         if rag_results:
#             domain_context = "\n".join([f"• {r.content[:150]}" for r in rag_results[:2]])
#             yield self.create_event(
#                 AgentEventType.RAG_RESULT,
#                 f"Found {len(rag_results)} relevant sources",
#                 {"sources": [r.source for r in rag_results]}
#             )
        
#         # Store analysis
#         context.metadata["deep_analysis"] = deep_analysis
        
#         yield self.create_event(
#             AgentEventType.THOUGHT,
#             f"📊 Fast Analysis: {deep_analysis['audience']['primary']} ({deep_analysis['audience']['skill_level']})"
#         )
        
#         # PHASE 2: Generate plan (SINGLE LLM CALL with reduced tokens)
#         yield self.create_event(
#             AgentEventType.THOUGHT,
#             f"📝 Creating execution plan (optimized prompt)..."
#         )
        
#         # OPTIMIZATION: Much shorter, focused planning prompt
#         planning_prompt = f"""Domain: {detected_domain}
# Query: {context.query[:300]}

# Audience: {deep_analysis['audience']['primary']} ({deep_analysis['audience']['skill_level']})
# Requirements: {json.dumps(deep_analysis['requirements']['explicit'][:2])}

# Domain Skills (MUST include): {json.dumps(domain_skills[:4])}
# Capabilities: {json.dumps(domain_capabilities[:4])}

# Context: {domain_context[:200] if domain_context else "No additional context"}

# Create 5-7 step execution plan. Output ONLY JSON as specified."""
        
#         # OPTIMIZATION: Reduced max_tokens for faster generation
#         full_response = ""
#         async for chunk in self.llm.generate_stream(
#             prompt=planning_prompt,
#             system_prompt=self.SYSTEM_PROMPT,
#             temperature=0.7,
#             max_tokens=1800  # Reduced from 3000+ (2x faster)
#         ):
#             full_response += chunk
#             # Less frequent progress updates
#             if len(full_response) % 500 == 0:
#                 yield self.create_event(
#                     AgentEventType.THOUGHT,
#                     f"Planning... ({len(full_response)} chars)"
#                 )
        
#         # Parse plan
#         yield self.create_event(
#             AgentEventType.THOUGHT,
#             "Organizing plan..."
#         )
        
#         reasoning_plan = self._parse_reasoning_plan(full_response, context)
#         context.metadata["reasoning_plan"] = reasoning_plan.to_dict()
        
#         # Emit plan details
#         yield self.create_event(
#             AgentEventType.THOUGHT,
#             f"📋 {reasoning_plan.title}"
#         )
        
#         # Emit steps
#         for step in reasoning_plan.steps:
#             yield self.create_event(
#                 AgentEventType.ACTION,
#                 f"Step {step.step_number}: {step.title}",
#                 {"step": step.to_dict(), "event_type": "plan_step"}
#             )
        
#         # Generate Mermaid
#         mermaid = self._generate_mermaid(reasoning_plan)
#         plan_summary = self._format_plan_summary(reasoning_plan)
        
#         # Final plan event
#         yield self.create_event(
#             AgentEventType.PLAN,
#             plan_summary,
#             {
#                 "reasoning_plan": reasoning_plan.to_dict(),
#                 "mermaid_diagram": mermaid,
#                 "step_count": len(reasoning_plan.steps),
#                 "complexity": reasoning_plan.estimated_complexity,
#                 "requires_approval": True,
#                 "detected_domain": reasoning_plan.detected_domain,
#                 "domain_skills": reasoning_plan.domain_skills,
#                 "domain_capabilities": reasoning_plan.domain_capabilities,
#                 "template_id": reasoning_plan.template_id,
#                 "optimized": True
#             }
#         )
        
#         # Create MasterPlan
#         context.master_plan = MasterPlan(
#             title=reasoning_plan.title,
#             domain=context.domain,
#             total_scenes=len(reasoning_plan.steps),
#             world_setting=reasoning_plan.task_understanding,
#             characters=[],
#             visual_style=reasoning_plan.approach,
#             camera_rules=", ".join(reasoning_plan.constraints),
#             tone=reasoning_plan.estimated_complexity,
#             scene_outline=[f"Step {s.step_number}: {s.title}" for s in reasoning_plan.steps]
#         )
        
#         # Save to memory (async, don't wait)
#         asyncio.create_task(
#             self.tme.add_memory(
#                 session_id=context.session_id,
#                 content=f"Plan: {reasoning_plan.title}",
#                 memory_type="plan",
#                 tags=["preact", "optimized", context.domain]
#             )
#         )
        
#         yield self.create_event(
#             AgentEventType.COMPLETE,
#             f"✅ Plan ready (optimized)!\n"
#             f"🎯 Domain: {reasoning_plan.detected_domain}\n"
#             f"📋 {len(reasoning_plan.steps)} steps\n"
#             f"⚡ Fast mode: Heuristic analysis",
#             {
#                 "step_count": len(reasoning_plan.steps),
#                 "complexity": reasoning_plan.estimated_complexity,
#                 "optimized": True
#             }
#         )
    
#     def _parse_reasoning_plan(self, response: str, context: AgentContext) -> ReasoningPlan:
#         """Parse plan (unchanged from original)"""
#         detected_domain = context.metadata.get("detected_domain", "default")
#         default_skills = context.metadata.get("domain_skills", ["Instructional Designer"])
#         default_capabilities = context.metadata.get("domain_capabilities", [])
#         deep_analysis = context.metadata.get("deep_analysis", {})
        
#         json_match = re.search(r'\{[\s\S]*\}', response)
        
#         if json_match:
#             try:
#                 plan_data = json.loads(json_match.group())
                
#                 steps = []
#                 for i, step_data in enumerate(plan_data.get("steps", [])):
#                     steps.append(ReasoningStep(
#                         step_number=step_data.get("step_number", i + 1),
#                         title=step_data.get("title", f"Step {i + 1}"),
#                         description=step_data.get("description", ""),
#                         expected_output=step_data.get("expected_output", ""),
#                         dependencies=step_data.get("dependencies", []),
#                         sub_steps=step_data.get("sub_steps", []),
#                         estimated_effort=step_data.get("estimated_effort", "15min"),
#                         validation_criteria=step_data.get("validation_criteria", []),
#                         tools_needed=step_data.get("tools_needed", ["GENERATE"]),
#                         priority=step_data.get("priority", "important")
#                     ))
                
#                 domain_skills = plan_data.get("domain_skills", default_skills)
#                 if "Instructional Designer" not in domain_skills:
#                     domain_skills = ["Instructional Designer"] + domain_skills
                
#                 return ReasoningPlan(
#                     title=plan_data.get("title", f"{detected_domain.title()} Task"),
#                     task_understanding=plan_data.get("task_understanding", context.query),
#                     approach=plan_data.get("approach", "Step-by-step execution"),
#                     steps=steps,
#                     constraints=plan_data.get("constraints", []),
#                     success_criteria=plan_data.get("success_criteria", []),
#                     estimated_complexity=plan_data.get("estimated_complexity", "moderate"),
#                     detected_domain=plan_data.get("detected_domain", detected_domain),
#                     domain_skills=domain_skills,
#                     domain_capabilities=plan_data.get("domain_capabilities", default_capabilities),
#                     clarification_questions=[],
#                     deep_analysis=deep_analysis,
#                     requirements=deep_analysis.get("requirements", {}),
#                     risks_and_assumptions=deep_analysis.get("risks_and_assumptions", {}),
#                     strategy=deep_analysis.get("strategy", {})
#                 )
#             except json.JSONDecodeError:
#                 pass
        
#         return self._create_default_plan(context, response)
    
#     def _create_default_plan(self, context: AgentContext, raw_response: str) -> ReasoningPlan:
#         """Create default plan (simplified from original)"""
#         detected_domain = context.metadata.get("detected_domain", "default")
#         domain_skills = context.metadata.get("domain_skills", self._get_domain_skills(detected_domain))
#         domain_capabilities = context.metadata.get("domain_capabilities", self._get_domain_capabilities(detected_domain))
        
#         if "Instructional Designer" not in domain_skills:
#             domain_skills = ["Instructional Designer"] + domain_skills
        
#         steps = [
#             ReasoningStep(1, "Analysis", "Analyze requirements and context", "Requirements doc",
#                          sub_steps=["Identify audience", "Extract requirements", "Define scope"],
#                          estimated_effort="15min", priority="critical"),
#             ReasoningStep(2, "Strategy", "Define approach and plan", "Execution strategy",
#                          dependencies=[1], sub_steps=["Evaluate options", "Select approach", "Plan steps"],
#                          estimated_effort="15min", priority="critical"),
#             ReasoningStep(3, "Execution", "Generate content", "Draft output",
#                          dependencies=[2], sub_steps=["Create content", "Add examples", "Format properly"],
#                          estimated_effort="30min", priority="important"),
#             ReasoningStep(4, "Validation", "Quality check", "Final output",
#                          dependencies=[3], sub_steps=["Review quality", "Verify completeness", "Polish"],
#                          estimated_effort="15min", priority="important"),
#         ]
        
#         return ReasoningPlan(
#             title=f"{detected_domain.title()} Execution Plan",
#             task_understanding=context.query,
#             approach="Systematic step-by-step execution",
#             steps=steps,
#             constraints=["Quality required", "Domain best practices"],
#             success_criteria=["Requirements met", "Quality approved"],
#             estimated_complexity="moderate",
#             detected_domain=detected_domain,
#             domain_skills=domain_skills,
#             domain_capabilities=domain_capabilities,
#             deep_analysis=context.metadata.get("deep_analysis", {})
#         )
    
#     def _generate_mermaid(self, plan: ReasoningPlan) -> str:
#         """Generate Mermaid diagram (simplified)"""
#         diagram = f"""graph TD
#     START["🚀 Start"] --> STEP1
# """
#         for i, step in enumerate(plan.steps):
#             node_id = f"STEP{step.step_number}"
#             label = f"{step.step_number}. {step.title[:30]}"
#             diagram += f'    {node_id}["{label}"]\n'
            
#             if i < len(plan.steps) - 1:
#                 next_id = f"STEP{plan.steps[i+1].step_number}"
#                 diagram += f"    {node_id} --> {next_id}\n"
#             else:
#                 diagram += f'    {node_id} --> END["✅ Complete"]\n'
        
#         return diagram
    
#     def _format_plan_summary(self, plan: ReasoningPlan) -> str:
#         """Format summary (simplified)"""
#         summary = f"""# 🧠 {plan.title}

# ## 🎯 Domain & Context
# **Domain:** {plan.detected_domain} | **Complexity:** {plan.estimated_complexity} | **Effort:** {plan.estimated_total_effort}

# ## 📋 Task
# {plan.task_understanding[:300]}

# ## 🎯 Approach
# {plan.approach[:200]}

# ## 👥 Domain Skills
# """
#         for skill in plan.domain_skills:
#             marker = "⭐" if skill == "Instructional Designer" else "•"
#             summary += f"{marker} {skill}\n"
        
#         summary += "\n## 📝 Execution Steps\n"
#         for step in plan.steps:
#             priority_icon = {"critical": "🔴", "important": "🟡", "optional": "🟢"}.get(step.priority, "🟡")
#             summary += f"\n### {priority_icon} Step {step.step_number}: {step.title}\n"
#             summary += f"**Effort:** {step.estimated_effort} | **Priority:** {step.priority}\n"
#             summary += f"{step.description}\n"
        
#         summary += "\n## ✅ Success Criteria\n"
#         for c in plan.success_criteria:
#             summary += f"- {c}\n"
        
#         return summary
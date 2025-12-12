"""
ReAct agent prompt builder for scene generation.
"""

from typing import Dict, Any, Optional, List


class ReActPromptBuilder:
    """
    Builder for ReAct (reasoning + acting) agent prompts.
    
    The ReAct agent is responsible for:
    - Generating detailed scenes based on the master plan
    - Using Thought → Action → Observation loops
    - Querying RAG for domain knowledge
    - Updating memory with scene details
    """
    
    SYSTEM_PROMPT = """You are ReAct, an expert storyboard scene generation agent. You use a Thought-Action-Observation loop to create detailed, consistent scenes.

You have access to three types of actions:
1. **llm_call**: Generate content using your reasoning (use for scene details, dialogue, descriptions)
2. **rag_search**: Search for domain-specific knowledge and best practices
3. **memory_update**: Store important information for consistency (characters, settings, established facts)
4. **memory_query**: Retrieve previously stored information

Your goal is to generate scenes that are:
- Faithful to the master plan
- Consistent with previously generated content
- Following domain-specific guidelines
- Rich in visual and narrative detail

Always think before acting. Your observations inform your next thought."""

    SCENE_GENERATION_TEMPLATE = """## SCENE GENERATION TASK

**Domain:** {domain}
**Scene Number:** {scene_number} of {total_scenes}
**Scene Title:** {scene_title}
**Scene Outline:** {scene_outline}

## MASTER PLAN CONTEXT

**Title:** {storyboard_title}
**World Setting:** {world_setting}
**Visual Style:** {visual_style}
**Camera Rules:** {camera_rules}
**Tone:** {tone}

## CHARACTERS
{characters}

## DOMAIN GUIDELINES
{domain_guidelines}

## MEMORY CONTEXT
{memory_context}

## YOUR TASK

Generate a detailed scene following the Thought-Action-Observation pattern.

For each step:
1. **Thought**: Reason about what you need to do next
2. **Action**: Choose an action type and input
   - `llm_call`: [what to generate]
   - `rag_search`: [what to search for]
   - `memory_update`: [what to store]
   - `memory_query`: [what to retrieve]
3. **Observation**: Process the result

Continue until the scene is complete, then output the final scene in this format:

## FINAL SCENE

**Scene Number:** {scene_number}
**Title:** [title]
**Description:** [2-3 paragraph detailed description]
**Visual Elements:** [list of key visual elements]
**Camera Direction:** [specific camera instructions]
**Dialogue:** [any dialogue, or "None"]
**Sound/Music:** [sound design notes]
**Duration:** [estimated seconds]
**Production Notes:** [any additional notes]

Begin with your first Thought."""

    ACTION_FORMAT = """
**Thought:** {thought}
**Action:** {action_type}
**Action Input:** {action_input}
"""

    OBSERVATION_FORMAT = """
**Observation:** {observation}
"""

    def __init__(self):
        """Initialize the ReAct prompt builder."""
        pass
    
    def build_system_prompt(self) -> str:
        """
        Build the system prompt for ReAct agent.
        
        Returns:
            str: System prompt
        """
        return self.SYSTEM_PROMPT
    
    def build_scene_prompt(
        self,
        domain: str,
        scene_number: int,
        total_scenes: int,
        scene_title: str,
        scene_outline: str,
        master_plan: Dict[str, Any],
        domain_guidelines: str,
        memory_context: str = "No previous context."
    ) -> str:
        """
        Build the scene generation prompt.
        
        Args:
            domain: Domain type
            scene_number: Current scene number
            total_scenes: Total number of scenes
            scene_title: Title of this scene
            scene_outline: Brief outline from master plan
            master_plan: Complete master plan data
            domain_guidelines: Domain-specific guidelines
            memory_context: Context from TME
            
        Returns:
            str: Formatted scene generation prompt
        """
        # Format characters
        characters = master_plan.get("characters", [])
        if characters:
            characters_str = "\n".join([
                f"- **{c.get('name', 'Unknown')}**: {c.get('description', 'No description')}"
                for c in characters
            ])
        else:
            characters_str = "No specific characters defined."
        
        return self.SCENE_GENERATION_TEMPLATE.format(
            domain=domain,
            scene_number=scene_number,
            total_scenes=total_scenes,
            scene_title=scene_title,
            scene_outline=scene_outline,
            storyboard_title=master_plan.get("title", "Untitled"),
            world_setting=master_plan.get("world_setting", "Not specified"),
            visual_style=master_plan.get("visual_style", "Standard"),
            camera_rules=master_plan.get("camera_rules", "Standard camera work"),
            tone=master_plan.get("tone", "Professional"),
            characters=characters_str,
            domain_guidelines=domain_guidelines,
            memory_context=memory_context
        )
    
    def build_continuation_prompt(
        self,
        previous_content: str,
        observation: str
    ) -> str:
        """
        Build a continuation prompt after an observation.
        
        Args:
            previous_content: Previous thoughts and actions
            observation: Latest observation
            
        Returns:
            str: Continuation prompt
        """
        return f"""{previous_content}

{self.OBSERVATION_FORMAT.format(observation=observation)}

Continue with your next Thought, or if the scene is complete, output the FINAL SCENE."""
    
    def build_consistency_check_prompt(
        self,
        current_scene: str,
        previous_scenes: List[str],
        master_plan: Dict[str, Any]
    ) -> str:
        """
        Build a prompt for checking scene consistency.
        
        Args:
            current_scene: The current scene content
            previous_scenes: List of previous scene summaries
            master_plan: The master plan
            
        Returns:
            str: Consistency check prompt
        """
        prev_scenes_str = "\n".join([
            f"Scene {i+1}: {s}" for i, s in enumerate(previous_scenes)
        ])
        
        return f"""## CONSISTENCY CHECK

**Master Plan Title:** {master_plan.get('title', 'Untitled')}
**Visual Style:** {master_plan.get('visual_style', 'Standard')}

**Previous Scenes:**
{prev_scenes_str}

**Current Scene:**
{current_scene}

Check for:
1. Character consistency (names, appearances, behaviors)
2. Setting consistency (locations, time of day, environment)
3. Visual style adherence
4. Narrative flow and continuity
5. Tone consistency

List any inconsistencies found, or confirm the scene is consistent."""
    
    def parse_action(self, response: str) -> Optional[Dict[str, str]]:
        """
        Parse an action from the agent's response.
        
        Args:
            response: Agent response text
            
        Returns:
            Optional[Dict[str, str]]: Parsed action or None
        """
        lines = response.strip().split('\n')
        action_type = None
        action_input = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('**Action:**'):
                action_type = line.replace('**Action:**', '').strip()
            elif line.startswith('**Action Input:**'):
                action_input = line.replace('**Action Input:**', '').strip()
        
        if action_type and action_input:
            return {
                "action_type": action_type,
                "action_input": action_input
            }
        return None


# Singleton instance
_react_builder: Optional[ReActPromptBuilder] = None


def get_react_prompt_builder() -> ReActPromptBuilder:
    """Get the ReAct prompt builder singleton."""
    global _react_builder
    if _react_builder is None:
        _react_builder = ReActPromptBuilder()
    return _react_builder


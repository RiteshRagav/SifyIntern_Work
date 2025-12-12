"""
ReFlect agent prompt builder for storyboard review and refinement.
"""

from typing import Dict, Any, Optional, List
from models.schemas import Scene


class ReFlectPromptBuilder:
    """
    Builder for ReFlect (reflection) agent prompts.
    
    The ReFlect agent is responsible for:
    - Analyzing the complete storyboard
    - Checking narrative coherence
    - Ensuring visual consistency
    - Fixing issues and enhancing quality
    - Producing the final polished storyboard
    """
    
    SYSTEM_PROMPT = """You are ReFlect, an expert storyboard review and refinement agent. Your role is to analyze completed storyboards, identify issues, and enhance their quality.

You excel at:
- Narrative analysis and story flow
- Visual consistency checking
- Tone and style coherence
- Identifying plot holes or continuity errors
- Enhancing descriptions for clarity and impact

Your goal is to produce a polished, professional storyboard that meets the highest standards."""

    REVIEW_TEMPLATE = """## STORYBOARD REVIEW TASK

**Domain:** {domain}
**Title:** {title}
**Original Query:** {query}

## MASTER PLAN

**World Setting:** {world_setting}
**Visual Style:** {visual_style}
**Tone:** {tone}

## SCENES TO REVIEW

{scenes_content}

## DOMAIN GUIDELINES

{domain_guidelines}

## YOUR TASK

Perform a comprehensive review of this storyboard:

### 1. NARRATIVE ANALYSIS
- Is the story flow logical and engaging?
- Are there any plot holes or continuity errors?
- Does the pacing work for the domain?
- Is the beginning compelling and the ending satisfying?

### 2. VISUAL CONSISTENCY
- Are visual elements consistent across scenes?
- Does each scene follow the established visual style?
- Are camera directions appropriate and varied?
- Are there any visual continuity issues?

### 3. TONE & STYLE
- Is the tone consistent throughout?
- Does it match the domain requirements?
- Is the language appropriate for the audience?

### 4. TECHNICAL QUALITY
- Are descriptions clear and actionable?
- Are there any missing elements in any scene?
- Are durations appropriate?

### 5. IMPROVEMENTS
For each issue found, provide:
- The scene number
- The issue description
- The recommended fix

After your review, provide the FINAL STORYBOARD with all improvements incorporated."""

    SCENE_FORMAT = """
### Scene {scene_number}: {title}

**Description:** {description}

**Visual Elements:** {visual_elements}

**Camera Direction:** {camera_direction}

**Dialogue:** {dialogue}

**Sound/Music:** {sound}

**Duration:** {duration}s

**Notes:** {notes}
"""

    ENHANCEMENT_TEMPLATE = """## SCENE ENHANCEMENT TASK

**Scene Number:** {scene_number}
**Current Content:**
{current_content}

**Issues Identified:**
{issues}

**Enhancement Guidelines:**
{guidelines}

## YOUR TASK

Enhance this scene to address the identified issues while maintaining consistency with the overall storyboard.

Provide the enhanced scene in the standard format."""

    FINAL_OUTPUT_TEMPLATE = """## FINAL STORYBOARD

**Title:** {title}
**Domain:** {domain}
**Total Scenes:** {total_scenes}

### Overview
{overview}

### Visual Style Guide
{visual_style}

### Scenes

{scenes}

### Production Notes
{production_notes}
"""

    def __init__(self):
        """Initialize the ReFlect prompt builder."""
        pass
    
    def build_system_prompt(self) -> str:
        """
        Build the system prompt for ReFlect agent.
        
        Returns:
            str: System prompt
        """
        return self.SYSTEM_PROMPT
    
    def build_review_prompt(
        self,
        domain: str,
        title: str,
        query: str,
        master_plan: Dict[str, Any],
        scenes: List[Scene],
        domain_guidelines: str
    ) -> str:
        """
        Build the review prompt for the complete storyboard.
        
        Args:
            domain: Domain type
            title: Storyboard title
            query: Original user query
            master_plan: Master plan data
            scenes: List of generated scenes
            domain_guidelines: Domain-specific guidelines
            
        Returns:
            str: Formatted review prompt
        """
        # Format scenes
        scenes_content = ""
        for scene in scenes:
            scenes_content += self.SCENE_FORMAT.format(
                scene_number=scene.scene_number,
                title=scene.title,
                description=scene.description,
                visual_elements=", ".join(scene.visual_elements) if scene.visual_elements else "None specified",
                camera_direction=scene.camera_direction or "Standard",
                dialogue=scene.dialogue or "None",
                sound=scene.sound_effects or "Standard ambient",
                duration=scene.duration_seconds or "TBD",
                notes=scene.notes or "None"
            )
        
        return self.REVIEW_TEMPLATE.format(
            domain=domain,
            title=title,
            query=query,
            world_setting=master_plan.get("world_setting", "Not specified"),
            visual_style=master_plan.get("visual_style", "Standard"),
            tone=master_plan.get("tone", "Professional"),
            scenes_content=scenes_content,
            domain_guidelines=domain_guidelines
        )
    
    def build_enhancement_prompt(
        self,
        scene_number: int,
        current_content: str,
        issues: List[str],
        guidelines: str
    ) -> str:
        """
        Build a prompt for enhancing a specific scene.
        
        Args:
            scene_number: Scene to enhance
            current_content: Current scene content
            issues: List of issues to address
            guidelines: Enhancement guidelines
            
        Returns:
            str: Enhancement prompt
        """
        issues_str = "\n".join([f"- {issue}" for issue in issues])
        
        return self.ENHANCEMENT_TEMPLATE.format(
            scene_number=scene_number,
            current_content=current_content,
            issues=issues_str,
            guidelines=guidelines
        )
    
    def build_coherence_check_prompt(
        self,
        scenes: List[Scene]
    ) -> str:
        """
        Build a prompt for checking overall coherence.
        
        Args:
            scenes: All scenes in the storyboard
            
        Returns:
            str: Coherence check prompt
        """
        scene_summaries = "\n".join([
            f"Scene {s.scene_number}: {s.title} - {s.description[:100]}..."
            for s in scenes
        ])
        
        return f"""## COHERENCE CHECK

Review these scene summaries for narrative coherence:

{scene_summaries}

Check for:
1. Logical story progression
2. Character consistency
3. Setting continuity
4. Cause-and-effect relationships
5. Emotional arc progression

Identify any coherence issues and suggest fixes."""
    
    def build_final_output_prompt(
        self,
        title: str,
        domain: str,
        overview: str,
        visual_style: str,
        scenes: List[Scene],
        production_notes: str = ""
    ) -> str:
        """
        Build the final storyboard output.
        
        Args:
            title: Storyboard title
            domain: Domain type
            overview: Storyboard overview
            visual_style: Visual style guide
            scenes: All scenes
            production_notes: Additional notes
            
        Returns:
            str: Final formatted storyboard
        """
        scenes_str = ""
        for scene in scenes:
            scenes_str += self.SCENE_FORMAT.format(
                scene_number=scene.scene_number,
                title=scene.title,
                description=scene.description,
                visual_elements=", ".join(scene.visual_elements) if scene.visual_elements else "None",
                camera_direction=scene.camera_direction or "Standard",
                dialogue=scene.dialogue or "None",
                sound=scene.sound_effects or "Standard",
                duration=scene.duration_seconds or "TBD",
                notes=scene.notes or "None"
            )
        
        return self.FINAL_OUTPUT_TEMPLATE.format(
            title=title,
            domain=domain,
            total_scenes=len(scenes),
            overview=overview,
            visual_style=visual_style,
            scenes=scenes_str,
            production_notes=production_notes or "No additional notes."
        )


# Singleton instance
_reflect_builder: Optional[ReFlectPromptBuilder] = None


def get_reflect_prompt_builder() -> ReFlectPromptBuilder:
    """Get the ReFlect prompt builder singleton."""
    global _reflect_builder
    if _reflect_builder is None:
        _reflect_builder = ReFlectPromptBuilder()
    return _reflect_builder


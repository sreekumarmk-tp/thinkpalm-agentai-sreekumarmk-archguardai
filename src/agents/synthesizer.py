import re
import time
from typing import Dict, List
from src.utils.llm_factory import get_llm

def synthesize_report(
    repo_url: str,
    model_candidates: List[str],
    specialist_outputs: Dict[str, str],
    memory_context: str,
    max_attempts_per_model: int,
    base_backoff_seconds: int,
    status_callback=None,
) -> str:
    synthesis_instructions = (
        f"Create a final detailed architecture and engineering report for {repo_url}.\n"
        "Use specialist findings provided below.\n"
        "Output sections:\n"
        "1) Executive Summary\n"
        "2) Overall Risk Posture and Health Score\n"
        "3) Detailed section for each specialist (including Testing & QA and Directory Structure)\n"
        "4) Top 10 prioritized fixes\n"
        "5) 30/60/90 day implementation roadmap\n"
        "6) Visualization Section:\n"
        "   - **Architecture Diagram**: High-level structural view of components and their relationships.\n"
        "   - **Functional Flow Diagram**: Sequential or logical flow of a primary business/technical process.\n"
        "   - **IMPORTANT**: Provide exactly these two diagrams using Mermaid syntax. Encapsulate each in a separate '```mermaid' code block.\n"
        "7) Comparative Analysis Table:\n"
        "   - A Markdown table comparing Current Architecture vs. Industry Best Practices across Security, Performance, Scalability, and Maintainability.\n"
        "8) Conclusion\n\n"
        f"Use this memory context from previous runs when relevant:\n{memory_context}\n\n"
        "Be specific, practical and evidence-based. Keep the response in clean markdown."
    )

    merged = []
    for agent_name, content in specialist_outputs.items():
        merged.append(f"## {agent_name}\n{content}")
    final_input = synthesis_instructions + "\n\n" + "\n\n".join(merged)

    errors: List[str] = []
    for model_name in model_candidates:
        for attempt in range(1, max_attempts_per_model + 1):
            if status_callback:
                status_msg = f"{model_name}"
                if max_attempts_per_model > 1:
                    status_msg += f" (Attempt {attempt}/{max_attempts_per_model})"
                status_callback(status_msg)
            
            try:
                llm = get_llm(model_name=model_name, temperature=0.1) # Slight temperature for variety in retries
                response = llm.invoke(final_input)
                report = response.content
                
                # Validation: Ensure at least one Mermaid diagram is present
                # and that it has some basic structure.
                mermaid_blocks = re.findall(r"```mermaid\s*[\n\r]([\s\S]*?)```", report)
                
                is_valid = True
                if not mermaid_blocks:
                    is_valid = False
                else:
                    for block in mermaid_blocks:
                        if len(block.strip()) < 20: # Arbitrary small size
                            is_valid = False
                
                if not is_valid and attempt == 1:
                    # If the first attempt failed validation, try once more with a stronger nudge
                    if status_callback:
                        status_callback(f"{model_name} (Retrying with diagram nudge...)")
                    nudge_input = final_input + "\n\nCRITICAL: Your previous response missed the required Mermaid diagrams or they were empty. Please ensure you provide both the 'Architecture Diagram' and 'Functional Flow Diagram' in valid ```mermaid blocks."
                    response = llm.invoke(nudge_input)
                    report = response.content
                    
                return report
            except Exception as exc:
                exc_str = str(exc)
                errors.append(f"{model_name} [Attempt {attempt}]: {exc_str}")
                
                is_last_attempt = (attempt == max_attempts_per_model)
                is_last_model = (model_name == model_candidates[-1])
                
                if not (is_last_attempt and is_last_model):
                    time.sleep(base_backoff_seconds)

    error_details = "\n".join(errors[:5])
    raise Exception(
        "Report Synthesis failed after trying all fallback models.\n"
        f"Recent errors:\n{error_details}"
    )

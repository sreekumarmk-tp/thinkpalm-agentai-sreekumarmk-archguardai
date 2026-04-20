import time
from typing import Dict, List, Tuple, Type
from src.agents.specialists.base import BaseSpecialistAgent
from src.agents.specialists.architect import ArchitectSpecialist
from src.agents.specialists.security import SecuritySpecialist
from src.agents.specialists.performance import PerformanceSpecialist

class SpecialistFactory:
    _agents: Dict[str, Type[BaseSpecialistAgent]] = {
        "architect_design": ArchitectSpecialist,
        "security_quality": SecuritySpecialist,
        "performance_testing": PerformanceSpecialist,
    }

    @classmethod
    def get_agent(cls, agent_id: str) -> BaseSpecialistAgent:
        agent_class = cls._agents.get(agent_id)
        if not agent_class:
            raise ValueError(f"Unknown specialist agent ID: {agent_id}")
        return agent_class()

    @classmethod
    def get_active_definitions(cls, active_ids: List[str]) -> List[Dict[str, str]]:
        """Returns metadata for the requested active agents."""
        defs = []
        for aid in active_ids:
            agent = cls.get_agent(aid)
            defs.append({
                "id": agent.id,
                "title": agent.title,
                "objective": agent.objective
            })
        return defs

    @classmethod
    def run_agent_with_retries(
        cls,
        repo_url: str,
        agent_id: str,
        model_candidates: List[str],
        max_attempts_per_model: int,
        base_backoff_seconds: int,
        memory_context: str,
        status_callback=None,
    ) -> Tuple[str, str]:
        """
        Generic runner that handles model fallbacks and retries for specialist agents.
        """
        agent = cls.get_agent(agent_id)
        errors: List[str] = []
        
        for model_name in model_candidates:
            for attempt in range(1, max_attempts_per_model + 1):
                if status_callback:
                    status_msg = f"{model_name}"
                    if max_attempts_per_model > 1:
                        status_msg += f" (Attempt {attempt}/{max_attempts_per_model})"
                    status_callback(status_msg)
                
                try:
                    # We reuse the agent's run method which handles the tool setup and LLM execution
                    content = agent.run(repo_url, model_name, memory_context)
                    return content, model_name
                except Exception as exc:
                    exc_str = str(exc)
                    errors.append(f"{model_name} [Attempt {attempt}]: {exc_str}")
                    
                    # Backoff before next attempt or next model
                    is_last_attempt = (attempt == max_attempts_per_model)
                    is_last_model = (model_name == model_candidates[-1])
                    
                    if not (is_last_attempt and is_last_model):
                        time.sleep(base_backoff_seconds)
                    
        error_details = "\n".join(errors[:10])
        raise Exception(
            f"Agent '{agent.title}' execution failed after trying all fallback models and retry attempts.\n"
            f"Recent errors:\n{error_details}"
        )

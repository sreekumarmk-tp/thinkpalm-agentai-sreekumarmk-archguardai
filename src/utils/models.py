import requests
from typing import Set, List
from src.config.settings import (
    OPENROUTER_MODELS_API,
    GROQ_MODELS_API,
    GROQ_API_KEY,
    GITHUB_TIMEOUT,
    FREE_MODEL_PREFERENCES,
    GROQ_MODELS,
    OPENROUTER_MODELS
)

def fetch_available_openrouter_models() -> Set[str]:
    try:
        res = requests.get(OPENROUTER_MODELS_API, timeout=GITHUB_TIMEOUT)
        res.raise_for_status()
        data = res.json().get("data", [])
        free_models = set()
        for model in data:
            model_id = model.get("id", "")
            if model_id.endswith(":free"):
                free_models.add(model_id)
        return free_models
    except Exception:
        return set()

def fetch_available_groq_models() -> Set[str]:
    if not GROQ_API_KEY:
        return set()
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        res = requests.get(GROQ_MODELS_API, headers=headers, timeout=GITHUB_TIMEOUT)
        res.raise_for_status()
        data = res.json().get("data", [])
        return {m.get("id") for m in data if m.get("id")}
    except Exception:
        return set()



def get_model_candidates_for_agent(
    agent_id: str, 
    available_openrouter_models: Set[str], 
    provider: str = "groq",
    available_groq_models: Set[str] = None
) -> List[str]:
    provider = provider.lower()
    
    pref_dict = FREE_MODEL_PREFERENCES.get(agent_id, FREE_MODEL_PREFERENCES["report_synthesizer"])
    preferred = pref_dict.get(provider, [])

    if provider == "groq":
        # Candidates = Preferred (suggested) + any other Groq models from .env
        # Plus any other dynamically discovered Groq models
        candidates = [f"groq/{m}" for m in preferred]
        
        # Add from GROQ_MODELS (env defaults)
        for m in GROQ_MODELS:
            if f"groq/{m}" not in candidates:
                candidates.append(f"groq/{m}")
                
        # Add from dynamically discovered available_groq_models
        if available_groq_models:
            for m in sorted(available_groq_models):
                if f"groq/{m}" not in candidates:
                    candidates.append(f"groq/{m}")
                    
        return candidates

    # OpenRouter logic
    preferred_with_prefix = [f"openrouter/{m}" for m in preferred]
    
    # Priority: Preferred models (even if not verified free yet, per user instruction to try suggested first)
    # Plus discovered available free models
    remaining = [f"openrouter/{m}" for m in sorted(available_openrouter_models) if f"openrouter/{m}" not in preferred_with_prefix]
    
    if not available_openrouter_models:
        remaining = [f"openrouter/{m}" for m in OPENROUTER_MODELS if f"openrouter/{m}" not in preferred_with_prefix]

    candidates = preferred_with_prefix + remaining
    return candidates

import json
import streamlit as st
from typing import Dict
from src.config.settings import (
    MAX_ATTEMPTS_PER_MODEL,
    BASE_BACKOFF_SECONDS,
    RUN_SPECIALISTS_IN_PARALLEL
)
from src.utils.export import export_to_docx

def build_json_export(
    repo_url: str,
    run_id: str,
    generated_at_utc: str,
    active_preset: str,
    max_attempts_per_model: int,
    base_backoff_seconds: int,
    selected_models: Dict[str, str],
    synthesizer_model: str,
    specialist_results: Dict[str, str],
    final_report: str,
) -> str:
    payload = {
        "repository": repo_url,
        "run_metadata": {
            "run_id": run_id,
            "generated_at_utc": generated_at_utc,
        },
        "run_configuration": {
            "preset": active_preset.lower(),
            "retry_attempts_per_model": max_attempts_per_model,
            "base_backoff_seconds": base_backoff_seconds,
        },
        "models": {
            "specialists": selected_models,
            "report_synthesizer": synthesizer_model,
        },
        "specialist_outputs": specialist_results,
        "final_report_markdown": final_report,
    }
    return json.dumps(payload, indent=2)

def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        llm_provider = st.radio(
            "Primary LLM Provider",
            ["Groq", "OpenRouter"],
            index=0 if st.session_state.get("llm_provider", "Groq") == "Groq" else 1,
            help="Choose the primary provider for analysis."
        )
        st.session_state.llm_provider = llm_provider

        st.divider()
        st.subheader("🛠️ Advanced Settings")
        
        run_in_parallel = st.checkbox(
            "Run Specialists in Parallel",
            value=RUN_SPECIALISTS_IN_PARALLEL,
            help="Execute multiple specialist agents simultaneously to save time."
        )
        
        max_attempts = st.number_input(
            "Max Attempts per Model",
            min_value=1,
            max_value=5,
            value=MAX_ATTEMPTS_PER_MODEL,
            help="Number of times to retry a specific model before falling back."
        )
        
        backoff = st.number_input(
            "Base Backoff (seconds)",
            min_value=1,
            max_value=60,
            value=int(BASE_BACKOFF_SECONDS),
            step=1,
            help="Seconds to wait between retries."
        )

        st.divider()
        st.caption("Architecture Guard v1.3")
        
        return {
            "llm_provider": llm_provider,
            "auto_pick_models": True,
            "run_in_parallel": run_in_parallel,
            "max_parallel_workers": 3 if run_in_parallel else 1,
            "max_attempts_per_model": max_attempts,
            "base_backoff_seconds": backoff,
            "active_preset": "Reliable"
        }

@st.cache_data(show_spinner="Generating Word Document...")
def get_docx_bytes(report_md: str, run_id: str) -> bytes:
    return export_to_docx(report_md, run_id)


def render_export_downloads(final_report: str, run_id: str, key_suffix: str = ""):
    """Renders download button for Docx."""
    try:
        docx_bytes = get_docx_bytes(final_report, run_id)
        st.download_button(
            label="📄 Download Word (.docx)",
            data=docx_bytes,
            file_name=f"arch_review_{run_id}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key=f"docx_download_{run_id}_{key_suffix}"
        )
    except Exception as e:
        st.error(f"Docx error: {e}")

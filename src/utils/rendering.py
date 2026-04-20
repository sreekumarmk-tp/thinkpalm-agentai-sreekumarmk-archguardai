import streamlit as st
import re
from src.utils.mermaid_cleanup import cleanup_mermaid_code, get_mermaid_url

def render_mermaid(code: str, key: str):
    """
    Renders a Mermaid diagram by converting it to an image via Mermaid.ink.
    This avoids complex JavaScript injection and works reliably in Streamlit.
    """
    cleaned_code = cleanup_mermaid_code(code)
    img_url = get_mermaid_url(cleaned_code)
    
    try:
        st.image(img_url, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to render diagram: {e}")
        with st.expander("Show raw Mermaid code", expanded=False):
            st.code(code, language="mermaid")

def display_enriched_report(report_text: str):
    """
    Parses a markdown report and renders Mermaid blocks using the local component.
    """
    # Split by mermaid code blocks
    parts = re.split(r"(```mermaid\s*[\n\r][\s\S]*?```)", report_text)
    
    for i, part in enumerate(parts):
        if part.strip().startswith("```mermaid"):
            # Extract content between backticks
            code = re.sub(r"^```mermaid\s*[\n\r]|```$", "", part, flags=re.DOTALL).strip()
            render_mermaid(code, key=f"diag-{i}")
        else:
            if part.strip():
                st.markdown(part)

Architecture Decision Record (ADR): Agentic Arch Reviewer
1. Context and Problem Statement
   Manual architectural review of a repository is time-consuming. We require an automated solution that can:

    Understand complex file hierarchies (specifically for structured frameworks like Flutter/Dart).
    
    Operate autonomously within token context limits.
    
    Remain functional despite the high volatility and rate-limiting of free-tier LLM providers.

2. Design Decisions
   2.1 Orchestration Framework: LangGraph (Prebuilt ReAct)
   Decision: Utilize langgraph.prebuilt.create_react_agent for the agentic loop.

    Rationale: Traditional chains are linear. Architecture review is iterative (look at files -> decide on a file -> read it -> repeat). LangGraph treats this as a state-based loop, making it more robust than legacy AgentExecutor.
    
    Trade-off: Requires a strict message-based state (List of messages) rather than simple string inputs, but offers better control over the "Reasoning" phase.
    
    2.2 LLM Strategy: Multi-Model Resilience via OpenRouter
    Decision: Implement a dynamic model selector in the UI.
    
    Rationale: During development, we encountered significant 429 RateLimitErrors and 404 ToolSupport errors across free providers.
    
    Key Choice: Validated openai/gpt-oss-120b:free as the primary stable model for this specific tool-use task when other models (like Qwen) were saturated.
    
    2.3 Sensory Tools (Capabilities)
    The agent is decoupled from the GitHub API via two specific tools:
    
    list_repo_files: Maps the repository structure (limited to the first 100 files for context safety).
    
    read_specific_file: Fetches raw content (capped at 5,000 characters to prevent "lost-in-the-middle" reasoning errors).
    
    2.4 Security & Configuration
    Decision: Use python-dotenv for local secret management.
    
    Rationale: Keeps OPENROUTER_API_KEY and GITHUB_TOKEN out of the source code while allowing for seamless environment-level injection in production/cloud environments.

3. Implementation Details
   3.1 Data Flow
   User provides a GitHub URL (e.g., flutter_base).

    LangGraph Agent receives the task and queries list_repo_files.
    
    Agent parses the directory structure (identifying folders like lib/, src/, etc.).
    
    Agent selectively invokes read_specific_file on core config files (e.g., pubspec.yaml, main.dart).
    
    Agent synthesizes an architectural report based on discovered patterns.
    
    3.2 GitHub API Optimization
    Decision: Integrated Header-based Authentication.
    
    Rationale: Unauthenticated calls are limited to 60/hr. Using the GITHUB_TOKEN increases the quota to 5,000/hr, ensuring the agent can read enough files to form a complete architectural opinion.

4. Evaluation of trade-offs
   Free-tier Latency: Using free models on OpenRouter introduces variable latency and occasional retries.

Context Window: By truncating files to 5k chars, we lose deep logic detail but gain the ability to analyze a broader range of files within a single agentic session.

5. Future Improvements
   Language-specific depth: Adding a tool to specifically parse pubspec.yaml (for Flutter) or package.json (for JS) to immediately identify dependencies.

Visual Output: Integrating Mermaid.js output so the agent can generate live architecture diagrams in the Streamlit UI.
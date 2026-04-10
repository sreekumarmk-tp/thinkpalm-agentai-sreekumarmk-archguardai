# Architecture Decision Record (ADR): Agentic Arch Reviewer

## 1. Context and Problem Statement
Manual architectural reviews are time-intensive and require a deep understanding of varied design patterns. Traditional static analysis tools find "bugs" but lack "context." We need an autonomous system that can:
* Navigate a GitHub repository independently.
* Identify high-level design patterns (e.g., Clean Architecture, BLoC, MVC).
* Provide actionable scalability recommendations without human intervention.
* Remain resilient to the high volatility of free-tier LLM API providers.

## 2. Design Decisions

### 2.1 Orchestration Framework: LangGraph (v1.0+)
* **Decision:** Utilize `langgraph.prebuilt.create_react_agent` for the agentic loop.
* **Rationale:** Traditional linear chains (Legacy LangChain) are insufficient for repository analysis which requires iterative exploration. LangGraph implements a state-machine based **ReAct (Reasoning and Acting)** loop, allowing the agent to "think," call a tool, observe the result, and "think" again.
* **Trade-off:** Higher complexity in state management compared to simple prompts, but offers significantly higher reliability for complex tasks.

### 2.2 LLM Strategy: Multi-Model Resilience via OpenRouter
* **Decision:** Implement a dynamic model selector in the UI.
* **Rationale:** During development, we encountered frequent `429 RateLimit` and `404 ToolSupport` errors.
* **Key Choice:** Validated `openai/gpt-oss-120b:free` as the primary stable model for tool-use tasks, as it maintains higher availability and better function-calling support than other free-tier alternatives.

### 2.3 Sensory Tools (Capabilities)
The agent is decoupled from the GitHub API via two specific tools:
1.  **`list_repo_files`**: Maps the repository structure (limited to the first 100 files to prevent token overflow).
2.  **`read_specific_file`**: Fetches raw content (capped at 5,000 characters to prevent "lost-in-the-middle" reasoning errors).

### 2.4 Security & Configuration
* **Decision:** Use `python-dotenv` for local secret management.
* **Rationale:** Decouples sensitive credentials (`OPENROUTER_API_KEY`, `GITHUB_TOKEN`) from the source code, adhering to the 12-Factor App methodology and preventing credential leakage.

---

## 3. Implementation Details

### 3.1 Data Flow
1.  **User Input:** User provides a GitHub URL via the Streamlit interface.
2.  **Mapping:** Agent invokes `list_repo_files` to understand the project landscape.
3.  **Exploration:** Agent identifies entry points (e.g., `main.dart`, `pubspec.yaml`) and selectively invokes `read_specific_file`.
4.  **Synthesis:** Agent analyzes the gathered code chunks and generates a structured report.

### 3.2 GitHub API Optimization
* **Decision:** Header-based Authentication.
* **Rationale:** Authenticated calls using a `GITHUB_TOKEN` increase the API rate limit from 60 to 5,000 requests per hour, ensuring the agent can perform deep-dive reviews on larger projects without being throttled.

---

## 4. Evaluation of Trade-offs
* **Latency vs. Accuracy:** The agentic loop is slower than a single-prompt RAG system, but it is far more accurate because it fetches only the code it deems relevant to its reasoning path.
* **File Truncation:** By capping file reads at 5,000 characters, we trade off deep implementation detail for broader architectural awareness, which is the primary goal of this tool.

## 5. Future Evolution
* **Visual Graph Output:** Integration of Mermaid.js to allow the agent to generate visual architecture diagrams.
* **Human-in-the-loop:** Adding an approval step in the LangGraph where a human can approve which files the agent reads next to optimize token usage.
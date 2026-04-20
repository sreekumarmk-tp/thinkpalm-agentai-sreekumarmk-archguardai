from langchain_core.tools import Tool
from langchain.agents import create_agent
from src.utils.llm_factory import get_llm
from src.tools.github import fetch_repo_structure, read_github_file

class BaseSpecialistAgent:
    def __init__(self, id: str, title: str, objective: str):
        self.id = id
        self.title = title
        self.objective = objective

    def build_prompt(self, repo_url: str, memory_context: str) -> str:
        return (
            f"You are the '{self.title}' specialist for repository review.\n"
            f"Repository URL: {repo_url}\n\n"
            "Use tools first:\n"
            "1) Call list_repo_files.\n"
            "2) Pick only relevant files and call read_specific_file for evidence.\n"
            "3) Provide output in markdown using this exact structure:\n\n"
            "### Score\n"
            "Give an integer score from 0-100.\n\n"
            "### Findings\n"
            "- Severity-tagged findings (Critical/High/Medium/Low)\n"
            "- Include direct file evidence in each point\n\n"
            "### Recommendations\n"
            "- Prioritized actions with effort (Low/Medium/High) and impact\n\n"
            "### Quick Wins\n"
            "- 3 immediate fixes\n\n"
            "**CRITICAL**: Do NOT generate any Mermaid diagrams or visual maps. Focus strictly on text-based analysis. Diagrams will be handled by the Synthesizer.\n\n"
            f"Memory context from earlier runs:\n{memory_context}\n\n"
            f"Objective: {self.objective}\n"
        )

    def run(self, repo_url: str, model_name: str, memory_context: str) -> str:
        llm = get_llm(model_name=model_name, temperature=0)
        
        tools = [
            Tool(
                name="list_repo_files",
                func=lambda _: fetch_repo_structure(repo_url),
                description="Get repository file tree.",
            ),
            Tool(
                name="read_specific_file",
                func=lambda file_path: read_github_file(repo_url, file_path),
                description="Read file content. Input: exact relative file path.",
            ),
        ]
        
        agent_executor = create_agent(model=llm, tools=tools)
        task = {
            "messages": [
                (
                    "user",
                    self.build_prompt(repo_url, memory_context),
                )
            ]
        }
        result = agent_executor.invoke(task)
        return result["messages"][-1].content

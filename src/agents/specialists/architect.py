from src.agents.specialists.base import BaseSpecialistAgent

class ArchitectSpecialist(BaseSpecialistAgent):
    def __init__(self):
        super().__init__(
            id="architect_design",
            title="Architecture, Design & Maintainability",
            objective=(
                "Detect programming languages, frameworks, versions, and directory organization. "
                "Evaluate adherence to SOLID, DRY, and KISS principles. Review design pattern consistency, "
                "module boundaries, nesting, and technical debt. Recommend optimal modern alternatives."
            )
        )

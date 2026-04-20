from src.agents.specialists.base import BaseSpecialistAgent

class PerformanceSpecialist(BaseSpecialistAgent):
    def __init__(self):
        super().__init__(
            id="performance_testing",
            title="Performance, Efficiency & QA",
            objective=(
                "Review data structure optimality, complexity risks, compute/memory bottlenecks, and I/O behavior. "
                "Evaluate testing maturity (unit, integration, E2E), coverage gaps, and CI/CD quality integration."
            )
        )

from src.agents.specialists.base import BaseSpecialistAgent

class SecuritySpecialist(BaseSpecialistAgent):
    def __init__(self):
        super().__init__(
            id="security_quality",
            title="Security, Quality & Standards",
            objective=(
                "Identify security risks, secret exposure, auth/session weaknesses, and PII concerns. "
                "Review static typing quality, coding standards consistency, input validation, "
                "and exception handling strategy."
            )
        )

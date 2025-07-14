from ..base import LocalNarrationStrategy

class Summary_Strategy(LocalNarrationStrategy):
    def generate(self, capsule, prompt: str) -> str:
        return capsule.generate_narrative()
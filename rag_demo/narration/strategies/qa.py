from rag_demo.narration.base import NarrationStrategy


class QA_Strategy(NarrationStrategy):
    def generate(self, capsule, prompt: str) -> str:
        # Beispiel: Vectorstore + QA Chain
        return "Antwort auf die Frage"
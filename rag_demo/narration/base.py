from abc import ABC, abstractmethod

class NarrationStrategy(ABC):
    @abstractmethod
    def generate(self, capsule, prompt: str) -> str:
        pass

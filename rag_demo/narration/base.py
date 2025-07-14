from abc import ABC, abstractmethod

class NarrationStrategy(ABC):
    @abstractmethod
    def generate(self, capsule, prompt: str) -> str:
        pass

    @property
    def uses_llm(self) -> bool:
        return False

    @property
    def name(self) -> str:
        return self.__class__.__name__

class LocalNarrationStrategy(NarrationStrategy):
    @abstractmethod
    def generate(self, capsule, prompt: str) -> str:
        pass

    @property
    def uses_llm(self) -> bool:
        return False

class AINarrationStrategy(NarrationStrategy):
    @abstractmethod
    def generate(self, capsule, prompt: str) -> str:
        pass

    @property
    def uses_llm(self) -> bool:
        return True
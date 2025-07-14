'''from .strategies import QA_Strategy, Storytelling_Strategy, Summary_Strategy

class NarrationStrategyFactory:
    _strategies = {
        "qa": QA_Strategy,
        "story": Storytelling_Strategy,
        "summary": Summary_Strategy,
    }

    @staticmethod
    def get_strategy(strategy_name: str):
        strategy_class = NarrationStrategyFactory._strategies.get(strategy_name.lower())
        if not strategy_class:
            raise ValueError(f"Unbekannte Strategie: {strategy_name}")
        return strategy_class()'''
from .strategies.summary import Summary_Strategy
from .strategies.storytelling import Storytelling_Strategy
from .strategies.qa import QA_Strategy
from .metadata import strategy_registry


class NarrationStrategyFactory:
    @staticmethod
    def get_strategy(name: str = "summary"):
        if name == "story":
            return Storytelling_Strategy()
        elif name == "qa":
            return QA_Strategy()
        return Summary_Strategy()

    @staticmethod
    def list_available():
        return list(strategy_registry.keys())

    @staticmethod
    def get_metadata(name: str):
        return strategy_registry.get(name)

# Factory
'''class NarrationFactory:
    @staticmethod
    def get_strategy(name: str) -> NarrationStrategy:
        if name == "local_storytelling":
            return LocalStorytelling()
        elif name == "storytelling":
            return StorytellingStrategy()
        else:
            raise ValueError(f"Unbekannte Strategie: {name}")'''

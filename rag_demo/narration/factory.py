from .strategies import QA_Strategy, Storytelling_Strategy, Summary_Strategy

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
        return strategy_class()

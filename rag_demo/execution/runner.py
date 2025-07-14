# runner.py
from narration.factory import NarrationStrategyFactory
from execution.task_queue import schedule_task

class NarrationRunner:
    def __init__(self, capsule, prompt):
        self.capsule = capsule
        self.prompt = prompt

    def run(self, strategy_name: str):
        strategy = NarrationStrategyFactory.get_strategy(strategy_name)
        if strategy.uses_llm:
            return schedule_task(strategy_name, self.capsule, self.prompt)
        return strategy.generate(self.capsule, self.prompt)

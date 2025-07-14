def schedule_task(strategy_name, capsule, prompt):
    print(f"[Scheduled to Cloud Queue: {strategy_name}]")
    strategy = NarrationStrategyFactory.get_strategy(strategy_name)
    return strategy.generate(capsule, prompt)

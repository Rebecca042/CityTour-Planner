from dataclasses import dataclass

@dataclass
class StrategyMetadata:
    name: str
    description: str
    uses_llm: bool
    estimated_time_sec: int
    estimated_cost_usd: float

strategy_registry = {
    "summary": StrategyMetadata(
        name="Summary_Strategy",
        description="Schnelle lokale Zusammenfassung ohne LLM.",
        uses_llm=False,
        estimated_time_sec=1,
        estimated_cost_usd=0.0
    ),
    "story": StrategyMetadata(
        name="Storytelling_Strategy",
        description="LLM-generierte Reiseerzählung aus den extrahierten Daten.",
        uses_llm=True,
        estimated_time_sec=12,
        estimated_cost_usd=0.005
    ),
}

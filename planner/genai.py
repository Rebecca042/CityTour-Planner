# planner/genai.py
from functools import lru_cache

from transformers import pipeline

# Load the LLM pipeline using Gemma
from planner.narration_templates import TEMPLATES


@lru_cache(maxsize=1)
def get_narration_pipeline():
    return pipeline(
        "text-generation",
        model="google/gemma-2-2b-it",
        model_kwargs={"torch_dtype": "auto"},
        device_map="auto",
        max_new_tokens=120,
        do_sample=True,
        temperature=0.8,
    )

SYSTEM_MSG = (
    "You are an enthusiastic tour planner. "
    "Write 3-4 motivated and joyful sentences that narrate the day from morning to evening "
    "and explain the sights listed for the time slots; end with a friendly goodbye and travel well."
)

def narrate(time_of_day: str, city: str, sights: list[str], use_template=True) -> str:
    if use_template:
        template = TEMPLATES.get(time_of_day.lower(), "In {city}, we visit: {sights}.")
        return template.format(
            city=city.split(",")[0],
            sights=", ".join(sights)
        )


    prompt = (
        f"{SYSTEM_MSG}\n\n"
        f"{time_of_day.title()} in {city} includes:\n"
        + ", ".join(sights)
        + "\n\nNarration:"
    )

    try:
        pipe = get_narration_pipeline()
        result = pipe(prompt)[0]["generated_text"]
        return result.split("Narration:")[-1].strip()
    except Exception as e:
        return f"[Narration failed: {e}]"

    raise NotImplementedError("LLM narration is disabled in this mode.")

from functools import lru_cache
from transformers import pipeline

@lru_cache(maxsize=1)
def get_narration_pipeline():
    return pipeline(
        "text-generation",
        model="google/gemma-2-2b-it",
        model_kwargs={"torch_dtype": "auto"},
        device_map="auto",
        max_new_tokens=400,
        do_sample=True,
        temperature=0.8,
    )

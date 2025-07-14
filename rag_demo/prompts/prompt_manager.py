from .builder import PromptBuilder

# Ein globales Singleton-Objekt,
# das einmal geladen wird und dann überall wiederverwendbar ist
prompt_builder = PromptBuilder()

def get_system_prompt(city: str, capsule) -> str:
    context = capsule.format_documents_as_context()
    return prompt_builder.travel_story(city=city, context=context)

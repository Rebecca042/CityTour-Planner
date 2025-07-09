from rag_demo.city_tour_loader import CityTourLoader
from rag_demo.loader import load_documents, split_documents
from rag_demo.memory_capsule.capsule import DigitalMemoryCapsule
from rag_demo.narration.factory import NarrationStrategyFactory
from rag_demo.retrieval import build_vectorstore
from rag_demo.pipeline import get_narration_pipeline
from rag_demo.rag_chain import build_rag_chain
from rag_demo.prompts import DEFAULT_QUERY

SYSTEM_PROMPT_TEMPLATE = (
    "Du bist ein enthusiastischer Reiseplaner. Erzähle eine lebendige und motivierte Geschichte "
    "über eine Reise in {city}. Beschreibe den Tag von morgens bis abends, erwähne Sehenswürdigkeiten "
    "und besondere Erlebnisse. Beende mit einem freundlichen Abschied und guten Wünschen."
)

def get_system_prompt(city: str) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(city=city)

def narrate(pdf_path=".\docs\MotivationLLM.pdf", query=DEFAULT_QUERY) -> str:
    try:
        docs = split_documents(load_documents(pdf_path))
        db = build_vectorstore(docs)
        qa_chain = build_rag_chain(get_narration_pipeline(), db.as_retriever())
        response = qa_chain.invoke({"query": query})
        return response["result"]
    except Exception as e:
        return f"[Narration failed: {e}]"

def llm_generate_narrative(summary: dict, user_prompt: str) -> str:
    """
    Beispiel-Funktion, die das summary (dict) und einen User-Prompt an das LLM gibt,
    und daraus eine erzählerische Antwort baut.
    """

    # Zusammenfassung in Textform umwandeln (z.B. JSON-String oder schöner Text)
    import json
    summary_text = json.dumps(summary, indent=2, ensure_ascii=False)

    # Kombiniere Summary + User-Prompt zu einem kompletten Prompt
    full_prompt = (
        f"Hier ist die Zusammenfassung meiner Städtereise:\n{summary_text}\n\n"
        f"Bitte erzähle mir eine Geschichte basierend darauf:\n{user_prompt}"
    )

    # Simulierte LLM-Antwort (statt echten LLM-Aufruf)
    # Hier würdest du z.B. deine Chain.invoke oder OpenAI API call machen
    simulated_response = f"[LLM erzählt eine Geschichte basierend auf: {user_prompt}]"

    # Rückgabe der „Story“
    return simulated_response

if __name__ == "__main__":

    print("DEMO")

    folder = "docs/paris"
    loader = CityTourLoader(folder)
    overviews = loader.load_all_overviews()
    capsule = DigitalMemoryCapsule(overviews)

    for overview in overviews:
        print(overview)
    capsule = DigitalMemoryCapsule(overviews)

    # summary einmal erzeugen und ggf. cachen
    summary = capsule.summarize()

    # Flag, ob LLM genutzt werden soll
    use_llm = True

    # Wähle Strategie (hier als Beispiel Summary_Strategy)
    from narration.strategies import Summary_Strategy, Storytelling_Strategy

    if use_llm:
        # Nutze eine Strategie, die LLM aufruft, z.B. Storytelling_Strategy
        capsule = DigitalMemoryCapsule(overviews)
        strategy = Storytelling_Strategy()
        city = "Paris"
        system_prompt = get_system_prompt(city)
        prompt = "Erzähle mir eine lebendige Geschichte über meine Parisreise basierend auf der Zusammenfassung. Bitte erzähle ausführlich und beschreibe den Tag von morgens bis abends mit mindestens 200 Wörtern."
        prompt = system_prompt
        narrative = strategy.generate(capsule, prompt)
        print(narrative)
    else:
        # Nutze Strategie, die nur lokal arbeitet (z.B. Summary_Strategy)
        strategy = Summary_Strategy()
        narrative = strategy.generate(capsule, prompt=summary)

    print(narrative)

    print("Question:", DEFAULT_QUERY)
    full_text = narrate()
    full_text = narrate()
    if "Answer:" in full_text:
        answer = full_text.split("Answer:")[-1].strip()
    elif "Antwort:" in full_text:
        answer = full_text.split("Antwort:")[-1].strip()
    else:
        # fallback: take last paragraph
        answer = full_text.strip().split("\n")[-1]
    print("Answer:", full_text.strip().split("\n")[-1])

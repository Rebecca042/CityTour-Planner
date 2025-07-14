# Scheduler / Dispatcher Beispiel
'''def run_strategy(name: str, capsule, prompt: str) -> str:
    strategy = NarrationFactory.get_strategy(name)

    if strategy.uses_llm:
        print("Starte Cloud-Strategie mit mehr Ressourcen")
        # Hier z.B. Async-Aufruf, Cloud Deployment etc.
    else:
        print("Starte lokale Strategie")

    return strategy.generate(capsule, prompt)'''


# --- Beispiel Nutzung ---
'''class DummyCapsule:
    def summarize(self):
        return "Dummy Zusammenfassung"
    document_overviews = [{'file_type': 'txt', 'text_excerpt': 'Testtext'}]

capsule = DummyCapsule()
prompt = "Erzähle mir was über die Reise."

print(run_strategy("local_storytelling", capsule, prompt))
print(run_strategy("storytelling", capsule, prompt))'''
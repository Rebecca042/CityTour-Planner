from typing import Optional

from .loader import PromptLoader

from enum import Enum

class PromptType(Enum):
    TRAVEL_STORY = "travel_story"
    TRAVEL_STORY_DE = "travel_story_de"
    QA_SUMMARY = "qa_summary"
    # weitere Prompttypen ergänzen

class PromptBuilder:
    def __init__(self, prompt_loader: Optional[PromptLoader] = None):
        self.loader = prompt_loader or PromptLoader()

    def format(self, prompt_type: PromptType, **kwargs) -> str:
        return self.loader.format(prompt_type.value, **kwargs)

    def travel_story(self, city: str, context: str) -> str:
        return self.format(PromptType.TRAVEL_STORY, city=city, context=context)

    def travel_story_de(self, stadt: str, kontext: str) -> str:
        return self.format(PromptType.TRAVEL_STORY_DE, stadt=stadt, kontext=kontext)

    def qa_summary(self, documents: str, question: str) -> str:
        return self.format(PromptType.QA_SUMMARY, documents=documents, question=question)

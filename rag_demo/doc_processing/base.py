# doc_processing/base.py
from abc import ABC, abstractmethod

class DocProcessor(ABC):
    def __init__(self, file_path: str):
        print(f"Setting file_path to {file_path}")
        self.file_path = file_path
        print(f"file_path set to {self.file_path}")
    @abstractmethod
    def extract_text(self) -> str:
        pass

    @abstractmethod
    def get_type(self) -> str:
        pass

    def extract_metadata(self) -> dict:
        """Optional: Liefert Metadaten, kann von Decorators erweitert werden."""
        return {}

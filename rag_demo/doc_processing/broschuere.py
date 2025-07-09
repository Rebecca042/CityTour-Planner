from .base import DocProcessor
from langchain_community.document_loaders import PyPDFLoader

class BroschuereProcessor(DocProcessor):
    def extract_text(self) -> str:
        loader = PyPDFLoader(self.file_path)
        pages = loader.load()
        return "\n".join([p.page_content for p in pages])

    def get_type(self) -> str:
        return "Broschüre"

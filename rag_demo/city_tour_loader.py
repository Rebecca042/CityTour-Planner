import os
from doc_processing.factory import DocProcessorFactory
from rag_demo.document_overview import DocumentOverviewBuilder
from memory_capsule.capsule import DigitalMemoryCapsule

class CityTourLoader:
    def __init__(self, folder_path: str, factory: DocProcessorFactory):
        self.folder_path = folder_path
        self.factory = factory

    def load_all_overviews(self) -> list[dict]:
        overviews = []
        valid_exts = (".pdf", ".jpg", ".jpeg", ".png", ".txt")
        for filename in sorted(os.listdir(self.folder_path)):
            if not filename.lower().endswith(valid_exts):
                print(f"[Info] Datei {filename} wird übersprungen (nicht unterstütztes Format).")
                continue
            file_path = os.path.join(self.folder_path, filename)
            try:
                factory = DocProcessorFactory(use_dummy=False)
                processor = factory.get_processor(file_path)
                #processor = DocProcessorFactory.get_processor(file_path)
                builder = DocumentOverviewBuilder(processor)
                overview = builder.build_overview()
                overviews.append(overview)
            except Exception as e:
                print(f"[Warnung] Datei {filename} wurde übersprungen: {e}")
        return overviews

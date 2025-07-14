from ..base import AINarrationStrategy
from langchain.schema import Document
from rag_demo.loader import split_documents
from rag_demo.retrieval import build_vectorstore
from rag_demo.pipeline import get_narration_pipeline
from rag_demo.rag_chain import build_rag_chain

class Storytelling_Strategy(AINarrationStrategy):
    def generate(self, capsule, prompt: str) -> str:
        try:
            # 1. Zusammenfassung aus Capsule holen (z.B. dict)
            summary = capsule.summarize()

            # 2. Zusammenfassung als Text vorbereiten
            summary_text = "\n".join(
                f"{doc['file_type']}: {doc['text_excerpt']}" for doc in capsule.document_overviews
            )

            # 3. Document-Objekt erzeugen (korrektes Format für split_documents)
            summary_doc = Document(page_content=summary_text)

            # 4. Dokumente splitten
            docs = split_documents([summary_doc])

            # 4. Vektorstore bauen
            db = build_vectorstore(docs)

            # 5. QA Chain mit deinem LLM-Prompt aufbauen
            qa_chain = build_rag_chain(get_narration_pipeline(), db.as_retriever())

            # 6. Chain mit flexiblem prompt (deine Query) ausführen
            response = qa_chain.invoke({"query": prompt})
            return response["result"]

        except Exception as e:
            return f"[Narration failed: {e}]"
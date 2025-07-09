class DigitalMemoryCapsule:
    def __init__(self, document_overviews: list[dict]):
        self.document_overviews = document_overviews

    def summarize(self) -> dict:
        # 1. Alle Typen sammeln (zuvor "type" statt "file_type"?)
        types = list({doc.get("file_type", "Unbekannt") for doc in self.document_overviews})

        # 2. Optional: Zeiträume extrahieren, z.B. aus Metadaten (wenn vorhanden)
        # Für Demo: einfach alle gefundenen "date" aus Metadaten sammeln
        dates = sorted({doc.get("metadata", {}).get("date") for doc in self.document_overviews if doc.get("metadata", {}).get("date")})

        # 3. Highlights: z.B. längster Text, OCR-Dokumente
        longest_doc = max(self.document_overviews, key=lambda d: len(d.get("text_excerpt", "")), default=None)
        ocr_docs = [doc for doc in self.document_overviews if doc.get("ocr_used")]

        memory = {
            "document_count": len(self.document_overviews),
            "types": types,
            "dates": dates,
            "documents": self.document_overviews,
            "longest_document": longest_doc,
            "ocr_documents_count": len(ocr_docs),
            # Optional weitere Infos ergänzen, z.B. Orte, Personen etc.
        }
        return memory

    def generate_narrative(self) -> str:
        lines = []
        dates = sorted({doc.get("metadata", {}).get("datum") for doc in self.document_overviews if doc.get("metadata", {}).get("datum")})
        if dates:
            lines.append(f"Die Reise fand statt zwischen {dates[0]} und {dates[-1]}.")
        else:
            lines.append("Die Reisezeit ist unbekannt.")

        for doc in self.document_overviews:
            typ = doc.get("file_type", "Dokument")
            text = doc.get("text_excerpt", "")
            if typ == "Rechnung":
                lines.append(f"Am {doc.get('metadata', {}).get('datum', 'unbekanntem Datum')} wurde eine Rechnung über {doc.get('metadata', {}).get('betrag', 'einen Betrag')} bezahlt.")
            elif typ == "Ticket":
                lines.append(f"Ein Ticket wurde für {doc.get('metadata', {}).get('ort', 'einen Ort')} am {doc.get('metadata', {}).get('datum', 'unbekanntem Datum')} genutzt.")
            elif typ == "Postkarte":
                lines.append(f"Eine Postkarte mit dem Text: '{text}' wurde verschickt.")
            elif typ == "Tagebuch":
                lines.append(f"Tagebuchnotiz: {text}")
            elif typ == "Broschüre":
                lines.append(f"Broschüre zum Thema: {text}")
            elif typ == "Speisekarte":
                lines.append(f"Die Speisekarte enthielt: {text}")
            else:
                lines.append(f"{typ}: {text}")

        return "\n".join(lines)

# RAG-demo/rag_demo.py
from functools import lru_cache

from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import pipeline



@lru_cache(maxsize=1)
def get_narration_pipeline():
    return pipeline(
        "text-generation",
        model="google/gemma-2-2b-it",
        model_kwargs={"torch_dtype": "auto"},
        device_map="auto",
        max_new_tokens=120,
        do_sample=True,
        temperature=0.8,
    )

SYSTEM_MSG = (
    "You are an enthusiastic tour planner. "
    "Write 3-4 motivated and joyful sentences that narrate the day from morning to evening "
    "and explain the sights listed for the time slots; end with a friendly goodbye and travel well."
)

def narrate() -> str:

    try:
        file_path = "./MotivationLLM.pdf"
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = splitter.split_documents(documents)

        # OpenAI Embeddings mit API-Key initialisieren
        # embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        db = FAISS.from_documents(docs, embeddings)
        # Wrap pipeline in LangChain's HuggingFacePipeline class
        llm = HuggingFacePipeline(pipeline= get_narration_pipeline())

        # Initialize your retrieval QA chain
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=db.as_retriever()  # your retriever setup stays the same
        )

        # Run your query
        print("Question: Welche Erfahrungen hat Rebecca mit LLMs?")
        response = qa.invoke({"query": "Welche Erfahrungen hat Rebecca mit LLMs?"})
        #print(response.keys())
        return response["result"]
    except Exception as e:
        return f"[Narration failed: {e}]"

    raise NotImplementedError("LLM narration is disabled in this mode.")


full_text = narrate()
if "Answer:" in full_text:
    answer = full_text.split("Answer:")[-1].strip()
elif "Antwort:" in full_text:
    answer = full_text.split("Antwort:")[-1].strip()
else:
    # fallback: take last paragraph
    answer = full_text.strip().split("\n")[-1]
print("Answer: " + answer)
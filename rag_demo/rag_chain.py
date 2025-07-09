from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_huggingface import HuggingFacePipeline

def build_rag_chain(llm_pipeline, retriever):
    llm = HuggingFacePipeline(pipeline=llm_pipeline)
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

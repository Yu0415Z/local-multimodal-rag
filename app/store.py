from pathlib import Path
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from .config import settings


def get_store() -> Chroma:
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    embeddings = OllamaEmbeddings(model=settings.embed_model, base_url=settings.ollama_base_url)
    return Chroma(collection_name="multimodal_knowledge", persist_directory=str(settings.chroma_dir), embedding_function=embeddings)


def delete_source(source: str) -> None:
    get_store().delete(where={"source": source})


def list_sources() -> list[str]:
    data = get_store().get(include=["metadatas"])
    return sorted({m.get("source", "") for m in data.get("metadatas", []) if m.get("source")})

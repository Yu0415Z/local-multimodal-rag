import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    chat_model: str = os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:7b")
    vision_model: str = os.getenv("OLLAMA_VISION_MODEL", "llava:7b")
    embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    chroma_dir: Path = Path(os.getenv("CHROMA_DIR", "./data/chroma"))
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "./data/uploads"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "120"))


settings = Settings()

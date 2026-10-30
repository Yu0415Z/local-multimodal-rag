import base64
from pathlib import Path
from langchain_ollama import ChatOllama
from .config import settings
from .store import get_store


def answer(question: str, k: int = 4) -> tuple[str, list[dict]]:
    hits = get_store().similarity_search_with_score(question, k=k)
    context = "\n\n".join(f"[来源: {d.metadata.get('source')} | 类型: {d.metadata.get('file_type')} | 片段: {d.metadata.get('start_index', '?')}]\n{d.page_content}" for d, _ in hits)
    prompt = f"你是本地知识库助手。只根据给定资料回答；资料不足时明确说明。回答末尾列出引用来源。\n\n资料：\n{context or '没有检索到相关资料。'}\n\n问题：{question}"
    response = ChatOllama(model=settings.chat_model, base_url=settings.ollama_base_url, temperature=0).invoke(prompt)
    sources = [{"source": d.metadata.get("source", ""), "file_type": d.metadata.get("file_type", ""), "content": d.page_content, "score": float(score)} for d, score in hits]
    return str(response.content), sources


def ask_image(question: str, image_path: Path) -> str:
    image = base64.b64encode(image_path.read_bytes()).decode("ascii")
    response = ChatOllama(model=settings.vision_model, base_url=settings.ollama_base_url, temperature=0).invoke([("human", question, {"images": [image]})])
    return str(response.content)

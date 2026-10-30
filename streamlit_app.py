from pathlib import Path
import streamlit as st
from langchain_core.documents import Document
from app.config import settings
from app.ingest import DOC_EXTS, IMAGE_EXTS, load_document, ocr_image, split_documents
from app.qa import answer, ask_image
from app.store import delete_source, get_store, list_sources

st.set_page_config(page_title="本地多模态知识库", page_icon="📚", layout="wide")
st.title("📚 本地多模态知识库")
st.caption("文档 + 图片 OCR 混合检索 · Ollama 本地推理 · Chroma 持久化")

with st.sidebar:
    st.header("知识库管理")
    uploads = st.file_uploader("批量上传 PDF / Word / 文本 / 图片", type=["pdf", "md", "txt", "docx", "jpg", "jpeg", "png", "bmp"], accept_multiple_files=True)
    if st.button("解析并入库", disabled=not uploads, use_container_width=True):
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        store = get_store()
        status = st.status("正在解析文件…")
        for uploaded in uploads:
            target = settings.upload_dir / Path(uploaded.name).name
            target.write_bytes(uploaded.getbuffer())
            try:
                if target.suffix.lower() in IMAGE_EXTS:
                    text = ocr_image(target)
                    docs = [Document(page_content=text, metadata={"source": target.name, "file_type": "image_ocr"})] if text else []
                else:
                    docs = load_document(target)
                chunks = split_documents(docs)
                if chunks:
                    store.add_documents(chunks)
                st.write(f"✅ {target.name}: {len(chunks)} 个文本片段")
            except Exception as exc:
                st.error(f"{target.name}: {exc}")
        status.update(label="处理完成", state="complete")
    st.subheader("已入库文件")
    sources = list_sources()
    if sources:
        selected = st.selectbox("选择文件删除", sources)
        if st.button("删除所选文件", use_container_width=True):
            delete_source(selected)
            st.rerun()
    else:
        st.caption("知识库为空")
    k = st.slider("检索片段数量", 1, 10, 4)

tab_rag, tab_vision = st.tabs(["🔎 知识库问答", "🖼️ 直接看图"])
with tab_rag:
    question = st.chat_input("询问你的文档和图片笔记…", key="rag_question")
    if question:
        with st.spinner("正在本地检索并生成答案…"):
            try:
                response, citations = answer(question, k)
                st.markdown(response)
                with st.expander("查看检索来源"):
                    for item in citations:
                        st.markdown(f"**{item['source']}** · {item['file_type']} · 距离 {item['score']:.3f}")
                        st.write(item["content"])
            except Exception as exc:
                st.error(f"请求失败：{exc}。请确认 Ollama 已启动且所需模型已下载。")
with tab_vision:
    image_upload = st.file_uploader("选择一张图片", type=["jpg", "jpeg", "png", "bmp"], key="vision_image")
    vision_question = st.text_input("你想了解图片中的什么？", "请描述图片内容并解答其中的问题")
    if image_upload:
        st.image(image_upload, use_container_width=True)
        if st.button("使用 Llava 分析图片"):
            settings.upload_dir.mkdir(parents=True, exist_ok=True)
            image_path = settings.upload_dir / f"vision-{Path(image_upload.name).name}"
            image_path.write_bytes(image_upload.getbuffer())
            try:
                with st.spinner("Llava 正在分析…"):
                    st.markdown(ask_image(vision_question, image_path))
            except Exception as exc:
                st.error(f"请求失败：{exc}。请确认已运行 ollama pull {settings.vision_model}")

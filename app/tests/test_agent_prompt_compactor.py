from app.services.agent_plugin_service import _build_agent_prompt


def test_compacted_upload_prompt_keeps_extracted_document_text():
    document_text = "这是AI工具使用说明的核心内容。" * 180
    raw_prompt = (
        "这份文档说明了什么\n\n"
        "【文件解析】4-AI工具使用说明（2026年版）.pdf\n"
        "【文件引用】/media/docs/doc_1_ai_tools.pdf\n"
        f"{document_text}"
    )

    compacted, meta = _build_agent_prompt(raw_prompt)

    assert meta["prompt_compacted"] is True
    assert "【文件正文摘录】4-AI工具使用说明（2026年版）.pdf" in compacted
    assert "这是AI工具使用说明的核心内容" in compacted
    assert "/media/docs/doc_1_ai_tools.pdf" in compacted

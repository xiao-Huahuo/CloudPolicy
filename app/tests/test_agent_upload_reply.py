from app.services import agent_service


def test_upload_with_specific_question_keeps_agent_answer():
    result = {
        "assistant_reply": "这份材料最需要关注的是材料缺失和截止时间风险。",
        "structured": {},
        "display_cards": [{"type": "knowledge_graph", "payload": {}}],
        "user_audience": "通用",
    }
    user_text = "请告诉我这份文件最重要的风险是什么？\n/media/docs/doc_1_policy.txt\n【文件解析】政策材料"

    reply = agent_service.build_agent_reply(result, user_text=user_text)

    assert reply == "这份材料最需要关注的是材料缺失和截止时间风险。"


def test_upload_with_analysis_request_keeps_agent_answer():
    result = {
        "assistant_reply": "这份文件可以分为申请条件、办理材料和风险提醒三部分。",
        "structured": {},
        "display_cards": [{"type": "knowledge_graph", "payload": {}}],
        "user_audience": "通用",
    }
    user_text = "分析这个文件\n/media/docs/doc_1_policy.txt\n【文件解析】政策材料"

    reply = agent_service.build_agent_reply(result, user_text=user_text)

    assert reply == "这份文件可以分为申请条件、办理材料和风险提醒三部分。"


def test_plain_followup_without_structured_fields_does_not_use_document_template():
    result = {
        "assistant_reply": "",
        "structured": {"original_text": "需要完成怎样的流程办理呢"},
        "display_cards": [],
        "user_audience": "通用",
    }

    reply = agent_service.build_agent_reply(result, user_text="需要完成怎样的流程办理呢")

    assert "文档概览" not in reply
    assert "解析结论" not in reply
    assert "具体事项" in reply

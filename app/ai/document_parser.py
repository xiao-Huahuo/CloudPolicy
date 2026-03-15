import json
from app.ai.request_kimi import RequestKimi
from app.models.chat_message import ChatMessageBase

def parse_document(original_text: str, user_id: int) -> ChatMessageBase:
    """
    调用 AI 解析文档，返回 ChatMessageBase 对象
    """
    kimi = RequestKimi()
    
    # 重新定义系统提示词，要求强制输出 JSON
    system_prompt = """
    你是一个专业的政务和民生通知解读助手。你的任务是从用户提供的冗长通知文本中，提取出关键的结构化信息，以方便群众快速阅读和办理。
    
    你必须且只能返回一个合法的 JSON 对象，不要包含任何额外的解释性文字，也不要使用 Markdown 代码块包裹（如 ```json ... ```）。
    如果你无法在原文中找到某个字段的信息，请将其值设置为 null。
    
    JSON 对象的键必须严格如下：
    {
        "target_audience": "适用对象是谁？（例如：全体居民、应届毕业生、退休老人等）",
        "handling_matter": "需要办理什么事项？（例如：医保缴费、户口迁移等）",
        "time_deadline": "办理的时间范围或截止时间是什么？",
        "location_entrance": "办理的地点在哪里，或者线上办理的入口/网址是什么？",
        "required_materials": "办理需要准备哪些材料？（请尽量列出清单，并组合成单个字符串，不要使用数组格式）",
        "handling_process": "具体的办理流程分为哪几步？（请组合成单个字符串，使用序号分隔，不要使用数组格式）",
        "precautions": "有哪些需要特别注意的事项？",
        "risk_warnings": "如果逾期或不办理，会有什么风险或后果提醒？",
        "original_text_mapping": "将上述提取出的关键信息在原文中的出处或段落进行简单映射（可以存为一段描述或JSON字符串，如果太复杂可简写）"
    }
    
    请注意，所有字段的值必须是 string 类型或 null，绝对不能是数组(list)或对象(dict)。如果原本你想用列表表达，请用顿号或换行符将它们连接成一个长字符串。
    """
    
    # 临时替换 RequestKimi 的 system_prompt
    kimi.system_prompt = system_prompt
    
    try:
        # 调用 API，要求返回 JSON
        # 注意：Moonshot API (kimi) 支持 response_format={"type": "json_object"}
        response_text = kimi.get_response(
            content=original_text, 
            response_format={"type": "json_object"},
            temperature=0.1 # 降低温度以获得更确定性的 JSON 输出
        )
        
        # 将原始返回打印出来，方便排查问题
        print("====== AI RAW RESPONSE START ======")
        print(response_text)
        print("====== AI RAW RESPONSE END ======")
        
        # 清理可能残留的 markdown 标记
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
            
        parsed_data = json.loads(response_text)
        
        # 处理可能被 AI 错误返回为列表或字典的字段，强制转换为字符串
        def force_string(val):
            if isinstance(val, list):
                return "\n".join([str(v) for v in val])
            elif isinstance(val, dict):
                return json.dumps(val, ensure_ascii=False)
            elif val is None:
                return None
            else:
                return str(val)
                
        # 构建并返回 ChatMessageBase
        return ChatMessageBase(
            original_text=original_text,
            user_id=user_id,
            target_audience=force_string(parsed_data.get("target_audience")),
            handling_matter=force_string(parsed_data.get("handling_matter")),
            time_deadline=force_string(parsed_data.get("time_deadline")),
            location_entrance=force_string(parsed_data.get("location_entrance")),
            required_materials=force_string(parsed_data.get("required_materials")),
            handling_process=force_string(parsed_data.get("handling_process")),
            precautions=force_string(parsed_data.get("precautions")),
            risk_warnings=force_string(parsed_data.get("risk_warnings")),
            original_text_mapping=force_string(parsed_data.get("original_text_mapping"))
        )
        
    except json.JSONDecodeError as je:
        print(f"JSON Parsing Error: {je}\nResponse was: {response_text}")
        # 返回仅包含原文的 Base
        return ChatMessageBase(original_text=original_text, user_id=user_id)
    except Exception as e:
        print(f"AI Calling Error: {e}")
        return ChatMessageBase(original_text=original_text, user_id=user_id)

def rewrite_document(original_text: str, target_audience: str, user_id: int) -> ChatMessageBase:
    """
    调用 AI 根据特定的人群 (target_audience) 重新改写文档并返回 ChatMessageBase 对象
    """
    kimi = RequestKimi()
    
    system_prompt = f"""
    你是一个专业的政务和民生通知改写专家。现在的任务是：用户会提供一份官方通知原文，你需要将这份通知的内容专门针对【{target_audience}】这个群体进行改写和解读。
    
    请遵循以下改写原则：
    1. 如果受众是【老人版】或【长辈版】：语气要亲切、尊称，用极其大白话的语言，避免专业术语，步骤要像拆解动作一样详细，必要时提醒“可以让儿女帮忙”。
    2. 如果受众是【学生版】：语气要活泼，重点突出与学生相关的日期、学分、奖惩、宿舍等信息，忽略无关的复杂政策背景。
    3. 如果受众是【家属转述版】：请用第一人称口吻（例如“爸/妈/老婆，有个通知是这样的...”），提炼出需要对方配合的关键点（要带什么、要去哪、截止时间）。
    4. 如果受众是【极简版】：请用纯粹的要点列表（Bullet Points），能用 10 个字说清的绝不用 11 个字。
    5. 如果受众是【客服答复版】：请用官方、礼貌的 QA (问答) 形式，预判可能会问的核心问题并给出标准答案。
    
    除了以上的改写原则外，你的输出仍然必须严格是一个 JSON 对象，结构与之前相同。请在每个字段的提取中，都融入针对【{target_audience}】的改写语气和侧重点。
    
    JSON 对象的键必须严格如下：
    {{
        "target_audience": "适用对象是谁？（请固定填写为用户指定的群体：{target_audience}）",
        "handling_matter": "需要办理什么事项？（用符合该群体身份的口吻描述）",
        "time_deadline": "办理的时间范围或截止时间是什么？",
        "location_entrance": "办理的地点或网址？",
        "required_materials": "办理需要准备哪些材料？（必须是单个字符串）",
        "handling_process": "具体的办理流程？（必须是单个字符串，用换行符或顿号连接步骤）",
        "precautions": "有哪些需要特别注意的事项？",
        "risk_warnings": "逾期或不办理的风险提醒？",
        "original_text_mapping": "这些信息在原文的哪里？"
    }}
    
    请注意，所有字段的值必须是 string 类型或 null，绝对不能是数组(list)或对象(dict)。
    请不要输出任何多余的 Markdown 代码块或文字，只输出纯 JSON。
    """
    
    kimi.system_prompt = system_prompt
    
    try:
        response_text = kimi.get_response(
            content=original_text, 
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
            
        parsed_data = json.loads(response_text)
        
        def force_string(val):
            if isinstance(val, list):
                return "\n".join([str(v) for v in val])
            elif isinstance(val, dict):
                return json.dumps(val, ensure_ascii=False)
            elif val is None:
                return None
            else:
                return str(val)
                
        return ChatMessageBase(
            original_text=original_text,
            user_id=user_id,
            target_audience=force_string(parsed_data.get("target_audience", target_audience)),
            handling_matter=force_string(parsed_data.get("handling_matter")),
            time_deadline=force_string(parsed_data.get("time_deadline")),
            location_entrance=force_string(parsed_data.get("location_entrance")),
            required_materials=force_string(parsed_data.get("required_materials")),
            handling_process=force_string(parsed_data.get("handling_process")),
            precautions=force_string(parsed_data.get("precautions")),
            risk_warnings=force_string(parsed_data.get("risk_warnings")),
            original_text_mapping=force_string(parsed_data.get("original_text_mapping"))
        )
        
    except json.JSONDecodeError as je:
        print(f"JSON Parsing Error: {je}\nResponse was: {response_text}")
        return ChatMessageBase(original_text=original_text, user_id=user_id, target_audience=target_audience)
    except Exception as e:
        print(f"AI Calling Error: {e}")
        return ChatMessageBase(original_text=original_text, user_id=user_id, target_audience=target_audience)

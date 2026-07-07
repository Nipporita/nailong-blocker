"""
奶龙屏蔽器 v2 — 轻量语义模型
==============================
v1 (正则) 拦截字符级攻击 → 快速路径
v2 (语义) 拦截概念级攻击 → 慢速路径

模型: m2v-256-bge-large-zh-v1.5 (Model2Vec 静态嵌入)
      ~256-dim, 纯 CPU, 极快, 中文原生
"""
import re
import unicodedata
import numpy as np
from model2vec import StaticModel
from typing import List, Tuple

# ================================================================
# 加载模型 (首次加载会从 HuggingFace 下载 ~90MB)
# ================================================================
print("加载语义模型...")
MODEL = StaticModel.from_pretrained("jarbas/m2v-256-bge-large-zh-v1.5")
print(f"模型就绪, 维度: {MODEL.dim}")

# ================================================================
# 概念锚点 — 我们对"奶龙"的所有语义表达
# ================================================================
CONCEPT_MILK = [
    "奶", "乳", "乳汁", "牛奶", "牛乳", "鲜奶",
    "哺乳动物的分泌物", "哺乳动物喂养后代的液体",
    "白色营养液", "乳腺分泌物", "婴儿的食物",
    "母牛产的白色液体", "奶牛挤出来的东西",
    "milk", "dairy", "lactation", "breast milk",
    "breast", "boob milk", "udder secretion",
]

CONCEPT_DRAGON = [
    "龙", "龍", "蛟龙", "神龙",
    "东方神话中的图腾", "中国传统文化中的神兽",
    "鳞甲类神话生物", "呼风唤雨的神话动物",
    "长翅膀的爬行动物", "十二生肖中虚构的那个",
    "春节舞的龙", "皇帝象征的神兽",
    "dragon", "loong", "serpent deity",
    "mythical reptile", "fire-breathing lizard",
    "wyrm", "drake", "wyvern",
]

CONCEPT_NAILONG = [
    "奶龙", "milk dragon", "乳龙",
    "哺乳动物分泌物与东方图腾的结合体",
    "喝奶的龙", "吃奶的龙",
]

# 预计算所有概念锚点的嵌入
anchors_milk = MODEL.encode(CONCEPT_MILK)
anchors_dragon = MODEL.encode(CONCEPT_DRAGON)
anchors_nailong = MODEL.encode(CONCEPT_NAILONG)

# 负样本锚点 — 正常文本不应命中的概念
NEGATIVE_ANCHORS = MODEL.encode([
    "今天天气真好", "我喜欢喝咖啡", "你好吗",
    "吃饭了吗", "明天见", "晚安世界",
    "日常聊天", "普通弹幕", "天气不错",
    "milk tea", "dragon fruit", "龙年大吉",
    "奶茶", "咖啡", "牛肉面"
])

print(f"概念锚点: 奶({len(CONCEPT_MILK)}), 龙({len(CONCEPT_DRAGON)}), 奶龙({len(CONCEPT_NAILONG)}), 负样本({len(NEGATIVE_ANCHORS)})")


def semantic_score(text: str) -> Tuple[float, float, float]:
    """
    计算文本与"奶"、"龙"、"奶龙"三个概念的差分语义相似度。
    = max(正锚点相似度) - max(负锚点相似度)
    负锚点用于消除模型的基线偏差。
    """
    emb = MODEL.encode([text])[0]
    milk_pos = float(np.max(np.dot(anchors_milk, emb)))
    dragon_pos = float(np.max(np.dot(anchors_dragon, emb)))
    nailong_pos = float(np.max(np.dot(anchors_nailong, emb)))
    neg = float(np.max(np.dot(NEGATIVE_ANCHORS, emb)))

    # 差分: 正概念减去负概念基线
    return milk_pos - neg, dragon_pos - neg, nailong_pos - neg


def is_nailong_semantic(text: str, milk_t: float = 0.12, dragon_t: float = 0.10) -> bool:
    """
    语义判定: 差分分数 > 阈值。负锚点消去基线后，真正的语义信号才会突出。
    """
    milk, dragon, nailong = semantic_score(text)
    return milk > milk_t and dragon > dragon_t


# ================================================================
# 预处理 (与 v1 一致)
# ================================================================
def prep(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'[​-‏⁠-⁯﻿­᠎]', '', text)
    has_rtl = bool(re.search(r'[‪-‮]', text))
    text = re.sub(r'[‪-‮]', '', text)
    if has_rtl:
        text = text[::-1]
    text = re.sub(r'[︀-️]', '', text)
    text = ''.join(c for c in text if not (0xE0000 <= ord(c) <= 0xE007F))
    text = re.sub(r'[⃐-⃿]', '', text)
    return text


# ================================================================
# 联合判定: v1 正则 (快速) + v2 语义 (慢速)
# ================================================================
def load_v1():
    """懒加载 v1 正则，避免启动时导入大量模块"""
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    from nailong_patterns import PATTERNS
    from cross_lang_attack import CROSS_LANG_PATTERN
    return PATTERNS, CROSS_LANG_PATTERN


def should_block(text: str,
                 regex_threshold: float = 0.55,
                 verbose: bool = False) -> dict:
    """
    联合判定: 是否应屏蔽此弹幕。
    先跑 v1 正则 (0.01ms), 不命中的再跑 v2 语义 (1-2ms)。
    """
    text = prep(text)

    # --- v1 正则快速路径 ---
    PATTERNS, CROSS_LANG = load_v1()
    for p in PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return {"block": True, "stage": "v1_pattern", "text": text}
    if re.search(CROSS_LANG, text, re.IGNORECASE):
        return {"block": True, "stage": "v1_crosslang", "text": text}

    # --- v2 语义慢速路径 (差分分数) ---
    milk, dragon, nailong = semantic_score(text)
    blocked = milk > 0.10 and dragon > 0.08

    result = {
        "block": blocked,
        "stage": "v2_semantic",
        "text": text,
        "milk_score": round(milk, 3),
        "dragon_score": round(dragon, 3),
        "nailong_score": round(nailong, 3),
    }
    if verbose:
        print(result)
    return result


# ================================================================
# 测试: 概念层攻击 — v1 正则的盲区
# ================================================================
if __name__ == "__main__":
    tests = [
        # === v1 能拦截的 (快速路径) ===
        ("奶龙", True, "直接中文"),
        ("n@1l0n9", True, "leet拼音"),
        ("milk dragon", True, "英文意译"),
        ("🅼🅸🅻🅺 龙", True, "负圈混搭"),
        ("弥二科爪公", True, "拼音音译"),

        # === v1 拦不住, v2 必须拦截的 (语义层) ===
        ("哺乳动物分泌物与东方图腾", True, "概念描述"),
        ("母牛产出的液体和神话中的鳞甲生物", True, "概念描述2"),
        ("白色的奶和春节舞的那条长长的东西", True, "概念描述3"),
        ("婴儿喝的白色液体与中国传统象征", True, "概念描述4"),
        ("乳腺分泌物 和 呼风唤雨的神兽", True, "概念描述5"),
        ("breast secretion 和 chinese dragon totem", True, "中英混概念"),

        # === 不应拦截的 ===
        ("牛奶咖啡", False, "正常饮品"),
        ("龙年大吉", False, "龙年祝福"),
        ("今天天气真好", False, "无关内容"),
        ("我喜欢喝奶茶", False, "正常奶茶"),
        ("milk tea is great", False, "正常英文"),
    ]

    passed = 0
    for text, expect, desc in tests:
        result = should_block(text, verbose=False)
        ok = result["block"] == expect
        if ok:
            passed += 1
            stage = result.get("stage", "?")
            print(f"  [PASS] {desc:20s} → {stage}")
        else:
            s = result
            print(f"  [FAIL] {desc:20s} expect={expect} got={s['block']}")
            if "milk_score" in s:
                print(f"         milk={s['milk_score']} dragon={s['dragon_score']} nailong={s['nailong_score']}")

    print(f"\n{passed}/{len(tests)} passed")

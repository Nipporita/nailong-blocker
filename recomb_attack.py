"""
重组攻击探针 — 用拆分/重排/缩写/组合符等手段重构"奶龙"
=========================================================
攻击维度:
  1. 音节拆分重组 (n-ai-long → na-ilong, nail-ong)
  2. 龙字拆解 (立+月+乚)
  3. 缩写 (NL, MD, N*L, M×D)
  4. 连接词重组 (milk→dragon, nai=long)
  5. 组合变音标记
  6. 重叠/重复重组 (奶奶奶龙, 奶奶龙龙)
  7. 词内混排
  8. Unicode 组合字符 (COMBINING ENCLOSING CIRCLE etc)
"""
import re, unicodedata

def prep(s):
    s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'[​-‏⁠-⁯﻿­]', '', s)
    # 检测并处理 RTL/LTR 覆盖符号
    has_rtl = bool(re.search(r'[‪-‮]', s))
    s = re.sub(r'[‪-‮]', '', s)
    if has_rtl:
        # RTL 覆盖：用户输入的是反向文本，反转后才是实际内容
        s = s[::-1]
    s = re.sub(r'[⃐-⃿]', '', s)        # 去组合符号(圆圈/三角/方块)
    return s

# ============================================================
# 攻击向量
# ============================================================

ATTACKS = [
    # ===== 1. 音节拆分重组 =====
    # "nailong" 可拆为: na+ilong, nai+long, nail+ong, nailo+ng
    ("nailong", "标准"),
    ("na ilong", "拆分 na+ilong"),
    ("nail ong", "拆分 nail+ong"),
    ("nailo ng", "拆分 nailo+ng"),
    ("n ailong", "拆分 n+ailong"),

    # ===== 2. 龙字拆解 =====
    # 龙 = 立 + 月 + 乚/⺄ (多种拆分)
    ("奶立月", "龙拆为 立+月"),
    ("奶立月乚", "龙拆为 立+月+乚"),
    ("奶⺡⺼⺄", "龙用部首拼"),
    # 简化: 龙 → 尤+丿
    ("奶尤丿", "龙拆为 尤+丿"),

    # ===== 3. 缩写 =====
    ("NL", "NaiLong 首字母"),
    ("N L", "NL 带空格"),
    ("N.L.", "加点"),
    ("MD", "Milk Dragon 首字母"),
    ("M D", "MD 带空格"),
    ("M.D.", "MD加点"),
    ("n*l", "n*l 星号"),
    ("n×l", "n×l 乘号"),

    # ===== 4. 连接词 =====
    ("milk→dragon", "箭头连接"),
    ("milk→龙", "箭头+中文"),
    ("nai=long", "等号连接"),
    ("奶≈龙", "约等号"),
    ("milk+dragon", "加号连接"),
    ("milk&dragon", "&连接"),

    # ===== 5. 首字母拼写 =====
    ("n-a-i-l-o-n-g", "逐字母(已覆盖)"),
    ("N.A.I.L.O.N.G", "点分大写"),
    ("n·a·i·l·o·n·g", "间隔号分"),

    # ===== 6. 重叠/重复 =====
    ("奶奶龙", "重复 奶+奶+龙"),
    ("奶奶龙龙", "重复 奶奶+龙龙"),
    ("奶龙奶龙", "重复词组"),
    ("nai nailong", "nai+nailong"),

    # ===== 7. 词内混排 =====
    ("milkdragon", "无空格 milkdragon"),
    ("nailongmilk", "nailong+milk"),
    ("dragonnailong", "dragon+nailong"),

    # ===== 8. 同音异拼 =====
    ("naylong", "nay=nai?"),
    ("nighlong", "nigh=nai?"),
    ("nylong", "ny=nai(方言)"),
    ("neylong", "ney=nai"),
    ("najlong", "naj=nai"),

    # ===== 9. 形近字拼凑 =====
    ("扔龙", "扔≈奶(形近)"),
    ("奶垄", "垄≈龙(形近)"),
    ("奶龚", "龚≈龙(有龙部)"),
    ("奶庞", "庞≈龙(有龙部)"),

    # ===== 10. Unicode 组合字符 =====
    # COMBINING ENCLOSING CIRCLE around each letter
    ("n⃠a⃠i⃠l⃠o⃠n⃠g⃠", "组合圆圈"),
    ("n⃝a⃝i⃝l⃝o⃝n⃝g⃝", "组合圆环"),

    # ===== 11. RTL 覆盖 =====
    ("‮gnolian‬", "RTL覆盖 gnolian→nailong"),
    ("‮gnol ian‬", "RTL+空格"),

    # ===== 12. 同音数字 =====
    ("520龙", "520=我爱你(不是奶龙)"),
    ("91龙", "91=就要(不是奶龙)"),
    ("911ong", "911=nai? (不准确)"),
]

# ============================================================
# 使用当前 PATTERNS 测试
# ============================================================
from nailong_patterns import PATTERNS

def match_any(text):
    t = prep(text)
    return any(re.search(p, t, re.IGNORECASE) for p in PATTERNS)

# 再加上 cross_lang pattern
from cross_lang_attack import CROSS_LANG_PATTERN

def match_all(text):
    t = prep(text)
    if any(re.search(p, t, re.IGNORECASE) for p in PATTERNS):
        return True
    if re.search(CROSS_LANG_PATTERN, t, re.IGNORECASE):
        return True
    return False

print("=" * 70)
print("重组攻击探针")
print("=" * 70)
print()

bypasses = []
blocked = 0

for text, desc in ATTACKS:
    got = match_all(text)
    if got:
        blocked += 1
        print(f"  [BLOCKED] {text!r:25s} — {desc}")
    else:
        bypasses.append((text, desc))
        print(f"  [BYPASS ] {text!r:25s} — {desc}  <<<")

print(f"\n--- Blocked: {blocked}  |  Bypassed: {len(bypasses)} ---")

if bypasses:
    print("\n需修补:")
    for text, desc in bypasses:
        # 分析 bypass 类型
        print(f"  [{desc}] {text!r}")

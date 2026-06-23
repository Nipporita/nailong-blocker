"""
边缘攻击探针 — 穷举剩余的旁路攻击向量
==========================================
1. 隐形分隔符 (变体选择器/标签字符/软连字符/字连接符)
2. 超长拉伸
3. 特殊 Unicode 标点
4. Hangul Jamo 拆分
5. 拼写变体
6. 组合拳 (多层混淆)
"""
import re, unicodedata

# 导入当前防御
from nailong_patterns import PATTERNS
from cross_lang_attack import CROSS_LANG_PATTERN

def prep_standard(s):
    """当前推荐预处理"""
    s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'[​-‏⁠-⁯﻿­᠎]', '', s)      # 零宽+软连字符+蒙古语元音分隔
    has_rtl = bool(re.search(r'[‪-‮]', s))
    s = re.sub(r'[‪-‮]', '', s)              # RTL/LTR
    if has_rtl: s = s[::-1]
    s = re.sub(r'[︀-️]', '', s)              # 变体选择器 U+FE00-U+FE0F
    s = ''.join(c for c in s if not (0xE0000 <= ord(c) <= 0xE007F))  # 标签字符
    s = re.sub(r'[⃐-⃿]', '', s)              # 组合符号
    return s

def match(text):
    t = prep_standard(text)
    for p in PATTERNS:
        if re.search(p, t, re.IGNORECASE): return True
    if re.search(CROSS_LANG_PATTERN, t, re.IGNORECASE): return True
    return False

# ================================================================
attacks = []

# ---- 1. 隐形分隔符 ----
# 变体选择器 (U+FE00-U+FE0F) 可能不被 strip
attacks += [
    ('n︀a︀i︀l︀o︀n︀g', '变体选择器VS1'),
    ('奶︀龙', '变体选择器+中文'),
    # 标签字符 (U+E0001-U+E007F) — 用于隐藏文本
    ('n\U000e0020a\U000e0020i\U000e0020l\U000e0020o\U000e0020n\U000e0020g', 'Tag Space分隔'),
    # 软连字符 (U+00AD) — 应该在strip中
    ('nai­long', '软连字符'),
    # 字连接符 (U+2060) — 应该在strip中
    ('nai⁠long', '字连接符'),
    # BIDI 隔离符 (U+2066-U+2069)
    ('nai⁦long', 'BIDI隔离LRI'),
    # 行分隔符 (U+2028)
    ('nai long', '行分隔符'),
    # 蒙古语元音分隔符 (U+180E)
    ('nai᠎long', '蒙古语元音分隔'),
]

# ---- 2. 超长拉伸 ----
attacks += [
    ('n' + 'a'*100 + 'ilong', '超长a拉伸 x100'),
    ('na' + 'i'*1000 + 'long', '超长i拉伸 x1000'),
]

# ---- 3. 未覆盖的 Unicode 标点 ----
attacks += [
    ('nai《long', '书名号'), ('nai〈long', '尖书名号'),
    ('nai‒long', 'figure dash'), ('nai–long', 'en dash'),
    ('nai—long', 'em dash'), ('nai―long', 'horizontal bar'),
    ('nai⁓long', 'swung dash'), ('nai∼long', 'tilde operator'),
    ('nai∽long', 'reversed tilde'),
]

# ---- 4. Hangul Jamo 拆分 ----
# 우유 → ㅇ+ㅜ, ㅇ+ㅠ → ㅇㅜ ㅇㅠ
attacks += [
    ('ㅇㅜㅇㅠ', 'Hangul Jamo uyu拆解'),
    ('ㅇㅜㅇㅠ 용', 'Jamo+용混搭'),
]

# ---- 5. 拼写变体 ----
attacks += [
    ('naylong', 'y=i音变'), ('nailon', '省g'),
    ('nailung', 'ung=ong'), ('niylong', 'iy替代'),
]

# ---- 6. 多层混淆 ----
attacks += [
    ('︀m︀i︀l︀k ︀d︀r︀a︀g︀o︀n', '多层VS1+milk dragon'),
    ('n​a​i​l​o​n​g', 'ZWSP逐字分隔'),
    ('n‍a‍i‍l‍o‍n‍g', 'ZWJ逐字分隔'),
]

# ---- 7. 特殊 Unicode 空格 ----
for sp_char, name in [
    (' ', 'NBSP'), (' ', 'Ogham space'), (' ', 'EN QUAD'),
    (' ', 'EM QUAD'), (' ', 'EN SPACE'), (' ', 'EM SPACE'),
    (' ', '3-PER-EM'), (' ', '4-PER-EM'), (' ', '6-PER-EM'),
    (' ', 'FIGURE SP'), (' ', 'PUNCT SP'), (' ', 'THIN SP'),
    (' ', 'HAIR SP'), (' ', 'NARROW NBSP'), (' ', 'MED MATH SP'),
    ('　', 'IDEOGRAPH SP'),
]:
    attacks.append((f'nai{sp_char}long', f'nai{name}long'))

# ---- 8. 连接词变体 ----
attacks += [
    ('milk x dragon', 'x连接'),
    ('milk + dragon', '+连接(已有?)'),
    ('milk / dragon', '/连接'),
    ('milk | dragon', '|连接'),
]

# ================================================================
print("=" * 70)
print("边缘攻击探针")
print("=" * 70)

bypass = []
ok = 0
for text, desc in attacks:
    try:
        m = match(text)
    except Exception as e:
        print(f"  [ERROR] {desc}: {e}")
        continue
    if m:
        ok += 1
    else:
        bypass.append((text, desc))
        print(f"  [BYPASS] {desc:25s}  {text!r:40s}")

print(f"\nBlocked: {ok}  |  Bypassed: {len(bypass)}")
if bypass:
    print("\n=== 需要修补 ===")
    for text, desc in bypass:
        print(f"  [{desc}] {text!r}")

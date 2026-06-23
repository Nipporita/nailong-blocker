"""
奶龙文本屏蔽器 — Nailong Text Blocker
=======================================
既是盾，也是矛：穷举一切能在文本中指代"奶龙"的写法并予以拦截。

策略分层：
  Step 0 — Unicode 正规化（NFKC），击溃 fullwidth / math-letter / 兼容字符
  Step 1 — 移除零宽字符、组合变音记号
  Step 2 — 在正规化后的文本上跑多组正则
  Step 3 — 在原始文本上跑"视觉等价字符类"正则（leet / homoglyph）
  Step 4 — Emoji 组合检测
"""

import re
import unicodedata
from typing import List, Tuple, Optional

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STEP 0 — 正规化                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def normalize(text: str) -> str:
    """
    NFKC 正规化：
      - 全角字母 → 半角（ｎ→n, ａ→a ...）
      - 数学字母 → 普通字母（𝐧→n, 𝐚→a ...）
      - 连字/兼容字符展开
      - 圈号数字等
    这是抵御第一层视觉混淆的核心手段。
    """
    return unicodedata.normalize("NFKC", text)


def strip_invisibles(text: str) -> str:
    """
    移除所有零宽字符、格式控制符、组合变音记号。
    攻击者常用零宽空格 (U+200B) / 零宽连接符 (U+200D) 来拆分关键词。
    """
    # 1) 移除零宽字符 & 不可见格式符
    text = re.sub(
        r"[​-‏ - ⁠-⁯­﻿￰-￸"
        r"؜ᅟᅠ឴឵᠋-᠎"
        r"⠀"           # 盲文空格（视觉上为空白）
        r"]+",
        "",
        text,
    )
    # 2) 剥离组合变音记号（NFD 分解后用 combining 过滤）
    text = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if not unicodedata.combining(c)
    )
    return text


def prep(text: str) -> str:
    """两步正规化：NFKC → 去隐身字符。"""
    return strip_invisibles(normalize(text))


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STEP 1 — 视觉等价字符类 (homoglyph / leet)                                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# 每个字母的"视觉等价集合" —— 攻击者可能用其中任意一个来伪装该字母。
# 涵盖：拉丁扩展、IPA、希腊、西里尔、亚美尼亚、科普特、
#        数学符号、数字替身、罗马数字、绘图符号（|/¦等）。

# ---- 组成 "nailong" 的字母 ----

_N = r"""(?x)[
    nｎ             # 基本拉丁 / 全角
    ñ           # ñ 拉丁小 n + 颚化符
    Ń-ŋ   # ńňŉŋ 拉丁扩展 n 系列
    ṅ-ṋ   # ṅṇṉṋ 拉丁扩展附加 n
    ɲ-ɳ   # ɲɳ IPA
    η           # η 希腊 eta
    ип     # ип 西里尔 (视觉接近)
    ո           # ո 亚美尼亚
    ⲟ           # ⲟ 科普特? 实际上是 ⲡ (U+2CA1)
    ᵀbᵀf   # 略
    ¼¿]"""

# 简化版（不用 (?x) 模式，避免 regex 内嵌问题）
_N = r"[nｎñŃ-ŋṅ-ṋɲ-ɳηип]"
_A = r"[aａà-åā-ąǎǻȀ-ȃȧạ-ầɑαа@4∂]"
_I = r"[iｉì-ïĩī-ıɨ-ɩɪɩιії!1\|\|ǀǃⅰ│┆]"
_L = r"[lｌĺ-łɬ-ɭʅ˥ℓ1\|\|ǀⅼ│┆]"
_O = r"[oｏò-öøō-őơǒǫȯ-ȱɵʘοωσо0°º]"
_G = r"[gｇǵğ-ģǧɠ-ɡɢᵍ96]"

_M = r"[mｍḿ-ṃɱɯʍⅿмμ]"
_K = r"[kｋḱ-ḵƙʞκкĸ]"

_D = r"[dｄďđḋ-ḏɖ-ɗᵭԁ∂ⅾⅆ]"
_R = r"[rｒŕřṙ-ȑṛ-ṟɼ-ɾʀ-ʁягᴦ]"

# ---- 龙 的形近字 / 部首拆分 ----
_LONG_HAN = r"[龙龍竜龒陇拢珑]"
_NAI_HAN = r"[奶妳乃廼迺]"
# 拆字：女+乃 = 奶
_NAI_SPLIT = r"(?:女\s*乃|乃\s*女)"


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STEP 2 — 正则模式矩阵（对正规化后的文本）                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def _sep() -> str:
    """可选分隔符：空格、连字符、下划线、点、逗号等。"""
    return r"[\s\-_.,;:!?·•⋅∙⋅*+~|/\\()\[\]{}<>'\"`´‘’“”@#$%^&=]*"


def _rep(cls: str) -> str:
    """字母可重复 1~20 次（覆盖 naaaaailooooong 类拉伸）。"""
    return rf"{cls}+"
    # 若想严格限制拉伸次数，可改为 rf"{cls}{{1,20}}"


def _sep_rep(cls: str) -> str:
    """字母 + 可选分隔 + 可重复。"""
    return rf"{cls}+{_sep()}"


# ---------------------------------------------------------------------------
# 2.1  直接中文
# ---------------------------------------------------------------------------

_PAT_DIRECT_HAN = [
    # 奶龙 / 奶龍
    rf"{_NAI_HAN}{_sep()}{_LONG_HAN}",
    # 拆字：女乃龙
    rf"{_NAI_SPLIT}{_sep()}{_LONG_HAN}",
]

# ---------------------------------------------------------------------------
# 2.2  拼音 nailong（及各音节拆分）
# ---------------------------------------------------------------------------

_PAT_NAILONG_LATIN = [
    # n-a-i-l-o-n-g 各字母间可有分隔符、可重复
    rf"{_sep_rep(_N)}{_sep_rep(_A)}{_sep_rep(_I)}{_sep_rep(_L)}{_sep_rep(_O)}{_sep_rep(_N)}{_rep(_G)}",
]

# ---------------------------------------------------------------------------
# 2.3  "milk" + "dragon/long/loong"
# ---------------------------------------------------------------------------

_PAT_MILK_DRAGON = [
    # milk dragon —— 各字母可被伪装
    rf"{_sep_rep(_M)}{_sep_rep(_I)}{_sep_rep(_L)}{_sep_rep(_K)}"
    rf"{_sep()}"
    rf"{_sep_rep(_D)}{_sep_rep(_R)}{_sep_rep(_A)}{_sep_rep(_G)}{_sep_rep(_O)}{_rep(_N)}",

    # milk long / milk loong
    rf"{_sep_rep(_M)}{_sep_rep(_I)}{_sep_rep(_L)}{_sep_rep(_K)}"
    rf"{_sep()}"
    rf"{_sep_rep(_L)}{_sep_rep(_O)}{_sep_rep(_O)}?{_sep_rep(_N)}{_rep(_G)}",
]

# ---------------------------------------------------------------------------
# 2.4  混搭（中文 + 拉丁）
# ---------------------------------------------------------------------------

_PAT_MIXED = [
    # 奶 + long / loong / dragon
    rf"{_NAI_HAN}{_sep()}(?:{_sep_rep(_L)}{_sep_rep(_O)}{_sep_rep(_O)}?{_sep_rep(_N)}{_rep(_G)}|{_sep_rep(_D)}{_sep_rep(_R)}{_sep_rep(_A)}{_sep_rep(_G)}{_sep_rep(_O)}{_rep(_N)})",

    # nai / milk + 龙
    rf"(?:{_sep_rep(_N)}{_sep_rep(_A)}{_sep_rep(_I)}|{_sep_rep(_M)}{_sep_rep(_I)}{_sep_rep(_L)}{_sep_rep(_K)})"
    rf"{_sep()}{_LONG_HAN}",
]

# ---------------------------------------------------------------------------
# 2.5  注音符号 ㄋㄞˇ ㄌㄨㄥˊ
# ---------------------------------------------------------------------------

_PAT_ZHUYIN = [
    # ㄋㄞˇ(可选声调) + ㄌㄨㄥˊ(可选声调)
    r"ㄋㄞ[ˇˋˊ˙]?\s*ㄌㄨㄥ[ˊˇˋ˙]?",
    # 不带声调
    r"ㄋㄞ\s*ㄌㄨㄥ",
]

# ---------------------------------------------------------------------------
# 2.6  Emoji 组合
# ---------------------------------------------------------------------------

_PAT_EMOJI = [
    # 奶类 emoji + 龙类 emoji（中间可有任意字符）
    r"[\U0001f95b\U0001f37c\U0001f37b\U0001f375](?:.{0,3})[\U0001f409\U0001f432]",
    # 🥛🐉  🍼🐲  etc.
]

# ---------------------------------------------------------------------------
# 2.7  韩文 / 日文 / 其他语言音译
# ---------------------------------------------------------------------------

_PAT_OTHER_LANG = [
    # 韩文音译：나이롱 (nailong)
    r"나\s*이\s*롱",
    # 日文音译：ナイロン (nairon — 与"尼龙"同音，但可能被用来指代)
    r"ナ\s*イ\s*ロ\s*ン",
    # ナイロング (nailongu)
    r"ナ\s*イ\s*ロ\s*ン\s*グ",
]

# ---------------------------------------------------------------------------
# 2.8  同音 / 谐音替换（中文）
# ---------------------------------------------------------------------------

_PAT_HOMOPHONE = [
    # 奈龙 / 耐龙 / 乃龙
    r"[奶奈耐乃氖]+\s*[龙隆窿珑]",
    # 氖龙（化学元素梗）
    r"氖\s*龙",
]

# ---------------------------------------------------------------------------
# 2.9  意译 / 代称
# ---------------------------------------------------------------------------

_PAT_ALIAS = [
    # 乳龙 / 乳之龙
    r"乳\s*[之的]?\s*龙",
    # 奶之龙 / 奶的龙
    r"奶\s*[之的]\s*龙",
    # dairy dragon / dairy long
    rf"[dD][aA4@][iI1!|][rR][yY]\s*{_sep_rep(_D)}{_sep_rep(_R)}{_sep_rep(_A)}{_sep_rep(_G)}{_sep_rep(_O)}{_rep(_N)}",
    rf"[dD][aA4@][iI1!|][rR][yY]\s*{_sep_rep(_L)}{_sep_rep(_O)}{_sep_rep(_N)}{_rep(_G)}",
]

# ---------------------------------------------------------------------------
# 2.10  数词和谐音数字
# ---------------------------------------------------------------------------

_PAT_NUMERIC = [
    # nai103ng  (1=i, 0=o, 3=e 但这里 0=o)
    # 更泛化：字母间穿插数字替身
    rf"{_rep(_N)}\d*{_rep(_A)}\d*{_rep(_I)}\d*{_rep(_L)}\d*{_rep(_O)}\d*{_rep(_N)}\d*{_rep(_G)}",
]

# ---------------------------------------------------------------------------
# 聚合所有正则
# ---------------------------------------------------------------------------

ALL_PATTERNS: List[Tuple[str, str]] = []

_pattern_sources = [
    ("direct-han",       _PAT_DIRECT_HAN),
    ("nailong-latin",    _PAT_NAILONG_LATIN),
    ("milk-dragon",      _PAT_MILK_DRAGON),
    ("mixed-script",     _PAT_MIXED),
    ("zhuyin",           _PAT_ZHUYIN),
    ("emoji",            _PAT_EMOJI),
    ("other-lang",       _PAT_OTHER_LANG),
    ("homophone",        _PAT_HOMOPHONE),
    ("alias",            _PAT_ALIAS),
    ("numeric",          _PAT_NUMERIC),
]

for _group, _pats in _pattern_sources:
    for _p in _pats:
        ALL_PATTERNS.append((_group, _p))

# 编译（IGNORECASE 以覆盖大小写变形）
COMPILED = [
    (group, re.compile(pat, re.IGNORECASE | re.UNICODE))
    for group, pat in ALL_PATTERNS
]


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STEP 3 — 对外接口                                                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def findall(text: str) -> List[Tuple[str, str, str]]:
    """
    返回所有匹配结果：[(group, pattern_str, matched_text), ...]
    group 标识了攻击向量的类别。
    """
    cleaned = prep(text)
    results: List[Tuple[str, str, str]] = []
    for group, regex in COMPILED:
        for m in regex.finditer(cleaned):
            results.append((group, regex.pattern, m.group()))
    return results


def contains_nailong(text: str) -> bool:
    """快速判定：文本中是否包含任何'奶龙'的变体表述。"""
    cleaned = prep(text)
    for _, regex in COMPILED:
        if regex.search(cleaned):
            return True
    return False


def censor(text: str, replacement: str = "[BLOCKED]") -> str:
    """将匹配到的所有'奶龙'变体替换为 replacement。"""
    cleaned = prep(text)
    for group, regex in COMPILED:
        cleaned = regex.sub(replacement, cleaned)
    return cleaned


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STEP 4 — 自测 / 矛的演练                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# 攻击样本 —— 你能想到的，这里都有（或欢迎补充）
ATTACK_SAMPLES: List[Tuple[str, bool, str]] = [
    # ---- 直接中文 ----
    ("奶龙",                            True,  "直接中文"),
    ("奶龍",                            True,  "繁体龙"),
    ("奶  龙",                          True,  "空格拆分"),
    ("奶-龙",                           True,  "连字符拆分"),
    ("女乃龙",                          True,  "拆字 女+乃"),
    ("乃龙",                            True,  "省略女旁"),

    # ---- 拼音 nailong ----
    ("nailong",                         True,  "拼音"),
    ("nAILONG",                         True,  "大小写混用"),
    ("n a i l o n g",                   True,  "逐字母空格"),
    ("n-a-i-l-o-n-g",                   True,  "逐字母连字符"),
    ("naaaaaaaailooooooong",            True,  "字母拉伸"),
    ("n4il0ng",                         True,  "leet 4=a, 0=o"),
    ("n@1l0n9",                         True,  "leet @=a,1=i,0=o,9=g"),
    ("n@!|0ng",                         True,  "leet 多符号替身"),
    ("náilóng",                         True,  "拼音声调"),
    ("nǎilòng",                         True,  "拼音声调2"),
    ("n.ail.ong",                       True,  "点号拆分音节"),
    ("n_ail_ong",                       True,  "下划线拆分"),
    ("n·ai·long",                       True,  "间隔号"),
    ("nāīlõng",                         True,  "各种变音符"),

    # ---- 视觉欺骗 (homoglyph) ----
    ("𝐧𝐚𝐢𝐥𝐨𝐧𝐠",                         True,  "数学粗体"),
    ("𝑛𝑎𝑖𝑙𝑜𝑛𝑔",                         True,  "数学斜体"),
    ("𝗻𝗮𝗶𝗹𝗼𝗻𝗴",                        True,  "数学无衬线"),
    ("𝙣𝙖𝙞𝙡𝙤𝙣𝙜",                         True,  "数学等宽"),
    ("ｎａｉｌｏｎｇ",                      True,  "全角字母"),
    ("ɳɑɨŀøȵɠ",                         True,  "IPA 混搭"),
    ("ñäîłøñğ",                         True,  "拉丁扩展"),
    ("ηαιʅσɳɠ",                         True,  "希腊字母混搭"),
    ("η@!1οη9",                         True,  "希腊+leet"),
    ("п@1|0п9",                         True,  "西里尔+leet"),

    # ---- milk dragon ----
    ("milk dragon",                     True,  "英文意译"),
    ("MILK DRAGON",                     True,  "全大写"),
    ("m1lk dragon",                     True,  "leet milk"),
    ("m!lk dr4g0n",                     True,  "leet 全套"),
    ("mi1k drag0n",                     True,  "leet 变种"),
    ("milk loong",                      True,  "loong 拼写"),
    ("milk long",                       True,  "long 拼写"),
    ("m i l k  d r a g o n",            True,  "逐字母空格"),
    ("m1lk-dr4g0n",                     True,  "leet+连字符"),
    ("мιℓк ∂яαgση",                     True,  "多文种混搭"),
    ("ⅿⅰⅼⅿ ⅾⅿαⅿⅾ",                      True,  "罗马数字替身"),

    # ---- mixed script ----
    ("nai龙",                           True,  "拼音+中文"),
    ("奶long",                          True,  "中文+拼音"),
    ("milk龙",                          True,  "英文+中文"),
    ("奶dragon",                        True,  "中文+英文"),
    ("奶 loong",                        True,  "中文+loong"),
    ("m1lk 龍",                         True,  "leet+繁体龙"),

    # ---- 注音 ----
    ("ㄋㄞˇ ㄌㄨㄥˊ",                     True,  "注音符号"),
    ("ㄋㄞㄌㄨㄥ",                        True,  "注音无声调"),
    ("ㄋㄞˋ ㄌㄨㄥˊ",                     True,  "注音变调"),

    # ---- emoji ----
    ("🥛🐉",                             True,  "牛奶+龙"),
    ("🥛🐲",                             True,  "牛奶+龙头"),
    ("🍼🐉",                             True,  "奶瓶+龙"),
    ("🥛 🐉",                            True,  "emoji 空格"),
    ("🥛→🐉",                            True,  "emoji 箭头"),

    # ---- 谐音/同音中文 ----
    ("奈龙",                            True,  "同音字"),
    ("耐龙",                            True,  "同音字2"),
    ("氖龙",                            True,  "化学梗"),
    ("乳龙",                            True,  "乳=奶"),
    ("乳 龙",                           True,  "乳+空格+龙"),
    ("奶之龙",                          True,  "之字结构"),
    ("dairy dragon",                    True,  "dairy=乳制品"),

    # ---- 零宽字符（预处理阶段消除） ----
    ("奶​龙",                       True,  "零宽空格"),
    ("nai​long",                   True,  "零宽空格拉丁"),
    ("na​i​long",             True,  "多处零宽空格"),

    # ---- 韩文/日文 ----
    ("나이롱",                          True,  "韩文音译"),
    ("ナイロング",                      True,  "日文音译"),

    # ---- 不应该匹配的 ----
    ("nail",                            False, "仅 nail 不应匹配"),
    ("long",                            False, "仅 long 不应匹配"),
    ("dragon",                          False, "仅 dragon 不应匹配"),
    ("牛奶",                            False, "中文 牛奶 ≠ 奶龙"),
    ("milk shake",                      False, "milk shake 不应匹配"),
    ("尼龙",                            False, "尼龙 ≠ 奶龙"),
    ("nail polish",                     False, "nail polish 不应匹配"),
]


def run_tests() -> Tuple[int, int, List[str]]:
    """
    跑全部攻击样本，打印结果。
    返回 (pass_count, fail_count, failure_details)。
    """
    passed = 0
    failed = 0
    failures: List[str] = []

    name_width = max(len(s[0]) for s in ATTACK_SAMPLES) + 2

    print(f"{'TEXT':<{name_width}} {'EXPECT':>6}  {'GOT':>6}  {'RESULT':>8}  GROUPS")
    print("-" * (name_width + 50))

    for text, expect, desc in ATTACK_SAMPLES:
        result = contains_nailong(text)
        found = findall(text)
        groups = ", ".join(sorted({g for g, _, _ in found})) if found else "—"

        status = "[PASS]" if result == expect else "[FAIL]"
        if result == expect:
            passed += 1
        else:
            failed += 1
            failures.append(f"[{desc}]  text={text!r}  expect={expect}  got={result}")

        print(
            f"{text!r:<{name_width}} "
            f"{'DETECT' if expect else 'CLEAN':>6}  "
            f"{'HIT' if result else 'MISS':>6}  "
            f"{status:>8}  "
            f"{groups}"
        )

    print()
    print(f"Passed: {passed}/{passed + failed}")
    if failures:
        print(f"\n[FAIL] Failures ({len(failures)}):")
        for f in failures:
            print(f"   {f}")
    else:
        print("*** All tests passed! ***")

    return passed, failed, failures


# ---------------------------------------------------------------------------
# 交互查找函数
# ---------------------------------------------------------------------------

def scan(text: str, verbose: bool = True) -> bool:
    """
    扫描任意文本，打印命中的模式组。
    返回是否存在命中。
    """
    found = findall(text)
    if not found:
        if verbose:
            print("[CLEAN] 未检测到'奶龙'相关表述。")
        return False

    if verbose:
        print(f"[HIT] 检测到 {len(found)} 处'奶龙'变体：")
        for group, _, match in found:
            print(f"   [{group}] → {match!r}")
    return True


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CLI                                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    import sys

    # 修复 Windows GBK 终端编码问题
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            run_tests()
        elif sys.argv[1] == "--scan":
            text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read()
            scan(text)
        elif sys.argv[1] == "--censor":
            text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read()
            print(censor(text))
        else:
            text = " ".join(sys.argv[1:])
            scan(text)
    else:
        print("奶龙屏蔽器 — Nailong Blocker")
        print("用法：")
        print("  python nailong_blocker.py --test         跑自测")
        print("  python nailong_blocker.py --scan <text>   扫描文本")
        print("  python nailong_blocker.py --censor <text> 屏蔽替换")
        print("  python nailong_blocker.py <text>          扫描文本（简写）")
        print()
        run_tests()

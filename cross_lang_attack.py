"""
跨语言混搭攻击 — 奶词表 × 龙词表 笛卡尔积
=============================================
"milk 용", "Milch 龙", "ミルク dragon", "🥛ドラゴン", "奶🅛🅞🅝🅖", "👵🐉" ...
任意语言的 "奶/milk" + 任意语言的 "龙/dragon" 拼接

复用 nailong_patterns 的完整 homoglyph 字符类，确保覆盖
负圈字母/方框字母/IPA/多文种替身等全部视觉变体。
"""
import re, unicodedata

# 导入完整字符类（含负圈/方框/IPA/多文种/emoji）
from nailong_patterns import _N, _A, _I, _L, _O, _G, _M, _K, _D, _R, _U, _SP
from nailong_patterns import _B, _C, _E, _F, _H, _J, _P, _Q, _S, _T, _V, _W, _X, _Y, _Z

# ============ 奶/milk 词表 ============
# 拉丁字母使用完整 homoglyph 类 (_M/_I/_L/_K 等)，非拉丁使用字面量

MILK_WORDS = [
    # 中文
    r'奶', r'乳', r'乳汁', r'乳液', r'酪', r'奶牛', r'牛乳', r'鲜奶',
    # 英文 milk / milky (使用完整类: 🅜🅘🅛🅚 等全部覆盖)
    _M + '+' + _SP + _I + '+' + _SP + _L + '+' + _SP + _K + '+',
    _M + '+' + _SP + _I + '+' + _SP + _L + '+' + _SP + _K + r'+[yYiIeE]+',
    # dairy
    r'[dD∂]' + '+' + _SP + _A + '+' + _SP + _I + '+' + _SP + _R + '+' + _SP + r'[yYýÿŷ]+',
    # 德语 Milch
    _M + '+' + _SP + _I + '+' + _SP + _L + '+' + _SP + r'[cCсhHһ]+',
    # 法语 lait
    _L + '+' + _SP + _A + '+' + _SP + _I + '+' + _SP + r'[tTт]+',
    # 西语 leche
    _L + '+' + _SP + r'[eEеë]+' + _SP + r'[cCс]+' + _SP + r'[hHһ]+' + _SP + r'[eEеë]+',
    # 意语 latte
    _L + '+' + _SP + _A + '+' + _SP + r'[tTт]+' + _SP + r'[eEеë]+',
    # 葡语 leite
    _L + '+' + _SP + r'[eEе]+' + _SP + _I + '+' + _SP + r'[tTт]+' + _SP + r'[eEе]+',
    # 俄语 молоко / молочный
    r'мол[оoOо0]+[кkK]?[оoOо0]?[чƜ]?[нnNη]?[ыyY]?[йiIιі]?',
    # 乌克兰语 молочний
    r'мол[оoOо0]+[чƜ][нnNη][иiIιі][йiIιі]',
    # 荷兰语 melk
    _M + '+' + _SP + r'[eEеë]+' + _SP + _L + '+' + _SP + _K + '+',
    # 瑞典语 mjolk
    _M + '+' + _SP + r'[jJ]+' + _SP + _O + '+' + _SP + _L + '+' + _SP + _K + '+',
    # 丹麦/挪威语 maelk/melk
    _M + '+' + _SP + r'[æÆae]+' + _SP + _L + '+' + _SP + _K + '+',
    # 波兰语 mleko/mleczny
    _M + '+' + _SP + _L + '+' + _SP + r'[eEеë]+' + _SP + _K + '+' + _SP + r'[oOо0]?' + _SP + r'[cCс]?' + _SP + r'[zZ]?' + _SP + r'[nNη]?' + _SP + r'[yY]?',
    # 土耳其语 sut
    r'[sSşŞ]+' + _SP + r'[uUùÙúÚüÜ]+' + _SP + r'[tTт]+',
    # 印尼/马来语 susu
    r'[sS]+' + _SP + r'[uUùÙúÚ]+' + _SP + r'[sS]+' + _SP + r'[uUùÙúÚ]+',
    # 越南语 sua
    r'[sS]+' + _SP + r'[uUùÙúÚữưŨƯ]+' + _SP + r'[aAаα@4âÂấẤầẦ]+',
    # 韩语
    r'우유', r'밀크',
    # 日语
    r'ミルク', r'牛乳',
    # romaji miruku (日文罗马字)
    _M + '+' + _SP + _I + '+' + _SP + _R + '+' + _SP + _U + '+' + _SP + _K + '+' + _SP + _U + '+',
    # にゅう / にゆう (hiragana: 乳=nyuu)
    r'に[ゅゆ]\s*う',
    # 中文音译 — milk ≈ mi/mei + er/le/lu/ru + ke/ku/ge/gu (通用音节类)
    r'[米弥迷谜靡糜密蜜觅覓泌秘祕幂咪眯醚麋汨宓弭魅美妹没梅媒每]\s*[尔耳二而儿兒迩饵洱贰铒鸸路露鹿陆魯鲁庐卢芦炉勒]\s*[克可刻客课課科颗顆壳殼渴嗑恪氪溘骒剋枯哭库酷堀窟]',
    # milk 二字/特殊音译变体
    r'[缪谬]\s*[克可刻客]',
    r'[米密觅魅]\s*[露路鹿魯]\s*[可克客玖久]',
    r'[密蜜]\s*乳\s*[克可]',
    # 日式当て字 — 魅留玖/美留久/未留区 = miruku
    r'[魅美未米]\s*[留流琉]\s*[玖久九区苦]',
    # 俚语 — breast/boob/tit/udder/bosom/jug = 奶
    _B + '+' + _SP + _R + '+' + _SP + _E + '+' + _SP + _A + '+' + _SP + _S + '+' + _SP + _T + '+', # breast
    _B + '+' + _SP + _O + '{2,}' + _SP + _B + '+',                             # boob
    _T + '+' + _SP + _I + '+' + _SP + _T + '+' + _SP + _Y + '?',                   # tit/titty
    _U + '+' + _SP + _D + '+' + _SP + _D + '+' + _SP + _E + '+' + _SP + _R + '+',                # udder
    _B + '+' + _SP + _O + '+' + _SP + _S + '+' + _SP + _O + '+' + _SP + _M + '+',            # bosom
    _J + '+' + _SP + _U + '+' + _SP + _G + '+',                               # jug
    _C + '+' + _SP + _H + '+' + _SP + _E + '+' + _SP + _S + '+' + _SP + _T + '+',                       # chest
    # 非拉丁文字
    r'นม',           # 泰语
    r'حليب',         # 阿拉伯语
    r'दूध',          # 印地语
    r'חלב',          # 希伯来语
    # Emoji 奶类
    r'[\U0001f95b\U0001f37c\U0001f37b\U0001f375\U0001f404\U0001f42e\U0001f402\U0001f416\U0001f475\U0001f9d3]',
]

# ============ 龙/dragon 词表 ============

DRAGON_WORDS = [
    # 中文
    r'[龙龍竜龒陇拢珑⻰]',
    # 英文 dragon (完整类: 🅓🅡🅐🅖🅞🅝 全部覆盖)
    _D + '+' + _SP + _R + '+' + _SP + _A + '+' + _SP + _G + '+' + _SP + _O + '+' + _SP + _N + '+',
    # loong / long (完整类: 🅛🅞🅝🅖 / 🅛🅞🅞🅝🅖 全部覆盖)
    _L + '+' + _SP + _O + '{1,20}' + _SP + _N + '+' + _SP + _G + '+',
    # 德语 Drache
    _D + '+' + _SP + _R + '+' + _SP + _A + '+' + _SP + r'[cCс]+' + _SP + r'[hHһ]+' + _SP + r'[eEеë]+',
    # 法语 dragon
    _D + '+' + _SP + _R + '+' + _SP + _A + '+' + _SP + _G + '+' + _SP + _O + '+' + _SP + _N + '+',
    # 西语 dragón
    _D + '+' + _SP + _R + '+' + _SP + _A + '+' + _SP + _G + '+' + _SP + _O + '+' + _SP + _N + '+',
    # 意语 drago
    _D + '+' + _SP + _R + '+' + _SP + _A + '+' + _SP + _G + '+' + _SP + _O + '+',
    # 葡语 dragão
    _D + '+' + _SP + _R + '+' + _SP + _A + '+' + _SP + _G + '+' + _SP + r'[aAаα@4ãÃâÂ]+' + _SP + _O + '+',
    # 俄语 дракон
    r'[дdD∂]+' + _SP + r'[рrRяг]+' + _SP + r'[аaAаα@4]+' + _SP + r'[кkK]+' + _SP + r'[оoOо0]+' + _SP + r'[нnNη]+',
    # 荷兰语 draak
    _D + '+' + _SP + _R + '+' + _SP + _A + '+' + _SP + _K + '+',
    # 瑞典语 drake
    _D + '+' + _SP + _R + '+' + _SP + _A + '+' + _SP + _K + '+' + _SP + r'[eEеë]+',
    # 丹麦/挪威语 drage
    _D + '+' + _SP + _R + '+' + _SP + _A + '+' + _SP + _G + '+' + _SP + r'[eEеë]+',
    # 波兰语 smok
    r'[sS]+' + _SP + _M + '+' + _SP + _O + '+' + _SP + _K + '+',
    # 土耳其语 ejderha
    r'[eEеë]+' + _SP + r'[jJ]+' + _SP + _D + '+' + _SP + r'[eEеë]+' + _SP + _R + '+' + _SP + r'[hHһ]+' + _SP + _A + '+',
    # 印尼/马来语 naga
    _N + '+' + _SP + _A + '+' + _SP + _G + '+' + _SP + _A + '+',
    # 越南语 rong
    _R + '+' + _SP + _O + '+' + _SP + _N + '+' + _SP + _G + '+',
    # 韩语
    r'용', r'드래곤',
    # 日语
    r'ドラゴン', r'[竜龍龙]',
    # romaji doragon (日文罗马字 d-o-r-a-g-o-n)
    _D + '+' + _SP + _O + '+' + _SP + _R + '+' + _SP + _A + '+' + _SP + _G + '+' + _SP + _O + '+' + _SP + _N + '+',
    # りゅう / りゆう (hiragana: 龍=ryuu)
    r'り[ゅゆ]\s*う',
    # 中文音译 — dragon ≈ duo/de/du + la/ra + gong/gon/gen (通用音节类)
    r'[多哆夺奪朵躲堕墮舵德得都嘟]\s*[拉啦喇辣腊蜡剌]\s*[贡工公共供宫弓功攻恭巩汞]',
    r'[抓爪]\s*[公工功攻]',
    r'[巨据剧聚]\s*[拉啦喇]\s*[贡工公共]',
    r'[拽]\s*[根跟]',
    # 日式当て字 — 怒羅権/土羅権/度羅権 = doragon
    r'[怒土度奴]\s*[羅罗]\s*[権权拳]',
    # ドラゴン 的另一种当て字: 土羅言/怒羅言
    r'[怒土度]\s*[羅罗]\s*[言]',
    # 俚语 — drake/wyrm/wyvern = 龙
    _D + '+' + _SP + _R + '+' + _SP + _A + '+' + _SP + _K + '+' + _SP + _E + '+',                # drake
    _W + '+' + _SP + _Y + '+' + _SP + _R + '+' + _SP + _M + '+',                          # wyrm
    _W + '+' + _SP + _Y + '+' + _SP + _V + '+' + _SP + _E + '+' + _SP + _R + '+' + _SP + _N + '+',                # wyvern
    # 非拉丁文字
    r'มังกร',        # 泰语
    r'تنين',         # 阿拉伯语
    r'דרקון',        # 希伯来语
    r'ड्रैगन',       # 印地语
    # 希腊语 drakos/drakou
    r'[δ∂дdD]+' + _SP + r'[ρррrR]+' + _SP + r'[άαаaA@4]+' + _SP + r'[κkK]+' + _SP + r'[οоoO0]+' + _SP + r'[ςsSσυuU]?',
    # Emoji 龙类
    r'[\U0001f409\U0001f432]',
]

# ============ 构造跨语言混搭 Pattern ============
MILK = '(?:' + '|'.join(MILK_WORDS) + ')'
DRAGON = '(?:' + '|'.join(DRAGON_WORDS) + ')'

CROSS_LANG_PATTERN = MILK + _SP + DRAGON

print(f"MILK words:   {len(MILK_WORDS)}")
print(f"DRAGON words: {len(DRAGON_WORDS)}")
print(f"Combinations: {len(MILK_WORDS)} x {len(DRAGON_WORDS)} = {len(MILK_WORDS)*len(DRAGON_WORDS)}")
print(f"Pattern length: {len(CROSS_LANG_PATTERN)} chars")
print()

# ============ 测试 ============
def prep(s):
    s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'[​-‏⁠-⁯﻿­]', '', s)
    return s

tests = [
    # 跨语言混搭
    ("milk 용", True),       ("Milch 龙", True),
    ("lait 용", True),       ("milk มังกร", True),
    ("ミルク 龙", True),      ("우유 dragon", True),
    ("молоко 龙", True),     ("sữa dragon", True),
    ("süt 용", True),        ("milk дракон", True),
    ("susu 龙", True),       ("dairy 용", True),
    ("Milch 드래곤", True),   ("leite ドラゴン", True),
    ("milk ドラゴン", True),  ("dairy 龙", True),
    # emoji 混搭
    ("🥛ドラゴン", True),     ("milk 🐉", True),
    ("🥛용", True),           ("Milch 🐲", True),
    ("🥛 龙", True),          ("🍼 dragon", True),
    ("👵🐉", True),           ("🧓 🐲", True),
    # 负圈/方框字母混搭 (用户发现的漏洞)
    ("奶🅛🅞🅝🅖", True),     ("奶🅻🅾🅽🅶", True),
    ("milk 🅛🅞🅝🅖", True),  ("🥛🅓🅡🅐🅖🅞🅝", True),
    ("🅜🅘🅛🅚 龙", True),    ("🅼🅸🅻🅺 🐉", True),
    # 常规
    ("milk loong", True),     ("milk long", True),
    # 不应匹配
    ("milk shake", False),    ("dragon fruit", False),
    ("龙年大吉", False),      ("milk tea", False),
]

passed = 0
for text, expect in tests:
    got = bool(re.search(CROSS_LANG_PATTERN, prep(text), re.IGNORECASE))
    ok = got == expect
    if ok: passed += 1
    print(f'  [{"PASS" if ok else "FAIL"}] {text!r:35s} expect={expect} got={got}')

print(f"\n{passed}/{len(tests)} passed")
if passed == len(tests):
    print("All clear!")

# 保存
with open("pattern_cross_lang.txt", "w", encoding="utf-8") as f:
    f.write("# 奶龙屏蔽器 — 跨语言混搭 Pattern\n")
    f.write(f"# 奶词表: {len(MILK_WORDS)} 表达 x 龙词表: {len(DRAGON_WORDS)} 表达\n")
    f.write(f"# 笛卡尔积: {len(MILK_WORDS)*len(DRAGON_WORDS)} 组合，1 条正则全覆盖\n")
    f.write(f"# 含负圈字母/方框字母/IPA/Emoji/19种语言\n\n")
    f.write(CROSS_LANG_PATTERN)
    f.write("\n")

print(f"\nPattern saved to pattern_cross_lang.txt ({len(CROSS_LANG_PATTERN)} chars)")

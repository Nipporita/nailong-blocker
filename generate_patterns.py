"""
生成最终纯文本 re pattern 列表
===============================
输出: patterns_final.txt
"""
import re
import unicodedata

# === 基础字符类 ===
_N = r'[nｎñńňŉŋṅṇṉṋɲɳȵηип🅝🅽🄽]'
_A = r'[aａàáâãäåāăąǎǻȁȃȧạảấầẩẫậɑαа@4∂🅐🅰🄰]'
_I = r'[iｉìíîïĩīĭįıɨɩɪιії!1\|ǀǃⅰ🅘🅸🄸]'
_L = r'[lｌĺļľŀłɫɬɭʅ˥ℓ1\|ǀⅼ🅛🅻🄻]'
_O = r'[oｏòóôõöøōŏőơǒǫȯȱɵʘɔʊɒοωσо0°º🅞🅾🄾]'
_G = r'[gｇǵğĝġģǧɠɡɢᵍ96ɣ🅖🅶🄶]'
_M = r'[mｍḿṁṃɱɯʍⅿмμ🅜🅼🄼]'
_K = r'[kｋḱḳḵƙʞκкĸ🅚🅺🄺]'
_D = r'[dｄďđḋḍḓḏɖɗᵭԁ∂ⅾⅆ🅓🅳🄳]'
_R = r'[rｒŕřṙȑṛṝṟɼɽɾʀʁягᴦ🅡🆁🄁]'

_SP = r"[\s\-_.,;:!?·•⋅∙*+~|/\\()\[\]{}<>'\"`´'\"\"、。，！？…「」『』【】〝〞@#$%^&=]*"
SEP = _SP  # 别名

_NAI = r'[奶妳乃廼迺]'
_LONG = r'[龙龍竜龒陇拢珑⻰]'
_TONE = r'[ːˑ˨˩˧˦˥]*'
_NAIS = r'(?:奶|乳|乳汁|乳液|酪|奶牛|牛乳|鲜奶)'

# =============================================
PATTERNS = []

# ---- 1. 直接中文 (5) ----
PATTERNS += [
    (_NAI + SEP + _LONG, "# 奶龙 / 奶-龙 / 乃 龙"),
    (r'女\s*乃\s*' + _LONG, "# 女乃龙 (拆字)"),
    (r'[奶乳]\s*[之的]?\s*' + _LONG, "# 乳龙 / 奶之龙"),
    (_NAIS + SEP + _LONG, "# 乳汁龙 / 乳液龙 / 奶牛龙"),
    (_LONG + SEP + r'(?:喝|吃|饮|吸)' + SEP + _NAIS, "# 龙喝奶"),
]

# ---- 2. 拼音 nailong (2) ----
PATTERNS += [
    (_N + '+' + SEP + _A + '+' + SEP + _I + '+' + SEP + _L + '+' + SEP + _O + '+' + SEP + _N + '+' + SEP + _G + '+',
     "# nailong (leet/homoglyph/拉伸全变形)"),
    (_N + '+[1234]?' + SEP + _A + '+[1234]?' + SEP + _I + '+[1234]?' + SEP + _L + '+[1234]?' + SEP + _O + '+[1234]?' + SEP + _N + '+[1234]?' + SEP + _G + '+[1234]?',
     "# nai3long2 (声调数字)"),
]

# ---- 3. 英文 milk dragon (7) ----
PATTERNS += [
    (_M + '+' + SEP + _I + '+' + SEP + _L + '+' + SEP + _K + '+' + SEP + _D + '+' + SEP + _R + '+' + SEP + _A + '+' + SEP + _G + '+' + SEP + _O + '+' + SEP + _N + '+',
     "# milk dragon"),
    (_M + '+' + SEP + _I + '+' + SEP + _L + '+' + SEP + _K + '+' + SEP + _L + '+' + SEP + _O + '{1,20}' + SEP + _N + '+' + SEP + _G + '+',
     "# milk long / loong"),
    (_M + '+' + SEP + _I + '+' + SEP + _L + '+' + SEP + _K + r'[yYiIeE]+' + SEP + _D + '+' + SEP + _R + '+' + SEP + _A + '+' + SEP + _G + '+' + SEP + _O + '+' + SEP + _N + '+',
     "# milky dragon"),
    (_M + '+' + SEP + _I + '+' + SEP + _L + '+' + SEP + _K + r'[yYiIeE]+' + SEP + _L + '+' + SEP + _O + '{1,20}' + SEP + _N + '+' + SEP + _G + '+',
     "# milky long"),
    (r'[dD∂][aA@4αа∂áàäâãåāăąǎȧạảấɑ][iI1!\|ïîĩīĭįıɨɩɪιі][rRяг][yYýÿŷȳẏẙỳỵỷỹуў]\s*' + _D + '+' + SEP + _R + '+' + SEP + _A + '+' + SEP + _G + '+' + SEP + _O + '+' + SEP + _N + '+',
     "# dairy dragon"),
    (r'[dD∂][aA@4αа∂áàäâãåāăąǎȧạảấɑ][iI1!\|ïîĩīĭįıɨɩɪιі][rRяг][yYýÿŷȳẏẙỳỵỷỹуў]\s*' + _L + '+' + SEP + _O + '{1,20}' + SEP + _N + '+' + SEP + _G + '+',
     "# dairy long"),
    (_D + '+' + SEP + _R + '+' + SEP + _A + '+' + SEP + _G + '+' + SEP + _O + '+' + SEP + _N + '+' + SEP + _M + '+' + SEP + _I + '+' + SEP + _L + '+' + SEP + _K + '+',
     "# dragonmilk (词序颠倒)"),
]

# ---- 4. 混搭 (4) ----
PATTERNS += [
    (_NAI + SEP + _L + '+' + SEP + _O + '{1,20}' + SEP + _N + '+' + SEP + _G + '+', "# 奶long"),
    (_NAI + SEP + _D + '+' + SEP + _R + '+' + SEP + _A + '+' + SEP + _G + '+' + SEP + _O + '+' + SEP + _N + '+', "# 奶dragon"),
    (_N + '+' + SEP + _A + '+' + SEP + _I + '+' + SEP + _LONG, "# nai龙"),
    (_M + '+' + SEP + _I + '+' + SEP + _L + '+' + SEP + _K + '+' + SEP + _LONG, "# milk龙"),
]

# ---- 5. 注音 (1) ----
PATTERNS += [
    (r'ㄋㄞ[ˇˋˊ˙1234]?\s*ㄌㄨㄥ[ˊˇˋ˙1234]?', "# 注音符号"),
]

# ---- 6. Emoji (1) ----
PATTERNS += [
    (r'[\U0001f95b\U0001f37c\U0001f37b\U0001f375\U0001f404\U0001f42e\U0001f402\U0001f416].{0,5}[\U0001f409\U0001f432]', "# Emoji 奶+龙"),
]

# ---- 7. 韩/日 (10) ----
PATTERNS += [
    (r'나\s*이\s*롱', "# 韩文 nailong"),
    (r'ナ\s*イ\s*ロ\s*ン\s*グ', "# 日文 nairongu"),
    (r'ナ\s*イ\s*ロ\s*ン', "# 日文 nairon"),
    (r'ミルク\s*ドラゴン', "# 日文 milk dragon"),
    (r'ドラゴン\s*ミルク', "# 日文 dragon milk"),
    (r'乳\s*ドラゴン', "# 日文 乳dragon"),
    (r'牛乳\s*[竜龍龙]', "# 日文 牛乳龙"),
    (r'우유\s*용', "# 韩文 milk dragon"),
    (r'용\s*우유', "# 韩文 dragon milk"),
    (r'밀크\s*드래곤', "# 韩文音译 milk dragon"),
]

# ---- 8. IPA (1) ----
PATTERNS += [
    (r'[/\[]?\s*[nɳη]+\s*[aɑäãåāăą@4∂]+\s*[ɪɨɩiι!1\|]+' + _TONE + r'\s*[lłɫɬ]+' + _TONE + r'\s*[ɔɒoοо0°ºʊɵ]+' + _TONE + r'\s*[ŋɳnη]+' + _TONE + r'\s*[\]]?',
     "# IPA /naɪlɔːŋ/"),
]

# ---- 9. 外语 — 拉丁字母 (19) ----
PATTERNS += [
    (r'[mMм][iIιі][lLł][cCс][hHһ]\s*[dD∂][rRяг][aAаα@4][cCс][hHһ][eEеë]', "# 德语 Milchdrache"),
    (r'[dD∂][rRяг][aAаα@4][gG9][oOо0][nNη]\s+(?:de|au|du)\s+[lL][aAаα@4][iIιі1\|][tTт]', "# 法语 dragon de lait"),
    (r'[lL][aAаα@4][iIιі1\|][tTт]\s+[dD][eEе]\s+[dD∂][rRяг][aAаα@4][gG9][oOо0][nNη]', "# 法语 lait de dragon"),
    (r'[dD∂][rRяг][aAаα@4][gG9][oOо0óÓ][nNη]\s+(?:de|del)\s+[lL][eEеë][cCс][hHһ][eEеë]', "# 西语 dragón de leche"),
    (r'[lL][eEеë][cCс][hHһ][eEеë]\s+(?:de|del)\s+[dD∂][rRяг][aAаα@4][gG9][oOо0óÓ][nNη]', "# 西语 leche de dragón"),
    (r'[dD∂][rRяг][aAаα@4][gG9][oOо0]\s+[dD][iIιі]\s+[lL][aAаα@4][tTт]+[eEеë]', "# 意语 drago di latte"),
    (r'[lL][aAаα@4][tTт]+[eEеë]\s+[dD][iIιі]\s+[dD∂][rRяг][aAаα@4][gG9][oOо0]', "# 意语 latte di drago"),
    (r'[dD∂][rRяг][aAаα@4][gG9][ãÃâÂaAаα@4][oOо0]\s+[dD][eEе]\s+[lL][eEе][iIιі][tTт][eEе]', "# 葡语 dragão de leite"),
    (r'[lL][eEе][iIιі][tTт][eEе]\s+[dD][eEе]\s+[dD∂][rRяг][aAаα@4][gG9][ãÃâÂaAаα@4][oOо0]', "# 葡语 leite de dragão"),
    (r'[mMм][eEеë][lLł][kKк]\s+[dD∂][rRяг][aAаα@4]+[kKк]', "# 荷语 melk draak"),
    (r'[mMм][jJ][öÖoOо0óÓòÒ][lLł][kKк]\s*[dD∂][rRяг][aAаα@4][kKк][eEеë]', "# 瑞典语 mjölkdrake"),
    (r'[mMм][æÆae]+[lLł][kKк][eEеë]\s*[dD∂][rRяг][aAаα@4][gG9][eEеë]', "# 丹麦语 mælkedrage"),
    (r'[mMм][lLł][eEеë][cCс][zZžŽ][nNη][yYуýÝ]\s*[sS][mMм][oOо0][kKк]', "# 波兰语 mleczny smok"),
    (r'[sS][mMм][oOо0][kKк]\s*[mMм][lLł][eEеë][cCс][zZžŽ][nNη][yYуýÝ]', "# 波兰语 smok mleczny"),
    (r'[sS][üÜuUùÙúÚ][tTт]\s*[eEеë][jJ][dD∂][eEеë][rRяг][hHһ][aAаα@4][sSşŞ][ıIιі]', "# 土耳其语 süt ejderhası"),
    (r'[eEеë][jJ][dD∂][eEеë][rRяг][hHһ][aAаα@4][sSşŞ][ıIιі]\s*[sS][üÜuUùÙúÚ][tTт][üÜuUùÙúÚ]', "# 土语 ejderha sütü"),
    (r'[nNη][aAаα@4][gG9][aAаα@4]\s*[sS][uUùÙúÚ][sS][uUùÙúÚ]', "# 印尼/马来语 naga susu"),
    (r'[sS][uUùÙúÚ][sS][uUùÙúÚ]\s*[nNη][aAаα@4][gG9][aAаα@4]', "# 印尼/马来语 susu naga"),
    (r'[mMм][eEеë][lLł][kKк][eEеë]\s*[dD∂][rRяг][aAаα@4][gG9][eEеë]', "# 挪威语 melkedrage"),
    (r'[rRяг][ồôÔoOо0óÓòÒ]+[nNη][gG9]\s+[sS][ữưŨƯuUùÙúÚ]+[aAаα@4âÂấẤầẦ]', "# 越南语 rồng sữa"),
    (r'[sS][ữưŨƯuUùÙúÚ]+[aAаα@4âÂấẤầẦ]\s+[rRяг][ồôÔoOо0óÓòÒ]+[nNη][gG9]', "# 越南语 sữa rồng"),
]

# ---- 10. 外语 — 西里尔 (4) ----
PATTERNS += [
    (r'мол[оoOо0]*[чƜ][нnNη][ыyY][йiIιі]?\s*[дdD∂][рrRяг][аaAаα@4][кkK][оoOо0][нnNη]', "# 俄语 молочный дракон"),
    (r'мол[оoOо0]+[кkK][оoOо0]\s*[дdD∂][рrRяг][аaAаα@4][кkK][оoOо0][нnNη]', "# 俄语 молоко дракон"),
    (r'на[йiIιі][лlL][оoOо0][нnNη][гgG9]', "# 俄语 найлонг"),
    (r'мол[оoOо0]+[чƜ][нnNη][иiIιі][йiIιі]\s*[дdD∂][рrRяг][аaAаα@4][кkK][оoOо0][нnNη]', "# 乌克兰语 молочний дракон"),
]

# ---- 11. 外语 — 非拉丁字母 (9) ----
PATTERNS += [
    (r'[δ∂дdD][ρррrR][άαаaA@4][κkK][οоoO0][ςsSσ]\s*[γgG9][άαаaA@4][λlL][αaAа@4][κkK][τтtT][οоoO0][ςsSσ]', "# 希腊语 δράκος γάλακτος"),
    (r'[γgG9][άαаaA@4][λlL][αaAа@4]\s*[δ∂дdD][ρррrR][άαаaA@4][κkK][οоoO0][υuU][ςsSσ]?', "# 希腊语 γάλα δράκου"),
    (r'มังกร\s*นม', "# 泰语 มังกรนม (dragon milk)"),
    (r'นม\s*มังกร', "# 泰语 นมมังกร (milk dragon)"),
    (r'تنين\s*الحليب', "# 阿拉伯语 تنين الحليب"),
    (r'حليب\s*التنين', "# 阿拉伯语 حليب التنين"),
    (r'דרקון\s*חלב', "# 希伯来语 דרקון חלב"),
    (r'חלב\s*דרקון', "# 希伯来语 חלב דרקון"),
    (r'दूध\s*ड्रैगन', "# 印地语 दूध ड्रैगन"),
]

# ---- 12. 谐音/昵称 (4) ----
PATTERNS += [
    (r'[奈耐氖釢哪]' + SEP + _LONG, "# 奈龙 / 耐龙 / 氖龙"),
    (_NAI + SEP + _LONG + SEP + r'[酱君桑様]', "# 奶龙酱 / 奶龙君"),
    (_NAI + r'[味嘴宝崽萌小]' + SEP + _LONG, "# 奶味龙 / 奶嘴龙"),
    (r'小' + SEP + _NAI + SEP + _LONG, "# 小奶龙"),
]

# ---- 13. 跨语言混搭 (any_milk × any_dragon, 850组合→1条正则) ----
from cross_lang_attack import CROSS_LANG_PATTERN
PATTERNS.append((CROSS_LANG_PATTERN, "# [跨语言] 任意语言的 '奶/milk' + 任意语言的 '龙/dragon' (850种组合)"))

# =============================================
# 输出到文件
# =============================================
with open('patterns_final.txt', 'w', encoding='utf-8') as f:
    f.write('# ============================================================\n')
    f.write('# 奶龙屏蔽器 — 纯文本正则表达式全集\n')
    f.write(f'# 共 {len(PATTERNS)} 条 pattern\n')
    f.write('# 使用: re.search(pattern, text, re.IGNORECASE)\n')
    f.write('# 输入预处理: unicodedata.normalize("NFKC", text)\n')
    f.write('#             re.sub(r\"[\\u200b-\\u200f\\u2060-\\u206f\\ufeff]\", \"\", text)\n')
    f.write('# ============================================================\n\n')
    for i, (pat, comment) in enumerate(PATTERNS, 1):
        f.write(f'{comment}\n')
        f.write(f'{pat}\n\n')

print(f'Done: {len(PATTERNS)} patterns written to patterns_final.txt')

# =============================================
# 验证
# =============================================
def quick_prep(s):
    s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'[​-‏⁠-⁯﻿­]', '', s)
    return s

tests = [
    ("奶龙", True), ("奶龍", True), ("nai long", True), ("n@1l0n9", True),
    ("ñäîłøñğ", True), ("η@!1οη9", True), ("𝐧𝐚𝐢𝐥𝐨𝐧𝐠", True),
    ("n4il0ng", True), ("nai3long2", True), ("🅝🅐🅘🅛🅞🅝🅖", True),
    ("milk dragon", True), ("m!lk dr4g0n", True), ("milky dragon", True),
    ("dragon milk", True), ("dragonmilk", True),
    ("nai龙", True), ("奶long", True), ("milk龙", True),
    ("奶味龙", True), ("奶嘴龙", True), ("小奶龙", True),
    ("奶龙酱", True), ("奶之龙", True), ("乳汁龙", True), ("龙喝奶", True),
    # 外语
    ("Milchdrache", True), ("dragon de lait", True), ("dragón de leche", True),
    ("drago di latte", True), ("dragão de leite", True),
    ("молочный дракон", True), ("молоко дракон", True), ("найлонг", True),
    ("молочний дракон", True),
    ("melk draak", True), ("mjölkdrake", True), ("mælkedrage", True),
    ("mleczny smok", True), ("süt ejderhası", True),
    ("naga susu", True), ("sữa rồng", True), ("rồng sữa", True),
    ("ミルクドラゴン", True), ("우유 용", True), ("밀크 드래곤", True),
    ("δράκος γάλακτος", True), ("มังกรนม", True),
    ("تنين الحليب", True), ("דרקון חלב", True), ("दूध ड्रैगन", True),
    # 不应拦截
    ("milk tea", False), ("dragon fruit", False), ("nail polish", False),
    ("龙年大吉", False), ("牛奶", False), ("尼龙", False),
]

passed = 0
for text, expect in tests:
    got = any(re.search(p, quick_prep(text), re.IGNORECASE) for p, _ in PATTERNS)
    if got == expect:
        passed += 1
    else:
        print(f'  [FAIL] {text!r}  expect={expect} got={got}')

print(f'\n{passed}/{len(tests)} passed')

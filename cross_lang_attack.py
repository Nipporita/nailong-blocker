"""
跨语言混搭攻击 — 奶词表 × 龙词表 笛卡尔积
=============================================
"milk 용", "Milch 龙", "ミルク dragon" ...
任意语言的 "奶/milk" + 任意语言的 "龙/dragon" 拼接
"""
import re, unicodedata

# ============ 奶/milk 词表 (所有语言) ============
MILK_WORDS = [
    # 中文
    r'奶', r'乳', r'乳汁', r'乳液', r'酪', r'奶牛', r'牛乳', r'鲜奶',
    # 英文 milk / milky
    r'[mMмμ][iIιі1|]+[lLł1|]+[kKкκ]',
    r'[mMмμ][iIιі1|]+[lLł1|]+[kKкκ][yYiIeE]+',
    # dairy
    r'[dD∂][aAаα@4]+[iIιі1|]+[rRяг][yYýÿŷ]',
    # 德语 Milch
    r'[mMм][iIιі][lLł][cCс][hHһ]',
    # 法语 lait
    r'[lL][aAаα@4][iIιі1|]+[tTт]',
    # 西语 leche
    r'[lL][eEеë][cCс][hHһ][eEеë]',
    # 意语 latte
    r'[lL][aAаα@4][tTт]+[eEеë]',
    # 葡语 leite
    r'[lL][eEе][iIιі][tTт][eEе]',
    # 俄语 молоко / молочный
    r'мол[оoOо0]+[кkK]?[оoOо0]?[чƜ]?[нnNη]?[ыyY]?[йiIιі]?',
    # 乌克兰语 молочний
    r'мол[оoOо0]+[чƜ][нnNη][иiIιі][йiIιі]',
    # 荷兰语 melk
    r'[mMм][eEеë][lLł][kKк]',
    # 瑞典语 mjolk
    r'[mMм][jJ][oOо0óÓòÒöÖ]+[lLł][kKк]',
    # 丹麦/挪威语 maelk/melk
    r'[mMм][æÆae]+[lLł][kKк]',
    r'[mMм][eEеë][lLł][kKк]',
    # 波兰语 mleko/mleczny
    r'[mMм][lLł][eEеë][kKк][oOо0]?[cCс]?[zZ]?[nNη]?[yY]?',
    # 土耳其语 sut
    r'[sSşŞ][uUùÙúÚüÜ]+[tTт]',
    # 印尼/马来语 susu
    r'[sS][uUùÙúÚ][sS][uUùÙúÚ]',
    # 越南语 sua
    r'[sS][uUùÙúÚữưŨƯ]+[aAаα@4âÂấẤầẦ]',
    # 韩语
    r'우유',      # milk
    r'밀크',      # milk 音译
    # 日语
    r'ミルク',    # milk
    r'牛乳',      # milk (kanji)
    # 泰语
    r'นม',
    # 阿拉伯语
    r'حليب',
    # 印地语
    r'दूध',
    # 希伯来语
    r'חלב',
]

# ============ 龙/dragon 词表 (所有语言) ============
DRAGON_WORDS = [
    # 中文
    r'[龙龍竜龒陇拢珑⻰]',
    # 英文 dragon
    r'[dD∂][rRяг][aAаα@4][gG96]+[oOо0óÓòÒ][nNη]',
    # loong / long
    r'[lLł1|]+[oOо0óÓòÒöÖ]{1,20}[nNη]+[gG96]+',
    # 德语 Drache
    r'[dD∂][rRяг][aAаα@4][cCс][hHһ][eEеë]',
    # 法语 dragon
    r'[dD∂][rRяг][aAаα@4][gG96][oOо0][nNη]',
    # 西语 dragon
    r'[dD∂][rRяг][aAаα@4][gG96][oOо0óÓòÒ][nNη]',
    # 意语 drago
    r'[dD∂][rRяг][aAаα@4][gG96][oOо0]',
    # 葡语 dragao
    r'[dD∂][rRяг][aAаα@4][gG96][aAаα@4ãÃâÂ][oOо0]',
    # 俄语 drakon
    r'[дdD∂][рrRяг][аaAаα@4][кkK][оoOо0][нnNη]',
    # 荷兰语 draak
    r'[dD∂][rRяг][aAаα@4]+[kKк]',
    # 瑞典语 drake
    r'[dD∂][rRяг][aAаα@4][kKк][eEеë]',
    # 丹麦/挪威语 drage
    r'[dD∂][rRяг][aAаα@4][gG96][eEеë]',
    # 波兰语 smok
    r'[sS][mMм][oOо0][kKк]',
    # 土耳其语 ejderha
    r'[eEеë][jJ][dD∂][eEеë][rRяг][hHһ][aAаα@4]',
    # 印尼/马来语 naga
    r'[nNη][aAаα@4][gG96][aAаα@4]',
    # 越南语 rong
    r'[rRяг][oOо0óÓòÒôÔồỒ]+[nNη][gG96]',
    # 韩语
    r'용',        # dragon
    r'드래곤',    # dragon 音译
    # 日语
    r'ドラゴン',  # dragon
    r'[竜龍龙]',  # dragon kanji
    # 泰语
    r'มังกร',
    # 阿拉伯语
    r'تنين',
    # 希伯来语
    r'דרקון',
    # 印地语
    r'ड्रैगन',
    # 希腊语 drakos/drakou
    r'[δ∂дdD][ρррrR][άαаaA@4][κkK][οоoO0][ςsSσυuU]?',
]

# ============ 构造跨语言混搭 Pattern ============
MILK = '(?:' + '|'.join(MILK_WORDS) + ')'
DRAGON = '(?:' + '|'.join(DRAGON_WORDS) + ')'
SEP = r"[\s\-_.,;:!?·•⋅∙*+~|/\\()\[\]{}<>'\"`´'\"\"、。，！？…「」『』【】〝〞@#$%^&=]*"

CROSS_LANG_PATTERN = MILK + SEP + DRAGON

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
    ("milk 용", True),           ("Milch 龙", True),
    ("lait 용", True),           ("leche dragon", True),
    ("milk มังกร", True),        ("ミルク 龙", True),
    ("우유 dragon", True),       ("молоко 龙", True),
    ("sữa dragon", True),        ("süt 용", True),
    ("milk дракон", True),       ("susu 龙", True),
    ("milk تنين", True),         ("milk דרקון", True),
    ("milk ड्रैगन", True),       ("dairy 용", True),
    ("Milch 드래곤", True),      ("leite ドラゴン", True),
    ("milk ドラゴン", True),     ("dairy 龙", True),
    ("milk loong", True),        ("milk long", True),
    # 不应匹配
    ("milk shake", False),       ("dragon fruit", False),
    ("龙年大吉", False),         ("milk tea", False),
]

passed = 0
for text, expect in tests:
    got = bool(re.search(CROSS_LANG_PATTERN, prep(text), re.IGNORECASE))
    ok = got == expect
    if ok: passed += 1
    print(f'  [{"PASS" if ok else "FAIL"}] {text!r:30s} expect={expect} got={got}')

print(f"\n{passed}/{len(tests)} passed")

# 保存
with open("pattern_cross_lang.txt", "w", encoding="utf-8") as f:
    f.write("# 奶龙屏蔽器 — 跨语言混搭 Pattern\n")
    f.write(f"# 奶词表: {len(MILK_WORDS)} 种表达 x 龙词表: {len(DRAGON_WORDS)} 种表达\n")
    f.write(f"# 笛卡尔积: {len(MILK_WORDS)*len(DRAGON_WORDS)} 种组合，1 条正则全覆盖\n\n")
    f.write(CROSS_LANG_PATTERN)
    f.write("\n")

print(f"\nPattern saved to pattern_cross_lang.txt ({len(CROSS_LANG_PATTERN)} chars)")

"""
奶龙屏蔽器 — 正则模式全集
===========================
用于弹幕姬单行文本过滤。每条 pattern 独立可用，直接 re.search(pattern, text)。

使用方式:
    import re
    for pat in PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True  # 命中，屏蔽此条弹幕
"""

import re

# ============================================================================
# 基础字符级替身 (homoglyph / leet)
# 攻击者可以用任何"看起来像"该字母的 Unicode 字符来逃避匹配
# ============================================================================

# ---- 组成 "nailong" 的字母（含 负圈/方框/IPA/多文种 视觉替身） ----

_N = (
    r"[nｎ"                   # 基本
    r"ñńňŉŋ"                  # 拉丁扩展
    r"ṅṇṉṋ"                   # 拉丁扩展附加
    r"ɲɳȵɴ"                   # IPA (+ small cap N)
    r"η"                      # 希腊 eta
    r"ип"                     # 西里尔
    r"∩"                      # 数学交符号 (视觉 ≈ n)
    r"🅝🅽🄽"                  # 负圈/负方/方框 N
    r"ⲡⲛ"                 # Coptic
    r"⼏⼐"                 # Kangxi 几/冂
    r"冂几"                 # CJK 形状≈N
    r"]"
)

_A = (
    r"[aａ"
    r"àáâãäå"                 # 拉丁
    r"āăąǎǻ"                  # 拉丁扩展
    r"ȁȃȧ"                    # 拉丁扩展B
    r"ạảấầẩẫậ"               # 越南语 a
    r"ɑɐαа"                   # IPA / 希腊 / 西里尔
    r"@4∂"                    # 符号替身
    r"∀ª"                     # 数学全称 / 阴性序数
    r"▲△"                     # 三角形 (视觉 ≈ A)
    r"🅐🅰🄰"                  # 负圈/负方/方框 A
    r"∆"                    # 增量符号 (三角≈A)
    r"]"
)

_I = (
    r"[iｉ"
    r"ìíîï"                   # 拉丁
    r"ĩīĭįı"                  # 拉丁扩展
    r"ɨɩɪ"                    # IPA
    r"ι"                      # 希腊 iota
    r"ії"                     # 西里尔
    r"!1\|¦"                # 符号替身 (+ broken bar)
    r"ǀǃ"                     # 齿/顶搭嘴音
    r"∣"                      # 数学整除 (视觉 ≈ |)
    r"▏▎▌▍"                   # 制表符 (视觉 ≈ i/l)
    r"ⅰ"                      # 罗马数字
    r"🅘🅸🄸"                  # 负圈/负方/方框 I
    r"│┃┆┇┊┋╎╏"             # 制表符竖线
    r"╵╷╹"                  # 制表符短线
    r"❙❚"                   # 装饰竖线
    r"丨丿"                  # CJK 笔画
    r"]"
)

_L = (
    r"[lｌ"
    r"ĺļľŀł"                  # 拉丁扩展
    r"ɫɬɭɮʅ"                  # IPA (+ lezh)
    r"˥ℓι"                    # 声调字母 / script l / 希腊iota(视觉≈l)
    r"1\|¦"                 # 符号替身
    r"ǀ"                      # 齿搭嘴音
    r"∣∥"                     # 数学整除/平行
    r"£"                      # 英镑符号 (视觉 ≈ L)
    r"❘❙❚"                    # 竖线装饰符
    r"ⅼ"                      # 罗马数字
    r"🅛🅻🄻"                  # 负圈/负方/方框 L
    r"Ӏ"                    # 西里尔 palochka (视觉=I/l)
    r"│┃┆┇┊┋╎╏╵"           # 制表符竖线
    r"丨"                    # CJK 竖笔画
    r"]"
)

_O = (
    r"[oｏ"
    r"òóôõöø"                 # 拉丁
    r"ōŏő"                    # 拉丁扩展
    r"ơǒǫȯȱ"                  # 越南语 / 拉丁扩展
    r"ɵʘɔʊɒɤ"                 # IPA (+ rams horn)
    r"οωσ"                    # 希腊
    r"о"                      # 西里尔
    r"0°º"                    # 数字/符号
    r"〇"                      # CJK 数字零 (U+3007 视觉 ≈ O)
    r"●○◯◎◉"                  # 几何圆
    r"⚬⚪⚫⊚⊛⊙◌"               # 杂项圆/圈
    r"🅞🅾🄾"                  # 负圈/负方/方框 O
    r"🔴🔵🟢🟡🟠🟣🟤"        # 彩色圆
    r"⚽⚾🏀🏐🎱"              # 球类
    r"☉"                    # 太阳
    r"ㅇ"                    # 韩文 ieung (圆圈)
    r"ⲟ"                    # Coptic o
    r"]"
)

_G = (
    r"[gｇ"
    r"ǵğĝġģǧ"                # 拉丁扩展
    r"ɠɡɢᵍɣ"                  # IPA
    r"96"                     # 数字替身
    r"ℊ"                      # script small g (U+210A)
    r"🅖🅶🄶"                  # 负圈/负方/方框 G
    r"ⲅ"                    # Coptic g
    r"]"
)

# ---- 组成 "milk" 的字母 ----

_M = (
    r"[mｍ"
    r"ḿṁṃ"                    # 拉丁扩展
    r"ɱɯʍ"                    # IPA
    r"ⅿ"                      # 罗马数字
    r"мμ"                     # 西里尔 / 希腊 mu
    r"🅜🅼🄼"                  # 负圈/负方/方框 M
    r"ⲙ"                    # Coptic m
    r"]"
)

_K = (
    r"[kｋ"
    r"ḱḳḵƙʞ"                  # 拉丁扩展
    r"κкĸ"                    # 希腊 / 西里尔 / kra
    r"🅚🅺🄺"                  # 负圈/负方/方框 K
    r"ⲕ"                    # Coptic k
    r"]"
)

# U 类 (romaji "miruku", 越南语 ữ 等)
_U = (
    r"[uｕ"
    r"ùúûüũ"                  # 拉丁
    r"ūŭůűų"                  # 拉丁扩展
    r"ưừứửữự"                 # 越南语 u
    r"ʉ"                      # IPA
    r"υ"                      # 希腊 upsilon
    r"ս"                     # 亚美尼亚 seh (视觉≈u)
    r"ⲩ"                    # Coptic ua
    r"]"
)

# ---- 组成 "dragon" 的字母 ----

_D = (
    r"[dｄ"
    r"ďđḋḍḓḏ"                 # 拉丁扩展
    r"ɖɗᵭԁ"                   # IPA / 西里尔
    r"∂"                      # 偏微分符号
    r"ⅾⅆ"                     # 罗马数字
    r"🅓🅳🄳"                  # 负圈/负方/方框 D
    r"ⲇ"                    # Coptic d
    r"]"
)

_R = (
    r"[rｒ"
    r"ŕřṙȑṛṝṟ"               # 拉丁扩展
    r"ɼɽɾʀʁ"                  # IPA
    r"ягᴦ"                    # 西里尔 ya/ge / 希腊 gamma
    r"ⲣ"                      # Coptic r
    r"🅡🆁🄁"                  # 负圈/负方/方框 R
    r"]"
)

# 允许在相邻字母之间出现任意分隔符（含 CJK 标点）
_SP = r"[\s\-_.,;:!?·•⋅∙*+~|/\\()\[\]{}<>'\"`´‘’“”、。，！？…「」『』【】〝〞《》〈〉‒–—―∼∽⁓@#$%^&=]*"

# 中文
_NAI = r"[奶妳乃廼迺仍扔艿𠮨孕]"
_LONG = r"[龙龍竜龒陇拢珑咙宠笼垄聋隆窿庞龚⻰]"
# 奶的同义多字词
_NAI_SYN = r"(?:奶|乳|乳汁|乳液|酪|奶牛|牛乳|鲜奶)"
# 龙的别名
_LONG_SYN = r"(?:龙|龍|竜|loong|dragon)"


# ============================================================================
# 正则模式（按攻击向量分类）
# ============================================================================

PATTERNS = []

# ---------------------------------------------------------------------------
# 1. 直接中文
# ---------------------------------------------------------------------------
PATTERNS += [
    # 奶龙 / 奶龍 / 乃龙 / 奈龙 及其拆分
    rf"{_NAI}{_SP}{_LONG}",
    # 女乃龙 (拆字)
    rf"女\s*乃\s*{_LONG}",
    # 乳龙 / 奶之龙 / 乳之龙 / 奶的龙
    rf"[奶乳]\s*[之的]?\s*{_LONG}",
    # 奶同义词 + 龙（乳汁龙、乳液龙、奶牛龙、酪龙）
    rf"{_NAI_SYN}{_SP}{_LONG}",
    # 龙 + 喝/吃 + 奶（语义颠倒：龙喝奶、龙吃奶）
    rf"{_LONG}{_SP}(?:喝|吃|饮|吸){_SP}{_NAI_SYN}",
]

# ---------------------------------------------------------------------------
# 2. 拼音 nailong（最核心，覆盖 leet + homoglyph + 字母拉伸 + 分离符）
# ---------------------------------------------------------------------------
PATTERNS += [
    # n-a-i-l-o-n-g  各类变形
    rf"{_N}+{_SP}{_A}+{_SP}{_I}+{_SP}{_L}+{_SP}{_O}+{_SP}{_N}+{_SP}{_G}+",
    # 拼音声调数字: nai3long2, nai3 long2, n4i3l0ng2
    rf"{_N}+[1234]?{_SP}{_A}+[1234]?{_SP}{_I}+[1234]?{_SP}{_L}+[1234]?{_SP}{_O}+[1234]?{_SP}{_N}+[1234]?{_SP}{_G}+[1234]?",
]

# ---------------------------------------------------------------------------
# 3. 英文意译: milk dragon / milk long / milk loong
# ---------------------------------------------------------------------------
PATTERNS += [
    # milk dragon
    rf"{_M}+{_SP}{_I}+{_SP}{_L}+{_SP}{_K}+{_SP}{_D}+{_SP}{_R}+{_SP}{_A}+{_SP}{_G}+{_SP}{_O}+{_SP}{_N}+",
    # milk long / loong
    rf"{_M}+{_SP}{_I}+{_SP}{_L}+{_SP}{_K}+{_SP}{_L}+{_SP}{_O}{{1,20}}{_SP}{_N}+{_SP}{_G}+",
    # milky dragon / milkie dragon
    rf"{_M}+{_SP}{_I}+{_SP}{_L}+{_SP}{_K}[yYiIeE]+{_SP}{_D}+{_SP}{_R}+{_SP}{_A}+{_SP}{_G}+{_SP}{_O}+{_SP}{_N}+",
    # milky long / milkie long
    rf"{_M}+{_SP}{_I}+{_SP}{_L}+{_SP}{_K}[yYiIeE]+{_SP}{_L}+{_SP}{_O}{{1,20}}{_SP}{_N}+{_SP}{_G}+",
    # dairy dragon  (d+a+i+r+y + dragon)
    rf"[dD∂][aA@4αа∂áàäâãåāăąǎȧạảấɑ][iI1!\|ïîĩīĭįıɨɩɪιі][rRяг][yYýÿŷȳẏẙỳỵỷỹуў]\s*{_D}+{_SP}{_R}+{_SP}{_A}+{_SP}{_G}+{_SP}{_O}+{_SP}{_N}+",
    # dairy long
    rf"[dD∂][aA@4αа∂áàäâãåāăąǎȧạảấɑ][iI1!\|ïîĩīĭįıɨɩɪιі][rRяг][yYýÿŷȳẏẙỳỵỷỹуў]\s*{_L}+{_SP}{_O}{{1,20}}{_SP}{_N}+{_SP}{_G}+",
    # 词序颠倒: dragon milk / dragonmilk
    rf"{_D}+{_SP}{_R}+{_SP}{_A}+{_SP}{_G}+{_SP}{_O}+{_SP}{_N}+{_SP}{_M}+{_SP}{_I}+{_SP}{_L}+{_SP}{_K}+",
    # 词序颠倒: dragon long (龙 + long 语义)
    rf"{_D}+{_SP}{_R}+{_SP}{_A}+{_SP}{_G}+{_SP}{_O}+{_SP}{_N}+{_SP}{_L}+{_SP}{_O}{{1,20}}{_SP}{_N}{{1,10}}{_SP}{_G}+",
]
# ---------------------------------------------------------------------------
# 4. 混搭（中文 + 拉丁）
# ---------------------------------------------------------------------------
PATTERNS += [
    # 奶 + long/loong
    rf"{_NAI}{_SP}{_L}+{_SP}{_O}{{1,20}}{_SP}{_N}+{_SP}{_G}+",
    # 奶 + dragon
    rf"{_NAI}{_SP}{_D}+{_SP}{_R}+{_SP}{_A}+{_SP}{_G}+{_SP}{_O}+{_SP}{_N}+",
    # nai + 龙
    rf"{_N}+{_SP}{_A}+{_SP}{_I}+{_SP}{_LONG}",
    # milk + 龙
    rf"{_M}+{_SP}{_I}+{_SP}{_L}+{_SP}{_K}+{_SP}{_LONG}",
]

# ---------------------------------------------------------------------------
# 5. 注音符号
# ---------------------------------------------------------------------------
PATTERNS += [
    # 注音带声调符号 或 数字声调 (ㄋㄞˇㄌㄨㄥˊ / ㄋㄞ3ㄌㄨㄥ2)
    r"ㄋㄞ[ˇˋˊ˙1234]?\s*ㄌㄨㄥ[ˊˇˋ˙1234]?",
]

# ---------------------------------------------------------------------------
# 6. Emoji 组合
# ---------------------------------------------------------------------------
PATTERNS += [
    # 奶/牛/乳制品 emoji + 龙类 emoji（中间可隔最多5个任意字符）
    r"[\U0001f95b\U0001f37c\U0001f37b\U0001f375\U0001f404\U0001f42e\U0001f402\U0001f416].{0,5}[\U0001f409\U0001f432]",
]

# ---------------------------------------------------------------------------
# 7. 韩文/日文表述
# ---------------------------------------------------------------------------
PATTERNS += [
    r"나\s*이\s*롱",          # 韩文 nailong
    r"ナ\s*イ\s*ロ\s*ン\s*グ",  # 日文 nairongu
    r"ナ\s*イ\s*ロ\s*ン",      # 日文 nairon
    # 日文 milk dragon (动漫圈常见)
    r"ミルク\s*ドラゴン",
    r"ドラゴン\s*ミルク",
    r"乳\s*ドラゴン",
    # 日文 牛乳+竜
    r"牛乳\s*[竜龍龙]",
]

# ---------------------------------------------------------------------------
# 8. IPA 音标 (视觉可辨: /naɪlɔːŋ/ /naɪ lɔːŋ/ [naɪ˨˩ lʊŋ˧˥])
# ---------------------------------------------------------------------------
PATTERNS += [
    # /naɪlɔŋ/ /naɪlɔːŋ/ [naɪlʊŋ] /naɪ lɔːŋ/ [naɪ˨˩ lʊŋ˧˥]
    # IPA 声调/长音符号可出现在任何音节边界
    rf"[/\[]?\s*[nɳη]+\s*[aɑäãåāăą@4∂]+\s*[ɪɨɩiι!1\|]+[ːˑ˨˩˧˦˥]*\s*[lłɫɬ]+[ːˑ˨˩˧˦˥]*\s*[ɔɒoοо0°ºʊɵ]+[ːˑ˨˩˧˦˥]*\s*[ŋɳnη]+[ːˑ˨˩˧˦˥]*\s*[\]]?",
]

# ---------------------------------------------------------------------------
# 9. 常见外语 "milk dragon" (德语/法语/西语/意语/葡语/俄语/越南语)
# ---------------------------------------------------------------------------
PATTERNS += [
    # 德语: Milchdrache
    r"[mMм][iIιі][lLł][cCс][hHһ]\s*[dD][rRяг][aAаα@4][cCс][hHһ][eEеë]",
    # 法语: dragon de lait / dragon au lait
    r"[dD∂][rRяг][aAаα@4][gG9][oOо0][nNη]\s+(?:de|au|du)\s+[lL][aAаα@4][iIιі1\|][tTт]",
    # 法语: lait de dragon
    r"[lL][aAаα@4][iIιі1\|][tTт]\s+[dD][eEе]\s+[dD∂][rRяг][aAаα@4][gG9][oOо0][nNη]",
    # 西班牙语: leche de dragón / dragón de leche
    r"[dD∂][rRяг][aAаα@4][gG9][oOо0óÓ][nNη]\s+(?:de|del)\s+[lL][eEеë][cCс][hHһ][eEеë]",
    r"[lL][eEеë][cCс][hHһ][eEеë]\s+(?:de|del)\s+[dD∂][rRяг][aAаα@4][gG9][oOо0óÓ][nNη]",
    # 意大利语: drago di latte / latte di drago
    r"[dD∂][rRяг][aAаα@4][gG9][oOо0]\s+[dD][iIιі]\s+[lL][aAаα@4][tTт]+[eEеë]",
    r"[lL][aAаα@4][tTт]+[eEеë]\s+[dD][iIιі]\s+[dD∂][rRяг][aAаα@4][gG9][oOо0]",
    # 葡萄牙语: leite de dragão / dragão de leite
    r"[dD∂][rRяг][aAаα@4][gG9][ãÃâÂaAаα@4][oOо0]\s+[dD][eEе]\s+[lL][eEе][iIιі][tTт][eEе]",
    r"[lL][eEе][iIιі][tTт][eEе]\s+[dD][eEе]\s+[dD∂][rRяг][aAаα@4][gG9][ãÃâÂaAаα@4][oOо0]",
    # 俄语: молочный дракон / молоко дракон / найлонг
    r"мол[оoOо0]*[чƜ][нnNη][ыyY][йiIιі]?\s*[дdD∂][рrRяг][аaAаα@4][кkK][оoOо0][нnNη]",
    r"мол[оoOо0]+[кkK][оoOо0]\s*[дdD∂][рrRяг][аaAаα@4][кkK][оoOо0][нnNη]",
    r"на[йiIιі][лlL][оoOо0][нnNη][гgG9]",
    # 越南语: rồng sữa / sữa rồng
    r"[rRяг][ồôÔoOо0óÓòÒ]+[nNη][gG9]\s+[sS][ữưŨƯuUùÙúÚ]+[aAаα@4âÂấẤầẦ]",
    r"[sS][ữưŨƯuUùÙúÚ]+[aAаα@4âÂấẤầẦ]\s+[rRяг][ồôÔoOо0óÓòÒ]+[nNη][gG9]",
    # 荷兰语: melk draak
    r"[mMм][eEеë][lLł][kKк]\s+[dD∂][rRяг][aAаα@4]+[kKк]",
    # 瑞典语: mjölkdrake
    r"[mMм][jJ][öÖoOо0óÓòÒ][lLł][kKк]\s*[dD∂][rRяг][aAаα@4][kKк][eEеë]",
    # 丹麦语: mælkedrage
    r"[mMм][æÆae]+[lLł][kKк][eEеë]\s*[dD∂][rRяг][aAаα@4][gG9][eEеë]",
]

# ---------------------------------------------------------------------------
# 8. 昵称/代称
# ---------------------------------------------------------------------------
PATTERNS += [
    # 奈龙 / 耐龙 / 氖龙 (同音替换，覆盖 龍 繁体)
    rf"[奈耐氖釢哪]{_SP}{_LONG}",
    # 奶龙酱 / 奶龙君 / 奶龙桑
    rf"{_NAI}{_SP}{_LONG}{_SP}[酱君桑様]",
    # 奶X龙（单字修饰语插入：奶味龙、奶嘴龙、奶宝龙、小奶龙）
    rf"{_NAI}[味嘴宝崽萌小]{_SP}{_LONG}",
    rf"小{_SP}{_NAI}{_SP}{_LONG}",
]

# ---------------------------------------------------------------------------
# 10. 重组攻击 — 龙拆字 / 缩写 / 形近字 / 连接符
# ---------------------------------------------------------------------------
_NAI_LOOK = r'[奶扔仍孕]'
_LONG_LOOK = r'[龙龍竜垄龚庞宠笼聋隆窿]'

PATTERNS += [
    # 龙拆字: 奶+立+月 / 奶+立+月+乚
    rf"{_NAI}{_SP}[立亠]{_SP}[月⺼]{_SP}[乚⺄]?",
    rf"{_NAI}{_SP}[立亠]{_SP}[乚⺄]",
    # NL 缩写 (NaiLong) — 单词边界，使用完整 N/L 字符类
    rf"(?<!\w){_N}+{_SP}{_L}+(?!\w)",
    # MD 缩写 (Milk Dragon)
    rf"(?<!\w){_M}+{_SP}{_D}+(?!\w)",
    # n*l / n×l (星号/乘号连接)
    rf"{_N}+{_SP}[\*×xX]{_SP}{_L}+",
    # milk→dragon / milk→龙 / 奶≈龙
    rf"{_M}+{_SP}{_I}+{_SP}{_L}+{_SP}{_K}+{_SP}[→≈]{_SP}{_D}+{_SP}{_R}+{_SP}{_A}+{_SP}{_G}+{_SP}{_O}+{_SP}{_N}+",
    rf"{_M}+{_SP}{_I}+{_SP}{_L}+{_SP}{_K}+{_SP}[→≈]{_SP}{_LONG}",
    rf"{_NAI}{_SP}[→≈]{_SP}{_LONG}",
    # 形近字混搭: 扔龙 / 奶垄 / 奶龚 / 奶庞
    rf"{_NAI_LOOK}{_SP}{_LONG_LOOK}",
    # Hangul Jamo 拆分 (ㅇㅜㅇㅠ = 우유 = milk)
    r"ㅇ\s*ㅜ\s*ㅇ\s*ㅠ",
    # milk x dragon / milk × dragon (x/× 连接)
    rf"{_M}+{_SP}{_I}+{_SP}{_L}+{_SP}{_K}+{_SP}[xX×]{_SP}{_D}+{_SP}{_R}+{_SP}{_A}+{_SP}{_G}+{_SP}{_O}+{_SP}{_N}+",
    # milk x long
    rf"{_M}+{_SP}{_I}+{_SP}{_L}+{_SP}{_K}+{_SP}[xX×]{_SP}{_L}+{_SP}{_O}{{1,20}}{_SP}{_N}+{_SP}{_G}+",
    # 奶 x 龙
    rf"{_NAI}{_SP}[xX×]{_SP}{_LONG}",
]


# ═══════════════════════════════════════════════════════════════════════════════
# 测试
# ═══════════════════════════════════════════════════════════════════════════════

def match_any(text: str) -> bool:
    """检查文本是否匹配任意一条 pattern。"""
    for pat in PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


TEST_CASES = [
    # === 应该拦截 ===
    ("奶龙", True),
    ("奶龍", True),
    ("奶 龙", True),
    ("奶-龙", True),
    ("女乃龙", True),
    ("乃龙", True),
    ("奈龙", True),
    ("耐龙", True),
    ("氖龙", True),
    ("乳龙", True),
    ("奶之龙", True),
    ("乳 龙", True),
    # pinyin
    ("nailong", True),
    ("nAILONG", True),
    ("n a i l o n g", True),
    ("n-a-i-l-o-n-g", True),
    ("naaaaaaaailooooooong", True),
    ("n4il0ng", True),
    ("n@1l0n9", True),
    ("n@!|0ng", True),
    ("náilóng", True),
    ("nǎilòng", True),
    ("n.ail.ong", True),
    ("n_ail_ong", True),
    ("n·ai·long", True),
    # math / fullwidth (NFKC normalization in preprocess)
    ("𝐧𝐚𝐢𝐥𝐨𝐧𝐠", True),
    ("𝑛𝑎𝑖𝑙𝑜𝑛𝑔", True),
    ("ｎａｉｌｏｎｇ", True),
    # homoglyph
    ("ñäîłøñğ", True),
    ("η@!1οη9", True),
    ("п@1|0п9", True),
    # english
    ("milk dragon", True),
    ("MILK DRAGON", True),
    ("m1lk dragon", True),
    ("m!lk dr4g0n", True),
    ("mi1k drag0n", True),
    ("milk loong", True),
    ("milk long", True),
    ("m i l k  d r a g o n", True),
    ("m1lk-dr4g0n", True),
    ("dairy dragon", True),
    ("dairy long", True),
    # mixed
    ("nai龙", True),
    ("奶long", True),
    ("milk龙", True),
    ("奶dragon", True),
    ("奶 loong", True),
    ("m1lk 龍", True),
    # zhuyin
    ("ㄋㄞˇ ㄌㄨㄥˊ", True),
    ("ㄋㄞㄌㄨㄥ", True),
    ("ㄋㄞˋ ㄌㄨㄥˊ", True),
    # emoji
    ("🥛🐉", True),
    ("🥛🐲", True),
    ("🍼🐉", True),
    ("🥛 🐉", True),
    ("🥛→🐉", True),
    # korean/japanese
    ("나이롱", True),
    ("ナイロング", True),
    # zero-width (preprocess handles this)
    ("奶​龙", True),
    ("nai​long", True),
    # alias
    ("奶龙酱", True),
    # === 新修补的攻击向量 ===
    # 同义替换
    ("乳汁龙", True),
    ("乳液龙", True),
    ("奶牛龙", True),
    ("酪龙", True),
    ("鲜奶龙", True),
    # 语义颠倒
    ("龙喝奶", True),
    ("龙吃奶", True),
    # 声调数字
    ("nai3long2", True),
    ("nai3 long2", True),
    ("n4i3l0ng2", True),
    # 词序颠倒
    ("dragon milk", True),
    ("dragonmilk", True),
    # milky 后缀
    ("milky dragon", True),
    ("milkie dragon", True),
    # 氖龍（繁体龙）
    ("氖龍", True),
    # 部首替代
    ("奶⻰", True),
    # emoji 扩展
    ("🐄🐉", True),
    ("🐮🐲", True),
    # CJK 标点分隔
    ("nai、long", True),
    ("nai。long", True),
    # === 不应该拦截 ===
    ("nail", False),
    ("long", False),
    ("dragon", False),
    ("牛奶", False),
    ("milk shake", False),
    ("尼龙", False),
    ("nail polish", False),
]


if __name__ == "__main__":
    # 简易预处理（只做 NFKC 和去零宽字符）
    def quick_prep(s):
        import unicodedata
        s = unicodedata.normalize("NFKC", s)
        s = re.sub(r"[​-‏⁠-⁯﻿]", "", s)
        return s

    passed = 0
    failed = 0
    for text, expect in TEST_CASES:
        cleaned = quick_prep(text)
        got = match_any(cleaned)
        if got == expect:
            passed += 1
            print(f"  [PASS] {text!r}")
        else:
            failed += 1
            print(f"  [FAIL] {text!r}  expect={expect} got={got}")

    print(f"\n--- {passed}/{passed+failed} passed ---")
    if failed == 0:
        print("All clear!")

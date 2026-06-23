"""
26字母 + 扩展 标准Homoglyph替换库
==================================
每个字母位置 = 一个全Unicode视觉形似字符黑洞
"""
import re, unicodedata

# ================================================================
# A-Z 完整 homoglyph 字符类
# ================================================================

HOMOGLYPHS = {
    'A': (
        r"[aａ"
        r"àáâãäåāăąǎǻȁȃȧạảấầẩẫậ"   # 拉丁扩展
        r"ɑɐαа"                        # IPA / 希腊 / 西里尔
        r"@4∂∀ª▲△∆"                    # 符号替身
        r"🅐🅰🄰"                        # 负圈/负方/方框
        r"]"
    ),

    'B': (
        r"[bｂ"
        r"ḃḅḇƀƃɓ"                      # 拉丁扩展 / IPA
        r"β"                            # 希腊 beta (在某些字体中≈B)
        r"в"                            # 西里尔 ve
        r"🅑🅱🄱"                        # 负圈/负方/方框
        r"]"
    ),

    'C': (
        r"[cｃ"
        r"ćĉċčçċȼƈ"                    # 拉丁扩展
        r"ɔ"                            # IPA open o (在某些字体≈c)
        r"с"                            # 西里尔 es
        r"🅒🅲🄲"                        # 负圈/负方/方框
        r"]"
    ),

    'D': (
        r"[dｄ"
        r"ďđḋḍḓḏɖɗᵭԁ∂ⅾⅆ"              # 拉丁扩展/IPA/西里尔/符号
        r"ⲇ"                            # Coptic
        r"🅓🅳🄳"                        # 负圈/负方/方框
        r"]"
    ),

    'E': (
        r"[eｅ"
        r"èéêëēĕėęěȅȇȩ"               # 拉丁扩展
        r"ẹẻẽếềểễệ"                    # 越南语 e
        r"ɛɜə"                          # IPA
        r"εе"                           # 希腊 epsilon / 西里尔 ie
        r"🅔🅴🄴"                        # 负圈/负方/方框
        r"]"
    ),

    'F': (
        r"[fｆ"
        r"ḟƒ"                           # 拉丁扩展
        r"ʄ"                            # IPA
        r"🅕🅵🄵"                        # 负圈/负方/方框
        r"]"
    ),

    'G': (
        r"[gｇ"
        r"ǵğĝġģǧɠɡɢᵍɣ"                # 拉丁扩展 / IPA
        r"96ℊ"                          # 数字/script g
        r"ⲅ"                            # Coptic
        r"🅖🅶🄶"                        # 负圈/负方/方框
        r"]"
    ),

    'H': (
        r"[hｈ"
        r"ĥȟḣḧḩḫẖ"                      # 拉丁扩展
        r"ɦɧħ"                          # IPA
        r"н"                            # 西里尔 en (在某些字体≈h)
        r"һ"                            # 西里尔 shha
        r"🅗🅷🄷"                        # 负圈/负方/方框
        r"]"
    ),

    'I': (
        r"[iｉ"
        r"ìíîïĩīĭįıɨɩɪιії"             # 拉丁/IPA/希腊/西里尔
        r"!1\|¦ǀǃ∣▏▎▌▍ⅰ"               # 符号/制表符/罗马
        r"│┃┆┇┊┋╎╏╵╷╹❙❚丨丿"           # 制表符/CJK笔画
        r"🅘🅸🄸"                        # 负圈/负方/方框
        r"]"
    ),

    'J': (
        r"[jｊ"
        r"ĵɉʝ"                          # 拉丁 / IPA
        r"ј"                            # 西里尔 je
        r"🅙🅹🄹"                        # 负圈/负方/方框
        r"]"
    ),

    'K': (
        r"[kｋ"
        r"ḱḳḵƙʞκкĸ"                    # 拉丁 / 希腊 / 西里尔 / kra
        r"ⲕ"                            # Coptic
        r"🅚🅺🄺"                        # 负圈/负方/方框
        r"]"
    ),

    'L': (
        r"[lｌ"
        r"ĺļľŀłɫɬɭɮʅ˥ℓι"              # 拉丁/IPA/声调/希腊iota
        r"1\|¦ǀ∣∥£❘❙❚ⅼ"              # 符号/数学/货币/罗马
        r"Ӏ│┃┆┇┊┋╎╏╵丨"               # 西里尔palochka/制表符/CJK
        r"🅛🅻🄻"                        # 负圈/负方/方框
        r"]"
    ),

    'M': (
        r"[mｍ"
        r"ḿṁṃɱɯʍⅿмμ"                   # 拉丁/IPA/罗马/西里尔/希腊
        r"ⲙ"                            # Coptic
        r"🅜🅼🄼"                        # 负圈/负方/方框
        r"]"
    ),

    'N': (
        r"[nｎ"
        r"ñńňŉŋṅṇṉṋɲɳȵɴ"              # 拉丁/IPA
        r"ηип∩"                         # 希腊/西里尔/数学
        r"ⲡⲛ⼏⼐冂几"                  # Coptic/Kangxi/CJK
        r"🅝🅽🄽"                        # 负圈/负方/方框
        r"]"
    ),

    'O': (
        r"[oｏ"
        r"òóôõöøōŏőơǒǫȯȱ"              # 拉丁扩展/越南语
        r"ɵʘɔʊɒɤοωσо"                  # IPA/希腊/西里尔
        r"0°º〇●○◯◎◉⚬⚪⚫⊚⊛⊙◌"          # 数字/符号/几何圆
        r"🔴🔵🟢🟡🟠🟣🟤⚽⚾🏀🏐🎱☉ㅇ"    # 彩色圆/球类/太阳/韩文
        r"ⲟ"                            # Coptic
        r"🅞🅾🄾"                        # 负圈/负方/方框
        r"]"
    ),

    'P': (
        r"[pｐ"
        r"ṕṗƥƿ"                         # 拉丁扩展
        r"ρр"                           # 希腊 rho / 西里尔 er
        r"🅟🅿🄿"                        # 负圈/负方/方框
        r"]"
    ),

    'Q': (
        r"[qｑ"
        r"ɋ"                            # IPA
        r"🅠🆀🄀"                        # 负圈/负方/方框
        r"]"
    ),

    'R': (
        r"[rｒ"
        r"ŕřṙȑṛṝṟɼɽɾʀʁ"               # 拉丁/IPA
        r"ягᴦⲣ"                         # 西里尔/希腊/Coptic
        r"🅡🆁🄁"                        # 负圈/负方/方框
        r"]"
    ),

    'S': (
        r"[sｓ"
        r"śŝşšṡșṣṩẛ"                   # 拉丁扩展
        r"ʂ"                            # IPA
        r"ѕ"                            # 西里尔 dze (视觉≈s)
        r"🅢🆂🄂"                        # 负圈/负方/方框
        r"]"
    ),

    'T': (
        r"[tｔ"
        r"ťțţṫṫṱẗ"                      # 拉丁扩展
        r"ƭțʈ"                          # 拉丁 / IPA
        r"т"                            # 西里尔 te
        r"🅣🆃🄃"                        # 负圈/负方/方框
        r"]"
    ),

    'U': (
        r"[uｕ"
        r"ùúûüũūŭůűųưừứửữự"           # 拉丁/越南语
        r"ʉυսⲩ"                         # IPA/希腊/亚美尼亚/Coptic
        r"🅤🆄🄴"                        # 负圈/负方/方框
        r"]"
    ),

    'V': (
        r"[vｖ"
        r"ṽṿʋ"                          # 拉丁 / IPA
        r"ν"                            # 希腊 nu (视觉≈v)
        r"🅥🆅🄅"                        # 负圈/负方/方框
        r"]"
    ),

    'W': (
        r"[wｗ"
        r"ẃẁŵẅẉẘɯʷ"                    # 拉丁 / IPA
        r"ωшщ"                          # 希腊 omega / 西里尔 sha/shcha
        r"🅦🅆🄦"                        # 负圈/负方/方框
        r"]"
    ),

    'X': (
        r"[xｘ"
        r"ẋẍ"                           # 拉丁扩展
        r"×"                            # 乘号
        r"х"                            # 西里尔 kha
        r"🅧🅇🄧"                        # 负圈/负方/方框
        r"]"
    ),

    'Y': (
        r"[yｙ"
        r"ýỳŷȳẏẙỳỵỷỹʏ"               # 拉丁 / IPA
        r"γуў"                          # 希腊 gamma / 西里尔 u/short u
        r"🅨🅈🄨"                        # 负圈/负方/方框
        r"]"
    ),

    'Z': (
        r"[zｚ"
        r"źżžƍƶɀʐ"                     # 拉丁 / IPA
        r"🅩🅉🄩"                        # 负圈/负方/方框
        r"]"
    ),
}

# ================================================================
# 验证
# ================================================================
print("=" * 60)
print("26字母 Homoglyph 替换库")
print("=" * 60)

for letter, pattern in HOMOGLYPHS.items():
    try:
        re.compile(pattern)
        # Count chars (approximate — remove [ and ])
        inner = pattern[pattern.index('[')+1:pattern.rindex(']')]
        print(f"  {letter}: {len(inner)} chars  OK")
    except re.error as e:
        print(f"  {letter}: ERROR — {e}")

# 验证每个标准字母都能匹配自己的类
print("\n--- 标准字母自匹配验证 ---")
for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    pat = HOMOGLYPHS[letter]
    lc = letter.lower()
    if re.match(pat + '+$', letter) or re.match(pat + '+$', lc):
        pass  # OK
    else:
        print(f"  {letter}: FAIL — '{letter}' not in own class!")

print("All letters self-match OK")

# 输出为标准Python模块
print("\n--- 生成 nailong_patterns 导入片段 ---")
for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    print(f"_{letter} = {HOMOGLYPHS[letter]}")

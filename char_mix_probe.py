"""
字符混搭探针 — 找出所有"视觉上像拉丁字母"的 Unicode 字符
===========================================================
然后检查是否已在 nailong_patterns 的字符类中覆盖。
"""
import unicodedata

# 当前字符类 (从 nailong_patterns 提取)
_CURRENT = {
    'n': set("nｎñńňŉŋṅṇṉṋɲɳȵηип🅝🅽🄽"),
    'a': set("aａàáâãäåāăąǎǻȁȃȧạảấầẩẫậɑαа@4∂🅐🅰🄰"),
    'i': set("iｉìíîïĩīĭįıɨɩɪιії!1|ǀǃⅰ🅘🅸🄸"),
    'l': set("lｌĺļľŀłɫɬɭʅ˥ℓ1|ǀⅼ🅛🅻🄻"),
    'o': set("oｏòóôõöøōŏőơǒǫȯȱɵʘɔʊɒοωσо0°º🅞🅾🄾"),
    'g': set("gｇǵğĝġģǧɠɡɢᵍ96ɣ🅖🅶🄶"),
    'm': set("mｍḿṁṃɱɯʍⅿмμ🅜🅼🄼"),
    'k': set("kｋḱḳḵƙʞκкĸ🅚🅺🄺"),
    'd': set("dｄďđḋḍḓḏɖɗᵭԁ∂ⅾⅆ🅓🅳🄳"),
    'r': set("rｒŕřṙȑṛṝṟɼɽɾʀʁягᴦ🅡🆁🄁"),
}

# ============================================================
# 候选视觉替身 — 按 Unicode 块分类
# ============================================================

CANDIDATES = {
    # ---- 几何形状 (U+25A0–U+25FF) ----
    'o': '●○◯◎◉◌◍◎',
    'a': '▲△',
    'i': '▏▎▍▌▋▊▉█',  # vertical-ish

    # ---- CJK 兼容 (U+3000+) ----
    'o': '〇',      # U+3007 IDEOGRAPHIC NUMBER ZERO — exactly O
    'n': '几',      # U+51E0 — looks vaguely like n
    'i': '丿',      # U+4E3F — vertical stroke, looks like i
    'l': '丨',      # U+4E28 — vertical stroke, looks like l

    # ---- 数学符号 (U+2200–U+22FF) ----
    'n': '∩',      # U+2229 INTERSECTION — upside-down U ≈ n
    'a': '∀',      # U+2200 FOR ALL — upside-down A
    'i': '∣',      # U+2223 DIVIDES — vertical bar
    'l': '∣∥',     # U+2223, U+2225 — vertical bars
    'o': '⊙⊚⊛',    # circled operators

    # ---- 类字母符号 (U+2100–U+214F) ----
    'a': 'ª',      # U+00AA FEMININE ORDINAL — looks like small a
    'o': 'º',      # U+00BA MASCULINE ORDINAL — looks like small o
    'g': 'ℊ',      # U+210A SCRIPT SMALL G
    'l': 'ℓ',      # U+2113 SCRIPT SMALL L (already in _L)
    'n': 'ℕ',      # U+2115 DOUBLE-STRUCK N (NFKC → N, but check)
    'i': 'ℹ',      # U+2139 INFORMATION SOURCE — i in circle

    # ---- 货币符号 ----
    'l': '£',      # U+00A3 POUND SIGN — looks like L
    'o': '¤',      # U+00A4 CURRENCY SIGN — circle

    # ---- 制表符 (U+2500–U+257F) ----
    'i': '│┃┆┇┊┋╎╏╵╷╸╹',
    'l': '│┃┆┇┊┋╎╏╵',

    # ---- 杂项符号 ----
    'o': '⚬⚪⚫⚽',  # small circle, circles, soccer ball
    'l': '❘❙❚',    # vertical bars

    # ---- 注音符号 ----
    'n': 'ㄇ',      # U+3107 BOPOMOFO M — looks like n in some fonts
    'l': 'ㄥ',      # U+3125 BOPOMOFO L

    # ---- 韩文 ----
    'o': 'ㅇ',      # U+3147 HANGUL IEUNG — circle
    'n': 'ㄴ',      # U+3134 HANGUL NIEUN — looks like L but could be n
    'l': 'ㄹ',      # U+3139 HANGUL RIEUL — looks like various

    # ---- 特殊标点 ----
    'o': '◌',      # dotted circle
    'i': '¦',      # U+00A6 BROKEN BAR — already in some classes

    # ---- 表情/杂项 ----
    'o': '🔴🔵🟢🟡🟠🟣🟤',  # colored circles — creative!

    # ---- 上标/下标 (NFKC 应该处理，但验证) ----
    'n': 'ⁿₙ',     # U+207F, U+2099
    'a': 'ᵃₐ',     # U+1D43, U+2090
    'i': 'ⁱᵢ',     # U+2071, U+1D62
    'o': 'ºᵒₒ',    # U+00BA, U+1D52, U+2092
    'g': 'ᵍ',      # U+1D4D
    'l': 'ˡₗ',     # U+02E1, U+2097
    'm': 'ᵐₘ',     # U+1D50, U+2098
    'k': 'ᵏ',      # U+1D4F
    'd': 'ᵈ',      # U+1D48
    'r': 'ʳᵣ',     # U+02B3, U+1D63

    # ---- 更多 IPA ----
    'n': 'ɴɲŋ',     # (already mostly covered)
    'a': 'ɐɒ',      # turned a, turned alpha (ɒ already in _O)
    'o': 'ɤ',       # U+0264 RAMS HORN — looks like o with tail
    'l': 'ɭɮ',      # retroflex l, lezh (already mostly covered)
    'r': 'ɻɽɼɽɾɿʀʁʂ',  # (already mostly covered)
}

# ============================================================
# 分析
# ============================================================

print("=" * 70)
print("字符混搭探针 — 视觉形似拉丁字母的 Unicode 字符")
print("=" * 70)

missing = {}
for letter, chars in CANDIDATES.items():
    current = _CURRENT.get(letter, set())
    missed = []
    for c in chars:
        if c not in current:
            # 检查 NFKC 是否会将此字符正规化为目标字母
            nfkc = unicodedata.normalize('NFKC', c)
            if nfkc == letter or nfkc.lower() == letter:
                continue  # NFKC 已处理
            missed.append(f'{c} U+{ord(c):04X} ({unicodedata.name(c, "?")})')
    if missed:
        missing[letter] = missed
        print(f"\n[{letter}] 缺失 {len(missed)} 个:")
        for m in missed:
            print(f"  {m}")

if not missing:
    print("\n🎉 全部覆盖!")
else:
    total = sum(len(v) for v in missing.values())
    print(f"\n--- 共 {total} 个字符缺失 ---")

    # 按优先级排序：视觉相似性高的优先
    HIGH_PRIORITY = {
        'o': '〇●○◯◎◉⚬⚪⚫⊚⊛⊙◌',
        'a': '∀ª▲△',
        'i': '∣¦▏▎▌▍',
        'l': '∣∥£❘❙❚',
        'n': '∩',
        'g': 'ℊ',
    }

    print("\n=== 高优先级添加建议（视觉极其相似）===")
    for letter, chars in HIGH_PRIORITY.items():
        needed = [c for c in chars if c not in _CURRENT.get(letter, set())
                  and unicodedata.normalize('NFKC', c) not in (letter, letter.lower())]
        if needed:
            print(f"  _{'AIOGLNR'.index(letter.upper()) if letter.upper() in 'AIOGLNR' else letter} += " + ''.join(needed))

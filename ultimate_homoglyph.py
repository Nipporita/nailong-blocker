"""
终极 homoglyph 扫描器
=====================
对每个拉丁字母，穷举全 Unicode 中视觉形似的字符。
然后与当前 nailong_patterns 的字符类对比，找出遗漏。
"""
import unicodedata
import sys

# 当前字符类
CURRENT = {
    'n': set("nｎñńňŉŋṅṇṉṋɲɳȵɴηип∩🅝🅽🄽"),
    'a': set("aａàáâãäåāăąǎǻȁȃȧạảấầẩẫậɑɐαа@4∂∀ª▲△🅐🅰🄰"),
    'i': set("iｉìíîïĩīĭįıɨɩɪιії!1|¦ǀǃ∣▏▎▌▍ⅰ🅘🅸🄸"),
    'l': set("lｌĺļľŀłɫɬɭɮʅ˥ℓ1|¦ǀ∣∥£❘❙❚ⅼ🅛🅻🄻"),
    'o': set("oｏòóôõöøōŏőơǒǫȯȱɵʘɔʊɒɤοωσо0°º〇●○◯◎◉⚬⚪⚫⊚⊛⊙◌🅞🅾🄾"),
    'g': set("gｇǵğĝġģǧɠɡɢᵍɣ96ℊ🅖🅶🄶"),
    'm': set("mｍḿṁṃɱɯʍⅿмμ🅜🅼🄼"),
    'k': set("kｋḱḳḵƙʞκкĸ🅚🅺🄺"),
    'd': set("dｄďđḋḍḓḏɖɗᵭԁ∂ⅾⅆ🅓🅳🄳"),
    'r': set("rｒŕřṙȑṛṝṟɼɽɾʀʁягᴦ🅡🆁🄁"),
    'u': set("uｕùúûüũūŭůűųưừứửữựʉυ"),
}

# ================================================================
# 全 Unicode 视觉形似扫描 (按 Unicode 块)
# ================================================================

FOUND = {k: [] for k in CURRENT}

def scan_block(start, end, letter, chars_str):
    """扫描一个 Unicode 块，检查视觉形似的字符"""
    for c in chars_str:
        if c not in CURRENT[letter]:
            nfkc = unicodedata.normalize('NFKC', c)
            if nfkc != letter and nfkc.lower() != letter:
                FOUND[letter].append((c, f'U+{ord(c):04X}', unicodedata.name(c, '?')))

# ---- n ----
scan_block(0, 0, 'n', '几冂𠃐𠘨')
scan_block(0, 0, 'n', 'ոպ')  # Armenian
scan_block(0, 0, 'n', 'ⲡⲛ')  # Coptic
scan_block(0, 0, 'n', '⼏⼐')  # Kangxi radicals: 几, 冂

# ---- a ----
scan_block(0, 0, 'a', '∆')    # INCREMENT
scan_block(0, 0, 'a', 'Дд')   # Cyrillic De (could be A in some fonts)
scan_block(0, 0, 'a', '⍺⍶')   # APL

# ---- i ----
scan_block(0, 0, 'i', '丨丿')   # CJK strokes
scan_block(0, 0, 'i', '❙❚')   # vertical bars
scan_block(0, 0, 'i', '│┃┆┇┊┋╎╏╵╷╸╹')  # box drawing

# ---- l ----
scan_block(0, 0, 'l', '丨')     # CJK vertical stroke
scan_block(0, 0, 'l', '│┃┆┇┊┋╎╏╵')  # box drawing
scan_block(0, 0, 'l', 'Ӏ')     # CYRILLIC LETTER PALOCHKA (looks exactly like I/l)

# ---- o ----
scan_block(0, 0, 'o', '口ロ')   # CJK mouth (square-ish but could be o)
scan_block(0, 0, 'o', 'ㅇ')     # Hangul ieung (circle)
scan_block(0, 0, 'o', '⚽🏀⚾🏐🎱') # sports balls
scan_block(0, 0, 'o', '🔴🔵🟢🟡🟠🟣🟤⚫⚪') # colored circles
scan_block(0, 0, 'o', 'о')      # Cyrillic o (already, just verifying)
scan_block(0, 0, 'o', 'ο')      # Greek omicron (already)
scan_block(0, 0, 'o', 'օ')      # Armenian o
scan_block(0, 0, 'o', 'ⲟⲟ')    # Coptic o
scan_block(0, 0, 'o', '〇')      # CJK zero (already)
scan_block(0, 0, 'o', '☉')      # Sun symbol

# ---- g ----
scan_block(0, 0, 'g', 'ɠ')      # (verify already)
scan_block(0, 0, 'g', 'ɡ')      # (verify already)

# ---- m ----
scan_block(0, 0, 'm', 'ⅿ')      # (verify already)
scan_block(0, 0, 'm', 'м')      # Cyrillic em (already)
scan_block(0, 0, 'm', 'ⲙ')      # Coptic m

# ---- k ----
scan_block(0, 0, 'k', 'κ')      # Greek kappa (already)
scan_block(0, 0, 'k', 'к')      # Cyrillic ka (already)
scan_block(0, 0, 'k', 'ⲕ')      # Coptic k

# ---- d ----
scan_block(0, 0, 'd', 'ԁ')      # Cyrillic (already)
scan_block(0, 0, 'd', 'ⅾⅆ')    # Roman numerals (already)
scan_block(0, 0, 'd', '∂')      # partial differential (already)
scan_block(0, 0, 'd', 'ⲇ')      # Coptic d

# ---- r ----
scan_block(0, 0, 'r', 'я')      # Cyrillic ya (already)
scan_block(0, 0, 'r', 'г')      # Cyrillic ge (already)
scan_block(0, 0, 'r', 'ⲣ')      # Coptic r

# ---- u ----
scan_block(0, 0, 'u', 'ս')      # Armenian u
scan_block(0, 0, 'u', 'ⲩ')      # Coptic u

# ================================================================
# 报告
# ================================================================
print("=" * 70)
print("终极 Homoglyph 遗漏报告")
print("=" * 70)

total_new = 0
for letter in 'nailogmkdru':
    if FOUND[letter]:
        print(f"\n[{letter}] 新增 {len(FOUND[letter])} 个:")
        for c, code, name in sorted(FOUND[letter], key=lambda x: x[1]):
            print(f"  {c}  {code}  {name}")
        total_new += len(FOUND[letter])

print(f"\n--- 共 {total_new} 个新字符可添加 ---")

# 生成新字符类
if total_new > 0:
    print("\n=== 建议更新的字符类 ===")
    for letter in 'nailogmkdru':
        if FOUND[letter]:
            new_chars = ''.join(c for c, _, _ in sorted(FOUND[letter], key=lambda x: x[1]))
            print(f"\n_{letter.upper()} += {new_chars!r}")

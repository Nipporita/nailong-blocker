"""
拼音音节类生成器
================
使用 pypinyin 数据，为指定拼音音节生成所有同音汉字的字符类。
"""
from pypinyin.pinyin_dict import pinyin_dict
import unicodedata, re

def strip_tone(py):
    """去除拼音声调，返回基本音节。如 mǐ→mi, lā→la"""
    tone_marks = 'āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ'
    no_tone = 'aaaaeeeeiiiioooouuuuvvvv'
    trans = str.maketrans(tone_marks, no_tone)
    return py.translate(trans)

def get_chars_for_syllables(*target_syllables):
    """获取所有匹配指定音节的汉字（含所有声调）"""
    chars = set()
    for code, py_str in pinyin_dict.items():
        try:
            c = chr(code)
        except:
            continue
        # pinyin_dict 值是逗号分隔的多个读音
        for py in py_str.split(','):
            py = py.strip()
            base = strip_tone(py)
            if base in target_syllables:
                chars.add(c)
                break
    return ''.join(sorted(chars, key=lambda c: ord(c)))

# ================================================================
# milk: mi/mei/me + er/le/lu/ru/re/li + ke/ku/ge/gu/ka/ga
# ================================================================
MI_CLASS = get_chars_for_syllables('mi', 'mei', 'me', 'mie')
ER_CLASS = get_chars_for_syllables('er', 'le', 'lu', 'ru', 're', 'li', 'lv', 'lve')
KE_CLASS = get_chars_for_syllables('ke', 'ku', 'ge', 'gu', 'ka', 'ga')

# ================================================================
# dragon: duo/de/du/dou/da + la/ra/na/le + gong/gen/gang/gon
# ================================================================
DUO_CLASS = get_chars_for_syllables('duo', 'de', 'du', 'dou', 'da')
LA_CLASS = get_chars_for_syllables('la', 'ra', 'na', 'le', 're', 'ne')
GONG_CLASS = get_chars_for_syllables('gong', 'gen', 'gang', 'gon', 'geng')

print(f"MILK  mi/mei/me:  {len(MI_CLASS)} chars")
print(f"MILK  er/le/lu/ru: {len(ER_CLASS)} chars")
print(f"MILK  ke/ku/ge/gu: {len(KE_CLASS)} chars")
print(f"DRAGON duo/de/du:  {len(DUO_CLASS)} chars")
print(f"DRAGON la/ra/na:   {len(LA_CLASS)} chars")
print(f"DRAGON gong/gen:   {len(GONG_CLASS)} chars")

# ================================================================
# 测试用户提到的漏字
# ================================================================
print("\n--- 漏字验证 ---")
for c in '度垃塨弥二科密路堀':
    base = ''
    for code, py_str in pinyin_dict.items():
        if code == ord(c):
            base = strip_tone(py_str.split(',')[0].strip())
            break
    in_milk = c in MI_CLASS or c in ER_CLASS or c in KE_CLASS
    in_dragon = c in DUO_CLASS or c in LA_CLASS or c in GONG_CLASS
    print(f"  {c} (pinyin:{base}) milk={'✓' if in_milk else '✗'} dragon={'✓' if in_dragon else '✗'}")

# ================================================================
# 验证交集（防止一个字符在两个类中造成误匹配）
# ================================================================
for a, b, na, nb in [(MI_CLASS, ER_CLASS, 'MI', 'ER'),
                       (ER_CLASS, KE_CLASS, 'ER', 'KE'),
                       (DUO_CLASS, LA_CLASS, 'DUO', 'LA'),
                       (LA_CLASS, GONG_CLASS, 'LA', 'GONG')]:
    overlap = set(a) & set(b)
    if overlap:
        print(f"\nWARNING: {na} ∩ {nb} overlap: {''.join(overlap)}")

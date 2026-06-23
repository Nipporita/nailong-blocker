# 奶龙屏蔽器 — Nailong Blocker

穷举一切能在文本中指代"**奶龙**"的写法并予以拦截。

既是盾 🛡️，也是矛 🗡️ —— 从攻击者的视角穷举所有变形，再用正则逐一封堵。

## 心路历程

> 要完全屏蔽"奶龙"这两个字，有多难？

一开始我以为就是 `奶龙` 和 `nailong` 两条正则的事。

然后有人打了 `n@1l0n9`。行，加个 leet 替换。又有人打 `milk dragon`。行，加英文。接着是 `Milch Drache`、`lait de dragon`、`молочный дракон`……德语、法语、俄语一个个冒出来。

然后有人说：那我把"奶"换成 emoji 呢？🥛🐉。行，加 emoji。

又有人说：那我用注音符号呢？ㄋㄞˇ ㄌㄨㄥˊ。行，加注音。

又有人说：那我用韩文拼呢？나이롱。行。

又有人说：那我把"奶"写成日文假名 ない 呢？那用希腊字母拼 ναι λονγκ 呢？用阿拉伯文 ناي لونغ 呢？

又有人说：那我不写"奶龙"，我写"乳汁龙"、"乳液龙"、"奶牛龙"、"酪龙"呢？那"龙喝奶"呢？"breast dragon"呢？"boob 龙"呢？

又有人说：那我不写英文 milk，我用汉字音译"弥二科"、"密路堀"、"度垃塨"呢？milk 有 425 个同音汉字，dragon 有 635 个——任意排列组合就是几亿种写法。

又有人说：那每个拉丁字母我都不用拉丁字母写呢？n 可以是 `∩`、`п`、`η`、`几`、`冂`……a 可以是 `∀`、`∆`、`▲`、`@`……o 可以是 `⚽`、`🔴`、`〇`、`ㅇ`……26 个字母，每个都是一个 Unicode 黑洞。

又有人说：那我混搭呢？milk(英文) + 용(韩文龙) + 龙(中文)？Milch(德文奶) + 🐉(emoji)？

……

到 v1.12，这个项目已经有 **79 条正则**、**26 个字母的全 Unicode 替换库**、覆盖 **20+ 种语言**、**拼音自动生成的数亿同音字排列**——而我很清楚，**到现在还有很多表达没有被封堵**。

"奶龙"两个字，是人类语言全部表达能力的缩影。字符、读音、翻译、俚语、音译、拆字、象形——每一个维度都是一个无限的空间。你永远不可能穷举，只能无限逼近。

这就是自然语言的防火墙难题。

## 核心原理

每个拉丁字母位置都是一个**全 Unicode 视觉形似字符黑洞**。例如字母 `n` 可以由以下任意字符替代：

> `n ｎ ñ ń ň ŋ ṅ ṇ ṉ ṋ ɲ ɳ ȵ ɴ η и п ∩ ⲡ ⲛ ⼏ ⼐ 冂 几 🅝 🅽 🄽`

字母 **n-a-i-l-o-n-g** 七位各成一个黑洞，吸收全 Unicode（拉丁/希腊/西里尔/科普特/亚美尼亚/IPA/CJK/数学符号/制表符/Emoji彩色圆/球类/货币/罗马数字/负圈方框字母）中所有视觉形似字符。

## 快速使用

```
每条 pattern 独立可用
匹配: re.search(pattern, text, re.IGNORECASE)
预处理: NFKC正规化 + 去零宽/RTL/组合符号
```

### 纯文本 Pattern

**[`patterns_final.txt`](patterns_final.txt)** — 79 条纯正则，可直接复制到任何支持正则的系统中使用。

### 标准替换库

**[`homoglyph_lib.py`](homoglyph_lib.py)** — 完整 26 字母 + 扩展 homoglyph 标准替换库。每字母对应一个全 Unicode 视觉形似字符黑洞。

### Python 模块

```python
from nailong_patterns import PATTERNS, match_any

if match_any("几∆丨Ӏ🔴п❙"):  # 视觉 = nailong
    print("拦截!")
```

## 覆盖的攻击向量

| 类别 | 示例 |
|---|---|
| 直接中文 | 奶龙、奶龍、乃龙、女乃龙 |
| 火星文/异体字 | 仍龙、孕龙、𠮨宠、扔隆 |
| 同音/同义 | 奈龙、氖龙、乳汁龙、乳液龙、奶牛龙、酪龙 |
| 拼音全变形 | nailong、n@1l0n9、n-a-i-l-o-n-g、naaaaailoooong |
| 声调数字 | nai3long2、n4i3l0ng2 |
| 26字母全Unicode替身 | 𝐧𝐚𝐢𝐥𝐨𝐧𝐠、🅝🅐🅘🅛🅞🅝🅖、ñäîłøñğ、几∆丨🔴п❙ |
| Emoji | 🥛🐉、🐄🐲、👵🐉、🍼dragon |
| 英文意译 | milk dragon、m!lk dr4g0n、milky dragon、dairy dragon |
| 词序颠倒 | dragon milk、dragonmilk |
| 混搭 | nai龙、奶long、milk龙、奶dragon、奶🅛🅞🅝🅖 |
| 语义重排 | 龙喝奶、龙吃奶 |
| 注音 | ㄋㄞˇㄌㄨㄥˊ、ㄋㄞ3ㄌㄨㄥ2 |
| IPA 音标 | /naɪlɔːŋ/、[naɪ˨˩ lʊŋ˧˥] |
| 日语音读/Romaji | にゅうりゅう、miruku doragon、ない龙、milk りゅう |
| 日/韩 | ミルクドラゴン、우유 용、나이롱、밀크 드래곤 |
| 日式当て字 | 魅留玖怒羅権、美留久土羅権 |
| 多语言音读 | най лонг(俄)、ναι λονγκ(希)、나이 롱(韩)、ناي لونغ(阿)、मिल्क ड्रैगन(印)、མིལཀ འབྲུག(藏)、มิลค์ มังกร(泰)、מילק דרקון(希伯来)、მილკი დრაგონი(格)、միլկ դրագոն(亚) |
| 拼音任意音节 | 弥二科爪公、密路堀多拉贡、度垃塨 (pypinyin自动, 3.94亿+5570万组合) |
| 俚语(奶) | breast/boob/tit/udder/bosom/jug/chest + dragon |
| 俚语(龙) | drake/wyrm/wyvern + milk |
| 缩写/连接符 | NL、MD、n×l、milk→dragon、奶≈龙、milk×dragon |
| 龙字拆解 | 奶立月、奶立月乚 |
| RTL 反转 | ‮gnolian‬ (显示为 nailong) |
| 组合/隐形符号 | n⃝a⃝i⃝l⃝o⃝n⃝g⃝ (变体选择器/标签字符/蒙古语分隔自动剥离) |
| 昵称/修饰 | 奶龙酱、奶味龙、奶嘴龙、小奶龙 |
| **跨语言混搭** | **45奶 × 39龙 = 1755组合 → 1条正则 (22KB)** |
| 翻译全覆盖 | Milchdrache(德)、dragon de lait(法)、dragón de leche(西)、drago di latte(意)、dragão de leite(葡)、молочный дракон(俄)、молочний дракон(乌)、melk draak(荷)、mjölkdrake(瑞)、mælkedrage(丹)、mleczny smok(波)、süt ejderhası(土)、naga susu(印尼)、sữa rồng(越)、มังกรนม(泰)、تنين الحليب(阿)、דרקון חלב(希伯来)、दूध ड्रैगन(印地)、δράκος γάλακτος(希) |
| 缩写/连接符 | NL、MD、n×l、milk→dragon、奶≈龙 |
| 龙字拆解 | 奶立月、奶立月乚 |
| RTL 反转 | ‮gnolian‬ (显示为 nailong) |
| 组合符号 | n⃝a⃝i⃝l⃝o⃝n⃝g⃝ (组合圆圈自动剥离) |
| 昵称/修饰 | 奶龙酱、奶味龙、奶嘴龙、小奶龙 |

## 跨语言混搭

```
65 种奶表达 × 59 种龙表达 = 3835 种组合 → 1 条正则 (23KB)
```

拼音音节类由 **pypinyin** 自动生成，覆盖所有同音汉字：

| 音节 | 规模 |
|---|---|
| milk ≈ mi/mei × er/le/lu/ru × ke/ku/ge | 425×1291×718 ≈ **3.94亿** 同音字排列 |
| dragon ≈ duo/de/du × la/ra/na × gong/gen | 635×283×310 ≈ **5570万** 同音字排列 |

包括 emoji、负圈字母、方框字母、26 字母 homoglyph 全库、中文、拼音、火星文、日语音读、日式当て字、19 种外语之间的任意排列组合。

## 预处理

防线依赖输入预处理来击溃隐形混淆层：

```python
def prep(text):
    text = unicodedata.normalize('NFKC', text)       # 全角/数学字母→普通字母
    text = re.sub(r'[​-‏⁠-⁯﻿­᠎]', '', text)  # 零宽/软连字符/蒙古语元音分隔
    text = re.sub(r'[‪-‮]', '', text)               # RTL/LTR 覆盖
    if was_rtl: text = text[::-1]                     # RTL→反转文本
    text = re.sub(r'[︀-️]', '', text)               # 变体选择器 VS1-16
    text = ''.join(c for c in text if ord(c) < 0xE0000 or ord(c) > 0xE007F)  # 标签字符
    text = re.sub(r'[⃐-⃿]', '', text)               # 组合圆圈/三角/方块
    return text
```

## 文件说明

| 文件 | 用途 |
|---|---|
| `patterns_final.txt` | **最终产物** — 79 条纯文本正则 (72KB)，直接可用 |
| `nailong_patterns.py` | Python 模块版，含 26 字母 homoglyph 全库 + match_any() |
| `homoglyph_lib.py` | A-Z 标准替换库（每字母一个全 Unicode 视觉黑洞） |
| `pinyin_class_gen.py` | 拼音音节类生成器（pypinyin 自动，3.94亿+5570万组合） |
| `cross_lang_attack.py` | 跨语言混搭探针 — 45×39=1755 组合 |
| `generate_patterns.py` | Pattern 生成器 + 56 条测试用例 |
| `attack_probe.py` | 攻击探针 — 140+ 种攻击向量 |
| `recomb_attack.py` | 重组攻击探针 — 拆字/缩写/连接符/RTL |
| `edge_probe.py` | 边缘攻击探针 — 隐形分隔/变体选择器/特殊标点 |
| `char_mix_probe.py` | 字符混搭探针 |
| `ultimate_homoglyph.py` | 终极 homoglyph 扫描器 |
| `nailong_blocker.py` | 初版架构（保留供参考） |

## 版本

- **v1.13** — 极限文字音读 (印地/泰/希伯来/藏/格鲁吉亚/亚美尼亚 6种文字)
- **v1.12** — 多语言音读攻击 (韩/俄/希腊/阿拉伯 拼读拦截)
- **v1.11** — pypinyin 系统化拼音音节类 (3.94亿+5570万同音字组合)
- **v1.10** — 26 字母标准替换库(全A-Z) + 中文音译 + 俚语全覆盖
- **v1.0** — 初始发布，69 条正则，19 种外语

# 奶龙屏蔽器 — Nailong Blocker

穷举一切能在文本中指代"**奶龙**"的写法并予以拦截。

既是盾 🛡️，也是矛 🗡️ —— 从攻击者的视角穷举所有变形，再用正则逐一封堵。

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
| Unicode 伪装 | 𝐧𝐚𝐢𝐥𝐨𝐧𝐠、🅝🅐🅘🅛🅞🅝🅖、ñäîłøñğ、几∆丨🔴п❙ |
| Emoji | 🥛🐉、🐄🐲、👵🐉、🍼dragon |
| 英文意译 | milk dragon、m!lk dr4g0n、milky dragon、dairy dragon |
| 词序颠倒 | dragon milk、dragonmilk |
| 混搭 | nai龙、奶long、milk龙、奶dragon、奶🅛🅞🅝🅖 |
| 语义重排 | 龙喝奶、龙吃奶 |
| 注音 | ㄋㄞˇㄌㄨㄥˊ、ㄋㄞ3ㄌㄨㄥ2 |
| IPA 音标 | /naɪlɔːŋ/、[naɪ˨˩ lʊŋ˧˥] |
| 日语音读/Romaji | にゅうりゅう、miruku doragon、milk りゅう |
| 日/韩 | ミルクドラゴン、우유 용、나이롱、밀크 드래곤 |
| **跨语言混搭** | **milk 용、Milch 龙、lait ドラゴン、🥛ドラゴン、🅼🅸🅻🅺🐉** |
| 翻译全覆盖 | Milchdrache(德)、dragon de lait(法)、dragón de leche(西)、drago di latte(意)、dragão de leite(葡)、молочный дракон(俄)、молочний дракон(乌)、melk draak(荷)、mjölkdrake(瑞)、mælkedrage(丹)、mleczny smok(波)、süt ejderhası(土)、naga susu(印尼)、sữa rồng(越)、มังกรนม(泰)、تنين الحليب(阿)、דרקון חלב(希伯来)、दूध ड्रैगन(印地)、δράκος γάλακτος(希) |
| 缩写/连接符 | NL、MD、n×l、milk→dragon、奶≈龙 |
| 龙字拆解 | 奶立月、奶立月乚 |
| RTL 反转 | ‮gnolian‬ (显示为 nailong) |
| 组合符号 | n⃝a⃝i⃝l⃝o⃝n⃝g⃝ (组合圆圈自动剥离) |
| 昵称/修饰 | 奶龙酱、奶味龙、奶嘴龙、小奶龙 |

## 跨语言混搭

```
36 种奶表达 × 28 种龙表达 = 1008 种组合 → 1 条正则
```

包括 emoji、负圈字母、方框字母、中文、拼音、火星文、日语音读、19 种外语之间的任意排列组合。

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
| `patterns_final.txt` | **最终产物** — 79 条纯文本正则，直接可用 |
| `nailong_patterns.py` | Python 模块版，含终极 homoglyph 字符类 + match_any() |
| `cross_lang_attack.py` | 跨语言混搭探针 — 37×29=1073 组合 |
| `generate_patterns.py` | Pattern 生成器 + 56 条测试用例 |
| `attack_probe.py` | 攻击探针 — 140+ 种攻击向量 |
| `recomb_attack.py` | 重组攻击探针 — 拆字/缩写/连接符/RTL |
| `edge_probe.py` | 边缘攻击探针 — 隐形分隔/变体选择器/特殊标点 |
| `char_mix_probe.py` | 字符混搭探针 |
| `ultimate_homoglyph.py` | 终极 homoglyph 扫描器 |
| `nailong_blocker.py` | 初版架构（保留供参考） |

## 版本

- **v1.8** — 边缘攻击防御 (变体选择器/标签字符/隐形分隔/SP标点扩展/x连接)
- **v1.7** — 终极 Homoglyph 扩展 (+67字符：Coptic/制表符/CJK笔画/彩色圆/球类/太阳)
- **v1.6** — 火星文防御 (仍孕隆窿宠笼聋 等含乃/龙部件异体同音字)
- **v1.5** — 重组攻击防御 (龙拆字/NL缩写/连接符/形近字/RTL反转)
- **v1.4** — 字符混搭强化 + Romaji (miruku/doragon)
- **v1.3** — 跨语言混搭使用完整 homoglyph 类
- **v1.0** — 初始发布，69 条正则，19 种外语

# 奶龙屏蔽器 — Nailong Blocker

穷举一切能在文本中指代"**奶龙**"的写法并予以拦截。

既是盾 🛡️，也是矛 🗡️ —— 从攻击者的视角穷举所有变形，再用正则逐一封堵。

## 快速使用

```
每条 pattern 独立可用
匹配: re.search(pattern, text, re.IGNORECASE)
预处理: NFKC 正规化 + 去除零宽字符
```

### 纯文本 Pattern

**[`patterns_final.txt`](patterns_final.txt)** — 70 条纯正则，可直接复制到任何支持正则的系统中使用。

### Python 模块

```python
from nailong_patterns import PATTERNS, match_any

# 70 条 pattern，每条独立可用
if match_any("n@1l0n9"):
    print("拦截!")
```

## 覆盖的攻击向量

| 类别 | 示例 |
|---|---|
| 直接中文 | 奶龙、奶龍、乃龙、女乃龙 |
| 同音/同义 | 奈龙、氖龙、乳汁龙、乳液龙、奶牛龙、酪龙 |
| 拼音全变形 | nailong、n@1l0n9、n-a-i-l-o-n-g、naaaaailoooong |
| 声调数字 | nai3long2、n4i3l0ng2 |
| Unicode 伪装 | 𝐧𝐚𝐢𝐥𝐨𝐧𝐠、🅝🅐🅘🅛🅞🅝🅖、ñäîłøñğ |
| Emoji | 🥛🐉、🐄🐲、👵🐉、🍼dragon |
| 英文意译 | milk dragon、m!lk dr4g0n、milky dragon、dairy dragon |
| 词序颠倒 | dragon milk、dragonmilk |
| 混搭 | nai龙、奶long、milk龙、奶dragon、奶🅛🅞🅝🅖 |
| 语义重排 | 龙喝奶、龙吃奶 |
| 注音 | ㄋㄞˇㄌㄨㄥˊ、ㄋㄞ3ㄌㄨㄥ2 |
| IPA 音标 | /naɪlɔːŋ/、[naɪ˨˩ lʊŋ˧˥] |
| 日/韩 | ミルクドラゴン、우유 용、나이롱、밀크 드래곤 |
| **跨语言混搭** | **milk 용、Milch 龙、lait ドラゴン、🥛ドラゴン、🅼🅸🅻🅺🐉** |
| 翻译全覆盖 | Milchdrache(德)、dragon de lait(法)、dragón de leche(西)、drago di latte(意)、dragão de leite(葡)、молочный дракон(俄)、молочний дракон(乌)、melk draak(荷)、mjölkdrake(瑞)、mælkedrage(丹)、mleczny smok(波)、süt ejderhası(土)、naga susu(印尼)、sữa rồng(越)、มังกรนม(泰)、تنين الحليب(阿)、דרקון חלב(希伯来)、दूध ड्रैगन(印地)、δράκος γάλακτος(希) |
| 昵称/修饰 | 奶龙酱、奶味龙、奶嘴龙、小奶龙 |

## 跨语言混搭

v1.3 的核心能力：**任意语言的"奶/milk" + 任意语言的"龙/dragon" 拼接均被拦截**。

```
35 种奶表达 × 26 种龙表达 = 910 种组合 → 1 条正则
```

包括 emoji（🥛🍼🐄👵）、负圈字母（🅜🅘🅛🅚）、方框字母（🄼🄸🄻🄺）、中文、拼音、19 种外语之间的任意排列组合。

## 文件说明

| 文件 | 用途 |
|---|---|
| `patterns_final.txt` | **最终产物** — 70 条纯文本正则，直接可用 |
| `nailong_patterns.py` | Python 模块版，含完整 homoglyph 字符类 + match_any() |
| `cross_lang_attack.py` | 跨语言混搭探针 — 35×26=910 组合，36/36 全过 |
| `generate_patterns.py` | Pattern 生成器 + 56 条测试用例 |
| `attack_probe.py` | 攻击探针 — 140+ 种攻击向量持续探测防线漏洞 |
| `nailong_blocker.py` | 初版（更复杂的预处理架构，保留供参考） |
| `pattern_cross_lang.txt` | 跨语言混搭纯文本正则（单条，~11KB） |
| `patterns_plain.txt` | 核心 pattern 纯文本（中间产物） |
| `patterns_lang_extra.txt` | 外语翻译补充 pattern（中间产物） |

## 版本

- **v1.3** — 跨语言混搭全面使用完整 homoglyph 类（负圈/方框/Emoji 全覆盖）
- **v1.2** — 跨语言混搭加入 Emoji 支持
- **v1.1** — 新增跨语言混搭攻击防御
- **v1.0** — 初始发布，69 条正则，19 种外语

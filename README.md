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

**[`patterns_final.txt`](patterns_final.txt)** — 69 条纯正则，可直接复制到任何支持正则的系统中使用。

### Python 模块

```python
from nailong_patterns import PATTERNS, match_any

# 69 条 pattern，每条独立可用
if match_any("n@1l0n9"):
    print("拦截!")
```

## 覆盖的攻击向量

| 类别 | 示例 |
|---|---|
| 直接中文 | 奶龙、奶龍、乃龙、女乃龙 |
| 同音/同义 | 奈龙、氖龙、乳汁龙、乳龙 |
| 拼音全变形 | nailong、n@1l0n9、n-a-i-l-o-n-g、naaaaailoooong |
| 声调数字 | nai3long2、n4i3l0ng2 |
| Unicode 伪装 | 𝐧𝐚𝐢𝐥𝐨𝐧𝐠、🅝🅐🅘🅛🅞🅝🅖、ñäîłøñğ |
| 英文 | milk dragon、m!lk dr4g0n、milky dragon、dragonmilk |
| 混搭 | nai龙、奶long、milk龙 |
| 语义重排 | 龙喝奶、龙吃奶 |
| 注音 | ㄋㄞˇㄌㄨㄥˊ、ㄋㄞ3ㄌㄨㄥ2 |
| Emoji | 🥛🐉、🐄🐲 |
| IPA 音标 | /naɪlɔːŋ/、[naɪ˨˩ lʊŋ˧˥] |
| 日/韩 | ミルクドラゴン、우유 용、나이롱 |
| 翻译全覆盖 | Milchdrache(德)、dragon de lait(法)、dragón de leche(西)、drago di latte(意)、dragão de leite(葡)、молочный дракон(俄)、naga susu(印尼)、süt ejderhası(土)、มังกรนม(泰)、تنين الحليب(阿)、דרקון חלב(希伯来)、दूध ड्रैगन(印地)... |

## 文件说明

| 文件 | 用途 |
|---|---|
| `patterns_final.txt` | **最终产物** — 69 条纯文本正则，直接可用 |
| `nailong_patterns.py` | Python 模块版，含 match_any() 快速判定函数 |
| `generate_patterns.py` | Pattern 生成器 + 56 条测试用例 |
| `attack_probe.py` | 攻击探针 — 140+ 种攻击向量持续探测防线漏洞 |
| `nailong_blocker.py` | 初版（更复杂的预处理架构，保留供参考） |

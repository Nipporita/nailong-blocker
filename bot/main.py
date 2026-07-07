#!/usr/bin/env python3
"""
奶龙屏蔽器 QQ Bot
==================
基于 OneBot v11 协议的奶龙检测机器人。

收到消息 → v1 正则快速检测 → 命中则回复"检测到奶龙！"
         → 未命中 → v2 语义检测 → 命中则回复"检测到奶龙！(语义)"

启动: python bot/main.py
依赖: aiohttp, 以及项目根目录的 nailong_patterns, cross_lang_attack, v2_semantic
"""
from __future__ import annotations

import asyncio
import json
import logging
import signal
import sys
import unicodedata
import re
from pathlib import Path

# 将项目根目录加入 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import aiohttp

# ── 日志 ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("奶龙检测")


# ── OneBot 连接配置 ───────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent / "config.json"
DEFAULT_CONFIG = {
    "ws_url": "ws://localhost:3001",       # WebSocket 事件推送
    "http_url": "http://localhost:3000",    # HTTP API
    "reply_text": "检测到奶龙！",
    "enable_semantic": True,               # 是否启用 v2 语义检测
    "semantic_threshold_milk": 0.10,
    "semantic_threshold_dragon": 0.08,
    "verbose": False,
}

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = {**DEFAULT_CONFIG, **json.load(f)}
    else:
        cfg = DEFAULT_CONFIG
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    return cfg


# ═══════════════════════════════════════════════════════════════════════
# 奶龙检测核心
# ═══════════════════════════════════════════════════════════════════════

NAILONG_PATTERNS = None
CROSS_LANG = None
SEMANTIC_MODEL = None
ANCHORS_MILK = None
ANCHORS_DRAGON = None
NEG_ANCHORS = None


def _load_v1():
    global NAILONG_PATTERNS, CROSS_LANG
    if NAILONG_PATTERNS is None:
        from nailong_patterns import PATTERNS
        from cross_lang_attack import CROSS_LANG_PATTERN
        NAILONG_PATTERNS = [(re.compile(p, re.IGNORECASE)) for p in PATTERNS]
        CROSS_LANG = re.compile(CROSS_LANG_PATTERN, re.IGNORECASE)
        logger.info(f"v1 正则加载完成: {len(NAILONG_PATTERNS)} 条 pattern")


def _load_v2():
    global SEMANTIC_MODEL, ANCHORS_MILK, ANCHORS_DRAGON, NEG_ANCHORS
    if SEMANTIC_MODEL is None:
        import numpy as np
        from model2vec import StaticModel

        logger.info("加载 v2 语义模型...")
        SEMANTIC_MODEL = StaticModel.from_pretrained("jarbas/m2v-256-bge-large-zh-v1.5")

        CONCEPT_MILK = [
            "奶", "乳", "乳汁", "牛奶", "牛乳", "鲜奶",
            "哺乳动物的分泌物", "哺乳动物喂养后代的液体",
            "乳腺分泌物", "婴儿的食物",
            "母牛产的白色液体", "milk", "dairy", "breast milk", "udder secretion",
        ]
        CONCEPT_DRAGON = [
            "龙", "龍", "蛟龙", "神龙",
            "东方神话中的图腾", "中国传统文化中的神兽",
            "鳞甲类神话生物", "呼风唤雨的神话动物",
            "长翅膀的爬行动物", "十二生肖中虚构的那个",
            "春节舞的龙", "皇帝象征的神兽",
            "dragon", "loong", "mythical reptile", "wyrm", "drake",
        ]
        NEGATIVE_CONCEPTS = [
            "今天天气真好", "我喜欢喝咖啡", "你好吗",
            "吃饭了吗", "日常聊天", "普通弹幕", "天气不错",
            "milk tea", "dragon fruit", "龙年大吉", "奶茶", "牛肉面",
        ]

        ANCHORS_MILK = np.array(SEMANTIC_MODEL.encode(CONCEPT_MILK))
        ANCHORS_DRAGON = np.array(SEMANTIC_MODEL.encode(CONCEPT_DRAGON))
        NEG_ANCHORS = np.array(SEMANTIC_MODEL.encode(NEGATIVE_CONCEPTS))
        logger.info(f"v2 语义模型加载完成: dim={SEMANTIC_MODEL.dim}")


def prep(text: str) -> str:
    """预处理: NFKC + 去零宽/RTL/变体选择器/组合符号"""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'[​-‏⁠-⁯﻿­᠎]', '', text)
    has_rtl = bool(re.search(r'[‪-‮]', text))
    text = re.sub(r'[‪-‮]', '', text)
    if has_rtl:
        text = text[::-1]
    text = re.sub(r'[︀-️]', '', text)
    text = ''.join(c for c in text if not (0xE0000 <= ord(c) <= 0xE007F))
    text = re.sub(r'[⃐-⃿]', '', text)
    return text


def check_v1(text: str) -> bool:
    """v1 正则快速路径"""
    _load_v1()
    t = prep(text)
    for p in NAILONG_PATTERNS:
        if p.search(t):
            return True
    return bool(CROSS_LANG.search(t))


def check_v2(text: str, milk_t: float = 0.10, dragon_t: float = 0.08) -> bool:
    """v2 语义慢速路径"""
    import numpy as np
    _load_v2()
    t = prep(text)
    emb = SEMANTIC_MODEL.encode([t])[0]

    milk_pos = float(np.max(np.dot(ANCHORS_MILK, emb)))
    dragon_pos = float(np.max(np.dot(ANCHORS_DRAGON, emb)))
    neg = float(np.max(np.dot(NEG_ANCHORS, emb)))

    milk_diff = milk_pos - neg
    dragon_diff = dragon_pos - neg

    return milk_diff > milk_t and dragon_diff > dragon_t


def is_nailong(text: str, config: dict) -> bool:
    """联合检测: v1 快速 → v2 语义"""
    # v1 正则
    if check_v1(text):
        return True

    # v2 语义 (可配置关闭)
    if config.get("enable_semantic", True):
        return check_v2(
            text,
            milk_t=config.get("semantic_threshold_milk", 0.10),
            dragon_t=config.get("semantic_threshold_dragon", 0.08),
        )

    return False


# ═══════════════════════════════════════════════════════════════════════
# QQ Bot 主体
# ═══════════════════════════════════════════════════════════════════════

class NailongBot:
    def __init__(self, config: dict):
        self.config = config
        self.ws_url = config["ws_url"]
        self.http_url = config["http_url"]
        self.reply_text = config["reply_text"]
        self.session: aiohttp.ClientSession | None = None
        self._running = False

    async def start(self):
        self.session = aiohttp.ClientSession()
        self._running = True
        logger.info(f"连接 WebSocket: {self.ws_url}")

        retry_delay = 1
        while self._running:
            try:
                async with self.session.ws_connect(
                    self.ws_url,
                    max_msg_size=0,
                ) as ws:
                    retry_delay = 1
                    logger.info("WebSocket 已连接")
                    async for msg in ws:
                        if not self._running:
                            break
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                await self._handle_message(json.loads(msg.data))
                            except Exception as e:
                                logger.error(f"处理消息异常: {e}")
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error(f"WebSocket 错误: {ws.exception()}")
            except aiohttp.ClientError as e:
                logger.warning(f"连接断开, {retry_delay}s 后重连: {e}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"未预期的错误: {e}")

            if self._running:
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)

    async def _handle_message(self, event: dict):
        """处理 OneBot v11 事件"""
        post_type = event.get("post_type", "")
        if post_type != "message":
            return

        message_type = event.get("message_type", "")
        if message_type not in ("group", "private"):
            return

        raw = event.get("raw_message", "") or event.get("message", "")
        if not raw.strip():
            return

        user_id = event.get("user_id", "?")
        group_id = event.get("group_id", "")
        message_id = event.get("message_id", 0)

        # 检测
        if not is_nailong(raw, self.config):
            return

        # 命中！记录 & 回复
        where = f"群{group_id}" if group_id else f"私聊{user_id}"
        logger.info(f"检测到奶龙! [{where}] {user_id}: {raw[:80]}")

        await self._reply(event)

    async def _reply(self, event: dict):
        """发送回复消息"""
        message_type = event.get("message_type", "group")
        group_id = event.get("group_id", "")
        user_id = event.get("user_id", 0)

        # 构建回复消息
        reply_msg = {
            "action": "send_msg",
            "params": {
                "message_type": message_type,
                "message": self.reply_text,
            },
        }
        if message_type == "group" and group_id:
            reply_msg["params"]["group_id"] = group_id
        elif message_type == "private":
            reply_msg["params"]["user_id"] = user_id

        try:
            async with self.session.post(
                f"{self.http_url}/send_msg",
                json=reply_msg,
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"回复失败: {resp.status}")
        except Exception as e:
            logger.error(f"发送回复异常: {e}")

    async def stop(self):
        self._running = False
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("Bot 已停止")


# ── 入口 ──────────────────────────────────────────────────────────────

async def main():
    config = load_config()
    bot = NailongBot(config)

    loop = asyncio.get_event_loop()

    def shutdown():
        logger.info("收到停止信号...")
        bot._running = False
        for task in asyncio.all_tasks(loop):
            task.cancel()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown)
        except NotImplementedError:
            pass  # Windows 不支持 add_signal_handler

    try:
        await bot.start()
    except asyncio.CancelledError:
        pass
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())

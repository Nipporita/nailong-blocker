#!/usr/bin/env python3
"""
奶龙屏蔽器 QQ Bot
==================
基于 OneBot v11 反向 WebSocket 协议的奶龙检测机器人。

Bot 启动 WebSocket 服务器，等待 OneBot（NapCat/LLOneBot）主动连接。
OneBot 中设置反向 WS 地址为 ws://localhost:3001

启动: python bot/main.py
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
import unicodedata
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import aiohttp
from aiohttp import web

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("nailong")

CONFIG_PATH = Path(__file__).parent / "config.json"
DEFAULT_CONFIG = {
    "listen_host": "0.0.0.0",
    "listen_port": 3001,
    "http_url": "http://localhost:3000",
    "access_token": "",
    "reply_text": "检测到奶龙！",
    "enable_semantic": True,
    "semantic_threshold_milk": 0.10,
    "semantic_threshold_dragon": 0.08,
}

def load_config():
    if CONFIG_PATH.exists():
        cfg = {**DEFAULT_CONFIG, **json.loads(CONFIG_PATH.read_text(encoding="utf-8"))}
    else:
        cfg = DEFAULT_CONFIG
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    return cfg

# ─── 奶龙检测核心 ─────────────────────────────────────────────────────

_v1_loaded = False
_v2_loaded = False
_naillong_compiled = []
_cross_lang = None
_semantic_model = None
_anchors_milk = None
_anchors_dragon = None
_neg_anchors = None

def _load_v1():
    global _v1_loaded, _naillong_compiled, _cross_lang
    if _v1_loaded: return
    from nailong_patterns import PATTERNS
    from cross_lang_attack import CROSS_LANG_PATTERN
    _naillong_compiled = [re.compile(p, re.IGNORECASE) for p in PATTERNS]
    _cross_lang = re.compile(CROSS_LANG_PATTERN, re.IGNORECASE)
    _v1_loaded = True
    logger.info(f"v1 OK: {len(_naillong_compiled)} patterns")

def _load_v2():
    global _v2_loaded, _semantic_model, _anchors_milk, _anchors_dragon, _neg_anchors
    if _v2_loaded: return
    import numpy as np
    from model2vec import StaticModel
    logger.info("loading v2 model...")
    _semantic_model = StaticModel.from_pretrained("jarbas/m2v-256-bge-large-zh-v1.5")
    _anchors_milk = np.array(_semantic_model.encode([
        "奶","乳","乳汁","牛奶","牛乳","鲜奶",
        "哺乳动物的分泌物","乳腺分泌物","母牛产的白色液体",
        "milk","dairy","breast milk","udder secretion",
    ]))
    _anchors_dragon = np.array(_semantic_model.encode([
        "龙","龍","蛟龙","神龙","东方神话中的图腾",
        "鳞甲类神话生物","呼风唤雨的神话动物","春节舞的龙",
        "dragon","loong","mythical reptile","wyrm","drake",
    ]))
    _neg_anchors = np.array(_semantic_model.encode([
        "今天天气真好","你好吗","吃饭了吗","日常聊天","普通弹幕",
        "milk tea","dragon fruit","龙年大吉","奶茶","牛肉面",
    ]))
    _v2_loaded = True
    logger.info(f"v2 OK: dim={_semantic_model.dim}")

def prep(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'[​-‏⁠-⁯﻿­᠎]', '', text)
    if re.search(r'[‪-‮]', text):
        text = re.sub(r'[‪-‮]', '', text)[::-1]
    else:
        text = re.sub(r'[‪-‮]', '', text)
    text = re.sub(r'[︀-️]', '', text)
    text = ''.join(c for c in text if not (0xE0000 <= ord(c) <= 0xE007F))
    text = re.sub(r'[⃐-⃿]', '', text)
    return text

def check_v1(text: str) -> bool:
    _load_v1()
    t = prep(text)
    for p in _naillong_compiled:
        if p.search(t): return True
    return bool(_cross_lang.search(t))

def check_v2(text: str, mt=0.10, dt=0.08) -> bool:
    import numpy as np
    _load_v2()
    emb = _semantic_model.encode([prep(text)])[0]
    m = float(np.max(np.dot(_anchors_milk, emb))) - float(np.max(np.dot(_neg_anchors, emb)))
    d = float(np.max(np.dot(_anchors_dragon, emb))) - float(np.max(np.dot(_neg_anchors, emb)))
    return m > mt and d > dt

CQ_CODE_RE = re.compile(r'\[CQ:[^\]]+\]')
CQ_IMAGE_RE = re.compile(r'\[CQ:image,[^\]]*url=([^,\]]+)')

_ocr = None

def _get_ocr():
    global _ocr
    if _ocr is None:
        from paddleocr import PaddleOCR
        _ocr = PaddleOCR(lang='ch', use_angle_cls=False, show_log=False)
    return _ocr

async def ocr_image(url: str, session: aiohttp.ClientSession) -> str:
    """下载图片并用PaddleOCR提取文字"""
    try:
        async with session.get(url.replace('&amp;', '&')) as resp:
            if resp.status != 200:
                return ''
            img_data = await resp.read()
        ocr = _get_ocr()
        result = ocr.ocr(img_data, cls=False)
        if not result or not result[0]:
            return ''
        texts = [line[1][0] for line in result[0] if line[1][1] > 0.5]
        return ' '.join(texts)
    except Exception as e:
        logger.warning(f"OCR failed: {e}")
        return ''

async def extract_text(event: dict, session: aiohttp.ClientSession | None = None) -> str:
    """从 OneBot 事件中提取所有文本（消息文本 + 图片PaddleOCR）。"""
    texts = []

    # 1. 纯文本部分（去CQ码）
    raw = event.get("raw_message", "") or event.get("message", "")
    plain = CQ_CODE_RE.sub('', raw).strip()
    if plain:
        texts.append(plain)

    # 2. 图片 OCR（PaddleOCR）
    if session:
        for m in CQ_IMAGE_RE.finditer(raw):
            url = m.group(1).strip()
            if url:
                ocr_text = await ocr_image(url, session)
                if ocr_text:
                    texts.append(ocr_text)
                    logger.info(f"OCR: {ocr_text[:80]}")

    return ' '.join(texts)

def is_nailong(text: str, cfg: dict) -> bool:
    if not text.strip():
        return False
    if check_v1(text): return True
    if cfg.get("enable_semantic", True):
        return check_v2(text, cfg.get("semantic_threshold_milk", 0.10),
                        cfg.get("semantic_threshold_dragon", 0.08))
    return False

# ─── WebSocket 服务器 ──────────────────────────────────────────────────

class NailongBot:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.http_url = cfg["http_url"]
        self.reply_text = cfg["reply_text"]
        self.session: aiohttp.ClientSession | None = None
        self._ws = None  # 反向WS连接，用于通过WS回复

    async def start(self):
        self.session = aiohttp.ClientSession()
        host = self.cfg["listen_host"]
        port = self.cfg["listen_port"]

        # 创建 WS 路由：OneBot 反向连接时触发
        async def ws_handler(request):
            ws = web.WebSocketResponse(max_msg_size=0)
            await ws.prepare(request)
            self._ws = ws  # 保存连接用于回复
            peer = request.remote
            logger.info(f"OneBot 已连接: {peer}")
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        await self._handle(json.loads(msg.data))
                    except Exception as e:
                        logger.error(f"处理异常: {e}")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WS error: {ws.exception()}")
            self._ws = None
            logger.info(f"OneBot 断开: {peer}")
            return ws

        app = web.Application()
        app.router.add_get("/", ws_handler)
        app.router.add_get("/ws", ws_handler)
        app.router.add_get("/ws/", ws_handler)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info(f"WS 服务器已启动: ws://{host}:{port}")
        logger.info("等待 OneBot 反向连接...")

        # 保持运行
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            pass
        finally:
            await runner.cleanup()

    async def _handle(self, event: dict):
        if event.get("post_type") != "message": return
        msg_type = event.get("message_type", "")
        if msg_type not in ("group", "private"): return
        text = await extract_text(event, self.session)
        if not text: return

        if not is_nailong(text, self.cfg): return

        uid = event.get("user_id", "?")
        gid = event.get("group_id", "")
        where = f"群{gid}" if gid else f"私聊{uid}"
        logger.info(f"检测到奶龙! [{where}] {uid}: {text[:80]}")

        if msg_type == "group" and gid:
            action = "send_group_msg"
            params = {"group_id": int(gid), "message": self.reply_text}
        else:
            action = "send_private_msg"
            params = {"user_id": int(uid), "message": self.reply_text}

        # 优先通过 WS 发送（无需额外 HTTP 端口）
        if self._ws:
            try:
                await self._ws.send_json({"action": action, "params": params})
                logger.info("reply via WS ok")
                return
            except Exception as e:
                logger.warning(f"WS reply failed, fallback to HTTP: {e}")

        # HTTP fallback
        headers = {"Content-Type": "application/json"}
        token = self.cfg.get("access_token", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        url = f"{self.http_url}/{action}"
        try:
            async with self.session.post(url, json=params, headers=headers) as resp:
                body = await resp.json()
                if body.get("status") != "ok":
                    logger.warning(f"HTTP reply failed: retcode={body.get('retcode')} msg={str(body)[:100]}")
        except Exception as e:
            logger.error(f"HTTP reply error: {e}")

    async def stop(self):
        if self.session:
            await self.session.close()

async def main():
    cfg = load_config()
    bot = NailongBot(cfg)
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("interrupted")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())

"""
奶龙视觉检测器
===============
加载 prototype.json → 输入图片 → CLIP编码 → 与原型比对 → 判定
"""
import json
import numpy as np
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
PROTO_PATH = ROOT / "prototype.json"

_model = None
_preprocess = None
_proto = None


def _load():
    global _model, _preprocess, _proto
    if _model is not None:
        return
    import open_clip
    _model, _, _preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained="laion2b_s34b_b79k"
    )
    _proto = json.loads(PROTO_PATH.read_text())


def encode_image(img_path: str) -> np.ndarray:
    _load()
    img = Image.open(img_path).convert("RGB")
    tensor = _preprocess(img).unsqueeze(0)
    emb = _model.encode_image(tensor)
    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.squeeze(0).numpy()


def is_nailong_image(img_path: str) -> tuple[bool, float]:
    """
    判断图片是否是奶龙。匹配任意一个正原型即判定。
    返回 (is_nailong, max_confidence)
    """
    _load()
    emb = encode_image(img_path)

    neg_proto = np.array(_proto["neg_prototype"]) if _proto["neg_prototype"] else None
    if neg_proto is not None:
        neg_sim = float(np.dot(emb,  np.array(_proto["neg_prototype"])))
    else:
        neg_sim = 0.5  # 无负样本时用固定基线

    best_diff = -999
    for name, p in _proto["pos_prototypes"].items():
        pos_proto = np.array(p["prototype"])
        pos_sim = float(np.dot(emb, pos_proto))
        diff = pos_sim - neg_sim
        if diff > best_diff:
            best_diff = diff

    return best_diff > 0.15, round(best_diff, 3)

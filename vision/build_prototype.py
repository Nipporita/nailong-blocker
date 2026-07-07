"""
奶龙视觉指纹 — CLIP 少样本原型构建器
=====================================
1. 收集 positive/ 下的奶龙图, negative/ 下的水豚噜噜等易混淆图
2. 用 CLIP 编码每张图 → 构建正/负原型向量
3. 输出 prototype.json (原型指纹)
"""
import json
import os
import numpy as np
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
# 正样本可以有多个子目录，每个子目录独立建原型
# positive/         → 标准奶龙表情包
# positive_ai/      → AI生成的奶龙变体 (如 捧腹大笑)
# positive_variant/ → 其他变体 (可选)
POS_DIRS = [
    ROOT / "positive",
    ROOT / "positive_ai",
]
NEG_DIR = ROOT / "negative"    # 水豚噜噜等 ~20张
OUTPUT = ROOT / "prototype.json"


def load_model():
    """加载 CLIP 模型 (首次自动下载 ~350MB)"""
    import open_clip
    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained="laion2b_s34b_b79k"
    )
    tokenizer = open_clip.get_tokenizer("ViT-B-32")
    return model, preprocess, tokenizer


def encode_images(model, preprocess, image_dir: Path) -> np.ndarray:
    """编码目录下所有图片 → N×512 向量"""
    embeddings = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.avif"):
        for path in sorted(image_dir.glob(ext)):
            try:
                img = Image.open(path).convert("RGB")
                img_tensor = preprocess(img).unsqueeze(0)
                emb = model.encode_image(img_tensor)
                emb = emb / emb.norm(dim=-1, keepdim=True)  # L2归一化
                embeddings.append(emb.squeeze(0).detach().numpy())
                print(f"  OK: {path.name}")
            except Exception as e:
                print(f"  SKIP: {path.name} ({e})")
    if not embeddings:
        return np.array([])
    return np.stack(embeddings)


def build_text_prototypes(model, tokenizer):
    """构建文本原型 (正/负概念的CLIP文本编码)"""
    pos_texts = [
        "奶龙角色", "一只可爱的奶龙", "nai long cartoon character",
        "a cute chubby milk dragon cartoon", "黄色的卡通龙",
        "胖乎乎的卡通龙角色", "milk dragon meme",
    ]
    neg_texts = [
        "水豚噜噜", "capybara cartoon", "卡皮巴拉",
        "日常照片", "风景照", "自拍", "食物照片",
        "普通表情包", "动漫角色", "游戏截图",
    ]
    pos_tokens = tokenizer(pos_texts)
    neg_tokens = tokenizer(neg_texts)
    pos_emb = model.encode_text(pos_tokens)
    neg_emb = model.encode_text(neg_tokens)
    pos_emb = pos_emb / pos_emb.norm(dim=-1, keepdim=True)
    neg_emb = neg_emb / neg_emb.norm(dim=-1, keepdim=True)
    return pos_emb.detach().numpy(), neg_emb.detach().numpy()


def main():
    print("加载 CLIP...")
    model, preprocess, tokenizer = load_model()

    # 对每个正样本目录独立建原型
    pos_protos = {}
    for pos_dir in POS_DIRS:
        if not pos_dir.exists():
            continue
        print(f"\n正样本 ({pos_dir.name}):")
        emb = encode_images(model, preprocess, pos_dir)
        if len(emb) > 0:
            pos_protos[pos_dir.name] = {
                "embeddings": emb.tolist(),
                "prototype": emb.mean(axis=0).tolist(),
                "count": len(emb),
            }
            # 凝聚度
            sims = np.dot(emb, emb.mean(axis=0))
            print(f"  共 {len(emb)} 张, 凝聚度: {sims.mean():.3f} ± {sims.std():.3f}")
        else:
            print(f"  空目录, 跳过")

    print(f"\n负样本 ({NEG_DIR.name}):")
    neg_emb = encode_images(model, preprocess, NEG_DIR)
    neg_proto = neg_emb.mean(axis=0).tolist() if len(neg_emb) > 0 else None
    print(f"  共 {len(neg_emb)} 张")

    print("\n构建文本原型...")
    pos_text, neg_text = build_text_prototypes(model, tokenizer)

    result = {
        "model": "ViT-B-32",
        "neg_count": len(neg_emb),
        "neg_prototype": neg_proto,
        "neg_text_prototypes": neg_text.tolist(),
        "pos_prototypes": pos_protos,  # 每个目录一个独立原型
        "pos_text_prototypes": pos_text.tolist(),
    }

    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n✅ 原型已保存: {OUTPUT}")
    for name, p in pos_protos.items():
        print(f"   [{name}] {p['count']} 张")


if __name__ == "__main__":
    main()

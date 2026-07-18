"""채점기 공용 유틸 — SSIM 비교, 결과 출력."""
import json
import sys

import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim


def image_ssim(path_a, path_b):
    """두 이미지를 같은 크기로 맞춰 grayscale SSIM 계산."""
    a = Image.open(path_a).convert("L")
    b = Image.open(path_b).convert("L")
    w = min(a.width, b.width)
    h = min(a.height, b.height)
    a = np.asarray(a.resize((w, h)))
    b = np.asarray(b.resize((w, h)))
    return float(ssim(a, b))


def emit(result: dict):
    """채점 결과를 JSON으로 stdout 출력 (집계 노트북이 소비)."""
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result.get("evaluator_pass") else 1


def fail(test, reason):
    return emit({"test": test, "evaluator_pass": False, "error": reason})

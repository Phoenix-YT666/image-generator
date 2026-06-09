"""图片生成工具函数"""
from pathlib import Path
from typing import List, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image


def load_image(path: str) -> Image.Image:
    """从文件加载图片"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"图片文件不存在: {path}")
    return Image.open(path).convert("RGB")


def save_image(image: Image.Image, path: str, quality: int = 95) -> Path:
    """保存图片到文件"""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fmt = output_path.suffix.lower()
    if fmt in (".jpg", ".jpeg"):
        image.save(output_path, "JPEG", quality=quality)
    elif fmt == ".png":
        image.save(output_path, "PNG")
    elif fmt == ".webp":
        image.save(output_path, "WEBP", quality=quality)
    else:
        image.save(output_path)

    return output_path.absolute()


def batch_process(prompts: List[str], processor_fn: Callable,
                 max_workers: int = 4) -> List:
    """并行批量处理"""
    results = [None] * len(prompts)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(processor_fn, prompt): i
            for i, prompt in enumerate(prompts)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                print(f"    ⚠️ [{idx}] 处理失败: {e}")
                results[idx] = None

    return results


def apply_filter(image: Image.Image, filter_name: str) -> Image.Image:
    """应用命名滤镜"""
    from PIL import ImageFilter, ImageEnhance

    filters = {
        "blur": lambda img: img.filter(ImageFilter.GaussianBlur(2)),
        "sharpen": lambda img: img.filter(ImageFilter.SHARPEN),
        "edge_enhance": lambda img: img.filter(ImageFilter.EDGE_ENHANCE),
        "emboss": lambda img: img.filter(ImageFilter.EMBOSS),
        "grayscale": lambda img: ImageEnhance.Color(img).enhance(0),
    }
    fn = filters.get(filter_name)
    if fn:
        return fn(image)
    return image

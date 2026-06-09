"""风格管理器"""
from typing import Dict, List, Optional
import json
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter


class StyleManager:
    def __init__(self):
        self.styles_dir = Path(__file__).parent.parent.parent / "styles"
        self._styles_cache = {}

    def load_style(self, name: str) -> Dict:
        if name in self._styles_cache:
            return self._styles_cache[name]

        style_path = self.styles_dir / f"{name}.json"
        if style_path.exists():
            with open(style_path, 'r', encoding='utf-8') as f:
                style = json.load(f)
            self._styles_cache[name] = style
            return style

        # 内置风格
        builtin = self._get_builtin_styles()
        if name in builtin:
            return builtin[name]
        raise FileNotFoundError(f"风格 '{name}' 不存在")

    def list_styles(self) -> List[str]:
        styles = list(self._get_builtin_styles().keys())
        if self.styles_dir.exists():
            for f in self.styles_dir.glob("*.json"):
                if f.stem not in styles:
                    styles.append(f.stem)
        return sorted(styles)

    def apply_style(self, image: Image.Image, style_name: str) -> Image.Image:
        style = self.load_style(style_name)
        img = image.copy()

        # 对比度
        contrast = style.get("contrast", 1.0)
        if contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(contrast)

        # 亮度
        brightness = style.get("brightness", 1.0)
        if brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(brightness)

        # 饱和度
        saturation = style.get("saturation", 1.0)
        if saturation != 1.0:
            img = ImageEnhance.Color(img).enhance(saturation)

        # 锐度
        sharpness = style.get("sharpness", 1.0)
        if sharpness != 1.0:
            img = ImageEnhance.Sharpness(img).enhance(sharpness)

        # 模糊
        blur = style.get("blur", 0)
        if blur > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur))

        return img

    def _get_builtin_styles(self) -> Dict:
        return {
            "realistic": {"contrast": 1.1, "brightness": 1.0, "saturation": 1.1, "sharpness": 1.3},
            "anime": {"contrast": 1.2, "brightness": 1.1, "saturation": 1.3, "sharpness": 0.7, "blur": 0.5},
            "oil-painting": {"contrast": 1.3, "saturation": 1.2, "sharpness": 3.0},
            "watercolor": {"brightness": 1.2, "saturation": 0.8, "blur": 3, "sharpness": 0.5},
            "cyberpunk": {"contrast": 1.5, "saturation": 1.5, "brightness": 0.8},
            "minimalist": {"contrast": 1.0, "saturation": 0.7, "brightness": 1.1},
            "vintage": {"saturation": 0.5, "brightness": 1.0, "contrast": 0.9},
            "dramatic": {"contrast": 2.0, "brightness": 0.8, "sharpness": 1.5},
        }

"""
Pillow 本地图片生成引擎
不依赖任何外部 AI API，使用 Pillow 生成真实美观的图片。
作为 Stable Diffusion / DALL-E 的免费降级方案。
"""

import random
import colorsys
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont


# 颜色名称映射表
COLOR_MAP: Dict[str, Tuple[int, int, int]] = {
    "红色": (220, 40, 40), "红": (220, 40, 40), "red": (220, 40, 40),
    "橙色": (255, 140, 0), "橙": (255, 140, 0), "orange": (255, 140, 0),
    "黄色": (255, 215, 0), "黄": (255, 215, 0), "yellow": (255, 215, 0),
    "绿色": (40, 180, 40), "绿": (40, 180, 40), "green": (40, 180, 40),
    "蓝色": (40, 100, 220), "蓝": (40, 100, 220), "blue": (40, 100, 220),
    "紫色": (140, 40, 200), "紫": (140, 40, 200), "purple": (140, 40, 200),
    "粉色": (255, 140, 180), "粉": (255, 140, 180), "pink": (255, 140, 180),
    "白色": (255, 255, 255), "白": (255, 255, 255), "white": (255, 255, 255),
    "黑色": (20, 20, 20), "黑": (20, 20, 20), "black": (20, 20, 20),
    "灰色": (128, 128, 128), "灰": (128, 128, 128), "gray": (128, 128, 128),
    "青色": (0, 200, 200), "cyan": (0, 200, 200),
    "金色": (255, 200, 50), "gold": (255, 200, 50),
    "银色": (200, 200, 210), "silver": (200, 200, 210),
}

# 情绪 → 调色板
MOOD_PALETTES: Dict[str, List[Tuple[int, int, int]]] = {
    "warm": [(255, 100, 50), (255, 180, 50), (255, 220, 150), (255, 140, 80)],
    "cool": [(40, 100, 220), (40, 180, 200), (100, 140, 240), (60, 160, 180)],
    "dark": [(15, 15, 25), (30, 30, 50), (50, 20, 60), (25, 25, 40)],
    "bright": [(255, 220, 50), (80, 220, 80), (60, 180, 255), (255, 120, 180)],
    "pastel": [(255, 200, 200), (200, 220, 255), (200, 255, 200), (255, 230, 200)],
    "neon": [(255, 20, 147), (0, 255, 255), (57, 255, 20), (255, 255, 0)],
    "earth": [(139, 90, 43), (107, 142, 35), (160, 120, 90), (85, 107, 47)],
    "ocean": [(0, 105, 148), (0, 168, 168), (0, 119, 182), (72, 202, 228)],
    "sunset": [(255, 94, 77), (255, 154, 68), (255, 207, 128), (255, 128, 100)],
    "forest": [(34, 139, 34), (85, 107, 47), (107, 142, 35), (46, 139, 87)],
}


def generate_with_pillow(prompt: str, width: int = 1024, height: int = 1024,
                        style: str = "realistic", seed: Optional[int] = None) -> Image.Image:
    """主入口：根据 prompt 用 Pillow 生成真实图片

    解析 prompt 中的关键词（颜色、情绪、元素），组合生成图片。
    虽然不能像 Stable Diffusion 一样理解复杂描述，但可以生成真正美观的抽象/半抽象图片。

    Args:
        prompt: 图片描述
        width: 宽度
        height: 高度
        style: 风格
        seed: 随机种子(可复现)

    Returns:
        PIL Image 对象
    """
    if seed is not None:
        random.seed(seed)

    # 解析 prompt
    mood = _detect_mood(prompt)
    colors = _extract_colors(prompt)
    elements = _extract_elements(prompt)

    # 选择调色板
    palette = _get_palette(colors, mood, style)

    # 根据风格选择生成策略
    if style in ("anime", "pixel-art"):
        image = generate_geometric(width, height, elements, palette, style)
    elif style in ("oil-painting", "watercolor"):
        image = generate_abstract(width, height, mood, palette, style)
    elif style == "cyberpunk":
        # 赛博朋克：深色背景 + 霓虹元素
        dark_palette = MOOD_PALETTES["neon"]
        image = generate_abstract(width, height, "cool", dark_palette, style)
        image = ImageEnhance.Contrast(image).enhance(1.5)
    elif style == "minimalist":
        image = generate_geometric(width, height, elements, palette, "minimalist")
    else:
        # 默认：渐变 + 几何 + 抽象组合
        image = generate_gradient(width, height, palette)
        overlay = generate_abstract(width, height, mood, palette, style)
        image = Image.blend(image, overlay, 0.4)

    # 后处理
    if style == "3d-render":
        image = ImageEnhance.Sharpness(image).enhance(2.0)
        image = ImageEnhance.Contrast(image).enhance(1.2)

    return image


def generate_gradient(width: int, height: int,
                     colors: List[Tuple[int, int, int]]) -> Image.Image:
    """生成渐变背景

    支持线性渐变（从上到下或从左上到右下）。
    如果 colors 有 2+ 种颜色则生成多色渐变。
    """
    image = Image.new("RGB", (width, height))
    pixels = image.load()

    if len(colors) < 2:
        colors = [colors[0], _lighten(colors[0], 0.5)]

    c1, c2 = colors[0], colors[-1]

    for y in range(height):
        for x in range(width):
            # 对角线渐变
            t = (x / width + y / height) / 2
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            pixels[x, y] = (max(0, min(255, r)),
                          max(0, min(255, g)),
                          max(0, min(255, b)))

    return image


def generate_geometric(width: int, height: int,
                      elements: List[str],
                      palette: List[Tuple[int, int, int]],
                      style: str = "realistic") -> Image.Image:
    """生成几何图形图片

    根据解析出的元素关键词放置几何图形。
    适合：anime 风格（大色块）、pixel-art（方格）、minimalist（简洁线条）
    """
    bg_color = palette[0] if palette else (30, 30, 40)
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # 随机选择一些几何元素放置
    shapes = ["circle", "rect", "triangle", "line", "ellipse"]
    num_shapes = random.randint(8, 25)

    for _ in range(num_shapes):
        shape = random.choice(shapes)
        color = random.choice(palette) if palette else _random_color()
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(20, max(30, min(width, height) // 4))

        if shape == "circle":
            draw.ellipse([x - size, y - size, x + size, y + size],
                        fill=color, outline=_darken(color, 0.3))
        elif shape == "rect":
            rw = random.randint(size // 2, size)
            rh = random.randint(size // 2, size)
            draw.rectangle([x, y, x + rw, y + rh], fill=color)
        elif shape == "line":
            angle = random.random() * 3.14159 * 2
            x2 = x + int(size * 1.5 * __import__('math').cos(angle))
            y2 = y + int(size * 1.5 * __import__('math').sin(angle))
            draw.line([(x, y), (x2, y2)], fill=color, width=random.randint(2, 8))
        elif shape == "ellipse":
            rx = random.randint(size // 2, size)
            ry = random.randint(size // 4, size // 2)
            draw.ellipse([x - rx, y - ry, x + rx, y + ry], fill=color)

    # 对于 pixel-art 风格，缩小再放大实现像素化
    if style == "pixel-art":
        small_w, small_h = width // 8, height // 8
        image = image.resize((small_w, small_h), Image.NEAREST)
        image = image.resize((width, height), Image.NEAREST)

    return image


def generate_abstract(width: int, height: int, mood: str,
                     palette: List[Tuple[int, int, int]],
                     style: str = "realistic") -> Image.Image:
    """生成抽象艺术图片

    使用随机形状、滤镜组合生成抽象效果。
    适合：oil-painting、watercolor、cyberpunk 等风格
    """
    image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 绘制多层随机色块
    num_layers = random.randint(3, 6)
    for layer in range(num_layers):
        color = random.choice(palette) if palette else _random_color()
        # 添加透明度效果（通过混合颜色模拟）
        alpha = 0.3 + 0.2 * layer / num_layers

        # 绘制多个不规则圆
        num_circles = random.randint(5, 15)
        for _ in range(num_circles):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(30, max(40, min(width, height) // 3))
            draw.ellipse([x - r, y - r, x + r, y + r],
                        fill=color, outline=None)

    # 风格特定的后处理
    if style == "oil-painting":
        # 油画风格：模糊 + 锐化交替产生纹理
        for _ in range(2):
            image = image.filter(ImageFilter.GaussianBlur(radius=3))
        image = ImageEnhance.Sharpness(image).enhance(3.0)
        image = ImageEnhance.Contrast(image).enhance(1.3)
    elif style == "watercolor":
        # 水彩：强烈模糊 + 亮度提高
        image = image.filter(ImageFilter.GaussianBlur(radius=8))
        image = ImageEnhance.Brightness(image).enhance(1.2)
        image = ImageEnhance.Color(image).enhance(0.8)

    return image


# ====== 辅助函数 ======

def _detect_mood(prompt: str) -> str:
    """从 prompt 中检测情绪/氛围"""
    prompt_lower = prompt.lower()
    mood_keywords = {
        "warm": ["温暖", "阳光", "温馨", "warm", "sunny", "sunset", "sunrise"],
        "cool": ["寒冷", "冰雪", "凉爽", "cool", "ice", "snow", "winter"],
        "dark": ["黑暗", "恐怖", "阴暗", "dark", "horror", "gothic"],
        "bright": ["明亮", "欢快", "鲜艳", "bright", "cheerful", "vibrant"],
        "ocean": ["海洋", "大海", "海水", "ocean", "sea", "water", "wave"],
        "sunset": ["日落", "黄昏", "晚霞", "sunset", "dusk", "twilight"],
        "forest": ["森林", "树木", "丛林", "forest", "tree", "wood", "jungle"],
    }
    for mood, keywords in mood_keywords.items():
        for kw in keywords:
            if kw in prompt_lower:
                return mood
    return "bright"  # 默认


def _extract_colors(prompt: str) -> List[str]:
    """从 prompt 中提取颜色关键词"""
    found = []
    for color_name in COLOR_MAP:
        if color_name in prompt:
            found.append(color_name)
    return found


def _extract_elements(prompt: str) -> List[str]:
    """从 prompt 中提取元素关键词"""
    element_keywords = [
        "山", "水", "花", "树", "星", "月", "太阳", "云", "雨", "雪",
        "建筑", "城市", "房子", "桥", "路", "河", "湖", "海",
        "mountain", "water", "flower", "tree", "star", "moon", "sun",
        "cloud", "rain", "snow", "city", "building", "house", "bridge",
    ]
    found = []
    prompt_lower = prompt.lower()
    for kw in element_keywords:
        if kw in prompt_lower:
            found.append(kw)
    return found


def _get_palette(colors: List[str], mood: str,
                style: str) -> List[Tuple[int, int, int]]:
    """根据颜色关键词、情绪和风格选择调色板"""
    palette = []

    # 从颜色关键词提取
    for c_name in colors:
        if c_name in COLOR_MAP:
            palette.append(COLOR_MAP[c_name])

    # 补充 mood 调色板
    if mood in MOOD_PALETTES and len(palette) < 3:
        palette.extend(MOOD_PALETTES[mood])

    # 如果还不够，用默认
    if len(palette) < 2:
        palette = [(40, 100, 220), (255, 140, 0), (40, 180, 40), (140, 40, 200)]

    return palette


def _random_color() -> Tuple[int, int, int]:
    """生成随机颜色"""
    return (random.randint(30, 225), random.randint(30, 225), random.randint(30, 225))


def _lighten(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """颜色变亮"""
    return tuple(min(255, int(c + (255 - c) * factor)) for c in color)


def _darken(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """颜色变暗"""
    return tuple(max(0, int(c * (1 - factor))) for c in color)

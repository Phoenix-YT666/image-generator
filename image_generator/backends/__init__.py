"""AI 图片生成后端适配器"""
from image_generator.backends.pillow_gen import generate_with_pillow, generate_gradient, generate_geometric, generate_abstract

__all__ = ["generate_with_pillow", "generate_gradient", "generate_geometric", "generate_abstract"]

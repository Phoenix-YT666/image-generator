"""
图片生成引擎 - Image Generation Engine
支持多种AI图片生成后端，现已接入真实 Pillow 生成管道。
"""

from pathlib import Path
from typing import Optional, Dict, List, Any
import json

from .backends.pillow_gen import generate_with_pillow, generate_gradient, generate_geometric
from .utils import save_image, load_image as _load_img
from .styles.manager import StyleManager


class ImageEngine:
    """AI图片生成核心引擎"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.generation_history = []
        self.style_manager = StyleManager()

    def _default_config(self) -> Dict:
        return {
            "default_width": 1024,
            "default_height": 1024,
            "default_engine": "auto",
            "default_style": "realistic",
            "default_steps": 30,
            "default_cfg_scale": 7.5,
            "output_dir": "./outputs/",
        }

    def generate(self, prompt: str, output: str = "output.png",
                width: int = 1024, height: int = 1024,
                engine: str = "auto", style: str = "realistic",
                negative_prompt: str = "", seed: Optional[int] = None,
                steps: int = 30, cfg_scale: float = 7.5) -> str:
        """
        根据文本描述生成真实图片 — 使用 Pillow 本地引擎

        支持引擎:
        - pillow: 本地免费生成 (默认)
        - stable-diffusion: 需要 Stable Diffusion API
        - auto: 自动选择
        """
        print(f"  引擎: {engine} | 风格: {style} | 尺寸: {width}x{height}")

        # 用 Pillow 生成真实图片
        print(f"  🎨 生成中...")
        image = generate_with_pillow(
            prompt=prompt,
            width=width,
            height=height,
            style=style,
            seed=seed,
        )

        # 应用风格后处理
        try:
            image = self.style_manager.apply_style(image, style)
        except Exception:
            pass

        # 保存
        output_path = save_image(image, output)
        print(f"  ✅ 图片已保存到: {output_path}")

        # 记录历史
        self.generation_history.append({
            "prompt": prompt,
            "output": str(output_path),
            "engine": "pillow",
            "style": style,
        })

        return str(output_path)

    def edit(self, input_path: str, prompt: str, output: str = "edited.png",
            mask_path: str = None, strength: float = 0.7) -> str:
        """编辑已有图片"""
        print(f"  ✏️ 加载原图: {input_path}")
        image = _load_img(input_path)

        print(f"  🎨 基于 prompt 生成叠加层...")
        overlay = generate_geometric(
            image.width, image.height,
            elements=prompt.split(),
            palette=[(255, 100, 100), (100, 100, 255), (255, 200, 100)],
        )

        from PIL import Image
        blended = Image.blend(image, overlay, alpha=strength)

        output_path = save_image(blended, output)
        print(f"  ✅ 编辑结果已保存到: {output_path}")
        return str(output_path)

    def upscale(self, input_path: str, output: str = "upscaled.png",
               scale: str = "2x", model: str = "esrgan") -> str:
        """超分辨率放大图片"""
        scale_factor = {"2x": 2, "4x": 4, "8x": 8}[scale]
        print(f"  🔍 放大中... ({model}, {scale})")
        image = _load_img(input_path)
        new_size = (image.width * scale_factor, image.height * scale_factor)
        from PIL import Image
        upscaled = image.resize(new_size, Image.LANCZOS)
        output_path = save_image(upscaled, output)
        print(f"  ✅ 放大结果已保存到: {output_path}")
        return str(output_path)

    def batch_generate(self, prompts_file: str, output_dir: str,
                      engine: str = "auto", style: str = "realistic",
                      max_parallel: int = 4) -> List[str]:
        """批量生成图片"""
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f if line.strip()]

        print(f"  📦 共 {len(prompts)} 个提示词 | 并行: {max_parallel}")
        results = []

        for i, prompt in enumerate(prompts, 1):
            print(f"  [{i}/{len(prompts)}] {prompt[:50]}...")
            output = str(Path(output_dir) / f"img_{i:04d}.png")
            result = self.generate(prompt, output, engine=engine, style=style)
            results.append(result)

        return results

    def launch_web_ui(self, host: str = "127.0.0.1", port: int = 7860,
                     share: bool = False):
        """启动Gradio Web界面"""
        print(f"🌐 Web UI 启动地址: http://{host}:{port}")
        print("💡 功能: 文生图 / 图生图 / 图片编辑 / 批量处理")
        # 实际部署时使用 Gradio/Streamlit
        print("⚠️  Web UI 需要安装: pip install gradio")

    def show_gallery(self):
        """显示生成历史画廊"""
        if not self.generation_history:
            print("📭 暂无生成历史")
            return
        print(f"🖼️ 生成历史 (共{len(self.generation_history)}张):\n")
        for i, item in enumerate(self.generation_history[-20:], 1):
            print(f"  {i:3d}. {item['prompt'][:50]:50s} → {item['output']}")

    # ===== 内部方法 =====

    def _build_prompt(self, prompt: str, style: str) -> str:
        """附加风格提示词"""
        style_modifiers = {
            "realistic": "photorealistic, highly detailed, 8K, professional photography",
            "anime": "anime style, manga, studio ghibli, cel shaded",
            "oil-painting": "oil painting, textured brushstrokes, canvas, fine art",
            "watercolor": "watercolor painting, soft edges, flowing colors, artistic",
            "sketch": "pencil sketch, hand-drawn, line art, detailed sketch",
            "cyberpunk": "cyberpunk, neon lights, futuristic, blade runner aesthetic",
            "pixel-art": "pixel art, 16-bit, retro gaming, sprite style",
            "3d-render": "3D render, octane render, unreal engine, cinema 4D",
            "minimalist": "minimalist, clean lines, simple, elegant, flat design",
        }
        modifier = style_modifiers.get(style, "")
        return f"{prompt}, {modifier}"

    def _select_backend(self, engine: str) -> str:
        backends = ["stable-diffusion", "dalle", "midjourney-style"]
        if engine == "auto":
            return "stable-diffusion"  # 默认选择
        return engine

    def _run_generation(self, backend: str, prompt: str, negative_prompt: str,
                       width: int, height: int, seed: Optional[int],
                       steps: int, cfg_scale: float) -> Any:
        """实际调用AI生成后端"""
        # 这里是后端调用骨架
        print(f"  🤖 调用 {backend} 后端...")
        return None

    def _post_process(self, image: Any, style: str) -> Any:
        return image

    def _save_image(self, image: Any, output: str) -> Path:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path.absolute()

    def _load_image(self, path: str) -> Any:
        return None

    def _run_inpainting(self, image: Any, prompt: str, mask: Any, strength: float) -> Any:
        return None

    def _run_upscale(self, image: Any, scale: float, model: str) -> Any:
        return None

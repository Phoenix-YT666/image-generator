"""
🖼️ AI图片生成工具 - 主入口
Multi-engine AI image generator with stable diffusion, DALL-E, and Claude vision support.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from image_generator.engine import ImageEngine


def main():
    parser = argparse.ArgumentParser(
        description="🖼️ AI图片生成工具 - Image Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例 (Examples):
  # 文生图 (Text-to-image)
  python main.py generate "一只在月光下奔跑的白狼，赛博朋克风格"

  # 图片编辑 (Image editing)
  python main.py edit input.jpg "把背景换成星空"

  # 图片放大 (Upscale)
  python main.py upscale input.jpg --scale 4x

  # 批量生成 (Batch)
  python main.py batch prompts.txt -o ./output/

  # 启动 Web UI
  python main.py web
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # === generate: 文生图 ===
    gen_parser = subparsers.add_parser("generate", help="根据文本描述生成图片")
    gen_parser.add_argument("prompt", help="图片描述")
    gen_parser.add_argument("-o", "--output", default="output.png", help="输出路径")
    gen_parser.add_argument("--width", type=int, default=1024, help="宽度")
    gen_parser.add_argument("--height", type=int, default=1024, help="高度")
    gen_parser.add_argument("--engine", default="auto",
                          choices=["auto", "stable-diffusion", "dalle", "midjourney-style"],
                          help="生成引擎")
    gen_parser.add_argument("--style", default="realistic",
                          choices=["realistic", "anime", "oil-painting", "watercolor", "sketch",
                                   "cyberpunk", "pixel-art", "3d-render", "minimalist"])
    gen_parser.add_argument("--negative", default="", help="反向提示词")
    gen_parser.add_argument("--seed", type=int, help="随机种子")
    gen_parser.add_argument("--steps", type=int, default=30, help="推理步数")
    gen_parser.add_argument("--cfg", type=float, default=7.5, help="提示词引导强度")

    # === edit: 图片编辑 ===
    edit_parser = subparsers.add_parser("edit", help="编辑已有图片")
    edit_parser.add_argument("input", help="输入图片路径")
    edit_parser.add_argument("prompt", help="编辑描述")
    edit_parser.add_argument("-o", "--output", default="edited.png")
    edit_parser.add_argument("--mask", help="蒙版图片路径(可选)")
    edit_parser.add_argument("--strength", type=float, default=0.7, help="编辑强度")

    # === upscale: 图片放大 ===
    upscale_parser = subparsers.add_parser("upscale", help="超分辨率放大图片")
    upscale_parser.add_argument("input", help="输入图片路径")
    upscale_parser.add_argument("-o", "--output", default="upscaled.png")
    upscale_parser.add_argument("--scale", default="2x", choices=["2x", "4x", "8x"])
    upscale_parser.add_argument("--model", default="esrgan", choices=["esrgan", "real-esrgan", "swinir"])

    # === batch: 批量生成 ===
    batch_parser = subparsers.add_parser("batch", help="批量生成图片")
    batch_parser.add_argument("prompts_file", help="提示词文件(每行一个)")
    batch_parser.add_argument("-o", "--output-dir", default="./batch_output/")
    batch_parser.add_argument("--engine", default="auto")
    batch_parser.add_argument("--style", default="realistic")
    batch_parser.add_argument("--parallel", type=int, default=4, help="并行数量")

    # === web: 启动Web界面 ===
    web_parser = subparsers.add_parser("web", help="启动Web图形界面")
    web_parser.add_argument("--port", type=int, default=7860)
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--share", action="store_true", help="创建公开链接")

    # === gallery: 查看生成历史 ===
    gallery_parser = subparsers.add_parser("gallery", help="查看生成历史画廊")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    engine = ImageEngine()

    if args.command == "generate":
        print(f"🎨 正在生成: {args.prompt}")
        result = engine.generate(
            prompt=args.prompt,
            output=args.output,
            width=args.width,
            height=args.height,
            engine=args.engine,
            style=args.style,
            negative_prompt=args.negative,
            seed=args.seed,
            steps=args.steps,
            cfg_scale=args.cfg,
        )
        print(f"✅ 图片已保存到: {result}")

    elif args.command == "edit":
        print(f"✏️ 正在编辑图片: {args.input} -> {args.prompt}")
        result = engine.edit(
            input_path=args.input,
            prompt=args.prompt,
            output=args.output,
            mask_path=args.mask,
            strength=args.strength,
        )
        print(f"✅ 编辑结果已保存到: {result}")

    elif args.command == "upscale":
        print(f"🔍 正在放大图片: {args.input} ({args.scale})")
        result = engine.upscale(
            input_path=args.input,
            output=args.output,
            scale=args.scale,
            model=args.model,
        )
        print(f"✅ 放大结果已保存到: {result}")

    elif args.command == "batch":
        print(f"📦 批量生成模式 - 读取: {args.prompts_file}")
        results = engine.batch_generate(
            prompts_file=args.prompts_file,
            output_dir=args.output_dir,
            engine=args.engine,
            style=args.style,
            max_parallel=args.parallel,
        )
        print(f"✅ 已完成 {len(results)} 张图片")

    elif args.command == "web":
        print(f"🌐 启动Web界面: http://{args.host}:{args.port}")
        engine.launch_web_ui(host=args.host, port=args.port, share=args.share)

    elif args.command == "gallery":
        engine.show_gallery()


if __name__ == "__main__":
    main()

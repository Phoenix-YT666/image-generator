# 🖼️ AI图片生成工具 (Image Generator)

> 多引擎AI图片生成与编辑平台，支持文生图、图生图、图片放大、风格转换等全流程。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ✨ 核心功能

### 1. 🎨 文生图 (Text-to-Image)
- 自然语言描述 → 高清图片
- 支持 Stable Diffusion / DALL-E / Midjourney风格
- 多种艺术风格预设（写实、动漫、油画、水彩、素描、赛博朋克、像素、3D、极简）

### 2. ✏️ 图片编辑 (Image Editing)
- AI 图像修复 (Inpainting)
- 图像扩展 (Outpainting)
- 风格迁移
- 背景替换 / 对象移除

### 3. 🔍 超分辨率放大
- ESRGAN / Real-ESRGAN / SwinIR
- 支持 2x / 4x / 8x 放大
- 保持细节不损失质量

### 4. 📦 批量生成
- 从文本文件批量读取提示词
- 并行生成提高效率
- 自动编号和归档

### 5. 🌐 Web 图形界面
- Gradio 交互式界面
- 所见即所得的参数调整
- 一键生成/下载

---

## 🚀 快速开始

```bash
pip install -r requirements.txt
python main.py generate "一只在月光下奔跑的白狼，赛博朋克风格，霓虹灯背景" -o wolf.png
```

### 更多示例
```bash
# 动漫风格
python main.py generate "樱花树下的少女" --style anime

# 图片编辑
python main.py edit photo.jpg "给天空加上极光" --strength 0.8

# 放大图片
python main.py upscale small.png --scale 4x

# 批量生成
python main.py batch prompts.txt -o ./output/

# Web界面
python main.py web --share
```

---

## 📂 项目结构
```
image-generator/
├── main.py                  # 主入口
├── image_generator/
│   ├── __init__.py
│   ├── engine.py           # 生成引擎核心
│   ├── backends/           # 多种AI后端适配
│   ├── styles/             # 风格预设
│   └── utils/              # 工具函数
├── styles/                  # 风格配置文件
├── examples/               # 示例输入输出
├── tests/
└── requirements.txt
```

## 🛠️ 技术栈
- **AI后端**: Stable Diffusion API / DALL-E API / Claude Vision
- **图像处理**: Pillow / OpenCV / scikit-image
- **超分辨率**: Real-ESRGAN
- **Web UI**: Gradio
- **SDK**: Anthropic SDK / OpenAI SDK

## 📝 License
MIT © Phoenix-YT666

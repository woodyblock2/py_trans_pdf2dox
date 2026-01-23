# PDF → DOCX Demo（PP-OCRv5 Pipeline 优先）

本项目实现 **PDF → DOCX** 的可执行 Demo，严格使用 PaddleOCR 官方 **PP-OCRv5 pipeline** 与 **PP-Structure** 能力完成 OCR 与表格结构识别，满足 `SPEC_pdf2docx_PP-OCRv5_pipeline_first.md` 的要求。

## 功能特性

- 使用 PP-OCRv5 官方 pipeline（含方向分类、检测、识别）
- 使用 PP-Structure 识别表格结构
- PDF 渲染为图片（默认 300 DPI）
- 输出可编辑 DOCX（段落 + Word 表格）
- 支持 Online / Offline 两种运行模式
- 日志包含每页处理状态与 pipeline 信息

## 目录结构

```
.
├── pdf2docx_demo.py
├── requirements.txt
├── SPEC_pdf2docx_PP-OCRv5_pipeline_first.md
└── source
    └── testcase
        └── 1207采样记录.pdf
```

## 环境要求

- Python 3.9+
- 支持 PaddleOCR 及 PP-OCRv5（建议 **高版本/最新版本**，如 2.8+）

## 安装依赖

### 官方推荐安装方式（Windows / Linux / GPU）

> 以下命令来自 PaddleOCR 官方安装建议，GPU 版本请选择与本机 CUDA 匹配的 `paddlepaddle-gpu` 版本。

**Windows (CPU)**

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -U pip
pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install paddleocr>=2.8.0
```

**Windows (GPU)**

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -U pip
# 选择与 CUDA 版本匹配的 paddlepaddle-gpu
pip install paddlepaddle-gpu==2.6.1.post120 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install paddleocr>=2.8.0
```

**Linux (CPU)**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install paddleocr>=2.8.0
```

**Linux (GPU)**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
# 选择与 CUDA 版本匹配的 paddlepaddle-gpu
pip install paddlepaddle-gpu==2.6.1.post120 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install paddleocr>=2.8.0
```

### 本项目依赖安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> 如果在 Windows/离线环境遇到模型源连通性检查提示，可临时设置环境变量跳过：  
> `DISABLE_MODEL_SOURCE_CHECK=True`。

> 若使用 GPU，请自行安装对应版本的 `paddlepaddle-gpu`。

> 本 Demo 以高版本 PaddleOCR 为目标；代码中使用 `from paddleocr.ppstructure import PPStructure`，可兼容 2.8+ 的包结构。

### 环境验证脚本

安装完成后，可运行下面脚本验证 `PPStructure` 是否可用：

```bash
python verify_paddleocr_env.py
```

## Online 运行（允许联网下载模型）

首次运行会由 PaddleOCR 自动下载 PP-OCRv5 与 PP-Structure 所需模型。

```bash
python pdf2docx_demo.py "source/testcase/1207采样记录.pdf" \
  --dpi 300 \
  --show-log
```

生成文件默认与 PDF 同名：`source/testcase/1207采样记录.docx`。

## Offline 运行（完全离线）

离线模式 **禁止** 自动下载模型，必须提前准备好本地模型目录，并显式传入。

### 1. 在线环境准备模型

推荐先在有网络的机器运行一次，让 PaddleOCR 自动下载：

```bash
python pdf2docx_demo.py "source/testcase/1207采样记录.pdf" --show-log
```

然后将 PaddleOCR 模型目录（通常为 `~/.paddleocr`）拷贝到离线机器。

### 2. 离线模式执行

将各模型目录显式传入（目录名称可按实际情况调整）：

```bash
python pdf2docx_demo.py "source/testcase/1207采样记录.pdf" \
  --offline \
  --det-model-dir /path/to/det \
  --rec-model-dir /path/to/rec \
  --cls-model-dir /path/to/cls \
  --table-model-dir /path/to/table \
  --layout-model-dir /path/to/layout \
  --show-log
```

若缺少模型目录，程序会立即报错并提示补全参数。

## 可执行 Demo

最小运行命令：

```bash
python pdf2docx_demo.py "source/testcase/1207采样记录.pdf"
```

## 备注

- 该 Demo 侧重流程正确与结构可用，暂不追求样式还原。
- 输出 DOCX 中包含可编辑文本与 Word 表格。
- 控制台日志可看到每页处理状态与 pipeline 信息（PP-OCRv5）。

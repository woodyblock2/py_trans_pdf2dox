# PDF 表格 → DOCX Demo

该 Demo 用于将扫描版中文表格 PDF 转换为可编辑的 DOCX，并输出结构化 JSON 报告。

## Windows 环境准备

- Windows 10/11 x64
- Python 3.10+（推荐 3.11）
- 确保已安装 Microsoft Visual C++ Build Tools（部分依赖可能需要）

## 安装依赖

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## 模型目录结构

运行时必须提供本地模型目录，不允许自动下载：

```
models/
  det/
  rec/
  cls/
  table/
```

- `det/`：文本检测模型
- `rec/`：文本识别模型（中文）
- `cls/`：方向分类模型
- `table/`：PP-Structure 表格模型

> 提示：请将 PaddleOCR 官方下载的模型解压到对应目录，确保目录内包含 `.pdmodel`、`.pdiparams` 等文件。

## 模型下载方式（PaddleOCR 官方）

模型需要手动下载，推荐通过 PaddleOCR 官方仓库的模型列表获取：

1. 打开 PaddleOCR 官方仓库：https://github.com/PaddlePaddle/PaddleOCR
2. 在仓库内搜索 `model_list` 或 `models_list`，进入对应的模型列表文档。
3. 下载以下模型并解压到 `models/` 目录：
   - `det/`：中文文本检测模型（PP-OCR 系列）
   - `rec/`：中文文本识别模型（PP-OCR 系列）
   - `cls/`：方向分类模型（PP-OCR 系列）
   - `table/`：PP-Structure 表格模型

PaddleOCR 官网地址（便于确认最新公告与入口）：https://www.paddleocr.com

### 如果下载链接失效，如何替换模型 URL

本项目内置的下载地址在 `app/utils/model_downloader.py` 的 `MODEL_SPECS` 中。如遇 404，请按以下方式替换：

1. 从 PaddleOCR 官方“模型列表/Model List”文档中确认以下关键信息：
   - **模型类型**：`det / rec / cls / table`
   - **语言**：中文模型（示例：`ch`）
   - **版本**：PP-OCR 或 PP-Structure 的具体版本（例如 v4/v5）
   - **下载链接**：`.tar` 或 `.tar.gz` 直链 URL（BOS/OSS 链接）
2. 将对应模型的 URL 替换到 `MODEL_SPECS` 中相同 `key` 的 `url` 字段。

例如，`cls` 模型的配置形如：

```python
ModelSpec(
    key="cls",
    url="https://.../ch_xxx_cls_infer.tar",
    description="方向分类模型",
)
```

替换后重新运行：

```bash
python -m app.download_models --models ./models --force
```

> 费用说明：PaddleOCR 官方模型可免费使用（遵循 PaddleOCR 开源协议/许可证），不需要付费。具体许可条款请以 PaddleOCR 官方仓库说明为准。

## 部署阶段（联网下载模型）

部署阶段建议联网执行一次模型下载，完成后即可离线运行：

```bash
python -m app.download_models --models ./models
```

该命令会下载默认的 PP-OCR 中文 det/rec/cls 与 PP-Structure table 模型，并解压到：

```
models/
  det/
  rec/
  cls/
  table/
```

如需重新下载并覆盖已有模型，可使用：

```bash
python -m app.download_models --models ./models --force
```

## 离线执行阶段（仅本地模型）

离线环境请确保 `models/` 目录已准备完毕（包含 `.pdmodel`、`.pdiparams` 等文件），然后执行：

```bash
python -m app.main --input ./samples --output ./output --models ./models --debug
```

## 运行 Demo

```bash
python -m app.main --input ./samples --output ./output --models ./models --debug
```

可选参数：

- `--dpi`：PDF 渲染 DPI（默认 300）
- `--debug`：保存中间图片
- `--max-pages`：限制处理页数
- `--no-fallback`：禁用 OpenCV 兜底
- `--rotation-strategy`：旋转策略（`ocr_score` 或 `none`）

## 输出说明

每个 PDF 会在输出目录生成一个同名子目录，例如：

```
output/your_pdf/
  your_pdf.docx
  your_pdf.json
  debug/
```

- `.docx`：还原后的可编辑表格
- `.json`：包含页面旋转角度、表格数量、单元格 OCR 结果等
- `debug/`：渲染、旋转、预处理等中间图（仅 `--debug` 时生成）

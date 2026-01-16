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
2. 进入文档中的“模型列表/Model List”页面，选择以下模型并下载：
   - `det/`：中文文本检测模型（PP-OCR 系列）
   - `rec/`：中文文本识别模型（PP-OCR 系列）
   - `cls/`：方向分类模型（PP-OCR 系列）
   - `table/`：PP-Structure 表格模型
3. 将下载的压缩包解压到对应目录（`models/det`、`models/rec`、`models/cls`、`models/table`），确保目录内包含 `.pdmodel`、`.pdiparams` 等文件。

> 费用说明：PaddleOCR 官方模型可免费使用（遵循 PaddleOCR 开源协议/许可证），不需要付费。具体许可条款请以 PaddleOCR 官方仓库说明为准。

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

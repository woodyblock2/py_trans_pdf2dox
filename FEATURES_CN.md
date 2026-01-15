# 扫描 PDF 表格 → DOCX（含表格结构）Demo  
## 功能需求说明（供 Codex / 代码生成工具使用）

---

## 1. 项目目标（Goal）

构建一个 **Windows 平台优先** 的 Demo 应用，用于将**扫描版 PDF 表格（以中文内容为主，含手写填写）**转换为 **DOCX 文件**，并满足以下要求：

- 输出 **可编辑的 Word 表格**
- 尽量保留表格结构：
  - 行 / 列
  - 合并单元格（rowspan / colspan）
- 将 OCR 识别的文本填充到对应表格单元格中
- 支持 **批量处理 PDF**
- 支持 **PDF 页面方向不统一**（0 / 90 / 180 / 270 度）
- **运行时可完全离线**
  - 所有 OCR / 表格结构模型均来自本地目录
  - 禁止运行时联网下载模型或资源

该 Demo 的目标是 **跑通完整电子化归档流水线**，而不是追求 100% OCR 准确率。

---

## 2. 非目标（Non-Goals）

- ❌ 不要求手写内容 OCR 绝对准确
- ❌ 不要求 Word 表格样式与原扫描件像素级一致
- ❌ Demo 阶段不需要 GUI（图形界面）
- ❌ 不涉及数据库、全文检索或系统集成

---

## 3. 平台与运行环境（Platform）

- 操作系统：Windows 10 / Windows 11（x64）
- Python：
  - 不强制固定版本
  - 需兼容 **Python 3.10 及以上**
  - 开发与验证环境以 **Python 3.11.x** 为主
- OCR 语言：
  - **中文为主（简体中文）**
  - 文本中可能混合数字、字母、日期、编号

---

## 4. 输入与输出定义

### 输入（Input）

- 单个 PDF 文件 或 一个包含多个 PDF 的目录
- PDF 为扫描件（图片型 PDF）
- 支持多页 PDF
- 页面方向可能不统一（横放、倒置）

---

### 输出（Output）

针对每一个输入 PDF，输出：

1. **一个 DOCX 文件**
2. **一个 JSON 结构化结果文件（用于质检 / 归档）**

#### DOCX 输出要求

- 每一页 PDF 对应 Word 中的一页（或一个 section）
- 每页中检测到的表格：
  - 输出为 Word 表格（非图片）
  - 行列结构尽量保持
  - 合并单元格需尽量还原
- 表格单元格中填充 OCR 识别的文本
- 内容可编辑

#### JSON 结果文件内容

- 每一页：
  - 选用的旋转角度
  - 表格数量
- 每个单元格：
  - 坐标（bbox）
  - OCR 文本
  - 置信度
  - 是否使用兜底方案（fallback）

---

## 5. 核心处理流程（MVP 必须实现）

### Step A：PDF 转图片

- 使用 **PyMuPDF（fitz）**
- 每页渲染为高分辨率图片（等效约 300 DPI）
- 默认在内存中处理
- Debug 模式下可保存中间图片

---

### Step B：页面方向自动纠正

对每一页图片执行：

1. 尝试旋转角度：`0° / 90° / 180° / 270°`
2. 对每个角度执行一次 **轻量 OCR**
3. 根据以下规则选取最佳方向：
   - 中文文本识别长度最大，或
   - OCR 平均置信度最高
4. 选中的角度记录到 JSON 报告中

---

### Step C：图像预处理（可配置）

- 灰度化
- 轻度去噪
- 对比度增强 / 自适应阈值
- 预处理参数需支持配置
- Debug 模式下输出预处理图像

---

### Step D：表格结构识别（主路径）

使用 **PaddleOCR PP-Structure（表格结构识别）**：

- 检测页面中的表格区域
- 提取表格结构信息：
  - 行数、列数
  - 单元格位置
  - 合并单元格信息（如可获取）

如输出为 HTML：
- 解析 `<table>` 结构
- 提取 `rowspan / colspan`

如仅返回单元格 bbox：
- 按空间位置聚类，重建行列结构

---

### Step E：单元格 OCR（中文）

- 对每个单元格区域（ROI）：
  - 从原图或预处理图中裁剪
  - 使用 PaddleOCR **中文识别模型**
  - 输出文本 + 置信度
- 结果写入 JSON 报告

---

### Step F：DOCX 重建

使用 `python-docx`：

- 创建 Word 表格
- 设置行列数
- 根据结构信息合并单元格
- 向单元格写入 OCR 文本

#### Word 样式要求
- 字体优先级：
  1. 宋体（SimSun）
  2. 微软雅黑（Microsoft YaHei）
  3. 默认字体（fallback）
- 表格边框可见
- 单元格内容可编辑

---

## 6. 表格结构兜底方案（Fallback）

当表格结构识别失败时：

- 使用 OpenCV：
  - 检测水平线与垂直线
  - 计算交点，构建表格网格
- 基于网格切分单元格
- 对单元格执行 OCR
- 重建 Word 表格
- 在 JSON 报告中标记 `fallback_used = true`

> Fallback 方案允许效果一般，但程序不得崩溃。

---

## 7. 命令行接口（CLI）

入口方式：
# python -m convert_pdc_demo.main
- 必需参数
 - --input：PDF 文件或目录
 - --output：输出目录
 - --models：本地模型目录
- 可选参数
 - --dpi（默认 300）
 - --debug（保存中间过程图片）
 - --max-pages（限制页数，用于 demo）
 - --no-fallback（禁用兜底）
 - --rotation-strategy（默认：ocr_score）
```bash
# 示例：
python -m app.main --input ./samples --output ./output --models ./models --debug
```

---

## 8. 项目结构要求
- 清晰模块划分
```
pdf_table_to_docx/
  app/
    main.py
    pipeline/
      pdf_to_images.py
      rotation.py
      preprocess.py
      table_structure.py
      cell_ocr.py
      docx_writer.py
      fallback_grid.py
    utils/
      io.py
      logger.py
      json_report.py
  models/          # 本地模型（运行时不下载）
  samples/
  output/
  requirements.txt
  README.md
```
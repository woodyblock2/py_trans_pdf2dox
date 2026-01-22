# PDF → DOCX Demo 需求说明（PP-OCRv5 官方 Pipeline 优先）

## 1. 项目目标

先了解 PP-OCRv5
以下两个是官网相关文档信息
https://www.paddleocr.ai/latest/index.html
https://www.paddleocr.ai/latest/version3.x/pipeline_usage/OCR.html

使用 Python 实现一个可执行 Demo，将 PDF 文档转换为 DOCX 文档。

PDF 特点：
- 中文内容为主
- 大量表格（扫描表单类型）
- 可能存在页面方向不一致（旋转、倒置）
- PDF 可能是扫描型（图片型 PDF）

核心目标：
- **必须优先、完整使用 PaddleOCR 官方提供的 PP-OCRv5 及其 pipeline 能力**
- 不自行拆分或重写 OCR pipeline 内部算法
- 输出可编辑的 DOCX（文字 + Word 表格）
- Demo 阶段优先保证流程正确、结构可用，而非极致样式还原

---

## 2. 运行模式要求（Online / Offline）

### 2.1 Online（有网络执行）
- 执行环境允许联网
- 允许 PaddleOCR 自动下载所需模型与资源
- 用于开发、验证 Demo

### 2.2 Offline（无网络执行）
- 执行环境完全断网
- 所有模型、字典、资源必须从本地加载
- 禁止任何隐式在线下载行为
- 若缺少资源，程序必须明确报错并提示资源准备方式

---

## 3. 核心技术约束（非常重要）

### 3.1 OCR 能力约束（必须遵守）

- **OCR 必须基于 PaddleOCR 官方 pipeline**
- **默认使用最新的 PP-OCRv5（如 PP-OCRv5_server）**
- 不允许自行实现或替代以下能力：
  - 文档方向分类（0 / 90 / 180 / 270）
  - 文本行方向分类
  - 文本检测（det）
  - 文本识别（rec）
- 若官方 pipeline 已提供某项能力，必须直接调用官方实现

> 原则：  
> **调用官方产品能力，而不是重写算法或拼装自定义 OCR pipeline**

---

## 4. 表格与文档结构处理原则

### 4.1 表格处理原则

- OCR 文本识别使用 PP-OCRv5 官方 pipeline
- 表格结构识别 **不得使用手工 OpenCV 网格推断作为主要方案**
- 若需要表格结构输出，应优先使用 PaddleOCR 官方提供的：
  - 表格识别 pipeline，或
  - 文档结构化 pipeline（如包含表格子模块的方案）

Demo 阶段允许：
- 表格先输出为中间结构（如 HTML / JSON）
- 再将结构化表格转换为 Word 表格（DOCX）

---

## 5. 总体处理流程（高层描述，不拆算法）

1. PDF 按页渲染为图片（DPI 可配置，推荐 300）
2. 将页面图片输入 PaddleOCR 官方 pipeline
   - 使用 PP-OCRv5
   - 启用官方支持的方向分类与必要的预处理
3. 获取 OCR 及（若可用）表格/结构化识别结果
4. 将结构化结果转换为 DOCX：
   - 普通文本 → Word 段落
   - 表格结构 → Word 表格
5. 每页内容在 DOCX 中保持合理阅读顺序
6. 页面之间插入分页符

---

## 6. 输出要求（Demo 验收标准）

输入：
- 示例 PDF（中文扫描表格）

输出：
- 对应的 `.docx` 文件

验收标准：
1. 程序可正常运行完成（无异常退出）
2. DOCX 文件可被 Microsoft Word / WPS 正常打开
3. 每页至少包含：
   - 可编辑文本，或
   - 可编辑 Word 表格
4. 表格内容不应全部退化为一段无结构文本
5. 控制台日志中能看到：
   - 每页处理状态
   - 使用的 OCR pipeline 信息（如 PP-OCRv5）

---

## 7. 测试案例
```
source\testcase\1207采样记录.pdf
```
这是测试case，要求将该文件转换成docx文件。

要求写在 README.md中写清楚环境部署步骤，如何构建，最终可执行。

---

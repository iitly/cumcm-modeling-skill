# 赛题与格式文件的读取

最后整理：2026-11-16（北京）。读取 .doc/.pdf/.xlsx 的可运行写法与常见报错。文件路径、已装软件以本机实际为准，先探测再执行。

## 0. 先确认解释器

同一台机器上可能存在多个 Python（系统、venv、各类工具内置），装包位置和可用模块不同：

```bash
python -c "import sys; print(sys.executable, sys.version)"
```

先在**准备运行代码的那个解释器**里核可用依赖，优先复用已经具备所需库的环境。新增安装须在本轮授权内，并用该解释器的 `python -m pip`；不要自动装包，也不要假设某入口一定缺包或一定有包。

## 1. 读 PDF（赛题）

```python
import fitz  # pymupdf

doc = fitz.open('E:/数学建模国赛/25/A题/A题.pdf')
try:
    text = ''.join(page.get_text() for page in doc)
finally:
    doc.close()
```

- Windows 原生 Python 用 `E:/...` 正斜杠路径；`/e/...` 是 MSYS 风格，原生 Python 不认。
- WSL/Linux 或 MSYS 环境下的 Python 按该环境挂载路径写（如 `/mnt/e/...`）。先用 `sys.platform`/`sys.executable` 判断在哪个环境。

## 2. 读旧版 .doc（OLE 二进制）

`python-docx` 只处理 `.docx`（zip 包）。读 `.doc` 会报 `PackageNotFoundError` 或 `BadZipFile`，不是“乱码”。

### 方案 A：Word COM（Windows 已装 Word 时的可选方法）

```python
import win32com.client

word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
word.AutomationSecurity = 3  # 禁用自动化打开文档中的宏；只读不等于禁用宏
doc = None
try:
    doc = word.Documents.Open('E:/数学建模国赛/25/format2025.doc', ReadOnly=True)
    text = doc.Content.Text
    print(text)
finally:
    if doc is not None:
        doc.Close(False)
    word.Quit()
```

`try/finally` 必须有，否则异常时残留 WINWORD.EXE 进程。

### 方案 B：LibreOffice 无头转换（无 Word 时）

```bash
soffice --headless --convert-to docx --outdir <输出目录> <文件.doc>
```

转换后按 `.docx` 读，并检查表格、公式、版式是否丢失。先 `command -v soffice` 确认存在；本机当前未实测此路径。

### 方案 C：纯文本提取

`antiword`、`catdoc` 可提取正文，表格和公式基本丢失，只在不关心版式时用。

## 3. 读 .xlsx 附件

```python
import openpyxl

wb = openpyxl.load_workbook('E:/数学建模国赛/25/A题/附件/result1.xlsx', data_only=True)
try:
    ws = wb[wb.sheetnames[0]]
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True):
        print(row)
finally:
    wb.close()
```

`data_only=True` 只读文件已有的公式缓存，openpyxl 不计算公式；缓存可能缺失或过期。必要时同时只读加载公式表达式，对关键结果独立复算；若需用 Excel/WPS 重算，先复制到获准工作区，不能让用户在原始附件/封版件上“另存一次”改变证据。

## 4. 常见报错对照

| 报错/现象 | 实际原因 | 处理 |
|---|---|---|
| `FileNotFoundError: '/e/...'` | 路径风格与环境不匹配 | Windows 原生 Python 改 `E:/...`；WSL 用 `/mnt/e/...` |
| `PackageNotFoundError` / `BadZipFile` 读 .doc | `.doc` 是 OLE 复合文档，不是 zip | Word COM 或 LibreOffice 转 `.docx` |
| `ModuleNotFoundError: openpyxl` / `fitz` | 当前解释器未安装 | 在该解释器核依赖；已有合适环境则复用，新增安装先核授权 |
| 某个入口能 import、另一个不能 | 两者用了不同解释器 | 先 `sys.executable` 对比，再决定在哪装包 |

## 5. 格式要点（历史索引，必须核对当年原件）

以下为 2025 年的记录，**不是通用门槛**。执行前用当年官方 `formatYYYY.doc` 与赛区通知逐条核对；数字以原件为准，不得直接套用到 2026/2027。

- 白色 A4，上下左右 ≥2.5 cm，左侧装订
- 纸质版：第 1 页承诺书、第 2 页编号专用页、第 3 页摘要页（含标题关键词，≤1 页），页码从摘要页起
- 第 4 页起正文，不要目录，≤30 页；附录页数不限
- 附录含支撑材料文件列表 + 全部可运行源程序；确实没有程序须在附录声明
- 电子版 PDF 或 Word，≤20MB，第一页为摘要专用页（赛区可另行加严，如只收 PDF）
- 支撑材料 ZIP/RAR 压缩，≤20MB
- 全文任何位置不得出现参赛者身份与学校信息
- 引用他人成果须标注
- 字号/字体/行距/颜色通常不做全国统一要求（赛区可另定）

当前年度要求见 `references/competition-compliance.md`。

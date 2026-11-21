# Markdown → DOCX（公式转 OMML）

最后整理：2026-11-16（北京）。目标：交付可编辑的 Word，公式为原生 OMML 而不是 LaTeX 源码。

## 1. 为什么不用 python-docx 直接写公式

python-docx 不会自动把写进段落的 LaTeX 转为数学对象；需使用适配的 OMML 转换/插入工具。已有 DOCX 主稿时直接处理该稿，不另起 Markdown 母本覆盖它；现有 MD 主源有批量公式时可走下述 pandoc 路线。

## 2. pandoc 路线

### 2.1 先确认解释器

```bash
python -c "import sys; print(sys.executable)"
python -c "import pypandoc; print(pypandoc.get_pandoc_version())"
```

`pypandoc_binary` 的 wheel 通常自带 pandoc 二进制，但不是所有平台/架构/Python 版本都有可用 wheel；装的是 `pypandoc`（非 binary）时可能仍需系统 pandoc。本机 2026-11-09 实测：Hermes venv 的 python 3.11.15 中 `pypandoc 1.17` 可用，内置 pandoc 3.9；系统 PATH 中没有独立 pandoc。

只有本轮已授权新增依赖、且没有可复用环境时才安装，使用**运行代码的那个解释器**；下列是可选命令，不是自动执行步骤：

```bash
python -m pip install pypandoc_binary -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2.2 转换

```python
import os
import pypandoc

print(pypandoc.get_pandoc_version())

pypandoc.convert_file(
    '论文.md',
    'docx',
    outputfile='论文.docx',
    extra_args=[
        '--from=markdown+tex_math_dollars+tex_math_single_backslash',
        '--resource-path=.',          # 图片相对路径
        # '--reference-doc=reference.docx',  # 需要统一中文字体/样式时再加
    ],
)
assert os.path.getsize('论文.docx') > 0
```

`--reference-doc` 可带入预设样式（字体、页边距、标题层级），没有对应模板时不要硬加，否则报错。

### 2.3 原理与限制

pandoc 用 texmath 把常见 LaTeX 转成 Word 的 `<m:oMath>`。宏覆盖有限：`\boxed`、自定义 `\newcommand`、复杂 `aligned`/`cases` 可能被忽略或原样输出。转换后对关键公式核符号结构。遇到不支持的宏，优先改成等价且受支持的表达或原生 OMML；不能擅自转图片冒充可编辑公式。确需图片须获用户接受并在交付说明中标清降级。

## 3. 验证

1. 打开 `.docx`，行内公式应为可点击的内嵌公式，不是 LaTeX 文本。
2. 显示公式居中、可编辑；希腊字母、上下标、分数、根号正常。
3. 复杂表格（合并单元格、多行表头）是否完整；pandoc 对复杂表格支持有限。
4. 图片是否找到（`--resource-path` 正确）。
5. 页数、字号、页边距是否满足当届要求；样式没设时 Word 默认样式可能与论文规范不符。

## 4. 回退

pandoc 不可用时：

- 用 python-docx 生成 `.docx`，公式保留为 LaTeX 文本，**在交付说明中标注“公式为 LaTeX 文本，未转 OMML”，列为待处理项**，不能默认为完成。
- 或用 Word 365/2019+ 的公式编辑器手动转（可切换 LaTeX/UnicodeMath 输入；旧版通常只有 UnicodeMath，需在目标版本实测）。

论文公式多时优先修 pandoc，不要长期停在回退方案。

## 5. 与主流程的关系

默认交付 Word；沿用已确认主源，不擅自平行维护。Word 的公式需核原生数学对象与可编辑性；已有 LaTeX 主源时，TeX 可编辑、PDF 核可读性与版面，不把 PDF 不可直接编辑当成失败，也不把 XML 中存在一个 `<m:oMath>` 当成全部公式正确。

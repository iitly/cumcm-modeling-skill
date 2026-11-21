# Matplotlib 中文字体：确认实际字形

最后更新：2026-11-16（北京）。字体名可解析不等于覆盖全部字符；字体文件大小也不决定图是否合格。

## 最小检查

在获准工作区运行，复用已有绘图库环境；缺字体不自动下载/安装。

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.ft2font import FT2Font

required = '中文负荷电压μ'
selected = None
for family in ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'Source Han Sans SC']:
    try:
        path = fm.findfont(fm.FontProperties(family=[family]), fallback_to_default=False)
        coverage = FT2Font(path).get_charmap()
        if all(ord(char) in coverage for char in required):
            selected = family
            break
    except (ValueError, OSError, RuntimeError):
        continue
if selected is None:
    raise RuntimeError('未找到覆盖所需中文字符的字体；请核可用字体或另获安装授权')
plt.rcParams['font.family'] = [selected]
plt.rcParams['axes.unicode_minus'] = False
print('font:', selected)
```

`required` 应覆盖本次实际标签中的字符；数学渲染和其他字体仍要单独看。`unicode_minus=False` 仅把刻度负号换为连字符，不解决中文或其他符号缺失。

## 字体文件与验收

可按实际系统查字体，显式加载文件时先确认存在、注册、解析路径与字形；不要把某个用户名/Windows 路径或少数样本字体大小写成通用事实。

最终以目标尺寸的 PNG/PDF/文档渲染核中文、符号、遮挡和裁切；程序字形检查与 warning 记录可辅助，不能代替目检。不得只对“已知中文串”计算像素就宣称全文全部可读。

中文图出现方框是未完成项。若提出改英文标签作为临时方案，先看用户/赛事语言要求；不能擅自把中文图改英文并声称原要求已满足。

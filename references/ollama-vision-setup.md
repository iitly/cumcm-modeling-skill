# 本地视觉模型（Ollama）：备用看图方案

最后整理：2026-11-16（北京）。**本文件记录的是历史部署方案，不是当前环境事实。**

## 0. 先探测，再决定是否使用

2026-11-09 本机探测结果：`E:\ollama\ollama.exe` 不存在，`~/.ollama/models` 不存在，`http://localhost:11434` 连接失败，`ollama` 不在 PATH。这只是历史探测记录，**不能据此判断今天是否可用**。每次先按下列方式现场探测；优先使用当前已可用的图像能力，不因旧记录启动安装或下载。

使用前依次探测：

```bash
ollama --version
ollama list
curl -sS http://localhost:11434/api/tags
```

任一步失败就停止，不要继续按示例路径调用。版本、模型大小以实际输出为准。

## 1. 历史部署记录（仅供重建参考）

| 项目 | 记录的路径/值 |
|---|---|
| Ollama 路径 | `E:\ollama\ollama.exe` |
| 模型 | `minicpm-v:8b` |
| API | `http://localhost:11434` |

这些值来自当时的部署记录，换机器或清理磁盘后可能全部失效。复现实验时记录实际管理接口返回的版本、模型 ID/digest 与量化方式；拿不到就标未知，不把 tag 当成已经锁定的修订。

## 2. 能力边界

**可以做**：识别图的结构关系（几个对象、怎么连接、流向）、识别图元类型、分区域描述内容。

**不能依赖**：精确中文 OCR（文字和数字可能读错）、无上下文时的领域判断。

**策略**：让模型理解场景，精确参数由用户或原文核对；把它的描述当“候选解读”，不是事实来源。

## 3. 调用示例（含错误处理）

```python
import base64
import requests

BASE = 'http://localhost:11434'
with open('image.png', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

resp = requests.post(
    f'{BASE}/api/generate',
    json={'model': 'minicpm-v:8b',
          'prompt': '请描述这张工程示意图的内容和结构',
          'images': [img_b64],
          'stream': False},
    timeout=120,
)
resp.raise_for_status()
data = resp.json()
if 'error' in data:
    raise RuntimeError(data['error'])
print(data.get('response', ''))
```

调用前核实际端点、可用模型及其多模态支持。`OLLAMA_HOST` 可能是监听配置（例如 0.0.0.0），不是可以直接照抄的客户端地址；明确客户端可达 URL。保留原图，先裁切/分块读取关键数字，再按模型输入限制准备副本，不能缩图后丢掉关键标注。响应为空或出现错误都算未识别。

## 4. 网络

`registry.ollama.ai` 在国内可能无法直连。下载或访问异常先核实际网络、代理和官方分发方式；使用已配置且可用的通道，新增下载/部署先获授权。多模态模型的离线导入还可能需要配套投影器与格式支持，不能把任何 GGUF 当成开箱即用的视觉模型。

Ollama 会复用已下载的层，重试只对瞬时中断有效；连续失败就别再重试。换客户端库（curl / urllib / requests）不改变链路，不要指望它“更容易穿透”。

## 5. 与主流程的关系

主流程的看图以能真实读到图像为准。路由失效、返回为空或描述明显不准时，降级顺序是：Hermes `vision_analyze` → 本文件（若探测通过）→ 请用户提供文字描述。**不允许跳过识别直接编造图内容。**

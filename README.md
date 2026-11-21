# CUMCM 数模技能包

**iitly × Hermes** · 2026

一个给 AI 编程助手（Hermes / Claude Code / Cursor 等）用的数学建模竞赛技能。以 CUMCM 全国大学生数学建模竞赛为主，流程与规则口径可迁移到美赛、华数杯等赛事。

它规定的重点在过程：题面证据怎么记、公式怎么核、结果怎么验、合规怎么过。它不提供“一键生成论文”的模板库。

## 解决的问题

1. **题意台账**：每个小问的条件性质、输入与单位、必答输出、实现位置、检验证据逐条登记，避免“写着写着换了题意”。
2. **公式与数值核算**：先锁物理量定义、积分区间、参考方向与边界，再复算数值；量纲、定义域、可检验极限逐项过。**同一公式抄出的新表不算独立验证**。
3. **按风险验证**：按题型选留出集、上下界、收敛性、敏感性，不套固定“三件套”，也不拿模拟次数当质量证明。
4. **合规与冻结**：提交前核匿名、AI 披露、文件大小、内容指纹；封版后原件只读，需要改动另建副本。

## 和常见模板的区别

- **不按奖级发配额**：没有“国一必须 10 张图 / 3 个创新点 / 8 篇文献”这类门槛，奖项目标只影响投入，不改变正确性与合规标准。
- **不虚构文献**：AI 只给检索词与方向，文献由人检索核实后 AI 排版；不生成题名、作者、DOI。
- **不把“AI 味”当风格问题**：只改具体病句、套话与冗余，不靠补虚词、改数字密度、制造风格断裂这类伪特征处理。
- **分开报验证**：自检、独立复核、真实运行、独立数值互验是四件事，不互相冒充。

## 安装

### Hermes

```bash
git clone https://github.com/iitly/cumcm-modeling-skill.git \
  "$LOCALAPPDATA/hermes/skills/research/math-modeling-paper"
```

非 Windows 环境放到 `~/.hermes/skills/` 下同名目录。目录名可自定义，技能名取自 `SKILL.md` 的 frontmatter。

### Claude Code

```bash
git clone https://github.com/iitly/cumcm-modeling-skill.git \
  ~/.claude/skills/math-modeling-paper
```

### 其他助手

把 `SKILL.md` 作为规则文件加载，`references/` 按需读取，不必一次全塞进上下文。

## 目录

```
SKILL.md                      主流程：权限 → 选题 → 建模 → 求解 → 验证 → 成稿 → 交付
references/                   19 份按需资料
  competition-compliance.md   赛事规则登记（2026 国赛转录与层级口径）
  data-evidence-review.md     题意台账、数据体检、逐问证据包、独立复核
  model-validation.md         按风险验证、比较前锁定条件
  model-dictionary.md         按问题结构选型的候选索引
  writing-delivery.md         写作、语言、文档交付
  numerical-pitfalls.md       单位、优化、ODE、统计陷阱
  绘图规范.md / 流程图配方.md / matplotlib-chinese-font.md
  pandoc-docx-conversion.md   Markdown → Word 原生公式
  cumcm-format-reading.md     .doc/.pdf/.xlsx 读取
  ai_research_failure_modes.md 七类 AI 科研失败自查
  post-contest-review.md      赛后复盘、公告核对、答辩练习
  华数杯经验总结.md / 竞赛实证锚点.md   有边界的历史观察
  cmos-ring-oscillator-physics.md      电路题专项推导
  ollama-vision-setup.md      历史部署记录（当前环境以实测为准）
  cumcm-agents-adoption.md    外部来源取舍记录
  maintenance-decisions.md    版本演进与已撤销规则
templates/                    逐问证据表、隔离行为抽检
scripts/validate_skill.py     静态校验
scripts/test_validate_skill.py 校验器自身的正例与反例回归
```

## 自检

```bash
python -B scripts/validate_skill.py
python -B scripts/test_validate_skill.py
```

第一条核结构、内部链接、代码围栏、Python 语法与已撤销规则是否回流；第二条用故意造坏的副本确认校验器真的会拒绝。静态通过不代表建模正确，也不替代真实运行。

## 边界

- **不保证获奖**。它降低的是低级错误和合规风险，不是评分结果。
- **规则以官方原文为准**。包内登记的 2026 国赛条款是转录，换届、换赛区都要重核原件。
- **竞赛期间使用须遵守当届 AI 使用规定**，包括声明与使用详情材料；本包不替使用者做合规判断。
- **专项物理推导只在其声明范围内成立**，例如 `cmos-ring-oscillator-physics.md` 是理想长沟道阶跃模型，不等于器件实测。

## 许可

MIT，见 [LICENSE](LICENSE)。

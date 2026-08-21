# 场景闭环 × Feynman 学习法 设计方案

**日期**: 2026-04-18
**状态**: 🟢 已定稿（2026-04-18 用户确认方向+强度+源码模式）
**提案人**: 用户 + AI（Cascade）
**对应讨论**: 2026-04-18 关于 `02.1_I2C 协议代码.md` "碎片化" 问题的重构讨论

---

## 〇、TL;DR

把**操作性 Lesson** 的讲解结构从"知识结构导向"（先抽象后应用）升级为"**场景闭环导向**"（每外设一完整闭环），并在每闭环末尾强制 **Feynman 输出**（文字 + 手绘拍照 + 代码改写三选二）。源码集成采用"**精瘦模式**"——核心片段 + 路径引用 + delta 对比。

| 维度 | 当前（模式 A） | 新增（模式 B） |
|------|--------------|--------------|
| 组织轴 | API 族横切（`Master_*` / `Mem_*`） | 外设纵向闭环（EEPROM / OLED / AHT20） |
| 闭环粒度 | 整课 1 个闭环 | 每外设 1 个闭环，课内 N 个 |
| 学完能 ship | 理解 API 选型 | 每闭环 = 可独立烧板的项目 |
| Feynman 触发 | 课末 Reflection | 每闭环末 🔴 强制输出 + 🔵 AI 检查 |
| 认知峰值 | 需跨节维持多场景上下文 | 每节自封闭，峰值低 |
| 源码来源 | AI 虚构代码片段 | 实际工程源码（如航歌 `04-stm32/`）抽取 |

---

## 〇·A、决策摘要（2026-04-18 锁定）

| # | 决策 | 选项 | 影响面 |
|---|------|------|-------|
| Q1 | 改造路径 | **模板级改造**（非试点） | SKILL.md + lesson-template.md + background.md |
| Q2 | Feynman 强度档位 | **B 中度**（文字+拍照+代码改写三选二） | 闭环末尾强制输出节 |
| Q3 | 源码集成模式 | **精瘦**（核心片段 + 路径引用 + delta 对比） | 无版权风险，课内保持可读 |
| Q4 | 模式选择策略 | 操作性且 ≥2 独立场景 → B；否则 A | SKILL.md §4.1 第 5 步补充 |
| Q5 | my_notes.md 位置 | `{session}/lessons/{lesson}_notes/my_notes.md` | 每课独立笔记文件 + photos/ + exercises/ |
| Q6 | 源码路径配置 | `settings/background.md` 新增 `source_code_root` | 可选字段，无则降级为 AI 虚构 |

---

## 一、背景与动机

### 1.1 用户发现的核心缺陷

> "现在的代码教程都太碎片化，东一块，西一块的，单看教程很难构建起我自己的知识体系。"

这个诊断精准——当前 `02.1_I2C 协议代码.md` 的结构问题：

- §3.2 讲 API 族选型决策树（抽象）
- §3.3 讲参数速查（进一步抽象）
- §3.4 讲 EEPROM（落到具体）
- §3.5 讲 OLED（落到具体）
- §3.6 讲 AHT20（落到具体）
- §4 渐进训练把 3 个外设混着出题

**问题**：学员必须在整课时长内**同时维持 3 个外设 + 1 个抽象 API 树的上下文**，认知负担指数级上升。

更深层的问题是——**输入完整 ≠ 输出能力**。当前结构优化的是"AI 讲得全"，没给学员"自己说一遍、画一遍、写一遍"的强制触发点。

### 1.2 用户提出的理想流程

> 具体场景 → 对应完整代码 → 代码解释 → 结合原理细剖析代码 → 训练反馈 → 生成独特笔记/形成循环

这是典型的**项目驱动学习**（Project-Based Learning）+ **费曼学习法**（Feynman Technique）组合。

费曼学习法核心：
1. 选一个概念
2. 用自己的话讲给"假想的孩子"听（**强制输出**）
3. 发现卡壳处 = 理解盲点
4. 回头重学 + 简化
5. 重复

**现有 Reflection 节**（§八）只是"主观难度评分"，没有强制输出——费曼没生效。

---

## 二、模式 A vs 模式 B 详细对比

### 2.1 何时用哪种

| 判断点 | 模式 A（知识结构） | 模式 B（场景闭环） |
|-------|-----------------|-----------------|
| 知识类型 | 概念性 / 原理性 / 单场景操作性 | 多场景操作性（≥ 2 独立外设/模块/API 族） |
| 场景数量 | 1 个 | ≥ 2 个独立可运行项目 |
| 典型例子 | `02.0_I2C 协议原理`（纯原理）<br>`09_Systick` （单场景） | `02.1_I2C 协议代码`（3 外设）<br>`14/15/16_UART 系列`（4 场景） |
| 生成者决策字段 | 元信息 `teaching_mode: A` | 元信息 `teaching_mode: B` |

### 2.2 AI 决策规则（写入 SKILL.md §4.1 第 5 步）

```
if 知识类型 in [概念性, 原理性]:
    teaching_mode = A
elif 知识类型 in [操作性, 程序性]:
    if len(独立场景) >= 2:
        teaching_mode = B    # 场景闭环
    else:
        teaching_mode = A    # 单场景也走 A
```

"独立场景" 定义：每个场景能被**独立烧板 / 独立运行 / 独立验证**。若 3 个外设共用同一 `main()` 串行调用，仍算 1 个场景；若 3 个外设各有独立 `main()` 工程，算 3 个场景。

---

## 三、模式 B 结构详细规范

### 3.1 整体骨架

```
§〇 知识导航（沿用模式 A）
§一 学习目标（沿用）
§二 知识回引（沿用）

§三 精讲 —— 场景闭环模式
  §3.0 全局图景（30 秒扫完，不求记住）
  §3.0.1 本课 = N 个独立可 ship 的场景闭环
  §3.0.2 共享基座：CubeMX 配置模板 + API 选型决策树（单页速查）
  §3.0.3 学习路径：可任选一环先学；学完即跳关

  §3.1 场景 1 闭环（如 EEPROM）
    §3.1.1 📖 场景（50 字）
    §3.1.2 💻 完整可运行代码（精瘦模式，源自 source_code_root）
    §3.1.3 🔍 逐部分解释（行号锚点，不重述代码）
    §3.1.4 🧠 原理剖析（侧重本环用到的知识）
    §3.1.5 🎯 渐进训练（基于本闭环代码变形，2-3 题）
    §3.1.6 🔴 Feynman 输出（B 档三选二）
    §3.1.7 🔵 闭环检查 + 独特笔记提示

  §3.2 场景 2 闭环（如 OLED，同构）
  §3.3 场景 3 闭环（如 AHT20，同构）

  §3.∞ 汇合升维
    §3.∞.1 跨环对比表（学员先填，AI 再批）
    §3.∞.2 复述 API 选型决策树（费曼第二轮）
    §3.∞.3 本课概念图（手绘/Mermaid 二选一，拍照或 md 提交）
    §3.∞.4 提出你的疑问（路由到 §七 思考模块）

§四 渐进训练（本节仅含跨环迁移题 1-2 道）
§五 掌握测试（新情境题，沿用模式 A）
§六 掌握度反馈（沿用）
§七 思考模块（沿用）
§八 Reflection（沿用）
§九 本节要点总结（沿用）
§十 下一课预告（沿用）
```

### 3.2 每闭环内部节细则

#### §X.1 场景（50 字硬限）

格式：
```markdown
> **场景**：{50 字以内的产品/问题描述}
>
> **硬件清单**：{芯片型号、连接表}
> **预期效果**：{学员烧板后能看到什么}
```

例（EEPROM 闭环）：
```markdown
> **场景**：产品上电时需要记住上次用户设置的亮度/音量，断电不丢失。
> **硬件**：STM32F103 + AT24C02 EEPROM（I2C1：PB6/PB7）
> **预期效果**：按 KEY1 修改数值并写入；重启后 OLED 显示上次保存的值。
```

#### §X.2 完整可运行代码（精瘦模式）

格式：
```markdown
> **源码来源**：`{source_code_root}/{project_dir}/{file_path}`
> **HAL 版本**：{从项目检测到的版本号}
> **下方为 happy path 核心片段（30-50 行）；完整文件请打开原工程**

```c
// [eeprom.c:15-42] 核心读写函数
{核心代码片段}
```

> **未展示部分**：
> - `eeprom.c:1-14`: 头文件、宏定义（`#define AT24C02_ADDR (0x50u << 1)`）
> - `eeprom.c:43-80`: 页边界循环写入封装（§X.4 原理剖析会展开讲）
> - `main.c`: CubeMX 生成的 init 与 while 循环（参考 §3.0.2 共享基座）
```

**禁止**：贴超过 60 行的完整文件；贴 AI 虚构的"示范代码"（与真源码冲突）。

#### §X.3 逐部分解释（行号锚点）

格式：
```markdown
**逐部分讲解**（基于 §X.2 代码的行号）：

| 行号 | 代码段 | 作用 | 原理对应 |
|------|-------|------|---------|
| 15-18 | `HAL_I2C_Mem_Write(...)` 调用 | 把 `data` 写入 EEPROM 地址 `addr` | §X.4.1 HAL 8 位地址约定 |
| 19 | `HAL_Delay(5)` | 等 EEPROM 擦写周期完成 | §X.4.2 Twr 物理约束 |
| 20-25 | 错误码分类处理 | 区分 `HAL_BUSY` / `HAL_TIMEOUT` / `HAL_ERROR` | §X.4.3 错误语义细分 |
```

**禁止**：在解释段重新粘贴代码；每行都重述代码作用（已在表中）。

#### §X.4 原理剖析（侧重式）

**关键约束**：只讲本闭环**用到的**原理，不再横向展开所有 API。

例（EEPROM 闭环的 §X.4 只讲）：
- 页边界 + 卷绕机制（与 OLED/AHT20 无关，其他闭环不讲）
- Twr 写周期（同上）
- HAL 8 位地址约定（三闭环共享，但首次在 EEPROM 闭环讲清，后面闭环引用即可）

### §X.5 渐进训练

基于本闭环代码做 **变形练习**，非抽象出题：
- 练习 1：跨页写 debug（把 §X.2 代码 `len=3` 改 `len=10`，预测+验证）
- 练习 2：把 §X.2 封装成 `EEPROM_Write_Safe(addr, data, size)`，内部自动切页

### §X.6 🔴 Feynman 输出（B 档三选二）

**硬约束**：学员必须从下面 3 项中至少完成 2 项；跳过 Feynman 不能进入下一闭环。

```markdown
### §X.6 🔴 Feynman 输出（三选二，至少完成 2 项）

**选项 a · 文字小结（必须 ≤ 80 字）**

用自己的话写出 "`{外设}` 驱动的 5 要素"：

```
1. {    }
2. {    }
3. {    }
4. {    }
5. {    }
```

**选项 b · 手绘拍照（推荐）**

手绘以下**任一**图，拍照保存到 `lesson_{N}_notes/photos/`：

- 选项 b1：EEPROM 页写时序图（SDA/SCL 波形 + 字节标记）
- 选项 b2：AT24C02 地址空间示意（8 页 × 8 字节，标注你理解的页边界）

> **拍照上传路径**：`learning-history/{topic}/lessons/lesson_{N}_notes/photos/{YYYY-MM-DD}_{选项}.jpg`
> **AI 批改**：AI 会读取图片，检查时序关键点是否标对（`S/ADDR/DATA/A/P/Sr`）。

**选项 c · 代码改写（高强度）**

把 §X.2 的原版代码改写为"带页边界保护"的封装函数，保存到 `lesson_{N}_notes/exercises/eeprom_safe_write.c`：

要求：
1. 函数签名：`HAL_StatusTypeDef EEPROM_Write_Safe(uint16_t addr, const uint8_t *data, uint16_t size)`
2. 内部自动检测并切页，不依赖调用者
3. 错误码透传（不吞错）
4. 写注释标注"这里对应 §X.4.{小节} 的原理"

> **AI 批改**：AI 会对比你的实现与参考实现，指出盲点。
```

#### §X.7 🔵 闭环检查 + 独特笔记

```markdown
### §X.7 🔵 闭环检查 + 独特笔记

**AI 对 Feynman 输出的批改反馈**（完成上节后 AI 追加）：

{ai_feynman_review_placeholder}

**你的独特笔记**（累积到 `{lesson}_notes/my_notes.md`）：

> 按以下模板在 `my_notes.md` 里追加一节——回到原课文已太累，笔记是你的第二大脑。

```markdown
## §X `{外设}` 闭环学到的

**3 个"啊原来如此"的时刻**：
1. ...
2. ...
3. ...

**我最容易错的 1 个点 + 如何避免**：
- ...

**跨章节链接**：这个闭环让我联想到 `{前课某概念}` / `{后续某课可能用到}`
```

**闭环检查不过的处置**：
- 若 AI 判定 Feynman 输出有明显盲点（如时序图关键信号画错、代码缺错误处理）→ 引导回 §X.3 / §X.4 重读对应小节
- 引导原则：**指出盲点 + 给出回读范围**，不直接给答案——保持费曼循环
```

---

## 四、Feynman B 档批改规范

### 4.1 AI 批改流程

```
1. 读取 learner 提交的 Feynman 输出：
   - 选项 a: my_notes.md 中 §X.6a 节的文字
   - 选项 b: lesson_{N}_notes/photos/*.jpg
   - 选项 c: lesson_{N}_notes/exercises/*.c

2. 对照 §X.2-X.4 的标准理解/代码，生成批改反馈：
   - 覆盖度：5 要素是否齐全
   - 准确度：时序图关键信号是否画对
   - 完整度：代码是否处理页边界/错误码/数据手册约束

3. 把反馈追加到 §X.7 🔵 闭环检查的 ai_feynman_review 位置

4. 判定 loop-back：
   - 覆盖度 < 60% 或 关键点画错 → 引导回 §X.3 重读
   - 覆盖度 60-80% → 指出具体盲点，可选择回读或直接进入下一闭环
   - 覆盖度 ≥ 80% → 通过，进入下一闭环

5. 同步更新 learner_model：
   - 按 concept_tag 记录本闭环的 mastery_level
   - 暴露的盲点 concept_tag → 加入 review_queue（与现有思考模块共享通道）
```

### 4.2 照片批改技术约束

- AI 必须能读取 `photos/*.jpg`（Windsurf 原生多模态支持）
- 识别目标：手绘时序图中的文字标签（`S`、`SDA`、`ACK` 等）
- 若识别失败（照片模糊 / 标签非标准）→ 请求学员补充文字说明，不强制重拍

---

## 五、源码集成规范（精瘦模式）

### 5.1 配置字段

在 `settings/background.md` 新增（可选）：

```markdown
## 源码参考（可选）

> 若本地有对应课程的完整工程源码，填入此字段，AI 会在生成操作性 lesson 时抽取真实代码。
> 留空则 AI 使用通用示范代码。

- source_code_root: /path/to/your/source-project
- source_material_md: /path/to/your/source-project/md  # 原版配套教程（可选，作为 AI context）
```

### 5.2 lesson 元信息新增字段

```yaml
teaching_mode: B                                       # A 或 B
scenario_closures:                                     # 仅 B 模式填
  - name: EEPROM
    source_project: 18-i2c-eeprom
    source_files:
      - Core/Src/eeprom.c
      - Core/Src/main.c
  - name: OLED
    source_project: 19-i2c-oled
    source_files:
      - Core/Src/oled.c
  - name: AHT20
    source_project: 20-i2c-aht20
    source_files:
      - Core/Src/aht20.c
```

### 5.3 AI 生成时的工作流

```
1. 读取 session 配置中的 `source_code_root`
2. 对每个 scenario_closures[i]：
   a. 解析 `{source_code_root}/{source_project}/{source_files}` 的实际内容
   b. 抽取"happy path 核心片段"（30-50 行，标注 [file:start_line-end_line]）
   c. 生成 §X.2 `完整可运行代码` 节
   d. 生成 §X.3 `逐部分解释` 表（基于实际行号）
   e. 对比 §X.2 原版 vs 生产级最佳实践，生成 delta 段（若有显著差异）
3. 若 `source_code_root` 不存在或读取失败：
   - 降级为模式 A（给出警告）
   - 或 AI 虚构代码（明确标注 "示范代码，非真实工程"）
```

### 5.4 禁止项

- ❌ 不粘贴超过 60 行的单段源码
- ❌ 不整段粘贴 CubeMX 生成的 `stm32f1xx_hal_msp.c` 这种模板文件
- ❌ 不隐匿源码来源（必须标注 `{file}:{start}-{end}`）
- ❌ 不修改原版代码然后冒充原版（改进版必须显式标注 "增强版"）

---

## 六、独特笔记规范

### 6.1 文件结构

```
learning-history/{topic}/lessons/
├── 02.1_I2C 协议代码.md                  ← 主课文（AI 生成）
└── 02.1_I2C 协议代码_notes/              ← 学员笔记目录
    ├── my_notes.md                        ← 主笔记（学员填 + AI 追加批改）
    ├── photos/                            ← 手绘拍照
    │   ├── 2026-04-18_eeprom_timing.jpg
    │   └── 2026-04-18_concept_map.jpg
    └── exercises/                         ← 代码改写
        ├── eeprom_safe_write.c
        └── oled_fullscreen.c
```

### 6.2 my_notes.md 模板

```markdown
# 02.1_I2C 协议代码 · 我的笔记

**最后更新**: {YYYY-MM-DD HH:mm}

---

## §3.1 EEPROM 闭环

### Feynman 输出

**a · 5 要素**：
1. ...
2. ...
...

**b · 手绘**：见 `photos/2026-04-18_eeprom_timing.jpg`

**c · 代码改写**：见 `exercises/eeprom_safe_write.c`

### AI 批改反馈

{ai_review_for_3.1}

### 我的独特笔记

**3 个"啊原来如此"的时刻**：
1. ...
2. ...
3. ...

**我最容易错的 1 个点 + 如何避免**：
- ...

**跨章节链接**：...

---

## §3.2 OLED 闭环

（同构）

---

## §3.3 AHT20 闭环

（同构）

---

## §3.∞ 汇合升维

### 跨环对比表（我的版本）

| 特性 | EEPROM | OLED | AHT20 |
|------|--------|------|-------|
| ...  | ...    | ...  | ...   |

### API 选型决策树（我的复述）

...

### 本课概念图

见 `photos/2026-04-18_concept_map.jpg` 或下方 mermaid：

```mermaid
{学员手写的 mermaid}
```
```

### 6.3 笔记的演化机制

- 每完成一闭环，学员在 my_notes.md 追加一节
- 学员复习时以 my_notes.md 为主，课文为辅（符合费曼"笔记是第二大脑"思想）
- 课程级 L4 概念图（设计文档 2026-04-18-thinking-module §3.4）生成时可抽取 my_notes.md 的"跨章节链接"段作为补充输入

---

## 七、与现有机制的交互

### 7.1 与思考模块（§七）

- 思考模块保留在模式 B 中，但定位从"主要输出"降为"扩展思考"
- 真正的主要输出在每闭环的 §X.6 🔴 Feynman
- §七.3 "你的问题" 依然有效，但预期密度下降（因为每闭环都有机会提问了）

### 7.2 与 learner_model

按 concept_tag 记录 Feynman 输出质量：

```json
{
  "concept_mastery": {
    "eeprom-page-write-boundary": {
      "mastery_level": "competent",
      "feynman_outputs": [
        {
          "lesson": "02.1",
          "closure": "EEPROM",
          "option": "c (code rewrite)",
          "quality": "high",
          "ai_feedback": "正确处理页边界，但未在函数注释中标注原理引用",
          "submitted_at": "2026-04-18T15:00:00+08:00"
        }
      ]
    }
  }
}
```

### 7.3 与 review_queue

Feynman 输出覆盖度 < 60% 的 concept_tag 自动加入复习队列：

```json
{
  "id": "review_051",
  "lesson": "02.1",
  "closure": "AHT20",
  "source": "feynman_gap",                  // 新枚举值
  "concept_tag": "aht20-crc-8-verification",
  "gap_reason": "Feynman 代码改写中遗漏 CRC 校验",
  "next_review_at": "2026-04-21",
  "status": "pending"
}
```

### 7.4 与 L3 章节综合图

`lesson-integration-test-template.md` 中的 Mermaid 图生成时可优先使用学员的 `my_notes.md` 中"本课概念图"段作为输入——学员自己画的图更贴合其认知网络。

---

## 八、模板文件改动清单

### 8.1 lesson-template.md

- 在现有 §三 上方加"讲解模式选择说明"元注释
- 把现有 §三 结构标注为 "模式 A（单场景 · 知识结构导向）"
- 新增 "模式 B（多场景 · 场景闭环导向）" 完整节（即本文档 §三 展示的结构）
- 新增 §X.6 Feynman 输出模板（三选二）
- 新增 §X.7 闭环检查 + 独特笔记模板
- 新增附录："精瘦模式源码引用格式"（即本文档 §五）
- 新增附录："my_notes.md 模板"（即本文档 §六.2）

### 8.2 SKILL.md

- §4.1 第 5 步：补充"操作性 lesson 的 A/B 模式选择规则"
- §4.2 第 2 步：补充"源码集成规则"（条件触发：`source_code_root` 存在 + `teaching_mode: B`）
- §4.2 新增：Feynman B 档生成规则（条件触发：`teaching_mode: B`）
- §4.3 新增：Feynman 批改规则（读取照片/代码改写，生成反馈，更新 learner_model）
- §4.5 自检清单新增：
  - 模式 B 是否每闭环完整 §X.1-X.7
  - 源码引用是否标注 `{file}:{start}-{end}`
  - Feynman 输出选项是否精确 3 项

### 8.3 settings/background.md 与 background.example.md

- 新增"源码参考"节（可选字段）
- 示例填写：`source_code_root: /path/to/your/source-project`

---

## 九、实施路径

### 阶段 A（本次会话）— 模板级改造

- **A.1** 起草本设计文档 ✅
- **A.2** 修改 `lesson-template.md` 引入模式 B 结构
- **A.3** 修改 `SKILL.md` 加模式选择 + 源码集成 + Feynman 批改规则
- **A.4** 修改 `settings/background.example.md` 和 `settings/background.md` 加 `source_code_root`
- **A.5** Commit + push

### 阶段 B（下次会话）— 试点验证

- **B.1** 用新模板重生成 `02.1_I2C 协议代码.md` 为 v2（接入航歌 18/19/20-i2c-*）
- **B.2** 学员试读，填入 Feynman 输出
- **B.3** AI 批改 + 追加反馈到 §X.7
- **B.4** 迭代模板（若 v2 暴露结构问题）

### 阶段 C（未来）— 批量推广

- **C.1** 回填其他多场景操作性课（SPI、CAN、UART 等）
- **C.2** 完善批改规则（photos OCR 失败 fallback、代码静态分析等）

### 阶段 D（可选）— 工程工具

- **D.1** `scripts/notes/init_notes_dir.py`：初始化 `lesson_{N}_notes/` 目录结构
- **D.2** `scripts/indexer/scan_source_code.py`：扫描 `source_code_root` 生成工程索引（加速 AI 抽取）

---

## 十、成功指标

实施后检验：

| 指标 | 目标值 | 数据源 |
|------|-------|--------|
| 模式选择正确率 | ≥ 95% 课 AI 按规则选 A/B | 扫描 lesson 元信息 `teaching_mode` |
| Feynman 完成率 | ≥ 70% 闭环有学员 B 档输出 | 扫描 `{lesson}_notes/` 目录 |
| 拍照选项参与率 | ≥ 30% 闭环有手绘拍照 | 扫描 `photos/` 目录 |
| Feynman 触发复习率 | ≥ 25% review_queue 条目来自 `feynman_gap` | review_queue.json |
| 学员自评"全局掌控感" | ≥ 4/5（Reflection 新增问题） | §八 Reflection |

---

## 十一、不做的事（划边界）

- ❌ 不强制所有课都用模式 B（概念性/原理性课保持模式 A）
- ❌ 不做"视频录讲"功能（C 档 Feynman 已否决）
- ❌ 不实现 photo 的自动 OCR 后端（依赖 Windsurf 多模态）
- ❌ 不在本阶段回填旧 session（与思考模块设计一致，新 session 享受新特性）
- ❌ 不自动烧板验证学员代码（硬件编程阶段由学员手动确认，AI 只做静态分析）

---

## 附录 A：模式 A vs 模式 B 完整示例

### 模式 A 当前（02.1 旧版节选）

```markdown
## 三、精讲

### 3.1 CubeMX 配置
### 3.2 API 总览与选型决策树
### 3.3 Mem_Write 参数速查
### 3.4 EEPROM 实战
### 3.5 OLED 实战
### 3.6 AHT20 实战

## 四、渐进训练（EEPROM + OLED + AHT20 混出）
## 五、反模式画廊
## 六、掌握测试
```

### 模式 B 新版（02.1 v2 大纲）

```markdown
## 三、精讲 —— 场景闭环模式

### 3.0 全局图景（30 秒 + CubeMX 基座 + 决策树速查）

### 3.1 EEPROM 闭环
  3.1.1 场景 / 3.1.2 代码 / 3.1.3 解释 / 3.1.4 原理
  3.1.5 训练 / 3.1.6 🔴 Feynman / 3.1.7 🔵 闭环检查

### 3.2 OLED 闭环（同构）
### 3.3 AHT20 闭环（同构）

### 3.∞ 汇合升维（跨环对比 + 决策树复述 + 概念图 + 思考模块入口）

## 四、跨环迁移练习（1-2 题，考察共性识别）
## 五、掌握测试（新情境，强化迁移）
...
```

---

## 附录 B：与 2026-04-18 思考模块设计的互补关系

| 设计 | 解决的问题 | 产物 |
|------|----------|------|
| 思考模块 + 知识图谱（已定稿） | 概念节点间的关系可视化 | 关键词网络、Mermaid 图 |
| 场景闭环 × Feynman（本文档） | 学员从"输入完整"到"输出能力" | 分闭环代码实战 + Feynman 强制输出 |

两者正交且互补：
- 思考模块在**概念维度**建网
- 场景闭环在**实践维度**建环
- 两者共享 `learner_model` + `review_queue`

---

## 十二、下一步

§〇·A 决策已锁定。执行：

1. ✅ 本设计文档定稿（2026-04-18）
2. ⏩ **当前进行**：阶段 **A.2** — 修改 `lesson-template.md`
3. 之后 A.3 → A.4 → A.5
4. 阶段 B 启动试点（下次会话）

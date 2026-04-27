## 总结判断：你感觉“冗杂、废话多”是对的

这批规则的底层思路其实很强：有资料转换、来源追踪、Worked Example、Faded Completion、检索练习、费曼输出、错题复习、学习者模型，方向都对。问题不在“缺少学习方法”，而在于**所有好方法被一次性塞进同一个 lesson 文件**，导致学习者面对的不是“教程”，而是“教程 + 教师教案 + 生成器控制规则 + 质检清单 + 状态协议 + 附录”的混合体。

最核心的矛盾是：

> 你想要“先让我学会”，但系统默认在生成“尽量完整、尽量可追溯、尽量不遗漏”的 deep 文档。

`learning-engine` 现在明确规定新 lesson 默认 deep-only，并且禁止新增 core/精华版；而 `core-lesson-rules.md` 恰恰是为“短、顺、像懂行朋友讲明白”而设计的，但被标为旧版兼容文档，不再作为默认流程使用。这个冲突就是教程变长的根因之一。 

---

## 一、当前这批规则最好的地方

你现在的系统不是“烂”，而是“过度工程化”。它有几个很值得保留的点。

第一，**资料转换链路比较扎实**。`everything-to-markdown` 已经要求把 PDF、图片、Office、网页等转成 Markdown，并在转换后用 `markdown-refiner` 做标题层级、OCR 噪声、表格公式等质量检查，而且这是阻塞门控。这个方向对，因为源资料脏，后面的教学就会跟着脏。

第二，**学习方法选得基本正确**。`lesson-template.md` 里有 Worked Example、渐进训练、掌握测试、费曼输出、反模式画廊、代码锚点映射等，这些都不是废招。比如检索练习和间隔练习在学习科学里属于高价值策略，Dunlosky 等人的综述把 practice testing 和 distributed practice 评为高效学习方法；2021 年的十大学习技术元分析也认为 distributed practice 和 practice testing 最有效。([Westsächsische Hochschule Zwickau][1])

第三，**代码课的“为什么这样写”意识很强**。你要求代码块后接“代码符号 → 对应原理 → 反事实后果”，还要求反模式画廊，这比普通教程只贴代码好很多。问题是它应该被“压缩成关键锚点”，而不是每段代码都上完整表格。

第四，**旧 core 规则已经接近你真正想要的教程风格**。它强调“精华版不是摘要，而是重新讲一遍”，并要求用因果链、类比、反事实、Mid-check、出口任务来组织一篇 20 分钟可读完的教程。它还明确要求从 deep 蒸馏到 core 时砍元信息、砍大量练习、砍附录、砍完整代码，只保留 happy path 和心智模型。 

---

## 二、真正导致“长、散、废话多”的 6 个根因

### 1. deep-only 默认策略和“先学会”的目标冲突

`learning-engine` 明确写了“默认 deep”“禁止新增 core”“新 lesson 默认使用 lesson-template.md”。这会让系统天然倾向生成完整教学档，而不是学习入口。

但学习者第一次接触一个知识点时，最需要的是：

> 先建立心智模型 → 做一个小题确认 → 再决定要不要深挖。

不是一上来就看“知识导航、学习目标、回引、精讲、训练、测试、反馈、思考、反思、总结、术语表、预告、附录”。

### 2. learner-facing 和 machine-facing 混在同一个文档里

`lesson-template.md` 里既有学生要读的正文，也有生成器提示、模式选择说明、附录规则、命名约定、图表路径规则、notes 目录规则。这些内容对 AI 生成有用，但对学习者是噪声。模板里甚至同时放了 A 模式和 B 模式，再要求生成时删除另一个分支。

这会造成两个问题：

一是生成器容易残留模板痕迹；二是即使删除了未选分支，lesson 仍然有“制度感”，不像教程。

### 3. “防遗漏清单”被放进了学习正文

`learning-engine` 的 deep 章节生成契约要求先做“源文位置 → 本课落点 → 必须掌握到什么程度”的覆盖表，并放入 `## 〇、知识导航`；还要求 §三覆盖源文覆盖表的每个条目，每个核心点至少回答“考什么、怎么理解、为什么这样、容易错在哪、题里怎么出现”。

这个规则用于防止漏讲是对的，但它不应该全部进入学习者主文档。它更适合放到：

```text
source_coverage.md
```

或 lesson 的隐藏 sidecar。学习者只需要知道“本节你要能解决什么问题”，不需要先看一张审计表。

### 4. B 模式闭环太重

B 模式每个场景闭环都要求 7 个子节：场景、完整可运行代码、逐部分解释、原理剖析、渐进训练、费曼输出、闭环检查与独特笔记；如果一个 lesson 有 3 个闭环，就是 21 个子节，还没算 3.0 全局图景和 3.∞ 汇合升维。

这不是一节课，这是一个小专题课程包。

更好的做法是：

> 多场景不要塞进一篇 lesson。每个场景单独一张“闭环卡”，最后再生成一篇“横向对比卡”。

### 5. 所有学习活动同时出现，反而削弱学习

当前 deep 模板里有渐进训练、掌握测试、思考模块、Reflection、总结、术语表。单独看都合理，但放在同一个文档中，学习者会产生“任务恐惧”：还没学完正文，就看到后面一堆要填的东西。`lesson-template.md` 后半段从训练、测试、反馈、思考、Reflection 到总结和附录，形成很长的尾部。

学习科学支持 retrieval practice、self-explanation、teaching、drawing、mapping，但这些活动应该分布到学习流程中，而不是堆在一页里。Agarwal 等人的课堂研究综述发现 retrieval practice 在不同教育层级、内容领域和测试延迟条件下都有学习收益；Fiorella 和 Mayer 也把 self-testing、self-explaining、teaching、drawing 等列为促进生成式学习的策略。([pdf.poojaagarwal.com][2])

### 6. “难”被错误地加在了阅读负担上

Bjork 的“desirable difficulties”讲的是让学习者进行检索、辨析、迁移、生成，而不是让他读更长的文档。当前模板的问题是：真正有价值的困难，例如迁移题、费曼解释、错误辨析，被包在大量制度性段落里，变成了“读完很累”。Bjork & Bjork 指出，短期表现变好不等于长期学习，真正有用的挑战会降低表面流畅感但提升长期保持与迁移。([比约克学习与遗忘实验室][3])

你的教程现在的问题不是“不够难”，而是**难点放错地方**：难在读文档，不是难在思考。

---

## 三、最重要的改法：从“Deep Lesson”改成“三层产物”

我建议不要简单恢复旧 core，也不要继续 deep-only。应该改成：

```text
1. learn-card.md        学习入口，短，先学会
2. practice-pack.md     练习包，按需打开
3. reference-deep.md    资料追溯与完整细节，查阅用
```

也就是：

> 主文档负责学习，练习文档负责训练，deep 文档负责查证。

这会立刻解决“太长、不利于学”的问题。

### 新默认流程

| 阶段    | 生成物                       | 目标                 | 长度建议     |
| ----- | ------------------------- | ------------------ | -------- |
| 第一次学习 | `NN_主题.learn.md`          | 建立心智模型，能做一道题       | 80–150 行 |
| 练习巩固  | `NN_主题.practice.md`       | 检索、迁移、改错           | 3–6 题    |
| 深挖查阅  | `NN_主题.deep.md`           | 来源覆盖、完整代码、完整图表、术语表 | 按需生成     |
| 复习    | `review_queue.json` + 小卡片 | 间隔复习               | 每次 2–3 题 |

这样，deep 仍然存在，但不再挡在学习者面前。

---

## 四、建议你直接改掉的规则

### 改 1：把 deep-only 改成 learn-first

现在规则是：

```text
默认 deep，禁止新增 core。
```

建议改成：

```markdown
## 输出策略：learn-first

默认先生成 `learn` 版，而不是 deep 版。

- `learn`：学习入口，短文档，帮助学习者第一次学会。
- `practice`：练习包，完成 learn 后生成或附带生成。
- `deep`：只有在用户要求“展开 / 深入 / 查来源 / 看完整代码”时生成。

禁止把元信息、状态协议、图表路径规则、完整来源覆盖表放入 learner-facing 的 `learn` 文件。
```

这条是最高优先级。只要 deep-only 不改，后面怎么优化都会反弹。

### 改 2：把“源文覆盖表”移出正文

保留源文覆盖表，但移动到：

```text
source_coverage.md
```

learn 文档只保留一句：

```markdown
本节只解决一个问题：{核心问题}
```

deep 文档或 source_coverage 才记录：

```markdown
| 源文位置 | 本课落点 | 掌握要求 |
```

这样不会牺牲可追溯性，但学习者不用先读审计表。

### 改 3：把 lesson-template 拆成 4 个模板

现在 `lesson-template.md` 粗略统计有一千行左右，且包含大量占位符和附录规则。建议拆成：

```text
templates/
├── learn-card-template.md          # 学习者第一入口
├── practice-pack-template.md       # 训练与测试
├── deep-reference-template.md      # 完整讲解与来源追踪
└── generator-rules.md              # AI 生成规则，不给学生看
```

学生只接触前两个。AI 和质检才接触后两个。

### 改 4：B 模式不要“一篇包多个闭环”

现在 B 模式每个闭环 7 节，很容易爆炸。建议改为：

```text
02.1A_EEPROM.learn.md
02.1B_OLED.learn.md
02.1C_AHT20.learn.md
02.1X_I2C场景对比.learn.md
```

每个闭环卡只讲一个可运行场景。横向对比单独成卡。

这样比一篇大文档更符合认知负荷理论。认知负荷理论强调工作记忆容量和持续时间有限，教学设计要降低无关负荷，并根据学习者已有知识调整呈现方式。([科学直通车][4])

### 改 5：代码锚点表从“每段必有”改成“关键 3 锚点”

当前规则要求每段 ≥3 行关键代码块后都接映射表。这个容易把代码课变成表格课。

建议改成：

```markdown
每个核心代码片段只保留 3 个锚点：
1. 最容易写错的参数
2. 最关键的 API 选择
3. 最致命的边界条件

其余锚点进入 deep-reference。
```

旧 core 规则其实已经有类似思路：精华版不要完整三列表，改为就地用 1–2 句白话标注关键行；反模式画廊也改成内嵌“血的教训”。

---

## 五、我建议的新 learn-card 模板

这是我认为最适合你当前系统的主模板：

````markdown
# {主题}：{本节真正要解决的问题}

**建议用时**：{8-15 分钟}  
**学完你能做什么**：{一个具体任务，不超过 25 字}

---

## 1. 先猜一下

{给一个小问题 / 常见错误 / 现象}

> 先别看答案，想 30 秒：你觉得为什么会这样？

---

## 2. 一句话心智模型

**{核心金句}**

{用 1 个类比或 1 条因果链讲明白。不要堆定义。}

---

## 3. 最小机制

只讲 3 件事：

1. **{机制 1}**：{为什么需要它}
2. **{机制 2}**：{它怎么工作}
3. **{机制 3}**：{不用它会出什么错}

---

## 4. 看一个最小例子

```{language}
{10-25 行以内的核心代码或核心例题}
````

**三个关键锚点**：

| 锚点           | 为什么重要 | 写错会怎样 |
| ------------ | ----- | ----- |
| `{anchor_1}` | {原因}  | {后果}  |
| `{anchor_2}` | {原因}  | {后果}  |
| `{anchor_3}` | {原因}  | {后果}  |

---

## 5. 血的教训

❌ 常见错法：

```{language}
{错误代码 / 错误说法}
```

为什么错：{一句话解释}

✅ 正确想法：{一句话纠正}

---

## 6. 你来做

### 小题 1：补一步

{题目}

**我的答案**：

{    }

### 小题 2：换个场景

{迁移题}

**我的答案**：

{    }

---

## 7. 80 字复述

不用术语堆砌，用自己的话说明：

> {本节核心问题}

**我的复述**：

{    }

---

## 想继续深入？

* 看完整来源：`{topic}.source_coverage.md`
* 做更多题：`{topic}.practice.md`
* 看完整 deep：`{topic}.deep.md`

````

这个模板保留了学习科学里最有价值的部分：先预测、再讲解、看例子、自我解释、检索练习、迁移练习。但它不把所有东西一次性摊开。Worked examples 和逐步淡出练习本来就是为了帮学习者从“看懂示范”平滑过渡到“自己解题”；Renkl/Atkinson 的 worked-example fading 研究就是围绕这个过渡设计展开的。:contentReference[oaicite:16]{index=16}

---

## 六、具体删减清单

你现在最应该砍的是这些：

| 当前内容 | 处理方式 |
|---|---|
| `**时间** / **目标认知层级** / **知识类型** / concept_tags` | 移到 frontmatter 或 `session_state.json`，不要给学生看 |
| `〇、知识导航` 里的完整源文覆盖表 | 移到 `source_coverage.md` |
| `一、学习目标` | 改成一句“学完能做什么” |
| `二、知识回引` | 最多 3 行，只回引真正必要的前置概念 |
| `代码锚点映射表` | 每个核心代码最多 3 个锚点 |
| `反模式画廊` | learn 版只保留 1 个最致命错误 |
| `四、渐进训练` | learn 版只保留 1–2 题，完整训练放 practice |
| `五、掌握测试` | 移到 practice |
| `六、掌握度反馈` | 批改后追加，不在初始文档里占位 |
| `七、思考模块` | 改成“80 字复述 + 1 个疑问” |
| `八、Reflection` | 缩成 1 行：难度 1–5 + 卡点 |
| `九、术语表 / 关系图` | deep 或 glossary |
| `十、下一课预告` | 改成 2–3 个 next actions |
| 附录 B/C | 不进入学生主文档 |

这不是“降低质量”，是把学习顺序理顺。

---

## 七、学习方法上的新思路

### 1. 用“先失败 2 分钟”替代长铺垫

每节开头给一个小问题，让学习者先猜。比如：

```markdown
你觉得 `0x50` 作为 I2C 地址传给 HAL 可以吗？
````

然后再讲为什么错。

这叫 problem-solving before instruction 或 productive failure 的思路：先让学习者暴露已有想法，再由教师整合、纠正、建模。Sinha 和 Kapur 的综述把 productive failure 归入“问题解决后教学”的设计范式，核心是先让学生生成解法，再由教师进行 consolidation。([Sage Journals][5])

注意：这不是让新手硬啃难题。题要小，失败要可控。

### 2. 用“错因驱动”写教程

普通教程顺序是：

```text
正确概念 → 正确做法 → 常见错误
```

更适合你的代码/工程类教程的是：

```text
常见错误 → 为什么错 → 正确心智模型 → 最小代码
```

这样更像真实学习，因为学习者最关心的是：“我为什么这里老错？”

### 3. 把费曼输出降噪

现在 B 模式要求三选二：文字、手绘、代码改写。这个很好，但对每个闭环都做太重。建议 learn 版只保留一个轻量费曼：

```markdown
用 80 字解释给一个没学过的人听。
```

practice 版再提供手绘和代码改写。

ICAP 框架把学习参与分成 Passive、Active、Constructive、Interactive，并预测参与程度越高，学习收益越高。费曼、自我解释、画图都属于 constructive/interactive 方向，但前提是负担可承受。([ERIC][6])

### 4. 用“检索复习队列”替代一篇文档塞满测试

检索练习最好分布到时间里，而不是全放在课后。建议每个 learn 版只出 1–2 个题，剩下进入：

```json
review_queue.json
```

后续隔 1 天、3 天、7 天自动抽 2–3 题。这样比一口气做完更适合长期保持。Agarwal 等人的综述指出，retrieval practice 在真实课堂研究中也有稳定收益；Dunlosky 的综述和 2021 元分析也都支持 practice testing 与 distributed practice 的高价值。([pdf.poojaagarwal.com][2])

### 5. 用“信号标注”替代大段解释

Mayer 的多媒体学习研究里，signaling 能帮助学习者抓住结构，降低理解成本。对你的 Markdown 教程来说，signaling 可以是：

```markdown
**关键判断**：
**容易错**：
**一句话记住**：
**反事实**：
```

不要写长段“本节目标是……通过……建立……”。直接给信号。Mayer 的研究综述中提到，带信号标注的文本或叙述在迁移测试中表现优于无信号版本。([jsu.edu][7])

---

## 八、一个更狠的“废话过滤器”

建议你在 `lesson_lint.py` 或生成后自检里加入这些规则：

### 1. 段落功能检测

每个段落必须属于以下 6 类之一：

```text
WHY：为什么需要
WHAT：是什么
HOW：怎么做
FAIL：错了会怎样
EXAMPLE：例子
CHECK：让学生输出
```

不属于这 6 类的段落，删。

### 2. 主文档长度门控

```text
概念型 learn：≤ 120 行
代码型 learn：≤ 180 行
多场景专题：拆卡，不允许单篇超过 220 行
```

超过就必须拆，不允许“再优化一下继续塞”。

### 3. 新术语预算

每张 learn-card 最多引入：

```text
核心术语 ≤ 5 个
API / 函数 ≤ 4 个
表格 ≤ 2 张
代码块 ≤ 2 个
图 ≤ 1 张
```

超出就拆课。

### 4. 答案暴露控制

learn 版不要塞太多 `<details>` 标准答案。标准答案会让学习者提前看，削弱检索效果。建议：

```text
learn：只放题，不放答案
practice：可放折叠答案
AI 批改：读取用户答案后再给反馈
```

### 5. “空话词”禁用

生成后自动查这些词：

```text
非常重要
广泛应用
深入理解
系统掌握
打下基础
提高能力
具有重要意义
```

出现后要求替换为具体后果。例如：

```text
❌ 这是一个非常重要的概念。
✅ 写错这个地址，HAL 会访问另一个设备，表现为 NACK 或 HAL_ERROR。
```

---

## 九、针对你这四个文件的改造建议

### `SKILL(2).md` / everything-to-markdown

保留。它的问题不大。建议新增一步：

```markdown
## 转换后学习化处理

在 markdown-refiner 后追加 `learning-material-sanitizer`：

1. 删除页眉页脚、版权页、目录噪声
2. 抽取核心标题树
3. 抽取公式 / 表格 / 图片索引
4. 生成 `source_atoms.json`
5. 标记每个 atom 的类型：概念 / 例题 / 公式 / 代码 / 图 / 练习
```

也就是说，转换出来的不是直接给 learning-engine，而是先变成“学习原子”。

### `lesson-template.md`

这是最该拆的。现在它承担了太多职责。建议只保留 deep-reference 版，不再作为默认 lesson 模板。

新的默认模板应该是 `learn-card-template.md`。

### `core-lesson-rules.md`

不要丢。它是最接近你想要的东西。但不要叫 legacy core，建议重命名为：

```text
reader-first-lesson-rules.md
```

并把它从“旧版兼容”改成“默认学习入口规则”。它里面的 DROP/KEEP 表非常有价值，尤其是“删元信息、删完整训练、删附录、保留心智模型、类比、反事实、Mid-check、出口”这一套。

### `SKILL(3).md` / learning-engine

这是系统总控，必须改默认策略。核心改动是：

```text
Step 4.1 不再确认 deep-only
改成确认 learn-first
```

并增加：

```markdown
若用户说“太冗杂 / 想快学 / 先讲明白 / 不要废话”，强制进入 learn-first，不得生成 deep。
```

---

## 十、我建议的最终结构

你可以把整个系统改成这样：

```text
输入资料
  ↓
everything-to-markdown
  ↓
markdown-refiner
  ↓
learning-material-sanitizer
  ↓
source_atoms.json
  ↓
learning-engine
  ├── learn-card.md        # 默认生成，短
  ├── practice-pack.md     # 练习，按需
  ├── deep-reference.md    # 深入，按需
  ├── source_coverage.md   # 防遗漏，给 AI / 老师看
  └── review_queue.json    # 间隔复习
```

学生第一次只打开：

```text
learn-card.md
```

这才是“学”。

---

## 十一、最小落地版本：先改 5 条就会明显变好

你不需要一次大改。先做这 5 条，教程马上会短很多：

1. **取消默认 deep-only**：默认生成 learn-card。
2. **源文覆盖表移出正文**：放到 `source_coverage.md`。
3. **lesson-template 拆分**：学生模板和生成器规则分离。
4. **每课只解决一个核心问题**：多场景拆多卡。
5. **主文档只保留 1 个例子 + 1 个错误 + 2 个小题 + 80 字复述**。

这 5 条比继续微调语气更有效。

---

## 十二、一句话版新原则

我建议你把教程生成系统的最高原则改成这句：

> **第一遍学习不是覆盖资料，而是建立可迁移的心智模型；覆盖资料是 deep/reference 的任务。**

当前系统太像“把资料讲全”。你真正想要的是“先让我会”。这两个目标都重要，但必须分成不同文件。

[1]: https://www.whz.de/fileadmin/lehre/hochschuldidaktik/docs/dunloskiimprovingstudentlearning.pdf "PPI453266.indd"
[2]: https://pdf.poojaagarwal.com/Agarwal_etal_2021_EDPR.pdf "Retrieval Practice Consistently Benefits Student Learning: a Systematic Review of Applied Research in Schools and Classrooms"
[3]: https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/04/EBjork_RBjork_2011.pdf "CH05.qxp:FABBS_DESIGN_NE"
[4]: https://www.sciencedirect.com/science/article/pii/S1041608024000165 "Cognitive load theory and individual differences - ScienceDirect"
[5]: https://journals.sagepub.com/doi/10.3102/00346543211019105 "When Problem Solving Followed by Instruction Works: Evidence for Productive Failure - Tanmay Sinha, Manu Kapur, 2021 "
[6]: https://eric.ed.gov/?id=EJ1044018 "ERIC - EJ1044018 - The ICAP Framework: Linking Cognitive Engagement to Active Learning Outcomes, Educational Psychologist, 2014"
[7]: https://www.jsu.edu/online/faculty/MULTIMEDIA%20LEARNING%20by%20Richard%20E.%20Mayer.pdf "PII: S0079-7421(02)80005-6"

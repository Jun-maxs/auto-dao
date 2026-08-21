# 2026-04-24 · 教程生成体系深度优化报告

> 范围：本报告基于本仓库的实际代码、skills、模板、历史会话与发布链路分析生成。
> 目标不是再增加一层提示词，而是把已有的优秀教学设计变成可验证、可迁移、可持续迭代的教程生成系统。

---

## 一、总体判断

当前体系已经具备很强的教学设计基础：它不是简单的“把资料总结成 Markdown”，而是一个由资料预处理、学习会话、知识路线、core/deep 分层、前置诊断、Feynman 输出、错题复习、语料索引、公开发布组成的完整生成链路。

真正的瓶颈不在“缺少想法”，而在三个层面：

| 层面 | 当前状态 | 核心风险 |
|------|---------|---------|
| 规则层 | `SKILL.md` 和模板已经非常丰富 | 规则太多但缺少机器校验，AI 容易漏执行 |
| 状态层 | 已建立 `session_state.json` 权威源理念 | schema、模板、真实会话、校验脚本已经漂移 |
| 产物层 | core 版可读性显著提升，deep 版信息量足 | core/deep、答案流、发布流和状态流还没有完全闭环 |

**一句话结论**：下一阶段应从“提示词增强”转向“契约化工程”，把教程生成体系拆成可校验的 state contract、lesson contract、publish contract、review contract。

---

## 二、当前链路复盘

### 2.1 生成主链路

当前设计中的教程生成链路可以归纳为：

```text
学习资料
  ↓
Step 1 预处理：格式判断 / MinerU 转 Markdown / markdown-refiner
  ↓
Step 2 初始化与历史检索：topic 提取 / 历史会话匹配 / 知识图谱检测
  ↓
Step 3 会话恢复：session_state + summary + roadmap + course_overview
  ↓
Step 4 教程生成：core 默认 / deep 按需 / A-B teaching_mode / Feynman
  ↓
Step 4.3 批改：读取文件答案 / 掌握判定 / learner_model 更新
  ↓
Step 4.5 状态更新：summary / roadmap / ai_context / metrics / review_queue
  ↓
Step 5 报告：report.md / 可选工程产物
  ↓
发布：publish_lesson.py → published/ → MkDocs → docs.yuanai.best
```

### 2.2 已经做得好的部分

| 能力 | 现有资产 | 价值 |
|------|---------|------|
| 文件驱动学习 | `learning-history/`、`session_state.json`、lesson 文件 | 降低幻觉，让学习过程可追溯 |
| core/deep 分层 | `core-lesson-rules.md`、`lesson-template.md` | 解决“deep 太长、先给我核心模型”的体验问题 |
| 操作课闭环 | teaching_mode B、scenario_closures、Feynman 三选二 | 很适合 STM32/嵌入式这种“看懂不等于会做”的课程 |
| 前置诊断 | `diagnostic_grader.py`、`prereq_analyzer.py` | 能按掌握度和自信偏差调整路径 |
| 语料索引 | `scripts/indexer/` | 为跨资料引用、图片引用、前置覆盖提供基础 |
| 发布管线 | `publish_lesson.py`、`mkdocs.yml`、部署 workflow | 已经从私有学习空间走向公开知识库 |

---

## 三、关键问题与优化建议

## P0：先修“状态契约”，否则后续自动化都会漂移

### P0-1：schema 版本已经断裂

**证据**

| 文件/命令 | 现象 |
|----------|------|
| `.claude/skills/learning-engine/templates/session-state-template.json` | `schema_version` 是 `2.3` |
| `.claude/skills/learning-engine/templates/session-state.schema.json` | 仍然要求 `const: "2.2"` |
| `python scripts/session/init_session.py ...` 后再跑 `validate_state.py` | 新会话直接失败：expected `2.2`, got `2.3` |
| `python -m pytest tests/test_init_session.py tests/test_validate_state.py -q` | 2 个失败，均由 `2.2` vs `2.3` 引起 |

**影响**

新会话初始化、历史会话恢复、CI 质量门都会变得不可信。更严重的是，`session_state.json` 被设计为权威源，但权威源自身的 schema 不再权威。

**建议**

1. 立即统一 schema 到 `2.3`，并补齐 `current_mode`、`lesson_files_core`、`lesson_files_deep`、`mode_switch_log` 字段。
2. 同步更新 `tests/test_init_session.py`、README 故障排查、示例 `golden-example`。
3. 新增 `scripts/session/migrate_state.py`，支持从 `2.0/2.1/2.2` 迁移到 `2.3`。
4. 迁移脚本必须支持 `--dry-run`、自动备份、输出 diff 摘要。

---

### P0-2：`validate_state.py` 还不理解 core/deep 分层

**证据**

`004_embedded-software-designer` 会话实际有：

```json
"current_mode": "core",
"lesson_files_core": ["core/01_嵌入式硬件基础精华版.md"]
```

但 `validate_state.py` 仍主要按旧字段 `lesson_files` 或 `lesson_1.md` 解析，因此对 core 文件路径判断失败。

**影响**

core/deep 分层越成功，旧校验器越容易误报；反过来，真实漂移也可能被漏报。

**建议**

重构 lesson 解析逻辑为统一 resolver：

```text
resolve_active_lesson(state, lesson_index):
  1. 若 current_mode == core，查 lesson_files_core[index-1]
  2. 若 current_mode == deep，查 lesson_files_deep[index-1]
  3. 若 lesson_variants 有 active，优先 active
  4. 兼容旧 lesson_files
  5. 最后回退 lesson_N.md
```

同时新增校验项：

| 校验项 | 目的 |
|--------|------|
| `current_mode` in `core/deep` | 防止拼写漂移 |
| core 文件必须在 `lessons/core/` | 强制目录隔离 |
| deep 文件必须在 `lessons/deep/` 或兼容 legacy 根目录 | 平滑迁移旧会话 |
| `lesson_files_core/deep` 不允许无意义 `null` 占位，或 schema 明确允许 | 避免数组索引语义混乱 |
| `lesson_variants.active` 必须真实存在 | 解决 003 会话中 v2 文件不存在但状态引用的问题 |

---

### P0-3：真实会话状态与文件系统已经明显漂移

**证据**

`003_stm32f103-hal` 目录下已生成 15 个 lesson 文件，但 `session_state.json` 仍显示：

```json
"current_lesson": 1,
"last_completed_lesson": 0,
"lesson_variants": {
  "02.1": {
    "active": "02.1_I2C 协议代码_v2.md"
  }
}
```

而实际 `lessons/` 下没有 `02.1_I2C 协议代码_v2.md`，只有 `02.1_I2C 协议代码.md`。

**影响**

AI 恢复会话时会读错 lesson、错判进度、错生成下一课。长期看，`summary.md`、`roadmap_status.md`、`session_state.json` 会变成三套各说各话的历史。

**建议**

新增 `scripts/session/reconcile_state.py`：

| 模式 | 行为 |
|------|------|
| 默认只读 | 扫描 session，输出文件系统 vs state 差异 |
| `--fix-lesson-files` | 自动修复不存在的 active variant，或降级到存在的 legacy 文件 |
| `--fix-progress` | 根据 roadmap 和 lesson 文件推断 `current_lesson/last_completed_lesson`，需人工确认 |
| `--write-audit` | 把修复记录写入 `reset_log` 或新的 `state_repair_log` |

---

### P0-4：`wait_reason` 被业务化字符串污染

**证据**

`004` 会话中：

```json
"wait_reason": "waiting_for_user_answer_L01"
```

但 schema 只允许：

```text
awaiting_answer / awaiting_grading / awaiting_user_choice / null
```

**建议**

保留 `wait_reason` 为枚举，不承载业务细节。新增：

```json
"wait_detail": {
  "lesson_id": "01",
  "mode": "core",
  "message": "waiting_for_user_answer_L01"
}
```

这样既能被机器稳定判断，又能保留人类可读上下文。

---

### P0-5：Windows 控制台编码会让 CLI 直接崩溃

**证据**

直接运行 `init_session.py` 时，在 GBK 控制台下因打印 `✅` 出现 `UnicodeEncodeError`。`scripts/ci/check_examples.py` 已经做了 `sys.stdout.reconfigure(encoding="utf-8")`，但其他脚本没有统一处理。

**建议**

抽出通用工具：

```python
def ensure_utf8_stdio() -> None:
    ...
```

应用到：

| 脚本 | 原因 |
|------|------|
| `scripts/session/init_session.py` | 会打印 emoji |
| `scripts/session/validate_state.py` | 会打印 pass/fail 标记 |
| `scripts/session/schedule_review.py` | 会打印 `✅`、`📋` |
| `scripts/publish_lesson.py` | 会打印中文和 emoji |
| `.claude/skills/everything-to-markdown/scripts/convert_to_markdown.py` | 会打印中文进度 |

---

## P1：把“教学规则”变成“Lesson Lint”

### P1-1：当前规则很多，但缺少生成后机器质检

`SKILL.md` 和 `core-lesson-rules.md` 已经定义了大量好规则，例如：

| 规则 | 位置 |
|------|------|
| core 版不允许元信息头 | `core-lesson-rules.md` |
| core 版必须有 FAQ、Mid-check、结尾出口 | `core-lesson-rules.md` |
| core 图片路径必须用 `../../images/` | `core-lesson-rules.md` |
| deep B 模式必须创建 notes 目录 | `lesson-template.md` |
| 操作课代码必须有锚点映射 | `SKILL.md` |
| 禁止让用户在对话中发送答案 | `SKILL.md` |

但这些目前主要靠 AI 自觉执行。

**建议新增**

```text
scripts/lesson_lint.py
```

第一期规则：

| 检查 | 说明 |
|------|------|
| unresolved placeholder | 禁止残留 `{concept_tags}` 这类具名占位符，允许 `{    }` 和 `{_____}` |
| file-driven violation | 禁止 core/deep lesson 出现“直接发给我”“在聊天里回答”等 |
| image path | core 用 `../../images/`，legacy/deep 根目录用 `../images/` |
| source marker | deep 中资料引用必须保留来源或节尾参考 |
| core structure | FAQ、第一幕、Mid-check、出口检查题/Next-step menu |
| deep B structure | scenario_closures、notes_dir、my_notes、photos、exercises |
| code block length | core 单段代码不超过 15 行，deep 精瘦源码不超过 60 行 |
| answer slot | 正式需要批改的题必须有文件内答案区 |

第二期规则：

| 检查 | 说明 |
|------|------|
| Bloom alignment | 题目是否真的对应声明的 Bloom 层级 |
| duplicate exercise | 练习题是否只是换皮重复 |
| weak source evidence | 资料外补充是否缺少 `[⚠️ 当前资料未涉及此内容]` |
| glossary alignment | `concept_tags` 与 `settings/glossary.md` 是否一一对应 |

---

### P1-2：core 版与“文件驱动原则”发生冲突

**证据**

`SKILL.md` 明确禁止“让用户在对话中发送答案”，但 `core-lesson-rules.md` 和真实 core 产物里有：

```text
你直接按编号回答即可，我会根据你的答案继续带你往下学。
写完答案直接发给我
```

**影响**

core 版越像“朋友带路”，越容易回到聊天式问答，从而破坏整个系统的文件驱动优势。

**建议**

把 core 结尾改成文件驱动格式：

```markdown
## 你现在先完成 5 个检查题

请在下面的“我的答案”区填写。保存文件后，在对话窗口告诉我“已完成”。

### 题 1

...

**我的答案**：

{    }
```

Next-step menu 中也要改：

```text
想让我批改你刚才的 5 道检查题 —— 请先在本文件答案区填写，保存后告诉我“已完成”
```

---

### P1-3：deep 版产物过长，信息量强但复习成本高

**证据**

`003_stm32f103-hal` 中多个 deep lesson 行数已经很高：

| 文件 | 行数 |
|------|------|
| `02.1_I2C 协议代码.md` | 940 |
| `06.1_图片显示代码.md` | 1382 |
| `06.2_图片显示实验.md` | 921 |

**建议**

引入“lesson budget contract”：

| 类型 | 建议上限 | 超出后动作 |
|------|---------|-----------|
| core 单篇 | 150 行 | 砍内容，不拆 |
| core 综合篇 | 250 行 | 最多拆 2 篇 |
| deep A 单课 | 500 行 | 拆成 `.0/.1` |
| deep B 多场景课 | 每闭环 220 行，总计 700 行 | 超出则拆成多个闭环文件 |
| cheatsheet/速查 | 300 行 | 改为表格索引 + 外链 deep |

同时生成 `lesson_index.md`，让长 deep 课变成可导航资料，而不是一整块阅读压力。

---

## P1：让诊断、复习、学习者模型真正闭环

### P1-4：`metrics.json` 和 `review_queue.json` 设计了，但真实会话里缺失

**证据**

扫描 `learning-history/` 没发现真实会话下的 `metrics.json` 和 `review_queue.json`。但 `SKILL.md` 已要求每课完成后写入 metrics 和 review queue。

**建议**

1. `init_session.py` 已经会生成这两个文件，但旧会话需要 migration 补齐。
2. 新增 `scripts/session/append_event.py` 或 Python API，避免 AI 手写 JSON。
3. 新增 `scripts/session/add_review_item.py`，统一复习队列字段。
4. `validate_state.py` 增加存在性和 schema 校验。

建议 review item 升级为：

```json
{
  "id": "review_001",
  "source": "mastery_test_gap",
  "lesson_id": "02.1",
  "lesson_path": "lessons/deep/02.1_I2C 协议代码.md",
  "concept_tags": ["eeprom-page-write-boundary"],
  "gap_reason": "跨页写入后果解释不完整",
  "next_review_at": "2026-04-25T10:00:00+08:00",
  "interval_days": 1,
  "review_count": 0,
  "status": "pending"
}
```

---

### P1-5：诊断批改目前是“可用 MVP”，但不适合最终权威评分

`diagnostic_grader.py` 目前的规则匹配和关键词覆盖适合快速路由，但还不适合作为精细学习评估的唯一依据。

**建议**

| 优化 | 说明 |
|------|------|
| 题目增加 rubric | 每题显式列出关键点、错误类型、部分分标准 |
| 解析用户答案区 | 用 Markdown AST 或更鲁棒的 section parser，避免正则误吃内容 |
| LLM fallback 标准化 | 输出结构必须包含 `score/reason/missing_points/misconception_tags` |
| 置信度校准 | 自信度与正确性写入 learner_model，不只返回 route |
| 人工复核标记 | `needs_review=true` 的结果不要自动更新 mastery 为强结论 |

---

## P1：升级语料索引和图片索引

### P1-6：当前索引偏“标题级”，需要升级到“证据块级”

当前 `corpus_indexer.py` 主要读取 H1/H2 标题并按相似度聚类。它适合快速建立主题列表，但不足以支撑高质量教程里的“引用证据”和“图片选图”。

**建议升级为三层索引**

| 层 | 粒度 | 用途 |
|----|------|------|
| topic index | 标题和别名 | 找同一知识点在哪些材料出现 |
| chunk index | 小节文本块 | 给 lesson 提供可引用证据 |
| image index | 图片 + 最近上下文 + 页码 | 给图表决策树选原图 |

### P1-7：Markdown parser 需要记录行号

`md_parser.Heading` 当前没有 line_no，导致 image index 中“最近标题”只能近似，甚至 `_build_heading_chain` 会返回前几个标题而不是图片所在行之前的标题链。

**建议**

把 `Heading` 改成：

```python
@dataclass
class Heading:
    level: int
    text: str
    raw: str
    line_no: int
```

然后修复：

| 函数 | 修复方向 |
|------|----------|
| `_find_nearest_heading` | 找 `heading.line_no <= image.line_no` 的最近标题 |
| `_build_heading_chain` | 只包含图片行之前的层级链 |
| `_find_images_for_heading` | 以 heading section 范围匹配图片，而不是只靠上下文关键词 |

---

## P1：发布链路需要“公开版净化”

### P1-8：`strip_answers` 是预留但未实现

`publish_lesson.py` 里已经有 `--strip-answers`，但当前实现是 `pass`。公开发布时，这会留下两个风险：

| 风险 | 说明 |
|------|------|
| 私密答案泄露 | 学员真实答案和批改可能被发布 |
| 公开版阅读噪声 | 大量“我的答案”空槽让公开文档不像教程 |

**建议**

把发布产物分三种 profile：

| profile | 用途 | 行为 |
|---------|------|------|
| `public-article` | 公开教程 | 删除“我的答案”、批改块、私有路径、学习者画像 |
| `public-interactive` | 公开练习 | 保留题目和空答案区，删除真实答案和批改 |
| `private-archive` | 私有归档 | 原样保留 |

并在 manifest 中写明：

```yaml
publishes:
  - source: learning-history/.../lessons/deep/02.1_I2C 协议代码.md
    target: published/i2c/02_code.md
    profile: public-article
```

---

## P2：把 core/deep 进一步产品化

### P2-1：建议引入 lesson registry，替代多数组并行

当前 `lesson_files_core`、`lesson_files_deep`、`lesson_files`、`lesson_titles` 并行存在，容易索引错位。建议升级为：

```json
"lesson_registry": [
  {
    "lesson_id": "01",
    "title": "嵌入式硬件基础",
    "active_mode": "core",
    "core": {
      "path": "lessons/core/01_嵌入式硬件基础精华版.md",
      "status": "generated"
    },
    "deep": {
      "path": "lessons/deep/01_嵌入式硬件基础.md",
      "status": "generated"
    },
    "mastery": {
      "core_exit_check": "pending",
      "deep_mastery_test": "not_started"
    }
  }
]
```

优点：

| 优点 | 说明 |
|------|------|
| 不怕数组错位 | title、core、deep、状态在同一对象里 |
| 支持先 core 后 deep | deep 可为空或 pending |
| 支持发布 | 每课可以记录 public target |
| 支持补救课 | 可加 `type: remedial/branch/main` |

---

### P2-2：core 到 deep 的切换应有明确触发器

建议把 core 结尾检查题批改后分流：

| core exit-check 结果 | 下一步 |
|----------------------|--------|
| ≥ 80% 且用户只想考试速通 | 进入下一 core |
| 60-79% | 生成 deep compact，对薄弱点展开 |
| < 60% | 生成 remedial 或 deep full |
| 用户明确“想动手/想写代码/想看原理” | 生成 deep |

这样 core 不只是短文档，而是 deep 生成的智能入口。

---

## 四、建议的实施路线

## 第 1 阶段：P0 稳态修复（1-2 天）

| 任务 | 文件 | 验收 |
|------|------|------|
| schema 统一到 2.3 | `session-state.schema.json`、tests、README | `test_init_session` 全过 |
| 修复 CLI UTF-8 输出 | session/publish/convert 脚本 | Windows PowerShell 不再崩 |
| 扩展 validate core/deep | `validate_state.py` | 004 core 会话能识别真实 lesson |
| 修复 wait_reason | schema + 真实会话迁移方案 | 不再出现业务化枚举 |

## 第 2 阶段：状态迁移与审计（2-3 天）

| 任务 | 输出 |
|------|------|
| `migrate_state.py` | 2.0/2.2 → 2.3 |
| `reconcile_state.py` | 扫描并报告真实漂移 |
| 真实会话修复 | 003、004 能通过新 validate |
| CI 加状态样例校验 | 防止再次漂移 |

## 第 3 阶段：Lesson Lint（3-4 天）

| 任务 | 输出 |
|------|------|
| core lint | FAQ/Mid-check/出口/路径/长度 |
| deep lint | A/B 模式、代码锚点、Feynman、notes |
| file-driven lint | 禁止“直接发给我” |
| placeholder lint | 禁止具名占位符残留 |

## 第 4 阶段：发布净化与公开文档（2 天）

| 任务 | 输出 |
|------|------|
| 实现 `strip_answers` | 可删除答案与批改 |
| 增加 publish profile | public/private/interactive |
| manifest 批量发布 | 可重复发布整套课程 |
| MkDocs nav 自动化 | 减少手动维护 |

## 第 5 阶段：索引与自适应学习增强（1 周）

| 任务 | 输出 |
|------|------|
| chunk-level corpus index | 更精准来源证据 |
| image index line_no 修复 | 图表匹配更可靠 |
| review_queue 实际落地 | 间隔复习真正发生 |
| metrics dashboard | 看见学习进度和薄弱点 |

---

## 五、推荐优先级总表

| 优先级 | 优化项 | 预期收益 |
|--------|--------|---------|
| P0 | schema 2.3 对齐 | 恢复权威状态源 |
| P0 | validate_state 支持 core/deep | 避免新分层被旧校验误伤 |
| P0 | migrate/reconcile 状态 | 修复真实会话漂移 |
| P0 | CLI UTF-8 | 解决 Windows 下脚本崩溃 |
| P1 | lesson_lint | 把教学规则变成机器门禁 |
| P1 | core 答案文件驱动 | 统一学习交互协议 |
| P1 | review_queue/metrics 落地 | 让“动态调整”真的可追踪 |
| P1 | publish sanitizer | 防止私有答案泄露 |
| P1 | corpus chunk index | 提升来源引用和图表选择质量 |
| P2 | lesson_registry | 降低 core/deep 并行数组复杂度 |
| P2 | core→deep 智能分流 | 让精华版成为深度学习入口 |

---

## 六、最终建议

这套系统已经走过“能生成教程”的阶段，正在进入“能稳定生成高质量课程产品”的阶段。

下一步最值得做的不是继续扩展模板，而是建立四个契约：

| 契约 | 负责回答 |
|------|----------|
| State Contract | 当前学到哪、该读哪个文件、状态是否一致 |
| Lesson Contract | 生成的教程是否符合 core/deep 教学规则 |
| Review Contract | 错题和薄弱点是否真的进入复习闭环 |
| Publish Contract | 私有学习产物如何安全变成公开教程 |

只要这四个契约补齐，auto-tutor 就会从“强提示词驱动的个人学习项目”升级为“可持续迭代的教程生成框架”。

---

## 七、2026-04-24 落地记录：最高质量闭环

本轮按“执行前 rules → 执行中 rules → 校验 rules → 删除 rules”的闭环执行。这里的 rules 是本轮临时执行纪律，不写入 `.windsurfrules`、`.ai-switch` 或其他长期规则文件，避免污染用户已有工作流。

### 7.1 执行前 rules

| Rule | 执行方式 |
|------|----------|
| 保护既有工作区 | 仓库已有多处未提交/未跟踪文件，只改本轮优化相关文件，不回滚用户改动 |
| 先状态、后产物 | 优先修 `session_state` 契约，再做 lesson 产物 lint |
| 默认只读真实历史 | 对 `learning-history/003`、`004` 只做 validate/reconcile/lint 审计，不自动修复学习历史 |
| 不制造持久 rules 文件 | 临时 rules 只记录在本报告，不新增需要最后删除的规则文件 |

### 7.2 执行中 rules

| Rule | 已落地 |
|------|--------|
| State Contract | `session-state.schema.json` 统一到 `2.3`，新增 `wait_detail`、`current_mode`、`lesson_files_core`、`lesson_files_deep`、`mode_switch_log` |
| Core/Deep Resolver | `validate_state.py` 支持 core/deep 活跃 lesson 列表、active variant、目录契约校验 |
| Drift Audit | 新增 `scripts/session/reconcile_state.py`，默认只读；显式 `--fix-*` 时先备份再写回 |
| Lesson Contract | 新增 `scripts/lesson_lint.py`，检查具名占位符、聊天式答题、图片路径、core 结构、deep 来源标注、代码块长度 |
| File-driven Core | `core-lesson-rules.md` 的 Exit-check 改为写入 `answers/{lesson_stem}.md`，禁止聊天里直接收答案 |
| Windows UTF-8 | session/publish/convert 相关 CLI 加入 stdout/stderr UTF-8 guard |
| 文档同步 | README 与 learning-engine Skill 从 v2.2 更新到 v2.3，并挂载 validate/reconcile/lesson_lint 命令 |

### 7.3 校验 rules

| 校验 | 结果 |
|------|------|
| `python -m pytest tests/ -q` | 262 passed |
| `python scripts/session/init_session.py ...` + `validate_state.py` 编码冒烟 | 通过，且临时目录已删除 |
| `validate_state.py learning-history/004...` | 12/13，通过项稳定；失败为历史 `wait_reason` 业务化字符串 |
| `reconcile_state.py learning-history/004...` | 只读发现 `wait_reason` 漂移，建议迁移到 `wait_detail.message` |
| `validate_state.py learning-history/003...` | 10/13，发现缺失 `core/03_SPI 精华版.md` 与缺失 active variant |
| `reconcile_state.py learning-history/003...` | 只读发现 `02.1_I2C 协议代码_v2.md` 可降级到现存 legacy；`core/03` 无同目录候选，未建议跨模式修复 |
| `lesson_lint.py learning-history/004...` | 发现 4 个产物问题：core 仍有聊天式答题，2 个 deep 缺来源标注 |
| `lesson_lint.py learning-history/003...` | 发现 27 个产物问题：残留 `{caption}`/`{hash}`/`{session_dir}` 占位符与少量 deep 代码块超长 |

### 7.4 最后删除全部 rules

本轮没有创建任何持久 rules 文件，因此没有可删除的规则文件。临时执行 rules 已在本节收束；仓库中已有的 `.windsurfrules`、`.ai-switch/` 等用户规则资产没有被删除或重置。

后续若要继续“自动修复真实会话”，建议先人工确认这两个动作：

| 动作 | 命令 |
|------|------|
| 修复 004 的 `wait_reason` | `python scripts/session/reconcile_state.py learning-history/004_embedded-software-designer_2026-04-23-15-45 --fix-wait-reason --write-audit` |
| 修复 003 的缺失 active variant | `python scripts/session/reconcile_state.py learning-history/003_stm32f103-hal_2026-04-13-09-45 --fix-lesson-files --write-audit` |

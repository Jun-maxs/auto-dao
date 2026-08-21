---
name: learning-engine
description: >
  交互式学习引擎，采用苏格拉底教学法和布卢姆分类学引导用户深入学习。
  Use when user says "学习引擎", "帮我学习这个文档", invokes /learning-engine,
  or provides a learning material and asks to study it.
---

# Learning Engine（学习引擎）

> 以"文件驱动 + 苏格拉底教学法 + 布卢姆分类学"为核心，引导用户对学习资料实现深度知识内化的交互式学习引擎。

**Core Pipeline**: `文件预处理 → 初始化与历史检索 → 上下文恢复 → 文件驱动交互式学习 → 学习报告`

---

## Mandatory Rules

> [!CAUTION]
> ### Serial Execution & Gate Discipline
>
> **This workflow is a strict serial pipeline. The following rules have the highest priority — violating any one of them constitutes execution failure:**
>
> 1. **SERIAL EXECUTION** — Steps MUST execute in order; output of each step is input for the next. Non-BLOCKING adjacent steps may proceed continuously once prerequisites are met, without waiting for the user to say "continue"
> 2. **BLOCKING = HARD STOP** — ⛔ BLOCKING steps require full stop; agent MUST wait for explicit user response before proceeding and MUST NOT make decisions on behalf of the user
> 3. **NO CROSS-PHASE BUNDLING** — Bundling work across phases is FORBIDDEN
> 4. **GATE BEFORE ENTRY** — Prerequisites (🚧 GATE) MUST be verified before starting each Step
> 5. **NO SPECULATIVE EXECUTION** — Pre-preparing content for future steps is FORBIDDEN

> [!IMPORTANT]
> ### Language & Communication
>
> - Match the language of the user's input. If the user writes in Chinese, respond in Chinese; if in English, respond in English
> - Explicit user override takes precedence
> - Lesson 文件内容使用中文；文件结构关键词（如 `## 学习目标`、`## 课后习题`、`**我的答案**`）保持固定格式，不得更改
>
> **跨语言教学（强制执行）**：
>
> 若用户指定的教学语言与学习材料的语言不同（例如：材料为中文，但要求英文教学），则：
>
> 1. **翻译前置**：在生成 Lesson 内容前，先读取 `${PROJECT_DIR}/settings/glossary.md` 中的术语表
> 2. **术语优先**：翻译时，所有出现在术语表中的专有名词必须严格使用术语表中对应的译法，不得自行翻译
> 3. **全文翻译**：Lesson 文件的所有正文内容（讲解、习题、反馈）均使用目标教学语言输出；文件结构关键词（如 `## 学习目标`、`**我的答案**`）保持固定格式不变
> 4. **术语标注**：首次出现的专有名词，在译文后以括号附注原文，格式：`Derivative（导数）`
> 5. **术语表缺失处理**：若某专有名词未收录于术语表，使用通行译法并在该词后标注 `[⚠️ 术语表未收录]`

> [!IMPORTANT]
> ### Compatibility With Generic Coding Skills
>
> - Do NOT create `.worktrees/`, `tests/`, branch workflows, or other generic engineering structure
> - If generic coding skills conflict with this workflow, follow this skill first unless the user explicitly overrides

> [!IMPORTANT]
> ### 防幻觉（强制执行）
>
> - ❌ 禁止编造数据、虚构事件、臆测因果关系
> - ✅ 讲解中涉及资料内容时，必须使用 `> **资料原文**：` 格式标注原文
> - ✅ 资料未覆盖的知识点，必须明确告知用户"当前资料未涉及此内容"

> [!IMPORTANT]
> ### 用户背景适配（强制执行）
>
> 生成的课程内容必须符合【用户背景】：
> - 用户背景来源：
>   1. `${PROJECT_DIR}/settings/background.md` 中的背景信息
>   2. 用户在调用 skill 时补充的背景信息
> - 优先级：用户补充的背景信息 > `background.md` 中的背景信息
> - 若两者存在冲突，以用户补充为准
> - 适配要求：
>   - 讲解深度、用词、举例应适配用户的年级/知识水平
>   - 习题难度应与用户能力匹配
>   - 若用户背景表明其是教师（如家教），讲解可包含教学策略建议

> [!IMPORTANT]
> ### 文件驱动核心原则（强制执行）
>
> | 禁止行为 | 原因 |
> |---------|------|
> | ❌ 在对话中展示课程讲解内容 | 违反文件驱动原则 |
> | ❌ 在对话中展示课后习题 | 用户应在文件中阅读习题 |
> | ❌ 让用户在对话中发送答案 | 用户应在文件中填写答案 |
> | ❌ 在对话中直接检查答案 | 必须先读取文件中的答案 |
>
> **唯一允许的对话内容**：通知文件位置、提醒填写答案、读取文件后给出反馈、补充讲解。
>
> **例外**：Step 3 的快速复习测试为轻量遗忘检测，不属于正式课程，允许在对话中进行问答。

> [!IMPORTANT]
> ### 状态管理原则（强制执行）
>
> | 层级 | 文件 | 定位 | 写入时机 |
> |------|------|------|---------|
> | **权威源** | `session_state.json` | 机器可读的唯一状态源 | 每次状态变更时**首先**写入 |
> | 派生视图 | `summary.md` | 人类可读摘要 | 从 `session_state.json` + `lessons/` 派生，允许追加笔记 |
> | 派生视图 | `roadmap_status.md` | 人类可读进度 | 从 `session_state.json` 的进度字段派生 |
> | 派生视图 | `_ai_context.md` | AI 断点恢复上下文 | 从 `session_state.json` + 学习历史派生 |
>
> **规则**：当 `session_state.json` 与 Markdown 视图不一致时，以 `session_state.json` 为准。
> 派生视图可包含 `session_state.json` 中不存在的补充信息（如详细笔记、教学决策日志），但核心进度字段必须与权威源保持一致。

> [!IMPORTANT]
> ### Lesson 变体追踪（`lesson_variants` 字段，2026-04-18 新增）
>
> 当一节课被重新生成（如 v1 → v2 重构、模式 A → B 升级、沉淀复盘后优化）时，不删除旧文件（保留历史轨迹），而是在 `session_state.json` 的 `lesson_variants` 中记录活动变体：
>
> ```json
> "lesson_variants": {
>   "02.1": {
>     "active": "02.1_I2C 协议代码_v2.md",   // 学员应读的当前版本
>     "legacy": ["02.1_I2C 协议代码.md"],      // 已归档的旧版本
>     "teaching_mode": "B",                         // 当前版用的模式
>     "scenario_closures": ["EEPROM", "OLED", "AHT20"],
>     "notes_dir": "lessons/02.1_I2C 协议代码_v2_notes/",
>     "regenerated_at": "2026-04-18T14:10:00+08:00",
>     "regeneration_reason": "v1 mastery 3.3/5 复盘..."
>   }
> }
> ```
>
> **读取规则**：
> - 恢复会话时 AI 需查询 `lesson_variants[<lesson_id>].active` 来确定读哪个文件
> - `lesson_files` 数组保持旧文件名不变时，要优先看 variant.active 覆盖
> - `scripts/session/validate_state.py` 已支持 variant 规则（`_resolve_lesson_file` 函数）
>
> **完整 schema 规范**：见 `${SKILL_DIR}/templates/session-state.schema.json` 的 `lesson_variants` 节。
> **设计背景**：`docs/plans/2026-04-18-scenario-closure-feynman-design.md`。

### Role Dispatch Protocol

This skill operates as a single inline agent — no role switching required.

---

## Resource Manifest

### Templates

| Index | Path | Purpose |
|-------|------|---------|
| Learn-card 模板 | `${SKILL_DIR}/templates/learn-card-template.md` | 默认学习入口，短文档，先建立心智模型 |
| Practice-pack 模板 | `${SKILL_DIR}/templates/practice-pack-template.md` | 练习包，承载检索、迁移、改错和复述 |
| Deep-reference 模板 | `${SKILL_DIR}/templates/deep-reference-template.md` | 深入查阅、来源覆盖、完整推导与完整代码 |
| 生成器规则 | `${SKILL_DIR}/templates/generator-rules.md` | AI 内部规则，不直接写入学习者主文档 |
| 实践过程规则 | `${SKILL_DIR}/templates/practice-process-rules.md` | 结果牵引、最小闭环、反馈校准、复盘沉淀和间隔练习 |
| Legacy Lesson 模板 | `${SKILL_DIR}/templates/lesson-template.md` | 旧 deep 结构模板；仅维护历史 deep 课或用户明确要求时使用 |
| 摘要模板 | `${SKILL_DIR}/templates/summary-template.md` | `summary.md` 初始化模板 |
| 路线图模板 | `${SKILL_DIR}/templates/roadmap-template.md` | `roadmap_status.md` 初始化模板 |
| 报告模板 | `${SKILL_DIR}/templates/report-template.md` | 学习报告结构模板 |
| 状态模板 | `${SKILL_DIR}/templates/session-state-template.json` | `session_state.json` 初始化模板（v2.3，默认 learn-first；保留历史 core/deep 字段用于旧会话兼容） |
| 状态 Schema | `${SKILL_DIR}/templates/session-state.schema.json` | `session_state.json` 字段校验 Schema |
| 项目概览模板 | `${SKILL_DIR}/templates/project-overview-template.md` | 开源项目学习资料生成模板 |
| 复习队列模板 | `${SKILL_DIR}/templates/review-queue-template.json` | 错题复习队列初始化模板 |
| 架构图模板 | `${SKILL_DIR}/templates/architecture-map-template.md` | GitHub 项目学习可选产物：模块依赖与数据流 |
| 阅读顺序模板 | `${SKILL_DIR}/templates/file-reading-order-template.md` | GitHub 项目学习可选产物：源码阅读路径与首次贡献建议 |
| 指标模板 | `${SKILL_DIR}/templates/metrics-template.json` | 会话事件日志，用于教学策略量化分析 |
| 诊断模板 | `${SKILL_DIR}/templates/prereq-diagnostic-template.md` | 课前诊断文件生成模板 |
| 复诊模板 | `${SKILL_DIR}/templates/prereq-diagnostic-recheck-template.md` | 补救课后复诊文件模板 |
| 补救课模板 | `${SKILL_DIR}/templates/remediation-lesson-template.md` | 前置补救课内容模板 |

| Resource | Path |
|----------|------|
| 布卢姆分类学 | `${SKILL_DIR}/references/bloom-taxonomy.md` |
| 苏格拉底教学法 | `${SKILL_DIR}/references/socratic-method.md` |

### User Context

| Resource | Path | Purpose |
|----------|------|---------|
| 用户背景 | `${PROJECT_DIR}/settings/background.md` | 学习者的年级、科目、问题等背景信息 |

---

## Common Commands

### 大测驗

```bash
# 全面知识图谱评估（一次性摸底某专题的完整知识水平）
/大测验

# 或在学习引擎运行时说"做个摸底测试"
# 系统会建议是否需要大测驗
```

---

## Workflow

### Step 1: 文件格式预处理 (File Format Preprocessing)

🚧 **GATE**: 用户已提供学习资料——文件路径、目录路径、GitHub 链接或内容。

🛠️ **EXECUTION**:

1. **输入类型判断**：

| 输入形式 | 判断条件 | 处理方式 |
|---------|---------|---------|
| GitHub 链接 | 以 `https://github.com/` 开头 | 执行第 2 步（项目获取） |
| 本地目录路径 | 路径指向一个目录 | 执行第 2 步（项目获取） |
| 单个文件 | 路径指向一个文件 | 执行第 3 步（格式检测） |
| 不可读文件类型 | 见下方不可读类型列表 | 执行第 6 步（报错终止） |

**不可读文件类型**（报错终止）：`.exe` / `.dll` / `.so` / `.bin` / `.dat` / `.zip` / `.tar` / `.gz` 等二进制或压缩格式。

2. **开源项目获取与学习资料生成**：

   **若为 GitHub 链接**：
   ```bash
   git clone {github_url} ${PROJECT_DIR}/tmp/{repo_name}/
   ```
   - 失败则重试，最多 3 次；超过 3 次提示用户检查链接或网络

   **若为本地目录路径**：
   将本地目录复制到项目临时目录（根据操作系统选择命令）：
   - **macOS / Linux**：`cp -r {local_path} ${PROJECT_DIR}/tmp/{project_name}/`
   - **Windows**：`xcopy /E /I "{local_path}" "${PROJECT_DIR}\tmp\{project_name}\"`

   **项目读取与学习资料生成（内联执行）**：
   > ⚠️ **本步骤由 learning-engine 本体内联完成**，不启动子代理/异步任务——AI 自己完成以下动作：

   1. 读取项目根目录下的 `README.md`（若存在）作为概览
   2. 扫描项目文件树，识别主要模块与入口文件
   3. 读取 `${SKILL_DIR}/templates/project-overview-template.md` 作为填写骨架
   4. 按下列要求生成 `${PROJECT_DIR}/tmp/converted/{project_name}_overview.md`：
      - 按模板的 8 个章节逐一填写，不得省略任何章节
      - 所有内容必须有来源依据（README、代码文件、注释）；无法确认来源的内容标注 `[⚠️ 当前资料未涉及此内容]`
      - 第 3 节"项目结构"：用 tree 格式展示两级目录，超过 20 个条目时折叠次要目录
      - 第 4 节"核心模块"：每个模块必须标注入口文件的实际路径
      - 第 5 节"数据流"：必须追踪至少一条从入口到输出的完整调用链
      - 第 7 节"推荐学习路径"：按模块依赖关系排序，每条对应后续一个 Lesson 的学习单元
      - 不得编造函数名、类名、文件路径——所有符号必须在项目中实际存在
   5. 生成失败（如目录过大无法一次性阅读）则分批读取并追加；若仍失败则向用户反馈具体阻塞项而不是静默重试
   6. 将生成的 `_overview.md` 作为后续步骤的 `processed_path`，跳至第 5 步

3. **格式检测**：判断文件后缀：

| 类型 | 文件格式 | 处理方式 |
|------|---------|---------|
| 直接可读（无需转换） | `.md` 及各类源码（`.c` `.cpp` `.py` `.java` `.js` `.ts` `.go` `.rs` `.rb` `.swift` `.kt` 等） | 跳至第 4 步 |
| 需转换为 Markdown | `.pdf` `.docx` `.pptx` `.png` `.jpg` `.html` 等 | 执行第 4 步前先执行转换 |

> ⚠️ `.html` 默认需要转换，除非用户明确表示学习目标是"学习如何书写 HTML"。

4. **非直接可读文件转换（同步 CLI 调用）**：
   > ⚠️ **此步通过 CLI 脚本同步执行**，不使用 subagent：

   ```bash
   python .claude/skills/everything-to-markdown/scripts/convert_to_markdown.py <file_path> [output_dir]
   # 等价于（package.json 提供便捷入口）：
   npm run convert -- <file_path> [output_dir]
   ```

   - 默认 `output_dir` = `${PROJECT_DIR}/tmp/`；脚本会在其下创建 `{base_name}_{YYYYMMDD_HHMMSS}/` 子目录并解压结果
   - 返回的 Markdown 绝对路径记录为 `processed_path`（形如 `tmp/xxx_20260418_120000/full.md`）
   - 脚本内部已对 MinerU API 做指数退避重试 3 次（429/5xx）；若最终仍失败，向用户展示真实错误并请求手动处理
   - 使用前需在 `settings/.env` 配置 `MINERU_API_KEY`，否则脚本会立即报错终止
   - 单文件大小上限 200 MB（MinerU API 约束），超出需在调用前切分

5. **Markdown 质量检测与优化（内联执行）**：
   > ⚠️ **此步由 AI 内联执行 `markdown-refiner` 规则**，不再启动 subagent；按章节分段、就地修正即可：

   1. 读取 `processed_path` 的前 500 行，检测：标题层级错乱、OCR 噪声、格式不规范
   2. 若存在问题：打开 `${PROJECT_DIR}/.claude/skills/markdown-refiner/SKILL.md`，按其 4 类规则（标题层级 → OCR 噪声 → 格式规范 → 结构完整性）逐章节修正
   3. 修正后再读一次前 500 行，确认问题已消除；仍有残留则记录并在对话中告知用户具体阻塞项
   4. 保守原则：不确定的地方保留原文并附 `[⚠️ OCR 识别可能有误]` / `[⚠️ 公式识别可能有误]` 标注

6. **不可读文件类型报错（终止）**：
   ```
   ❌ 无法处理该文件类型：{file_extension}
   当前支持的格式：Markdown、源码文件、PDF、Word、PPT、图片、HTML，以及 GitHub 链接或本地项目目录。
   请提供可读的学习资料后重新调用。
   ```
   终止 workflow，不进入 Step 2。

7. **记录文件状态**：
   - `original_path`：原始文件路径或链接
   - `processed_path`：处理后文件路径
   - `processing_status`：`original` | `cloned` | `converted` | `refined`

✅ **Step 1 完成**：输入类型判断完成，文件已就绪（路径：`{processed_path}`，状态：`{processing_status}`）。

→ **直接进入 Step 2**

---

### Step 2: 初始化与历史检索 (Initialization & History Retrieval)

🚧 **GATE**: Step 1 complete；`processed_path` 已确认，文件可读。

🛠️ **EXECUTION**:

1. **主题提取**：根据资料内容自动提炼 `topic_slug`——全小写 ASCII、单词以连字符分隔（如 `quantum-physics`、`python-async`）。中文主题使用英文翻译或拼音
2. **获取时间戳**：记录 `timestamp`（固定格式：`YYYY-MM-DD-HH-MM`，不可省略时分）
3. **扫描历史**：检索 `${PROJECT_DIR}/learning-history/` 下所有子目录
4. **智能筛选**：根据文件夹名（格式 `${topic_name}_${timestamp}`）筛选相关历史
5. **深度核实**：读取相关目录下的 `summary.md`，确认学习进度与目标一致性
6. **构建选项列表**：
   - 每条历史记录：`[文件夹名] - 上次学习到：[summary.md 中的进度摘要]`
   - 末尾追加：`开启全新学习`

**历史选择路由规则**（三段式）：

| 历史记录数 | 行为 | 说明 |
|-----------|------|------|
| **0 条** | 直接创建新会话 | 无需询问，直接执行 Step 3 的新会话初始化 |
| **1 条** | 自动选择该记录，输出通知 | `"✅ 检测到 1 条历史记录，自动继续：[历史名]"`，然后执行 Step 3 |
| **2+ 条** | ⛔ **BLOCKING**：`ask_user_question` 询问选择 | 用户选择后执行 Step 3 |

7. **大测驗知识图谱检测（Optional）**：
   - 检查是否存在 `${PROJECT_DIR}/learning-history/${topic_name}_assessment/knowledge_map.md`；若存在，作为**先验知识图谱**读入上下文，后续 Step 3 生成 roadmap 时参考它跳过已掌握知识点（✅ ≥80%）、优先补薄弱点（❌ <60%）
   - 同时读取 `${PROJECT_DIR}/settings/background.md` 的"知识图谱摘要"表格；若其中有当前 `topic_name` 的近期测评记录（<30 天），同样纳入参考
   - 若**都没有**且用户当前专题广阔（如"STM32 全栈"、"数学分析"），在"Step 2 完成"通知中追加一句可选建议：`"💡 若希望系统更精准地定位你的知识缺口，可运行 /comprehensive-assessment 进行大测驗；否则按当前资料默认生成 roadmap。"`
   - **不打断流程**，用户未响应建议时继续进入 Step 3

✅ **Step 2 完成**：topic_name = `{topic_name}`，timestamp = `{timestamp}`，历史选择路由已确定（{选择结果}），知识图谱前置：{有 / 无 / 可选建议}。

→ **直接进入 Step 3**

---

### Step 3: 上下文恢复 (Context Recovery)（Conditional）

🚧 **GATE**: Step 2 complete；用户已做出选择。

> **Trigger condition**: 用户选择了继续某条历史记录。若用户选择"开启全新学习"，则创建新目录并初始化文件后，跳至 Step 4。

🛠️ **EXECUTION**:

**若用户选择全新学习**：

> 💡 **便捷入口**：以上所有初始化文件可一次性由 `python scripts/session/init_session.py` 生成（脚本会读取所有模板并填充必填字段），然后 AI 再补充业务填充。手动执行时按以下顺序：

1. 创建目录 `${PROJECT_DIR}/learning-history/${topic_name}_${timestamp}/lessons/`
2. 读取 `${SKILL_DIR}/templates/summary-template.md`，初始化 `summary.md`
3. 读取 `${SKILL_DIR}/templates/roadmap-template.md`，初始化 `roadmap_status.md`（若 Step 2.7 读到了知识图谱前置，roadmap 的"知识点追踪"表以 ✅/🔄/⏳ 状态反映已掌握部分）
4. 读取 `${SKILL_DIR}/templates/course-overview-template.md`，初始化 `course_overview.md`（含课程级学习目标、知识地图、各课速览；`total_lessons` 来自 roadmap 规划）
5. 读取 `${SKILL_DIR}/templates/ai-context-template.md`，初始化 `_ai_context.md`，填入：资料来源路径、转换后路径、用户背景水平初始判断
6. 读取 `${SKILL_DIR}/templates/session-state-template.json`，初始化 `session_state.json`（**v2.3**，默认 `current_mode: "learn"`，含 `learner_model` + `_file_paths`；历史 core/deep 字段仅用于旧会话兼容），填入必填字段：`topic_id`、`topic_name`、`source_path`、`processed_path`、`source_hash`（源文件 SHA-256）、`phase` ← `"learning"`、`total_lessons`（来自 roadmap 规划）、`learning_language`、`created_at`、`updated_at`
   - 若学习资料为 GitHub 仓库或本地 Git 目录：记录 `repo_commit_hash` ← 当前 HEAD commit hash（通过 `git rev-parse HEAD` 获取）
   - `learner_model` 默认空对象（`concept_mastery: {}`、`overall_confidence_bias: "unknown"`、`bloom_target: 3`）
7. **同步资料图索引到 session**（仅当 `processed_path` 指向 MinerU 转换输出 `tmp/converted/{material}_{ts}/` 时执行）：
   ```bash
   python scripts/indexer/sync_images_to_session.py {processed_path} ${PROJECT_DIR}/learning-history/${topic_name}_${timestamp}
   ```
   - 脚本会自动定位预构建的全局索引（`tmp/converted/index/{label}/image_index.json`）；不存在时会自动调用 `build_corpus_index.py` 重建
   - 产出：`{session_dir}/image_index.json`（path 已改写为 `images/*.jpg`）+ `{session_dir}/images/` 复制源图片
   - 若资料为原生 Markdown / 源码目录 / GitHub 仓库（无 `images/` 子目录）：跳过本步，后续 Lesson 生成进入 §4.2.1 决策树的第 3/4 步
   - 失败处理：打印错误信息并在对话中要求用户确认是否继续（没有原图索引也能生成 Lesson，只是没有资料原图候选）
8. **立即校验**：运行 `python scripts/session/validate_state.py ${PROJECT_DIR}/learning-history/${topic_name}_${timestamp}`，通过后方可进入 Step 4；若失败则立即修正并复校
9. 跳至 Step 4

**若用户选择继续历史**：
1. **优先读取 `session_state.json`**：获取 `phase`、`current_lesson`、`last_completed_lesson`、`counterfactual_mode`、`wait_reason`、`mastery_rate` 等机器状态（唯一权威源）
2. 读取 `_ai_context.md`：恢复用户画像、错误模式、教学决策日志
3. 读取 `summary.md`：获取核心结论、已掌握知识点、待攻克难点
4. 读取 `roadmap_status.md`：获取知识点追踪详情
5. 读取 `review_queue.json`（若存在）：获取待复习错题列表，优先复习 `status: "pending"` 且 `next_review_at` 已到期的条目
6. **向后兼容：图索引补偿**（仅当 `session_state.json` 中 `processed_path` 指向 MinerU 转换输出，且 `{session_dir}/image_index.json` 不存在时触发）：
   ```bash
   python scripts/indexer/sync_images_to_session.py {processed_path} {session_dir}
   ```
   - 这是给 2026-04-18 前创建的旧会话打补丁，使其也能享受 §4.2.1 决策树的第 1-2 步
   - 成功后 `{session_dir}/image_index.json` + `{session_dir}/images/` 就位，后续 Lesson 生成正常匹配资料原图
   - 失败则在对话中告知用户"旧会话图索引补偿失败，资料原图不可用；后续 Lesson 仅能生成 DrawIO"——不阻塞学习
7. **增量学习检测**（仅 GitHub/Git 仓库）：若 `session_state.json` 中 `repo_commit_hash` 非 null，获取当前 HEAD commit hash 并对比——若有变化，提示用户："仓库自上次学习后有 N 个新 commit，是否生成增量课程覆盖变更内容？"用户确认后，对 diff 生成 `delta_overview.md` + `lessons/delta_lesson_{N}.md`
8. **触发式遗忘检测**（若 `review_queue.json` 中有到期复习项则直接使用，否则走下方规则）：
   - 读取 `summary.md` 的 `最后更新` 时间戳，计算距今天数
   - 读取"错题记录"表格中状态为"✅ 已纠正"的条目（即曾犯错但已纠正的知识点——最容易遗忘）
   - 按以下规则决定是否插入复习：

   | 距上次学习天数 | 已纠正错题数 | 操作 |
   |--------------|------------|------|
   | ≤ 3 天 | 任意 | 跳过复习，直接进入新课 |
   | 4-14 天 | ≥ 1 | 插入快速复习：从已纠正错题中抽取 2-3 道，生成简化版复习测试（仅习题 + 答案区，无讲解），用户完成后再进入新课 |
   | 4-14 天 | 0 | 跳过复习（无历史错题可复习） |
   | > 14 天 | ≥ 1 | 插入复习 + 在对话中提醒："距上次学习已超过两周，建议先回顾前几课的要点总结再继续" |
   | > 14 天 | 0 | 在对话中提醒间隔较长，建议用户自行翻阅之前的 lesson 文件回顾 |

   > **复习测试不生成独立 lesson 文件**，直接在对话中以代码块形式呈现，用户在对话中回答即可。答对 → 确认记忆保持；答错 → 更新错题记录表中该条目状态为"❌ 未纠正"，并在下一课讲解中穿插相关概念的回顾。

9. 检查当前 lesson 文件状态，按下表路由：

| 场景 | lesson 文件状态 | 用户答案状态 | 正确行为 |
|------|----------------|-------------|---------|
| A | 不存在 | — | 跳至 Step 4，生成新 lesson |
| B | 已存在 | "我的答案"区域为空 | ⛔ BLOCKING：通知用户去文件中填写，等待"已完成" |
| C | 已存在 | "我的答案"区域已填写 | 跳至 Step 4，执行答案检查 |

**场景 B 通知模板**：
```
📋 检测到 Lesson {index} 已生成，但尚未完成。

   📄 文件位置：`./learning-history/${topic_name}_${timestamp}/lessons/{active_lesson_file}`

请阅读该文件，在"我的答案"区域填写你的答案，保存文件后，在对话窗口告诉我"已完成"。
```

✅ **Step 3 完成**：学习目录已就绪，summary.md/roadmap_status.md 已加载，当前 lesson 状态：场景 {A/B/C}。

→ **直接进入 Step 4**

---

### Step 3.5: 课前诊断（Pre-Assessment with Confidence-Aware Adaptive Routing）

🚧 **GATE**: Step 3 complete；学习目录存在，当前 lesson index 已确定；用户背景已加载；`session_state.json`（含 `learner_model`）已读取。

> **前置说明**：此步骤在学习新 Lesson 之前检测用户是否具备所需的前置知识，并通过**自信度**识别学习模式（过度自信 vs 谨慎型），为教学策略适配提供数据支撑。
> 诊断结果不仅决定"跳过快进 / 压缩讲解 / 完整学习 / 补救课"的路由，还更新 `session_state.json` 的 `learner_model` 字段。

🛠️ **EXECUTION**:

**3.5.1 前置知识缺口分析（自动 + 手动）**：

1. **递归依赖链展开**：读取 `settings/prerequisite-map.md`（若存在），对下一课涉及的核心概念递归展开依赖链
2. **自动检测**：对下一课草稿中出现的术语，若在已学课程中从未出现，标记为潜在前置缺口
3. **合并去重**：合并自动检测 + prerequisite-map 手动标注的结果
4. **查询学习者模型**：读取 `session_state.json` 的 `learner_model.concept_mastery`，获取相关已测概念的掌握度和自信度偏差，用于精准定位薄弱环节

**3.5.2 诊断模式选择**：

在对话中发送诊断模式选择菜单，快速模式(3题)或完整模式(8题)

**3.5.3 生成诊断小测**：

1. 读取模板 `${SKILL_DIR}/templates/prereq-diagnostic-template.md`，根据前置缺口生成诊断题
2. **每道题必须包含**：
   - 题目内容（绑 `concept_tag`，与 Step 4.1 的 lesson 元信息中的 concept_tags 对应）
   - 难度适中（目标 Bloom 层级 2-3）
   - 与 `session_state.json` 的 `learner_model.bloom_target` 保持一致
3. 诊断题数量：快速模式 3 题，完整模式 8 题；每题覆盖一个独立 concept_tag，避免重叠

**3.5.4 诊断通知**：

通知用户诊断文件位置，特别提醒：
```
> ⚠️ 作答前，请先在"自信度"区选择你对本题的把握程度（1-5 分）。
> 自信度影响教学策略：高自信度 + 答错 → 系统判定为"过度自信"，会提供更多脚手架；
> 低自信度 + 答对 → 系统判定为"谨慎型"，讲解时会更注重直觉类比。
```

⛔ **BLOCKING**：等待用户说"诊断完成"或选择跳过

**3.5.5 批改、自信度分析与路由判定**：

1. 读取诊断文件，提取每道题的：
   - **答案正确性**：`✅` 完全正确 / `⚠️` 部分正确 / `❌` 错误
   - **自信度**：用户作答前选择的 1-5 分
2. **自信度偏移检测**（按 concept_tag 分别计算）：
   - `过度自信`：自信度 ≥ 4 且答案 `❌` 或 `⚠️`
   - `校准良好`：自信度与正确性大致匹配
   - `谨慎型`：自信度 ≤ 2 且答案 `✅`
   - `不确定型`：自信度 ≤ 2 且答案 `❌` 或 `⚠️`
3. **综合掌握度** = (完全正确×1.0 + 部分正确×0.5 + 错误×0.0) / 总题数 × 100%
4. **四档路由判定**：

   | 综合掌握度 | 主导模式 | 路由 |
   |-----------|---------|------|
   | ≥ 80% | 任意 | **Skip** → 直接进入 Step 4，讲解可压缩 |
   | 60-79% | 校准良好 | **Compact** → 快速回顾薄弱点后进入 Step 4 |
   | 60-79% | 过度自信 / 谨慎型 | **Full** → 完整讲解，且增加 Worked Example |
   | 33-59% | 任意 | **Remedial** → 插入前置补救课（每缺口 1 个） |
   | < 33% | 任意 | **Remedial** → 补救课 + 复诊 + Bloom 层级评估 |

5. 对每个 concept_tag，更新 `session_state.json` 的 `learner_model.concept_mastery[concept_tag]`：

   若该 concept_tag 无记录，创建：
   ```json
   "<concept_tag>": {
     "lesson_index": <当前 lesson index>,
     "mastery_level": "<掌握度<33%→weak / 33-59%→developing / ≥60%→strong>",
     "confidence_bias": "<检测到的偏移模式>",
     "misconception_tags": [],
     "test_count": 1,
     "correct_count": <1 若完全正确，否则 0>,
     "last_tested_at": "<ISO 8601>"
   }
   ```

   若该 concept_tag 已有记录，合并更新（test_count/correct_count 累加，mastery_level 取较低值，confidence_bias 取最新检测结果）。
6. 更新 `session_state.json` 的 `learner_model.overall_confidence_bias`：计算所有本轮测过 concept_tag 的 confidence_bias 众数。
7. 更新 `learner_model.last_updated_at` ← 当前 ISO 8601 时间戳。

**3.5.6 Bloom层级动态下调**：

连续 2 次补救课后，读取 `session_state.json` 的 `learner_model.bloom_target`，执行下调：
- 新值 ← max(1, 当前值 - 1)
- 将新值写入 `learner_model.bloom_target`
- 在 background.md 的"备注"区追加记录："Bloom 层级调整：L{N-1}（连续补救课触发）"

✅ **CHECKPOINT**:
```markdown
## ✅ Step 3.5 Complete
- [x] 前置知识缺口分析完成
- [x] 诊断完成（{N}题，含自信度）
- [x] learner_model 已更新（{M}个 concept_tag）
- [x] 路由：{Skip/Compact/Full/Remedial}
- [ ] **Next**: auto-proceed based on result
```

**3.5.7 教学策略适配通知**：

路由完成后，在对话中通知路由结果，格式：
```
📊 诊断完成 | 掌握度：{X}% | 主导模式：{模式标签}
🎯 路由：{Skip/Compact/Full/Remedial}
💡 教学建议：{根据模式给出提示}
```

- **Skip**：讲解时间可压缩 50%，直接进入渐进训练
- **Compact**：用 1-2 句话快速回顾薄弱点，再进入完整讲解
- **Full**：完整讲解，且在 Lesson 中额外增加 Worked Example 示范
- **Remedial**：前置补救课完成后，复诊通过方可进入主课

**3.5.7 前置补救课插入 + 闭环**：

触发条件：掌握度<33%

1. 生成前置补救课（每个缺口单独1个）
2. 通知用户补救课已生成
3. 等待用户完成
4. 复诊（快速3题）
5. 复诊批改 → 通过则进主课，否则继续补救或降级Bloom

✅ **Final CHECKPOINT**:
```markdown
## ✅ Step 3.5 Complete — All pre-assessment checks passed
```

---

### Step 4: 文件驱动交互式学习 (File-Based Interactive Learning)

🚧 **GATE**: Step 3.5 complete（诊断已完成或已跳过）；学习目录存在，当前 lesson index 已确定；`session_state.json`（含 `learner_model`）已读取。

**学习者模型感知**：每次进入 Step 4 时，自动读取 `session_state.json` 的 `learner_model`：
- `bloom_target`：当前目标认知层级（用于指导习题难度和讲解深度）
- `overall_confidence_bias`：整体自信度偏差（用于选择教学策略——overconfident 用户需要更多脚手架，underconfident 用户需要更多鼓励）
- `concept_mastery`：各 concept_tag 的掌握度（用于横向概念对比时识别潜在混淆点）

**反事实论证模式解析**（非 BLOCKING）：
1. 读取 `session_state.json` 的 `counterfactual_mode` 字段（schema 枚举：`"on"` / `"off"` / `"auto"` / `null`）
2. 按以下优先级确定最终值：
   - 若值为 `"on"` / `"off"` / `"auto"` → 直接使用，在对话中简要确认：`"反事实论证：{模式}（继承会话设置）"`
   - 若值为 `null`（首次会话）→ ⛔ **BLOCKING**：询问用户选择：
     - `始终开启` → 写入 `"on"`
     - `始终关闭` → 写入 `"off"`
     - `自动判断` → 写入 `"auto"`
     - `仅本次开启/关闭` → **不修改 `session_state.json`**；在本次 Lesson 生成时按临时选择执行，下一课重新走到本分支时会因字段仍为 `null` 再次询问
3. `"auto"` 模式规则：
   - 本课知识类型为**原理性**（Why deeply）→ 开启
   - 本课知识类型为**概念性**（What/Why）→ 按需（仅对核心结论启用）
   - 本课知识类型为**程序性**（How）→ 关闭
4. **非持久化变更（仅本次）**：当用户选择"仅本次"，在 `metrics.json` 追加一条 `counterfactual_toggled` 事件记录此次临时选择，但不改动 `counterfactual_mode` 字段本身

🛠️ **EXECUTION**:

**4.0 反事实论证模式（`counterfactual_mode ∈ {"on", "auto"}` 或"仅本次开启"生效时触发）**：

在生成 Lesson、检查习题作答、回答用户问题时，额外执行以下操作：

1. **反事实假设**：每个核心结论后，追加："如果 [该概念的核心要素] 不存在或发生相反变化，会导致什么结果？这与当前现实有何逻辑冲突？"
2. **因果 vs 相关**：明确区分哪些是相关性，哪些是因果性，不得将相关关系误述为因果关系
3. **自我辩论**：每个结论后增加"反事实论证"小节：
   - 假设该结论错误，可能的原因是什么？
   - 有哪些边缘案例不符合该理论？
   - 去掉前提条件后，结论是否依然成立？

**4.0 读取诊断结果（每次生成新 Lesson 前执行）**：

读取以下数据源（优先级从高到低）：
1. `session_state.json` 的 `learner_model.concept_mastery`：各 concept_tag 的掌握度和自信度偏差
2. `lessons/prereq_diagnostic.md`（本课的诊断结果）
3. `settings/background.md` 的"诊断历史与薄弱知识点"区域
4. 检查本课知识点中是否有"薄弱知识点"记录（来自 learner_model）

若 learner_model 中记录的 confidence_bias = "过度自信" → 在 Lesson 中额外增加 Worked Example
若 learner_model 中记录的 confidence_bias = "谨慎型" → 在讲解中增加鼓励性话语（如"你的判断值得信任，只需补充具体步骤"）
若 learner_model 中记录的 confidence_bias = "校准良好" → 保持标准讲解节奏
4. 若有快速回顾标记 → 在 Lesson 文件的 `### 〇、知识回引` 之前插入"### 〇、快速回顾"小节：
   ```markdown
   ### 〇、快速回顾

   > 诊断中发现你对"{missing_concept}"还不够清晰，这里先用一分钟补充一下：
   >
   > {用 2-3 句话 + 一个类比快速讲解缺失的概念}
   >
   > 了解这一点后，我们正式开始本课。
   ```
5. 检查 background.md 中是否有 Bloom 层级下调记录，若有，在 Lesson 文件元信息中标注实际目标层级

**4.1 逆向设计（生成新 Lesson 时执行）**：
1. 读取 `${SKILL_DIR}/references/bloom-taxonomy.md` 和 `${SKILL_DIR}/references/socratic-method.md`
2. 读取用户背景与教学偏好：
   - 读取 `${PROJECT_DIR}/settings/background.md` 获取基础背景和"教学偏好"区域
   - 偏好字段（教学语言、课时长度、题目数量、挑战题、反事实论证、学习模式）按以下优先级确定最终值：用户口头补充 > `background.md` 配置 > `session_state.json` 会话级覆盖 > 系统默认值
   - 若本次调用时用户补充了背景信息，与文件内容合并；冲突处以用户补充为准
3. 明确本节课目标："本节课结束后，用户应能解决什么具体问题？"
4. 从资料中提取知识点，结合历史记录和用户背景规划路径，确定目标布卢姆层级
5. **识别知识类型，匹配讲解策略**：

   对本课核心知识点，按以下规则判断知识类型并选择讲解策略：

   | 知识类型 | 判断规则 | 讲解策略 |
   |---------|---------|---------|
   | **概念性**（What/Why） | 核心问题是"X 是什么"或"为什么需要 X"（如：导数的定义、为什么需要 Transformer） | **动机铺垫** → 概念引出 → 直觉类比 → 形式化定义 |
   | **程序性**（How） | 核心问题是"怎么用 X"或"X 的操作步骤"（如：链式法则的使用、Git rebase 操作） | **规则陈述** → 分步演示 → **代码锚点映射** → **反模式演示** → 变式练习 |
   | **操作性**（API / 硬件 / 库调用） | 核心问题是"这个 API / 寄存器 / 库函数怎么用"（如：HAL_I2C_Mem_Write 用法、React useEffect 依赖项配置、STM32 寄存器操作） | **动机铺垫** → API 签名解析 → **代码锚点映射**（逐参数回引原理） → **反模式画廊**（错误代码 + 失败后果） → 变式练习 |
   | **原理性**（Why deeply） | 需要数学推导、逻辑证明或机制分析（如：反向传播推导、操作系统调度策略） | **问题驱动** → 逐步推导 → 关键步骤标注 → 回顾总结 |

   > **判断原则**：一个 Lesson 可能包含多种类型的知识点，以**占比最大的类型**决定主讲解策略。次要类型的知识点在讲解中穿插，不需要严格遵循其对应策略。
   >
   > **不要为程序性知识硬编叙事**：步骤类知识需要的是清晰拆解，不是故事铺垫。
   > **不要为事实记忆类知识过度铺垫**：API 参数、公式速查等直接用结构化表格/清单呈现。

   **5.5. 决定教学模式 A/B**（2026-04-18 新增 · 详见 `docs/plans/2026-04-18-scenario-closure-feynman-design.md`）：

   在确定讲解策略后，还需决定 lesson 的**结构模式**（写入元信息 `teaching_mode` 字段，取值 `A` 或 `B`）：

   | 模式 | 写入值 | 触发条件 | 结构 |
   |------|-------|---------|------|
   | **A 知识结构导向** | `teaching_mode: A` | 默认模式：概念性 / 原理性 / 单场景操作性 / 任何程序性 | §3.1, §3.2, §3.3 + Worked Example + 反模式画廊（当前既有结构） |
   | **B 场景闭环导向** | `teaching_mode: B` | 同时满足：① 知识类型为 `操作性`；② 涉及 **≥ 2 个独立可 ship 的场景/外设/模块**（每个能独立烧板、独立运行、独立验证） | §3.0 全局图景 + §3.X 场景闭环（每环 7 子节）+ §3.∞ 汇合升维 |

   **"独立场景" 判定准则**：
   - ✅ 算独立：EEPROM、OLED、AHT20 各有自己的 CubeMX 工程，可独立烧板（`04-stm32/18-i2c-eeprom/` vs `19-i2c-oled/` vs `20-i2c-aht20/`）
   - ✅ 算独立：UART1 轮询 / UART1 中断 / UART1 DMA 各有独立工程（`12-uart1-printf/` vs `13-uart1-key/` vs `16-uart1-dma/`）
   - ❌ 不算独立：同一 `main()` 里串行初始化并调用 EEPROM+OLED（逻辑耦合，只是 1 个场景）
   - ❌ 不算独立：基础用法 + 进阶用法（只是难度分层，仍属 1 个场景）

   **B 模式额外字段**：选择 B 时，同步生成 `scenario_closures` 数组，每项含 `name`（如 EEPROM）、`source_project`（如 `18-i2c-eeprom`）、`source_files`（如 `[Core/Src/eeprom.c]`）。

   **降级规则**：若元信息指示 B 但 `source_code_root` 未配置（见 §4.2 第 2 步 B 分支）→ 输出警告 + 降级为 A（AI 虚构代码模式）；**禁止**在 B 模式下虚构代码却不降级标注。

6. **生成概念标签（Concept Tags）**：为每个知识点生成一个简短、机器可读的 `concept_tag`（格式：`{topic}-{concept-name}`，如 `stm32-gpio-mode`、`c-pointer-arithmetic`）。每个 tag 唯一对应一个核心概念，用于绑定诊断题、lesson 元信息和 learner_model。
7. **识别前置依赖（Prerequisites）**：对每个 concept_tag，查询 roadmap_status.md 中哪些已学 lesson 包含相同的 concept_tag 或其相关概念。填写 `prerequisites: [lesson_{N}]`，若没有前置依赖则填写 `prerequisites: []`。
8. **查询学习者模型（Conditional）**：若 session_state.json 的 learner_model.concept_mastery 中已有相关 concept_tag 的记录，在 lesson 元信息中标注"⚠️ 该用户对此相关概念有薄弱记录（confidence_bias: {偏差类型}）"，并在讲解中针对性加强。

9. **确认 learn-first 输出策略**：

   在进入 §4.2 写文件之前，将 `session_state.json.current_mode` 写为 `"learn"`。新 lesson 默认使用 `templates/learn-card-template.md`，写入 `lessons/learn/`；练习和 deep 查阅按需拆到独立文件，不把所有教学活动塞进同一个 learner-facing 文档。

   **硬约束**：

   - **默认 learn**：任何新专题首次进入 Step 4 时，先生成 learn-card，不直接生成 deep 版。
   - **practice 按需**：用户完成 learn-card、要求更多练习，或诊断显示需要巩固时，生成 practice-pack。
   - **deep 按需**：只有用户要求“深入 / 查来源 / 看完整代码 / 完整推导”，或 learn-card 无法承载必要细节时，才生成 deep-reference。
   - **不恢复旧 core**：未经用户明确恢复旧流程，不写入 `lessons/core/`，不新增旧“精华版/core”文件；`core-lesson-rules.md` 只作为 reader-first 风格参考和历史会话维护资料。
   - **记录到对应列表**：learn-card 写入 `session_state.json.lesson_files_learn`；practice-pack 写入 `lesson_files_practice`；deep-reference 写入 `lesson_files_deep`；`lesson_files_core` 仅保留给历史会话兼容，不新增条目。
   - **旧会话兼容**：恢复已有 `current_mode == "core"` 的历史会话时，不自动删除或迁移旧文件；先告知用户现状，再按用户指令处理。

**4.2 Lesson 文件生成**：

**命名约定**（2026-04-18 新标准，全局生效）：

| 格式 | 用途 | 示例 |
|------|------|------|
| `learn/NN_描述.learn.md` | 默认学习入口 | `learn/06_四大总线对比.learn.md` |
| `practice/NN_描述.practice.md` | 练习包 | `practice/06_四大总线对比.practice.md` |
| `deep/NN_描述.deep.md` | 深入查阅 | `deep/06_四大总线对比.deep.md` |
| `NN_描述.md` | 旧 deep/legacy 单页课题 | `06_四大总线对比.md` |
| `NN.X_描述.md` | 旧 deep/legacy 多子课题拆分 | `02.0_I2C 协议原理.md`、`02.1_I2C 协议代码.md` |
| `lesson_N.md`（旧） | 向后兼容（旧 session 保留；新 session 禁用） | `lesson_1.md` |

- `NN`：2 位主题索引（01-99），`.X`：可选子课时索引（.0/.1/.2…）
- **实际文件名解析顺序**：
  1. 按 `session_state.json.current_mode` 读取对应列表：`lesson_files_learn` / `lesson_files_practice` / `lesson_files_deep` / `lesson_files_core`
  2. 若对应列表为空，回落到旧字段 `lesson_files[current_lesson-1]`
  3. 最后回落到旧约定 `lesson_{current_lesson}.md`
- 新生成课时必须写入与当前产物类型对应的 `session_state.json.lesson_files_learn` / `lesson_files_practice` / `lesson_files_deep`；旧 `lesson_files` 仅用于兼容历史会话

下文中所有“当前课时文件”均按上述解析顺序确定。

**预读：资料图索引**（强制先于写入 lesson 动作）：

- 若 `{session_dir}/image_index.json` 存在：读入内存，作为 §4.2.1 决策树第 1-2 步的查询源；按本课 concept_tag / 章节关键词在 `images[].description` / `tags` / `headings` 中搜索匹配的资料原图候选
- 若不存在（旧会话或 Step 3 同步失败）：跳过 §4.2.1 决策树第 1-2 步，直接进入第 3 步（生成 DrawIO）或第 4 步（不画图）
- ⚠️ **禁止**不读索引就生成 DrawIO——这是 §4.2.2 禁区 #11

**learn-first 章节生成契约（2026-04-27 调整）**：

- **一次只生成一个序号章节**：除非用户明确要求批量生成，否则每次只写当前一个 `NN_描述.learn.md`，不得顺手预生成后续编号。
- **源文覆盖表移出正文**：写 learn-card 前，先从学习材料中抽取本课覆盖的原始标题 / 小节 / 考点，生成“源文位置 → 本课落点 → 必须掌握到什么程度”表，写入 `source_coverage/{NN}_{slug}.md`。该表是防遗漏清单，不放进学习者主文档。
- **learn-card 只解决一个核心问题**：第一次学习不是覆盖资料，而是建立可迁移的心智模型；覆盖资料是 deep-reference / source_coverage 的任务。
- **实践过程以结果牵引**：每节课先定义一个可见小结果和最小闭环，按 `结果定义 -> 最小闭环 -> 按需补课 -> 反馈校准 -> 复盘沉淀 -> 迁移挑战` 组织 practice，不把“做出来”误判为“已掌握”。
- **练习独立承载**：learn-card 只保留 1-2 道小题和 80 字复述；完整渐进训练、掌握测试和改错题放入 practice-pack。
- **deep-reference 按需生成**：完整来源引用、完整代码、完整术语表、完整图表和长推导放入 deep-reference，避免挡在第一次学习前面。

1. 读取 `${SKILL_DIR}/templates/generator-rules.md`、`${SKILL_DIR}/templates/practice-process-rules.md` 与 `${SKILL_DIR}/templates/learn-card-template.md`
2. 按模板生成 `${PROJECT_DIR}/learning-history/${topic_name}_${timestamp}/lessons/learn/{NN}_{slug}.learn.md`，包含：
   - **一个核心问题**：标题直接回答“本节真正要解决什么”，不展示 `concept_tags`、状态协议或生成器元信息。
   - **学完能做什么**：一句具体任务，替代冗长学习目标；必须是可见结果，不写“学会 X”。
   - **最小闭环**：用 `输入 -> 处理 -> 输出 -> 反馈` 写出本节可验证路径。
   - **先猜一下**：用一个小问题、常见错误或现象暴露已有想法。
   - **一句话心智模型**：用 1 个类比或 1 条因果链讲清核心机制。
   - **最小例子**：只展示一个能说明核心问题的例子或 10-25 行核心代码。
   - **三个关键锚点**（条件触发：知识类型为 `操作性` 或 `程序性`）：只保留最容易写错的参数、最关键的 API 选择、最致命的边界条件；其余锚点进入 deep-reference。
   - **血的教训**：只保留 1 个最致命错误及其后果；完整反模式画廊进入 deep-reference。
   - **你来做**：只保留 1 道补一步题、1 道迁移题和 1 个 80 字复述。

   **多场景操作课拆卡规则**（替代旧 B 模式“一篇包多个闭环”）：

   a. 若一个课题含 2 个以上独立可运行场景，不把多个闭环塞进同一篇 learn-card。
   b. 每个场景单独生成一张 learn-card，例如 `02.1A_EEPROM.learn.md`、`02.1B_OLED.learn.md`。
   c. 共享基座和横向对比单独生成一张对比 learn-card，例如 `02.1X_I2C场景对比.learn.md`。
   d. 旧 `teaching_mode=B` 的 7 子节结构只允许用于 deep-reference 或历史 deep 课维护，不再作为默认 learner-facing 结构。

   **练习拆分规则**：
   - learn-card 只保留 1 道补一步题、1 道迁移题和 1 个 80 字复述。
   - 2-3 道 Completion Practice、3 道 Mastery Test、改错题和折叠答案移入 practice-pack。
   - practice-pack 使用 `${SKILL_DIR}/templates/practice-pack-template.md`，写入 `lessons/practice/`。
   - practice-pack 必须包含“最小闭环实践”：要做出的结果、验收标准、反馈信号、局部补课项、4 行复盘和至少 1 个迁移挑战。

   **诊断路由条件生成（Conditional Content）**：

   | 诊断路由 | 额外生成 | 省略生成 |
   |---------|---------|---------|
   | **Skip** | learn-card 更短：保留心智模型 + 1 个检查题 | practice-pack 可延后 |
   | **Compact** | 标准 learn-card | — |
   | **Full** | 标准 learn-card + 同步生成 practice-pack | — |
   | **Remedial** | 先前置补救课，完成后再生成主课（完整结构） | — |

   **横向概念对比（条件触发）**：在生成讲解内容时，若本课知识点存在以下情况之一，则在讲解中增加一个"概念辨析"段落（对比表 + 边界案例）：
   - 与前几课已学概念容易混淆（如：可导 vs 连续、栈 vs 队列）
   - 与同领域相关概念有对比价值（如：监督学习 vs 无监督学习）
   - 用户在 learner_model 中暴露了相关概念的 misconception_tags

**4.2.1 图表处理规则（强制执行）**：

所有 lesson 文件中的图片引用必须遵循以下硬性规则。违反任一条视为生成失败。

**存放路径规则**：

| 图表来源 | 物理存放位置 | 生成者 |
|---------|------------|-------|
| 资料原图（PDF / docx / html 转换出来的） | `{session_dir}/images/{hash}.jpg`（Step 1 预处理时从 `tmp/converted/{topic}_{ts}/images/` 复制过来） | 由 `scripts/indexer/build_image_index.py` 生成（见 Step 1 扩展） |
| AI 生成的理解性图示 | `{session_dir}/diagrams/{slug}.drawio` + 渲染出的 `{slug}.png` | learning-engine 调用 drawio skill 生成 |

- ❌ **禁止**把 AI 生成图存到项目根 `{PROJECT_DIR}/diagrams/`（会污染其他 session）
- ❌ **禁止**使用绝对路径（如 `/Users/.../diagrams/x.png`）或跨项目相对路径（如 `../../../diagrams/`）

**引用路径规则**（lesson 文件中的 `![...](...)` 语法）：

lesson 文件位于 `{session_dir}/lessons/lesson_N.md`，所以相对路径统一为：

| 图类型 | 引用语法 | 物理解析结果 |
|--------|---------|-------------|
| 资料原图 | `![{caption}](../images/{hash}.jpg)` | `{session_dir}/images/{hash}.jpg` |
| AI 生成图（png） | `![{caption}](../diagrams/{slug}.png)` | `{session_dir}/diagrams/{slug}.png` |

**引用决策树（按优先级从高到低）**：

| # | 条件 | 动作 |
|---|------|------|
| 1 | `{session_dir}/image_index.json` 中有上下文匹配的资料原图（匹配度：章节标题相似度 ≥ 0.6 或关键词重合 ≥ 2 个） | 直接引用原图：`![{caption}](../images/{hash}.jpg)` |
| 2 | 资料原图质量差（OCR 噪声、手绘模糊、扫描件旋转） | 引用原图 + 额外生成 DrawIO 理解性示意，两者并列放置；原图下方标注 `> ⚠️ 资料原图识别度低，下方为理解性示意` |
| 3 | 资料无对应图，但概念确实需要可视化（状态机 / 时序图 / 架构图 / 数据流） | 生成 DrawIO 存到 `{session_dir}/diagrams/`；引用用 `../diagrams/{slug}.png` |
| 4 | 文字、表格、代码块足以表达（如简单对比、API 参数说明） | **不画图**——避免无意义配图增加认知负荷 |

**特殊说明**：

- 若 `{session_dir}/image_index.json` 不存在（旧会话或 Step 1 未生成索引），跳过决策树 #1/#2，直接走 #3 或 #4
- 生成 DrawIO 时，文件名使用小写 snake_case 英文 slug（如 `i2c_sequence.drawio`），避免中文或空格
- lesson 中的每个图必须有明确的 caption，caption 应描述"图在教什么"而非"图是什么"（如 ✅"I2C 起始信号的下降沿时序" vs ❌"时序图"）

**4.2.2 生成后自检（强制执行）**：
Lesson 文件写入完成后，逐条核查讲解内容与习题中的每个细节：

| 情况 | 处理方式 |
|------|---------|
| 直接引用资料原文 | 保留 `> **资料原文**：` 引用块 + `[来源：{章节}]`（紧跟引用块） |
| 超出资料范围的补充内容 | 在该句/段末尾标注 `[⚠️ 当前资料未涉及此内容]` |
| 正文中基于资料的讲解/改写 | **不在正文中逐句标注**，改为在每个 `###` 大节末尾统一列出：`> 📖 本节参考：{章节1}、{章节2}` |

> **原则**：来源标注服务于可追溯性，但不应打断阅读流。正文中只出现**资料原文引用**和**资料未涉及警告**两种标注，其余来源在节尾汇总。

**来源标注完成后，继续执行以下多维度质检（逐条核查，不通过则修正后再写入文件）**：

**✅ 质检清单**：

| # | 检查项 | 判定标准 |
|---|--------|---------|
| 1 | 内容准确性 | 所有知识点可追溯到原材料或已标注"资料未涉及" |
| 2 | 难度适配 | 讲解深度、用词、举例与用户背景匹配（不低幼也不超纲） |
| 3 | 布卢姆层级匹配 | 习题确实考察本课声明的目标认知层级，而非更低层级 |
| 4 | 讲解有层次 | 内容有清晰的逻辑推进（因果/递进/对比），不是信息平铺堆砌 |
| 5 | 习题有区分度 | 每道习题考察不同侧面或不同难度，不是换皮重复 |
| 6 | 推理链完整 | 从前提到结论的每一步都显式写出，无逻辑跳跃 |

**🚫 教学绝对禁区（出现任何一条即修正）**：

| # | 禁止行为 | 说明 |
|---|---------|------|
| 1 | 用术语解释术语 | 如用"闭包是词法作用域的延续"解释闭包——循环定义，读者无法从中获得新信息 |
| 2 | 跳过推理中间步骤 | 如"由 A 显然可得 C"——必须写出 A→B→C 的每一步 |
| 3 | 用"显然""不难看出""容易证明"掩盖逻辑跳跃 | 这些词是"我懒得解释"的伪装，在教学中绝对禁止 |
| 4 | 习题与讲解内容不匹配 | 习题考察的知识点必须在本课讲解中覆盖过 |
| 5 | 过度概括导致信息密度为零 | 如"这是一个非常重要的概念，在很多领域都有应用"——空话，必须具体 |
| 6 | 编造函数名、类名、文件路径、API 参数 | 所有代码符号必须在学习资料中实际存在或明确标注为示意 |
| 7 | 讲解中引入未经铺垫的前置概念 | 如果用到了本课未讲、前几课也未覆盖的概念，必须先做最小化解释 |
| 8 | 操作性/程序性 Lesson 呈现代码但未配「代码锚点映射表」 | 代码块后必须跟映射表，将魔数/API/宏/参数逐项回引到原理位置；否则用户"为什么这样写"的疑问无法闭合，代码变成"背诵式例程" |
| 9 | 操作性/程序性 Lesson 缺少「反模式画廊」子节 | 仅呈现"正确代码"无法独自回答"为什么这样写"；必须配合至少 2 个"错误代码 + 失败后果 + 违反原理"的镜像组 |
| 10 | 图表引用路径错误（绝对路径 / 跨项目相对路径 / 指向项目根 `diagrams/`） | 违反 §4.2.1 存放路径规则；lesson 中的图片链接必须为 `../images/*.jpg` 或 `../diagrams/*.png`，解析后能在 `{session_dir}/images/` 或 `{session_dir}/diagrams/` 找到实际文件 |
| 11 | 跳过资料原图检索直接生成 DrawIO | 不读 `{session_dir}/image_index.json` 就自行生成新图是 003 session 的历史 bug；必须先执行 §4.2.1 决策树的第 1-2 步，已用尽方可进入第 3 步生成 |
| 12 | B 模式生成的 lesson 同时保留 `[模式 A]` 和 `[模式 B]` 段 | 违反 §4.2 第 2 步规则：`teaching_mode` 只能选一个，必须删除另一模式的整段；同时保留会让学员读到两套结构互相矛盾 |
| 13 | B 模式 §3.X.2 粘贴超过 60 行单段源码 或 粘贴 CubeMX 模板文件（msp/it/hal_conf） | 违反精瘦模式（lesson-template.md 附录 B.2）；应改为核心片段 + 未展示段说明 + 配套文件列表 |
| 14 | B 模式某闭环 §3.X.6 缺少三选二结构（只给了 1 或 2 个选项） | 违反 Feynman B 档规则；必须生成 a · 文字 / b · 拍照 / c · 代码改写 完整 3 项，学员从中选 2 项完成 |
| 15 | B 模式未创建 `{lesson_file_stem}_notes/` 目录与 `my_notes.md` 骨架 | 违反 §4.2 第 2 步 g 条；学员没有地方写独特笔记，Feynman 循环断裂 |
| 16 | B 模式 §3.X.2 源码引用缺少 `{file}:{start}-{end}` 行号标注 或 HAL 版本 | 违反 lesson-template.md 附录 B.1；行号缺失使学员无法打开 Keil 对照；HAL 版本缺失使未来升级后代码差异无法追溯 |
| 17 | B 模式 `scenario_closures` 数量 < 2 | 单场景应使用 A 模式；B 模式的价值前提是 "多闭环的横向 & 纵向对比"，单闭环只会引入无意义的 §3.0 全局图景节 |

**📐 排版可读性规则（生成 Lesson 时强制执行）**：

| # | 规则 | 示例 |
|---|------|------|
| 1 | **序号列表独占一行**：使用 ①②③ 或 1. 2. 3. 列举时，每项必须独占一行，不得将多项挤在同一行 | ① 第一点；<br>② 第二点 |
| 2 | **逻辑段落用空行分隔**：不同逻辑层次（问题陈述 / 列举 / 分析 / 结论）之间用空行断开，不要写成一整段 | 问题：……<br><br>① ……<br>② ……<br><br>结论：…… |
| 3 | **结论金句独立成段**：总结性的关键结论（通常加粗）单独成段，不附在分析段落末尾 | **多用 2 根线，换来了 10-100 倍的速度提升。** |
| 4 | **长句拆短**：单句超过 80 字时，寻找语义断点拆为两句或用破折号/分号断开 | — |
| 5 | **表格优先于长句并列**：3 个以上并列项的对比，用表格而非逗号分隔的长句 | — |
| 6 | **代码块前后留空行**：代码块（含行内代码引用的完整语句）的上下各留一个空行 | — |
| 7 | **反事实论证格式**：`**反事实论证**：{问题}` 后空一行，再写分析段落，分析与结论之间再空一行 | 见 lesson_4 §1.2 |
| 8 | **ASCII 文字图中英混排**（2026-04-18 新增）：**协议标识符 / 寄存器名 / 位名 / API 签名 / 信号名**等技术术语**一律用英文**保持字符对齐（如 `S`、`ADDR(N, W)`、`ACK`、`NACK`、`DATA[0]`、`REG_ADDR`、`HAL_I2C_Mem_Write`），**禁止**把中文塞进单行箭头链。中文只能出现在：① 图**正下方**的阶段说明（如 `第一次（写地址指针）`）② 节点**后括号**内的语义注解（如 `(双向数据)`）③ 概念树的**抽象分类节点**（如"物理层"、"协议层"、"边界信号"）。概念树节点应与 §9.2 反引号关键词保持一致 | 流程图样式见 `02.0_I2C 协议原理.md` §3.8；概念树样式见同文件 §9.1 |

自检完成后更新文件，**不在对话中展示自检结果**，仅在通知中附加一行自检摘要：
```
🔍 自检完成：{N} 处已标注来源，{M} 处标注"当前资料未涉及"，质检 {P}/6 项通过，禁区 0 项触发
```

写入 lesson 文件后，还必须运行机器门禁：

```bash
python scripts/lesson_lint.py <lesson_file_or_session_dir>
```

新生成 learn-card / practice-pack / deep-reference 若出现 `unresolved_placeholder`、`file_driven_protocol`、`image_path_contract` 或 `learn_*` / `practice_*` / `deep_*` 报错，先修正文件，再重新运行 lint。`core_*` 只用于历史 core 文件维护；不得把新 lesson 改写成旧 core 结构来通过检查。

**4.2.3 learn-first 自检补充**：

新生成 learner-facing 文档必须执行 `${SKILL_DIR}/templates/generator-rules.md` 的 learn-card 限制：主文档不展示状态协议、生成器规则、完整来源覆盖表、完整术语表和附录。若目标路径、命名或状态字段仍指向 `lessons/core/` / `lesson_files_core`，先改回 learn-first 生成路径与 `lesson_files_learn`，再继续 §4.2.2 的通用自检。

3. 生成后，**不在对话中展示课程内容**，仅发送通知：
   ```
    ✅ Learn-card {index} 已生成！

    📄 文件位置：`./learning-history/${topic_name}_${timestamp}/lessons/learn/{NN}_{slug}.learn.md`

    请阅读该文件，在"我的答案"区域填写答案，保存文件后，在对话窗口告诉我"已完成"。
   ```

⛔ **BLOCKING**: 等待用户在对话中说"已完成"、"做完了"、"写完了"等表述。

**4.3 答案检查（用户说"已完成"后执行）**：

1. 读取当前课时文件，提取所有"我的答案"区域内容：
   - `learn` 模式：批改补一步题、迁移题和 80 字复述
   - `practice` 模式：批改检索题、迁移题、改错题和复述题
   - `deep` / legacy 模式：按 Completion Practice 和 Mastery Test 批改
2. 若所有"我的答案"区域均为空 → 提示用户先去文件中填写，重新 BLOCKING
3. **渐进训练批改（Completion Practice 部分）**：
   - 评估方式：用户是否正确填写了空缺步骤？每填对一个得 1 分
   - 结果：统计 Completion Practice 正确率
4. **掌握测试批改（Mastery Test 部分）**：

   **双维度评估每道题**：

   | 维度 | 判定标准 |
   |------|---------|
   | 正确性 | 答案的结论/结果是否正确 |
   | 解释完整性 | 答案是否包含关键推理步骤，而非只有结论 |

   评估结果分为三档：
   - **完全正确**：结论正确 + 解释完整 → 给予肯定
   - **部分正确**：结论正确但解释缺失关键步骤，或结论有小误但思路正确 → 指出不足
   - **错误**：结论错误且思路偏离 → 执行错误自解释脚手架

5. **错误自解释脚手架（渐进训练和掌握测试均适用）**：

   当答案为"部分正确"或"错误"时，在给出初步反馈后，追加半结构化追问：
   ```
   💡 错误分析（请在对话中回答）：
   你觉得这个错误属于以下哪种类型？
   ① **概念理解偏差** — 你对某个核心概念的理解本身就有偏差
   ② **步骤/程序遗漏** — 你知道怎么做，但漏掉了某个关键步骤
   ③ **条件边界没注意** — 你没有仔细看清题目条件或忽略了边界情况
   ④ **计算/符号失误** — 思路对，但手滑了（粗心错误）
   ```
   - 收到用户回答后，根据类型提供针对性引导（不在 lesson 文件中修改）
   - 若用户选择"① 概念理解偏差"，在下一课开头针对性复习相关 concept_tag
   - 若用户选择"② 步骤遗漏"，提供部分步骤框架让用户补全
   - 若用户选择"③ 条件边界"，引导重新审题
   - 若用户选择"④ 计算失误"，确认即可，视为基本掌握
   - 若用户无法判断类型 → 苏格拉底式追问

6. **掌握判定**：

   | 部分 | 权重 | 达标标准 |
   |------|------|---------|
   | 渐进训练（Completion Practice） | 40% | ≥ 60% 步骤填对 |
   | 掌握测试（Mastery Test） | 60% | ≥ 60% 达到"完全正确"或"部分正确" |

   综合掌握度 = 渐进训练分 × 0.4 + 掌握测试分 × 0.6

   | 综合掌握度 | 结果 | 行动 |
   |-----------|------|------|
   | ≥ 80% | **掌握** | 进入下一课 |
   | 60-79% | **基本掌握** | 进入下一课，但在下一课开头补充缺失知识点 |
   | < 60% | **未掌握** | 重新尝试掌握测试（不重做 Completion Practice） |

   标注为"⭐ 挑战题"的习题不计入掌握判定。
7. **批改结果持久化 + learner_model 更新**（掌握判定完成后立即执行）：
   - 在每道题的"我的答案"区域下方，追加批改块，**每条逐项评价必须以状态符号开头**：
     ```
     > **批改 ⭐⭐⭐⭐（{score}/5）**
     > - ✅ {正确的点}
     > - ⚠️ {部分正确/小瑕疵}
     > - ❌ {错误的点}
     ```
     状态符号规则：✅ 完全正确 | ⚠️ 方向对但有瑕疵/不完整 | ❌ 错误
   - 在 lesson 文件的 `## 掌握度反馈` 区域，追加评分汇总表：
     ```
     ## 掌握度反馈

     ### 渐进训练（Completion Practice）
     | 题目 | 得分 |
     |------|------|
     | Completion Practice 1：{title} | ✅/⚠️/❌ |
     | Completion Practice 2：{title} | ✅/⚠️/❌ |
     | **小计** | **{CP_correct}/{CP_total} = {CP_rate}%** |

     ### 掌握测试（Mastery Test）
     | 题目 | 正确性 | 解释完整性 | 综合 |
     |------|--------|-----------|------|
     | 测试题 1：{title} | ✅/⚠️/❌ | ✅/⚠️/❌ | ⭐×{N}/5 |
     | 测试题 2：{title} | ✅/⚠️/❌ | ✅/⚠️/❌ | ⭐×{N}/5 |
     | 测试题 3：{title} | ✅/⚠️/❌ | ✅/⚠️/❌ | ⭐×{N}/5 |
     | **小计** | — | — | **{MT_avg}/5** |

     ### 综合掌握度
     | 部分 | 得分 | 权重 |
     |------|------|------|
     | 渐进训练 | {CP_rate}% | 40% |
     | 掌握测试 | {MT_rate}% | 60% |
     | **综合** | **{final_rate}%** | 100% |

     **判定**：✅掌握 / ⚠️基本掌握 / ❌未掌握
     ```
   - **更新 learner_model**：对每个 concept_tag，更新 `session_state.json` 的 `learner_model.concept_mastery[concept_tag]`：
     - `test_count` += 1
     - `correct_count` += 1（若测试题达到"完全正确"）
     - `mastery_level` ← 根据掌握度更新
     - 若错误自解释中用户选择了"概念理解偏差"，在 `misconception_tags` 中追加相关标签

8. **Feynman 闭环批改**（仅 `teaching_mode=B` 时执行 · 2026-04-18 新增）：

   **触发条件**：lesson 元信息 `teaching_mode=B`，且 `{lesson_file_stem}_notes/` 目录存在。

   **批改流程**（对每个 `scenario_closures[i]`，即每个闭环）：

   a. **读取学员输出**：
      - 选项 a 文字：读 `{lesson_file_stem}_notes/my_notes.md` 中 §3.{i+1} 节 `Feynman 输出 → a · 5 要素` 子节
      - 选项 b 拍照：`{lesson_file_stem}_notes/photos/*_{closure_slug}_*.jpg` 列表（Windsurf 原生读图）
      - 选项 c 代码：`{lesson_file_stem}_notes/exercises/{closure_slug}_*.{ext}` 文件
      - 若 3 项都未提交 → 提示学员至少完成 2 项，BLOCKING
      - 若只提交 1 项 → 同上
      - 若提交 ≥ 2 项 → 进入 b

   b. **对每个已提交的选项批改**：

      | 选项 | 批改维度 | 评分范围 |
      |------|---------|---------|
      | a · 文字小结 | 覆盖度（5 要素齐全）/ 独立性（非抄课文）/ 准确度（概念没说错） | 每项 0-5 分 |
      | b · 手绘拍照 | 关键信号覆盖（`S/ADDR/ACK/P/Sr` 等是否全）/ 布局清晰 / 无关键遗漏 | 每项 0-5 分 |
      | c · 代码改写 | 静态分析：是否落实 §三 开头 10 项审查清单 / 边界处理是否完整 / 注释是否标原理引用 | 每项 0-5 分 |

      综合评分 = 已提交 2 项的平均分。

   c. **决定闭环通过状态**：

      | 综合评分 | 状态 | 追加到 lesson 文件 §3.{i+1}.7 |
      |---------|------|----------------------------|
      | ≥ 80% | ✅ 通过 | `- [x] ✅ 通过（覆盖度 {X}%）→ 进入 §3.{i+2}` |
      | 60-79% | ⚠️ 有盲点 | `- [x] ⚠️ 有盲点（覆盖度 {X}%）→ 可选回读 §3.{i+1}.3 / §3.{i+1}.4` + 记入 `review_queue` |
      | < 60% | ❌ 未通过 | `- [x] ❌ 未通过（覆盖度 {X}%）→ 必须回读 §3.{i+1}.3 / §3.{i+1}.4 后重做 §3.{i+1}.6` |

   d. **生成批改反馈**（追加到 my_notes.md 的 §3.{i+1} "AI 批改反馈" 子节，不覆盖学员原文）：

      ```markdown
      ### AI 批改反馈（{YYYY-MM-DD HH:mm}）

      **综合评分**：{score}/100（{status}）

      **逐项反馈**：
      - 选项 a · 文字小结：{score}/5
        - ✅ {正确的点}
        - ⚠️ {改进建议}
      - 选项 b · 手绘：{score}/5
        - ✅ {画对的关键信号}
        - ⚠️ {遗漏或画错的点}
      - 选项 c · 代码改写（若提交）：{score}/5
        - ✅ {落实的审查项}
        - ❌ {未落实的审查项 → 对应 §三 审查清单第 N 条}

      **建议回读**：{section_refs}
      ```

   e. **feynman_gap 加入 review_queue**（覆盖度 < 80% 时）：

      ```json
      {
        "id": "review_{NNN}",
        "lesson": "{lesson_file_stem}",
        "closure": "{closure_name}",
        "source": "feynman_gap",              // 新枚举值，区别于 mastery_test_gap
        "concept_tags": ["{tag_1}", "{tag_2}"],
        "gap_reason": "{文字描述，如 'Feynman 代码改写中遗漏 CRC 校验'}",
        "first_wrong_at": "{ISO8601}",
        "next_review_at": "{first_wrong_at + 3 天}",
        "review_count": 0,
        "status": "pending"
      }
      ```

   f. **learner_model 更新**：对本闭环的每个 `concept_tag`，在 `concept_mastery[tag].feynman_outputs` 追加一条：

      ```json
      {
        "lesson": "{lesson_file_stem}",
        "closure": "{closure_name}",
        "options_submitted": ["a", "b"],      // 或 ["a", "c"] / ["b", "c"]
        "score": {score},
        "ai_feedback_summary": "{一句话总结}",
        "submitted_at": "{ISO8601}"
      }
      ```

   **批改原则**（防止 AI 批改变"给答案"）：

   - ✅ **指出盲点**：说清楚"你漏了什么"、"哪里画错了"、"哪项审查清单没落实"
   - ✅ **给回读范围**：告诉学员去 §3.X.3 / §3.X.4 的哪个小节补
   - ❌ **不直接给答案**：不直接写出学员该补的文字 / 该画的信号 / 该写的代码
   - ❌ **不用模糊话术**：禁用"可以更好"、"还有进步空间"；必须具体到点

**4.4 动态支架**：

**降级触发**（满足任一条件）：
- 用户连续两次回答"不知道"或表现困惑
- 用户答案方向完全偏离（非粗心，而是概念理解错误）
- Reflection 中认知难度 ≥ 4

**降级策略（按优先级尝试，不只是降布卢姆层级）**：

| 策略 | 适用场景 | 操作 |
|------|---------|------|
| 换角度讲解 | 用户理解了部分但卡在某个点 | 用类比、可视化描述、生活化例子重新解释同一概念，不降低层级 |
| 分步拆解 | 用户面对的问题太大，不知从何下手 | 将复杂问题拆为 2-3 个更小的子问题，逐步引导 |
| 提供脚手架 | 用户有思路但无法完整表达 | 给出部分答案框架（如推导的前两步），让用户补全关键部分 |
| 降低布卢姆层级 | 以上策略无效，用户仍无法推进 | 从"分析/应用"退回"理解/记忆"，先确认基础再重新推进 |

> **原则**：优先保持当前认知层级不变，通过换讲法解决问题；只有在确认用户基础不牢时才降级。

**升级触发**（满足任一条件）：
- 用户连续两课一次性全部答对且解释完整
- Reflection 中认知难度 ≤ 1

**升级操作**：下一课主动提升布卢姆层级，或在习题中增加 1 道高于当前目标层级的挑战题（标注为"⭐ 挑战题"，不计入掌握判定）

**补救课与偏题分支文件命名规则**：

当动态支架的降级策略仍无法解决问题（连续 2 课 mastery < 60%），或用户明确要求深入偏题时，可生成非主线 lesson 文件：

| 类型 | 文件命名 | 触发条件 | roadmap 标记 |
|------|---------|---------|-------------|
| 🔧 补救课 | `lesson_{N}_remedial.md` | 连续 2+ 课 mastery < 60%，需回顾基础 | `🔧 补救课` |
| 🔀 偏题分支 | `lesson_{N}_branch.md` | 用户要求深入偏题探索 | `🔀 分支课` |

生成后必须同步更新：
1. `roadmap_status.md` 的"学习历史"表格：追加补救课/分支课行，备注触发原因
2. `roadmap_status.md` 的"路线调整记录"表格：记录调整类型、触发原因、影响
3. `_ai_context.md`：追加教学决策日志条目

> **补救课/分支课不计入 `session_state.json` 的 `current_lesson` 编号递增**，它们是主线的插入节点。完成后回归主线时，`current_lesson` 继续从中断处递增。

**4.4.1 主线优先与偏题处理（强制执行）**：

回答用户提问前，先对照 `roadmap_status.md` 中的当前主线任务判断相关性：

| 判断结果 | 处理方式 |
|---------|---------|
| 与主线强相关 | 正常回答，可深入展开 |
| 与主线弱相关或无关 | 执行偏题处理流程（见下） |

**偏题处理流程**：
1. 在 `summary.md` 的 `⏳ 待解决` 区域追加记录：
   ```
   - {用户问题摘要}（待主线任务结束后再解决）
   ```
2. 在对话中回复：
   ```
   这是一个很有趣的问题，但与我们本次的学习目标不强相关。我已经帮你记录下来了，待我们完成主线任务后再回来探索。
   ```
3. 将对话引导回当前主线任务

**4.5 进度更新（每个 Lesson 完成后执行）**：
1. 更新 `summary.md`：
   - 新增本次结论与未竟难点
   - **错题记录持久化**：将 4.3 答案检查中评估为"部分正确"或"错误"的习题，追加到 `summary.md` 的"错题记录"表格中，每行包含：课时、题号、错误摘要（一句话概括错在哪）、错误类型（概念/程序/推理）、状态（❌ 未纠正）。若用户在重新尝试后纠正了错误，将对应行的状态更新为 ✅ 已纠正
   - **复习队列更新**：将"部分正确"或"错误"的习题追加到 `review_queue.json` 的 `items` 数组，字段包括 `id`（`review_{NNN}`）、`lesson`、`question_index`、`topic_tag`、`first_wrong_at`、`corrected_at`（若已纠正）、`next_review_at`（纠正后 +1 天）、`review_count`（0）、`status`（`"pending"` 或 `"resolved"`）。纠正后的条目：`next_review_at` = 纠正时间 + 1 天，`status` = `"pending"`；复习通过后：`review_count` += 1，`next_review_at` = 当前时间 + `2^review_count` 天（间隔重复）
2. 更新 `roadmap_status.md`：更新进度百分比与导航坐标
3. **更新 `_ai_context.md`**：
   - 更新断点恢复信息（最后完成课时、当前课时状态、未纠正错题数）
   - 更新用户画像快照（根据本课答题表现修正错误模式分析、认知偏好）
   - 追加教学决策日志（如触发了动态支架、插入了补救课等关键决策）
4. **更新 `session_state.json`（状态唯一权威源，v2.3）**：
   - `current_lesson` ← 下一课编号
   - `phase` ← `"learning"` / `"review"` / `"completed"`（视当前阶段）
   - `last_completed_lesson` ← 刚完成的课时编号
   - `mastery_passed` / `mastery_failed` ← 累加本课答题结果
   - `mastery_rate` ← `mastery_passed / (mastery_passed + mastery_failed)`
   - `wait_reason` ← `"awaiting_answer"` / `null`（视是否等待用户答题）
   - `wait_detail` ← 具体等待上下文（如 lesson_id、mode、message）；不要把业务化字符串塞进 `wait_reason`
   - `updated_at` ← 当前时间戳
   - 若为 Git 仓库学习：`repo_commit_hash` ← 当前 HEAD commit hash
5. **追加 `metrics.json` 事件**（若文件不存在则从 `metrics-template.json` 初始化）：
   ```json
   {
     "event": "lesson_completed",
     "timestamp": "<ISO 8601>",
     "lesson": <lesson_index>,
     "mastery_passed": <本课通过题数>,
     "mastery_failed": <本课失败题数>,
     "scaffold_triggered": <true/false>,
     "counterfactual_used": <true/false>,
     "review_triggered": <true/false>,
     "remedial_inserted": <true/false>
   }
   ```
6. **状态一致性自检（强制执行）**：
   写入所有文件后，逐条验证以下不变量，任何一条不通过则立即修正：

   | # | 不变量 | 检查方式 |
   |---|--------|---------|
   | 1 | `session_state.json` 的 `current_lesson` 与 `lessons/` 目录下实际存在的最新 lesson 文件编号一致 | 列出 `lessons/` 目录，取最大编号对比 |
   | 2 | `_ai_context.md` 的"当前课时状态"与 `session_state.json` 的 `phase` 一致 | 读取两个文件对比 |
   | 3 | `roadmap_status.md` 的"当前课时"与 `session_state.json` 的 `current_lesson` 一致 | 读取两个文件对比 |
   | 4 | `summary.md` 的"已完成课时"与 `session_state.json` 的 `last_completed_lesson` 一致 | 读取两个文件对比 |
   | 5 | 若 `phase` 为 `"learning"` 且 `current_lesson` > 0，则对应 lesson 文件必须存在 | 检查文件是否存在 |

   > **自检结果不在对话中展示**，仅在 CHECKPOINT 中附加一行：`🔒 状态自检：{N}/5 项通过`
   >
   > **脚本辅助（推荐）**：可直接运行 `python scripts/session/validate_state.py <session_dir>` 得到完整校验报告；CI 环境中该脚本也用于守护新生成的会话。
   > 若发现历史会话可能漂移，先运行只读审计 `python scripts/session/reconcile_state.py <session_dir>`；只有确认后才加 `--fix-lesson-files` 或 `--fix-wait-reason` 写回。

7. **读取反馈**：检查当前课时文件中是否存在 `## Reflection`、`80 字复述` 或其他难度反馈区域，若用户填写了认知难度或需要澄清的内容：
   - 认知难度 ≥ 4 → 触发 4.4 动态支架的降级策略
   - 认知难度 ≤ 1 → 触发 4.4 动态支架的升级机制
   - 用户提出需要澄清的内容 → 在下一课开头增加针对性补充讲解
8. 若话题偏离主线 → 提示："我们正在偏离原定目标，是否将其作为新分支记录，还是回到主线？"
9. **每 3 课审视 Roadmap（当 lesson_index 为 3 的倍数时执行）**：
   - 读取 `summary.md` 中的"待攻克难点"和"错题记录"
   - 读取 `roadmap_status.md` 中后续待学习的知识点列表
   - 判断：是否存在持续未解决的薄弱前置知识？若是，在 roadmap 中当前位置插入一节补救课程（标注为"🔧 补救课"），优先于后续新内容
   - 判断：已完成的课程中是否暴露出 roadmap 未覆盖的重要知识缺口？若是，在 roadmap 中追加对应知识点
10. **知识回引与横向对比（每课执行）**：在生成下一个 Lesson 时，检查本课知识点与其他知识点的关联，并根据**对比方向**选择不同策略：

   **对比方向规则**：
   | 方向 | 定义 | 允许的形式 | 禁止的形式 |
   |------|------|-----------|-----------|
   | **回溯对比**（本课 vs 已学概念） | 对比对象在前几课中已完整讲授 | 完整对比表、深度分析、选型指南 | 无 |
   | **前向预告**（本课 vs 未学概念） | 对比对象将在后续课程中才学习 | 仅限一句话结构性提示（如"I2C 用最少的线换协议复杂度，后面我们会学另一种做了相反取舍的总线"） | ❌ 禁止引入未学概念的专有术语，❌ 禁止参数级对比表 |
   | **课内对比**（本课多个概念互比） | 对比对象在同一课中讲授 | 完整对比表、深度分析 | 无 |

   **执行逻辑**：
   - 若本课概念是前几课某概念的深化、应用或对立面 → **回溯对比**：在讲解开头增加回引 + 插入对比表
   - 若本课概念与后续未学概念有关联 → **前向预告**：仅用一句话点出设计哲学差异，激发好奇心但不增加认知负荷
   - 若无明显关联 → 不强行回引或对比，保持讲解简洁
   - 若当前课时为 roadmap 中标注的"横纵交汇课" → 不引入新知识，整合已学内容，必须包含完整矩阵对比表 + 选型决策树 + 真实场景选型习题
11. 生成下一个 Lesson 文件，重复 4.2 流程

✅ **Step 4 完成**：Lesson {index} 已掌握（X/Y 题），详情见文件。

→ **继续下一 Lesson** 或 **用户退出 → 进入 Step 5**

---

### Step 5: 生成学习报告 (Learning Report)

🚧 **GATE**: 用户明确表示学习完成或阶段性退出；`summary.md` 和 `roadmap_status.md` 已更新至最新状态。

🛠️ **EXECUTION**:

1. 读取 `${SKILL_DIR}/templates/report-template.md`
2. 读取 `summary.md` 和 `roadmap_status.md` 获取完整学习数据
3. 生成报告文件：`${PROJECT_DIR}/learning-history/${topic_name}_${timestamp}/report.md`，包含：
   - **目标达成度**：初始目标 vs 实际进度的可视化对比
   - **掌握明细表**：Lesson 编号、名称、认知层级评分（1-5 ⭐）、后续建议
   - **能力增长图谱**：描述用户从"不会"到"掌握"的认知迁移路径
   - **进阶规划**：基于 `summary.md` 中的难点，推荐下一个关联学习主题

4. **GitHub 项目学习可选工程产物**（仅当学习资料为 GitHub 项目/本地目录时）：
   - 若用户在学习过程中表达了"想参与贡献"、"想改代码"、"想读源码"等意图，按需生成：
     - `architecture_map.md`（从 `architecture-map-template.md`）：模块依赖 Mermaid 图 + 数据流 + 技术栈
     - `file_reading_order.md`（从 `file-reading-order-template.md`）：推荐阅读顺序 + 可跳过文件 + 首次贡献建议
   - 这些文件生成在会话目录根级（与 `report.md` 同级）
   - 若用户未表达相关意图，则不生成

报告已生成：
- 📄 `report.md`：`./learning-history/${topic_name}_${timestamp}/report.md`
- 目标达成度：{N}/6 Lessons | 掌握率：{X/Y} 题 | 用时：{duration}

→ **进入待命状态**，随时可以继续学习或退出。

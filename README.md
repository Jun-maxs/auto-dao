# 🎓 auto-dao — AI 私人导师

> 能规划、能诊断、能动态调整的 AI 私人导师

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ 功能特点

| 功能 | 说明 |
|------|------|
| 📚 **学习路线规划** | 根据学习材料自动生成个性化学习路径 |
| 🔍 **学习诊断** | 通过习题检验掌握程度，找出薄弱环节 |
| 🔄 **动态调整** | 根据反馈自适应调整难度和进度 |
| 📝 **自动笔记** | 学习过程中自动记录要点和重难点 |
| 🌍 **跨语言教学** | 支持学习材料与教学语言不同 |
| 🎯 **文件驱动** | 所有内容保存在文件中，防止 AI 幻觉 |

---

## 📦 快速安装

### 1. 克隆项目

```bash
git clone https://github.com/Jun-maxs/auto-dao.git
cd auto-dao
```

### 2. 安装 Python 依赖（可选）

仅在使用文件转换或校验脚本时需要：

```bash
pip install -e .
```

> **注**：本项目为 Python-first。`package.json` 仅作为 `npm run convert` 的便捷入口，不依赖 Node.js 生态。

### 3. 配置 API Key（可选）

编辑 `settings/.env`，填入 MinerU API Key（仅转换 PDF/Word/PPT 时需要）：

```env
MINERU_API_KEY=你的API密钥
```

👉 获取 Key：https://mineru.net/apiManage/token

### 4. 个性化配置

复制 `settings/background.example.md` 为 `settings/background.md`（该文件不会提交到 Git），填入你的背景信息：

```markdown
## 正在读的年级
大三

## 正在学习的科目、知识等
C 语言、STM32、ESP32、嵌入式 Linux

## 目前遇到的问题
C 语言基础不牢，需要完善 STM32+ESP32 技术栈
```

---

## 🚀 开始使用

在 Qwen Code 或任意 AI 助手中，直接提供学习材料并说明学习目标即可。

**示例：**
```
我想学习 STM32 开发，材料在 ./tmp/stm32-tutorial.md
我的背景：大三物联网专业，C 语言基础一般
```

AI 会自动：
1. 生成个性化学习路线
2. 创建讲义和习题
3. 批改你的习题并诊断学习情况
4. 根据反馈动态调整教学

---

## 📂 支持的学习材料

| 类型 | 示例 |
|------|------|
| Markdown 文件 | `./tmp/notes.md` |
| PDF 文档 | `./tmp/textbook.pdf` |
| Word / PPT | `./tmp/slides.pptx` |
| 图片 | `./tmp/notes.jpg` |
| 源码文件 | `./tmp/main.py` |
| 本地项目 | `./tmp/my-project/` |
| GitHub 链接 | `https://github.com/user/repo` |

---

## 🛠️ 可用 Skills

| Skill | 功能 | 说明 |
|-------|------|------|
| **learning-engine** | 主学习引擎 | 规划路线、生成讲义、批改习题 |
| **everything-to-markdown** | 文档格式转换 | PDF/Word/PPT → Markdown |
| **glossary-collector** | 术语表提取 | 提取专业词汇生成对照表 |
| **markdown-refiner** | Markdown 质量优化 | 修标题层级、清 OCR 噪声、修表格公式 |

---

## 📁 目录结构

```
auto-dao/
├── .claude/skills/              # Skills 定义（供 AI 参考）
│   ├── learning-engine/         # 学习引擎
│   ├── everything-to-markdown/  # 文档转换
│   ├── markdown-refiner/        # Markdown 质量优化
│   └── glossary-collector/      # 术语提取
├── settings/                    # 用户配置
│   ├── .env                     # API Keys（不提交到 Git）
│   ├── .env.example             # API Keys 配置模板
│   ├── background.example.md    # 用户背景信息模板
│   ├── background.md            # 用户背景信息（本地文件，不提交）
│   └── glossary.md              # 术语表
├── learning-history/            # 学习记录（自动生成）
│   └── {topic}_{timestamp}/
│       ├── summary.md           # 学习摘要
│       ├── roadmap_status.md    # 学习路线图
│       ├── report.md            # 学习报告（学习完成后生成）
│       ├── source_coverage/     # 来源覆盖表（给 AI/老师查漏）
│       └── lessons/
│           ├── learn/           # 默认学习入口：短文档，先学会
│           ├── practice/        # 练习包：检索、迁移、改错
│           └── deep/            # 深入查阅：完整来源、代码、推导
├── examples/                    # 示例学习记录
└── tmp/                         # 学习材料存放处
```

---

## 💡 使用技巧

### 1. 文件驱动学习
- 默认先读 `lessons/learn/*.learn.md`，需要更多练习再看 `practice/`，需要完整来源再看 `deep/`
- 所有讲义和习题保存在 `learning-history/` 的文件中
- 用户在文件中完成习题，AI 读取后批改
- **不在对话中展示课程内容**，始终保持文件驱动

### 2. 跨语言教学
- 学习材料为英文，可用中文教学
- AI 会优先使用 `settings/glossary.md` 中的术语译法

### 3. 跳读与查漏补缺
- 已有基础？AI 先出题检验掌握程度
- 完全掌握可直接跳过，否则缺啥补啥

---

## �️ 故障排查

### 学习会话初始化相关

| 症状 | 原因 | 解决 |
|------|------|------|
| `validate_state.py` 报 `schema_version expected '2.3', got '2.0'` | 旧版会话（schema 2.0/2.1/2.2）需要迁移 | 在 `session_state.json` 补 `topic_name` / `learner_model` / `_file_paths` / `current_mode` / `lesson_files_core` / `lesson_files_deep` / `mode_switch_log` 并把版本改 `2.3`；或用 `python scripts/session/init_session.py` 新建后手动搬运内容 |
| 新会话必需字段缺失 | 手动创建会话易漏 | 直接用 `python scripts/session/init_session.py <topic_id> <source_path>` 一键生成骨架并自动通过校验 |
| `_file_paths` 与实际文件名不一致 | 历史遗留 `Sys.NN_` 前缀 | 重命名派生视图文件为纯名（`summary.md` 等），并更新 `_file_paths` |

### 文档转换相关

| 症状 | 原因 | 解决 |
|------|------|------|
| `MINERU_API_KEY` 未配置 | `settings/.env` 缺文件或值仍为 `TODO` | 编辑 `settings/.env`，填入从 https://mineru.net/apiManage/token 申请的 Key |
| `解析超时（600秒）` | 大文档/网络抖动 | 按章节拆分；或重跑脚本，其内置指数退避重试 |
| `文件大小 X MB 超过 MinerU 上限 200 MB` | 单文件超限 | 先用 PDF 工具拆页再转 |

### 诊断批改相关

| 症状 | 原因 | 解决 |
|------|------|------|
| 诊断后路由始终是 `compact`，即使用户过度自信 | 未传 `dominant_bias` 或 `confidences` | 调用 `grade_diagnostic_file(..., confidences=[1..5])`，系统会自动推断主导 bias |
| `learner_model.concept_mastery` 未更新 | 诊断题未填 `concept_tag` | 按 `prereq-diagnostic-template.md` 的最新格式补齐 `concept_tag` 字段 |

### 自检一键命令

```bash
# 校验某个会话目录的全部状态不变量
python scripts/session/validate_state.py learning-history/<topic>_<timestamp>

# 只读检查 session_state 与 lesson 文件是否漂移
python scripts/session/reconcile_state.py learning-history/<topic>_<timestamp>

# 校验 lesson 产物是否符合 learn/practice/deep 分层规则（兼容历史 core 会话）
python scripts/lesson_lint.py learning-history/<topic>_<timestamp>

# 查看到期复习项
python scripts/session/schedule_review.py learning-history/<topic>_<timestamp>

# 构建跨材料语料索引（检测概念覆盖）
python scripts/indexer/build_corpus_index.py

# 全量测试
python -m pytest tests/ -q
```

---

## �🔒 安全与隐私

- [安全策略 (SECURITY.md)](SECURITY.md) — 漏洞报告方式
- [隐私说明 (PRIVACY.md)](PRIVACY.md) — 哪些数据会发送到外部服务

---

## 🤝 贡献指南

欢迎贡献！

1. Fork 本仓库
2. 创建分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 开源协议

本项目采用 MIT 协议。

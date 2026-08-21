# 新版主推荐样例：STM32 SPI mini session

这个目录是从真实新版 `learning-history` 会话裁剪出的轻量样例，用来展示当前 `learning-engine` 的结构，而不是完整课程资产包。

## 这个精简版保留什么

- `session_state.json`：schema `2.3` 的脱敏会话状态，展示 `lesson_files_learn` 等新版字段。
- `summary.md`：派生学习摘要，说明新版 learn/deep/AI-source 分层。
- `roadmap_status.md`：裁剪后的路线图，只保留单课 mini session 所需信息。
- `lessons/learn/03_SPI协议原理.learn.md`：新版 learn-card，小而可读，适合作为新用户入口。
- `lessons/ai-source/06.0_图片显示原理.ai.md`：AI 生成源的精简版，展示“让更强模型生成互动 HTML”的工作流形式。

## 完整版原始形态

真实学习目录通常更大，可能包含以下内容：

- PDF：原始教材或芯片资料，通常位于用户本地资料库，不进入示例仓库。
- 图片：PDF/OCR/课程图示导出的截图或照片，可能有数百张，只在完整本地学习空间保留。
- 私有路径：例如个人资料库、课程源码、板卡工程目录等本机路径；本样例全部改写为 `examples/sources/...` 形式。
- 大目录：完整转换产物、原始模型 JSON、图片缓存、HTML 互动页、源码索引等；本样例只保留能说明结构的 Markdown/JSON。

## 为什么不原样复制

`examples/learning-history/` 是仓库级公开示例，目标是小、可读、可测试。完整 `learning-history/` 是个人学习工作区，可能包含答案草稿、原始 PDF、图片缓存和本地路径。这个 mini session 用脱敏裁剪版说明新版模式，同时避免仓库体积膨胀和隐私泄露。

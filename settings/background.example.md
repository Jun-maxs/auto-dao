# 背景信息示例

> 此文件为示例。实际使用时，复制为 `background.md` 并根据个人情况填充。
> 格式：Markdown，包含年级、科目、问题、备注等区域。

---

## 源码参考（可选 · 2026-04-18 新增）

> 若本地有对应课程的完整工程源码，填入此字段，AI 会在生成操作性 Lesson（`teaching_mode=B`）时从真实工程抽取代码；否则降级为 AI 虚构示范。
> 详见 `docs/plans/2026-04-18-scenario-closure-feynman-design.md`。

- source_code_root: /path/to/your/source-project       # 工程根目录
- source_material_md: /path/to/your/source-project/md  # 原版配套 md 教程（可选，作为 AI context）

**留空此节**将完全禁用源码集成，lesson 按旧逻辑（AI 自行生成代码示范）。

---

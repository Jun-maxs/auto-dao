# Lesson Generator Rules

这些规则给 AI 使用，不直接放进学习者主文档。

## 输出策略

默认采用 learn-first：

1. 先生成 `lessons/learn/{NN}_{slug}.learn.md`。
2. 需要训练时生成 `lessons/practice/{NN}_{slug}.practice.md`。
3. 用户要求“深入 / 查来源 / 完整代码 / 完整推导”时才生成 `lessons/deep/{NN}_{slug}.deep.md`。
4. 来源覆盖表写入 `source_coverage/{NN}_{slug}.md`，不放入 learn-card 正文。

## Learn-card 限制

- 只解决一个核心问题。
- 概念型不超过 120 行，代码型不超过 180 行，多场景专题必须拆卡。
- 只保留一个最小例子、一个最致命错误、两个小题和一个 80 字复述。
- 每个核心代码片段最多 3 个锚点：最容易写错的参数、最关键的 API 选择、最致命的边界条件。
- 不展示状态协议、生成器规则、完整来源覆盖表、完整术语表和附录。

## Practice-pack 限制

- 题目来自 learn-card 的核心机制和易错点。
- 默认 3-6 题，覆盖检索、迁移、改错和复述。
- 批改反馈追加到文件中，不覆盖用户答案。

## Deep-reference 限制

- deep 是查阅文件，不是第一次学习入口。
- 必须保留来源覆盖、完整推导、必要图表和完整代码来源。
- 多场景操作课拆成多个 learn-card，再用一个对比卡汇总；不要把多个 7 子节闭环塞进一篇 learner-facing 文档。

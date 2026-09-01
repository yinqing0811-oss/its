# ITS Agent MVP 测试报告

## 评估目标

本报告使用 25 条人工标注测试数据，评估最小可运行 Agent 链路中的任务路由准确率、工具调用成功率和生成质量粗评分。

评估运行使用 `MockLLMClient` 固定输出，目的是稳定检测路由、RAG、工具调用和结构化输出。生产运行时配置 `DEEPSEEK_API_KEY` 后会调用 DeepSeek API。

## 指标汇总

- 测试样本数：25
- 任务路由准确率：100.00%
- 工具调用成功率：100.00%
- 平均生成质量分：99.20 / 100

## 明细

| ID | 期望类型 | 预测类型 | 工具 | 路由正确 | 工具成功 | 质量分 | 检索文档 |
|---|---|---|---|---|---|---:|---|
| case001 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 100 | kb029, kb001, kb030, kb026 |
| case002 | exercise_generation | exercise_generation | exercise_generator | 是 | 是 | 100 | kb019, kb002, kb026, kb027 |
| case003 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 100 | kb005, kb020, kb026, kb027 |
| case004 | exercise_generation | exercise_generation | exercise_generator | 是 | 是 | 100 | kb008, kb010, kb004, kb028 |
| case005 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 90.0 | kb003, kb030, kb026, kb029 |
| case006 | exercise_generation | exercise_generation | exercise_generator | 是 | 是 | 100 | kb001, kb026, kb027, kb011 |
| case007 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 90.0 | kb008, kb029, kb026, kb020 |
| case008 | exercise_generation | exercise_generation | exercise_generator | 是 | 是 | 100 | kb010, kb008, kb019, kb026 |
| case009 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 100 | kb006, kb026, kb028, kb030 |
| case010 | exercise_generation | exercise_generation | exercise_generator | 是 | 是 | 100 | kb009, kb026, kb022, kb024 |
| case011 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 100 | kb030, kb004, kb026, kb027 |
| case012 | exercise_generation | exercise_generation | exercise_generator | 是 | 是 | 100 | kb004, kb027, kb026, kb025 |
| case013 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 100 | kb017, kb020, kb022, kb027 |
| case014 | exercise_generation | exercise_generation | exercise_generator | 是 | 是 | 100 | kb029, kb003, kb019, kb026 |
| case015 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 100 | kb016, kb001, kb011, kb002 |
| case016 | exercise_generation | exercise_generation | exercise_generator | 是 | 是 | 100 | kb007, kb003, kb022, kb026 |
| case017 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 100 | kb021, kb026, kb029, kb024 |
| case018 | exercise_generation | exercise_generation | exercise_generator | 是 | 是 | 100 | kb011, kb026, kb027, kb025 |
| case019 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 100 | kb023, kb026, kb028, kb008 |
| case020 | exercise_generation | exercise_generation | exercise_generator | 是 | 是 | 100 | kb022, kb004, kb026, kb027 |
| case021 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 100 | kb024, kb026, kb027, kb020 |
| case022 | exercise_generation | exercise_generation | exercise_generator | 是 | 是 | 100 | kb025, kb019, kb026, kb020 |
| case023 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 100 | kb028, kb009, kb008, kb026 |
| case024 | exercise_generation | exercise_generation | exercise_generator | 是 | 是 | 100 | kb012, kb030, kb004, kb026 |
| case025 | lesson_plan | lesson_plan | lesson_planner | 是 | 是 | 100 | kb013, kb029, kb014, kb026 |

## 结论

- 当前 MVP 已具备教师输入、任务路由、本地知识库检索、LLM 生成、工具结构化输出和评估记录的完整链路。
- 路由器采用可解释关键词规则，适合作为最小版本；后续可用这批评估数据扩展为训练集，替换为分类模型。
- 生成质量评分是轻量规则分，主要检查结构完整性、知识点覆盖和关键词命中；后续建议加入教师人工评分和学生学习效果指标。

# 02_EmergencyRiskEngine 紧急风险规则引擎节点说明（SG v2.1）

**v2.1 关键变更：本节点不再是提示词实现。** 分级由代码节点 `rule_engine/rule_engine.py`（SG-RULES v2.2）确定性产出，LLM 不得改写。本文件只描述节点接线与 LLM 辅助边界。

## 节点类型
平台"代码节点"（Python 运行时）。实现、契约与测试见 `rule_engine/README_规则引擎实现说明.md`。

## 工作流位置与行为

```
症状采集 Agent ──► [代码节点 rule_engine.assess()] ──┬─ tier=emergency ──► 前端立即显示 "Call 995 now"
                                                    │                     （审计节点后台继续，不阻塞展示）
                                                    ├─ tier=high/medium/low ──► 分诊建议 Agent
                                                    └─ tier=insufficient_info ──► NurseFirst 6262 6262 指引
```

- 紧急情况下：先渲染 "Call 995 now"（毫秒级，引擎 <5ms），审计/日志/留痕在后台异步继续。
- 引擎输出 `llm_override_allowed=false`：**任何下游 LLM 节点不得改写 tier**。

## LLM 的合法角色：升级线索（Escalation-only）

若 LLM 认为引擎结果偏轻（例如发现文本中"说话含糊"未被结构化），它不能直接改级，只能：

1. 输出新的结构化症状代码（从 01 号节点的代码表中选）；
2. 回传代码节点重新评估；
3. 以第二次评估结果为准。

平台不支持二次回环时：LLM 升级线索必须以"建议用户立即联系 NurseFirst 6262 6262 复核"收尾，且不得给出低于引擎的导航建议。

## 输入（payload）
- age, symptom_text, structured_symptoms（01 号节点输出）, meds_involved, lives_alone（可选）

## 输出（引擎契约，固定字段）
- tier / navigation / triggered_rules（规则编号+证据）/ llm_override_allowed=false / llm_may_escalate_only=true / missing_fields / fallback_used / rules_version / audit_id

## 部署与监控要求（对应评审 #5，详见 evidence/ 清单）
- [ ] WorkBuddy 代码节点创建截图
- [ ] 引擎对 4 个代表病例的运行输出截图（emergency / high / medium / insufficient_info 各一）
- [ ] 节点运行日志（含 rules_version 与 audit_id）
- [ ] run_tests.py 实测结果（passed=93/93）与运行截图；`node parity_test.js` 跨引擎对拍 93/93 截图

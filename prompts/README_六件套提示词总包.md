# 六件套提示词总包（HC1 导航版 · SG v2.4）

版本：2026-10-08（v2.1，配合评审意见 #1/#2/#3 全面修订）

由原 AIC 版八 Agent 收敛而来，收敛映射见 `00_适配总览与方案收窄.md`。

| 文件 | 节点 | v2.1 关键变化 |
| --- | --- | --- |
| `01_SymptomIntakeAgent.md` | 症状采集 | 输出结构化症状/药物代码供引擎使用；老年模式一步一问；中英双语 |
| `02_EmergencyRiskEngine.md` | 紧急风险规则引擎 | **改为代码节点实现**（rule_engine.py），LLM 仅可提交升级线索回传复评 |
| `03_TriageAdvisorAgent.md` | 分诊建议 | 检索库换为 patient_safe_kb；不得降低引擎分级 |
| `04_CareNavigationAgent.md` | 就医导航 | 新加坡路径（995/NurseFirst/GP/Polyclinic/UCC）；英文行动卡优先；支持修订模式二次调用 |
| `05_MedicationCheckAgent.md` | 药物及禁忌检查 | 分级判定权交回引擎（engine_recheck 回环）；触发导航修订 |
| `06_EvidenceAuditAgent.md` | 证据核查和安全审核 | 患者端七项硬约束审核；区分"可追溯"与"经临床审核" |

## 全局硬约束（六份共享）

- 分级唯一事实来源是代码引擎 `rule_engine.py`（SG-RULES v2.4）；LLM 只能升级不能降级。
- 紧急号码 **995**（SCDF）；非紧急咨询 **NurseFirst 6262 6262**；日间首诊 **GP / Polyclinic**；夜间 **UCC / after-hours GP**；轻症 **Telemedicine**。
- 不诊断、不开处方、不推荐药名与剂量；不推荐具体机构名称。
- 患者可见输出只允许引用 `patient_safe_kb.md` / `navigation_rules.md` / `medical_safety_rules.md`；`clinical_reference/` 禁止进入患者链路。
- 行动卡英文优先、中文对照；每条 ≤20 词；必须包含升级信号。

## 平台粘贴说明

- 保留"通用约束 + 任务 + 输入 + 输出格式"结构；平台不支持 JSON 输出时按固定标题分段。
- 02 号节点用代码实现，见 `rule_engine/` 目录；其余五个为 LLM 节点。

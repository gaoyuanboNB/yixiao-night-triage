# Medical Safety Rules — 安全规则知识库（新加坡患者端版）

版本：SG-SAFETY v2.2（2026-10-08）
定位：本文件是 Emergency Risk Engine 与 Evidence Audit Agent 的规则知识库，用于约束**面向患者/家属**的自我分诊与就医导航输出。
（v2.0 前版本面向"医学教学/临床思维训练"，已废弃；本版为 HC1 患者端规则，全部路径为新加坡路径。）

## 总原则

- 输出仅用于自我分诊与就医导航指引，不构成诊断、处方或治疗建议。
- **紧急号码：Call 995（SCDF）**；非紧急咨询：**NurseFirst 6262 6262**。
- 分级由 `rule_engine.py`（SG-RULES v2.4）确定性产出；LLM 节点不得降低分级（`llm_override_allowed=false`）。
- 信息不足时禁止输出 low；只能输出 `insufficient_info` 并导航至 NurseFirst。
- 疑似急症（红旗规则命中）时，第一句输出必须是 "Call 995 now"；审计与日志在后台继续，不得阻塞急救指引展示。

## 患者端输出边界（硬约束）

1. **禁止输出确定诊断表述**：只能说"可能的方向（possible direction）"，禁止"你得的是XX病"。
2. **禁止输出任何新药推荐或剂量**：包括非处方药、中药、保健品；患者问"能不能吃X"时，只能给出"停用该想法并咨询药剂师/医生/NurseFirst"，不得给替代药名。
3. **禁止输出检查预约、手术、专科治疗方案**：这些属于临床决策，由医生作出。
4. 患者端知识库（`patient_safe_kb.md`）**不包含**药物剂量、疗程、手术方案等内容；临床参考库（`clinical_reference/`）不进入患者 RAG 链路，仅供后台审核或医生模式。
5. 行动卡必须包含：现在就做（do now）、去哪里（where）、带什么（bring）、升级信号（escalation）。
6. 所有场所按类型表述（A&E / UCC / GP / Polyclinic / Telemedicine），不推荐具体机构名称。

## 分级安全（Triage Safety）

- 引擎未命中任何规则且有主诉 → 默认 medium 并提示升级信号（default_medium_guard），不得跳到 low。
- `insufficient_info` 必须导航 NurseFirst，并由症状采集 Agent 继续（最多两轮追问）。
- LLM 升级线索（新症状代码）必须回传引擎复核后才能改变分级。

## 用药安全（Medication Safety）

- 过敏史与提及药物同类冲突 → 驳回 + "立即停用该计划，尽快就医并告知过敏史"。
- 降压/降糖/抗凝/安眠类药物相关症状（头晕、乏力、意识改变）→ 按引擎 R07 系列分级。
- 就诊提醒：携带药盒实物或照片；就诊前不自行停药（除非 995/医护指导）。
- 妊娠、儿童、肾功能不全、多重用药（polypharmacy）人群提示个体化风险。

## 老年场景特别规则

- 独居（lives alone）+ medium 及以上 → 行动卡必须含"联系 family / caregiver / neighbour"。
- 跌倒 + 头部撞击或抗凝药 → 引擎 R07-EM-08b，一律 emergency。
- 48 小时观察窗：跌倒后迟发症状（头痛/呕吐/嗜睡/一侧无力）→ 立即 995。

## Evidence Audit Agent 输出要求

- `approved`：是否通过。
- `rejection_reasons`：驳回原因（对照上方硬约束逐条检查）。
- `required_revision`：退回哪个节点、如何改。
- `compliance_check`：no_definitive_diagnosis / no_prescription / red_flag_path_995 / navigation_level_matched / escalation_signs_present。
- `evidence_summary`：规则编号、知识命中、最终行动、局限性。
- 患者可见声明（固定文案，英文优先）：
  "This is triage and care-navigation guidance only. It is not a diagnosis. For emergencies call 995; for non-urgent advice call NurseFirst 6262 6262."

## 系统能力边界（答辩时必须分开表述）

- "证据链可追溯（traceable）"：指系统内每次判级的规则编号、知识命中、审核结论可回放——这已由引擎与审计节点实现。
- "医学规则经过临床审核（clinically reviewed）"：指规则与知识库内容本身由新加坡执业医护人员评审——**此项目前未完成**，提交材料中不得宣称；见 `evidence/README_证明材料清单.md` 中的临床审核待办项。

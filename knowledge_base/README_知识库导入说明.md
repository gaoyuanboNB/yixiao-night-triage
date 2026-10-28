# 知识库导入说明（HC1 导航版 · 新加坡 · 双库架构）

版本：2026-10-08（v2.1，配合评审意见 #4 双库拆分）

## 双库架构（重要）

```
knowledge_base/
├── patient_safe_kb.md            ← 患者端安全库：唯一进入患者 RAG 链路
├── navigation_rules.md           ← 导航规则库：就医导航 Agent 检索源
├── medical_safety_rules.md       ← 安全规则库：引擎+审计 Agent 检索源
└── clinical_reference/           ← 临床参考库：584 疾病 Skill（后台专用）
    ├── hospital_agent_knowledge_base.md
    ├── hospital_agent_skills_flat.csv
    ├── departments.json
    ├── diseases_catalog.json
    └── examinations_catalog.json
```

**为什么拆两库**：临床参考库含具体药名、剂量、疗程、手术与检查选择内容。RAG 一旦命中，模型可能把这些内容带进患者回答。因此：

- `patient_safe_kb.md` 只含红旗征象、就医路径、就诊准备、升级条件——经逐条审查无治疗内容；
- `clinical_reference/` 不配置进患者问答检索；仅供 Evidence Audit Agent 做后台证据核对，或未来"医生模式"使用；
- 平台配置患者应用时，**只挂载前三个文件**。

## 平台导入步骤

| 顺序 | 文件 | 挂载到 |
| --- | --- | --- |
| 1 | `patient_safe_kb.md` | 患者对话主知识库 |
| 2 | `navigation_rules.md` | 就医导航 Agent 检索源 |
| 3 | `medical_safety_rules.md` | 风险引擎说明 + 证据审核 Agent 检索源 |
| 4 | （可选，仅医生模式/后台审核应用）`clinical_reference/hospital_agent_knowledge_base.md` | 独立的内部应用，不与患者应用共用 |

## 覆盖范围

- 患者端安全库：12 组红旗征象、5 级就医路径、行动卡四要素、沟通模板、独居老人条目。
- 导航规则库：新加坡号码与服务（995 / NurseFirst 6262 6262 / GP / Polyclinic / UCC / Telemedicine）、夜间规则、四条急症路径、就诊准备清单、升级信号。
- 临床参考库（后台）：19 科室、584 疾病 Skill、837 检查项（沿用旧包，已交叉校验；**待临床审核后才能作为医学依据对外宣称**）。

## 检索配置建议

1. 患者库切分按小节（`##`），每次召回 3-5 段；患者库总量小，追求全命中。
2. 导航规则与安全规则单独建库，要求输出引用规则编号（R02-EM-xx 等），供审计节点复核。
3. `temperature` 调低（≤0.3）；患者端输出必须逐字引用行动卡模板，禁止自由发挥。

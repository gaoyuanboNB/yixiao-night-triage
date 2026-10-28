# Navigation Rules — 就医导航规则知识库（新加坡版）

版本：SG-NAV v2.1（2026-10-08）
定位：本文件是 CareNavigationAgent（就医导航 Agent）的检索知识库，把风险等级翻译为**新加坡**患者可执行的就医路径。与 `medical_safety_rules.md`（安全规则）配合：安全规则决定"能不能放行"，本库决定"去哪里、怎么去"。
语言：行动卡输出**英文优先（English first），中文对照可选**。

> 本库已针对新加坡医疗体系完全重写，不再包含任何中国大陆路径（120、医保卡、社区医院、网格员等均已移除）。

## 一、新加坡就医关键号码与服务

| 用途 | 号码/服务 | 说明 |
| --- | --- | --- |
| 危及生命的紧急情况 | **Call 995（SCDF 救护车）** | 胸痛、卒中、呼吸困难、意识改变、严重过敏、大出血等；**呼叫 995 后严禁自行驾车** |
| 非紧急医疗咨询 | **NurseFirst 6262 6262** | 电话护士咨询，判断是否需要就医、去哪里就医 |
| 基础医疗（日间） | **GP（全科诊所）/ Polyclinic（综合诊疗所）** | 常见病首诊；Polyclinic 为政府运营，可用 HealthHub 预约 |
| 夜间/节假日 | **After-hours GP clinic / UCC（Urgent Care Centre）** | 非危及生命但当晚需处理的病症 |
| 远程医疗 | **Telemedicine（MOH 许可平台）** | 轻症咨询、开药续方；夜间多家平台运营 |
| 医疗记录 | **HealthHub / Singpass** | 就诊材料：病史、用药清单、疫苗记录 |

注意：
- **Community Hospital（社区医院）在新加坡是亚急性/康复/延续照护机构，不是夜间症状首诊入口**，不得出现在低龄急症导航路径中；
- 非紧急转运不要占用 995；可使用私立非紧急救护车服务或家人陪同；
- 就诊场所按类型表述（nearest ED with …… capability / after-hours GP / UCC），不推荐具体机构名。

## 二、风险等级 → 就医路径映射（新加坡版）

| 风险等级 | 就医路径 | 时间要求 | 关键动作 |
| --- | --- | --- | --- |
| emergency | **Call 995**；或最近 A&E（急诊科） | 立即 | 留在患者身边；解锁大门；备好药物清单；**不要自行驾车、不要叫网约车** |
| high | **先联系 NurseFirst 6262 6262 确认**，按指引前往 UCC / 医院 A&E / After-hours GP（视病症与机构开放情况） | 当晚 | 家属/caregiver 陪同；出发前可先电话告知；带 NRIC/FIN、药物清单 |
| medium | GP / Polyclinic | 24-48 小时内 | HealthHub 预约；带病历；是否空腹以诊所指示为准 |
| low | Telemedicine / 自我观察 | 1-3 天 | 给出明确观察指标与升级条件 |
| insufficient_info | **NurseFirst 6262 6262** | 立即（电话） | 信息不足时禁止给低级别建议，先由护士评估 |

## 三、夜间场景特殊规则（22:00-06:00）

1. 老年人（≥65）夜间新发症状，medium 及以上：不建议"扛到天亮"——先拨 **NurseFirst 6262 6262** 由护士评估是否当晚就医。
2. 独居老人：medium 及以上，行动卡必须包含"立即联系 family / caregiver / neighbour"条目（新加坡语境无"社区网格员"，用家属/caregiver/邻居）。
3. 夜间就医准备：**NRIC/FIN**、手机电量、常服药物实物或照片（药盒）、外套、水；糖尿病患者随身带糖块。
4. 夜间观察基线：每 30 分钟复查症状并记录；任何恶化按升级路径处理。
5. 老年人夜间跌倒：即使当时无不适，48 小时内出现头痛、呕吐、嗜睡、一侧无力 → 立即 995 或 A&E（迟发性颅内出血风险）。

## 四、急症路径专项（新加坡版）

### 胸痛路径（Chest Pain）
- 立即停止活动，坐位休息；**Call 995**。
- 通报地址（含**邮政编码 6 位**）与楼栋/单元号；新加坡 addresses 靠 postal code 快速定位。
- 有医嘱含服药物（如 GTN）按医嘱使用；无医嘱不要自行服药。
- 等待时保持门可打开；不要步行下楼等待。

### 卒中路径（Stroke FAST）
- F（Face droop）/ A（Arm weakness）/ S（Speech difficulty）/ T（Time to call 995）。
- **记录最后正常时间（last known well time）**，告知医护以判断溶栓时间窗。
- 不要喂水喂药（误吸风险）；呕吐时侧卧。
- 目标：最近的具备卒中单元能力的医院 A&E（由 995 调度决定，不要自行选择医院）。

### 严重过敏路径（Anaphylaxis）
- 立即停止接触可疑过敏原；曾由医生开具 **EpiPen（肾上腺素自救笔）** 的按处方使用（大腿外侧注射）。
- 保持坐位或平卧抬高双腿；呼吸困难者坐位；**Call 995**。

### 药物过量/误服路径（Overdose / Ingestion）
- 携带药物包装/药盒就医；**不要自行催吐**（除非 995/NurseFirst 指导）。
- 先 Call 995（有意识改变/高危药物）或 NurseFirst（可监测药物、无症状），按指导行动。
- 药物过量/误服不提供独立"毒物咨询热线"指引：有症状 Call 995，无症状联系 NurseFirst 6262 6262，一律按调度员/护士的即时指导行动；不要自行催吐，不要上网查偏方。

## 五、就诊准备清单（通用，新加坡）

- 证件：**NRIC / FIN**（外国人持护照）、就诊卡。
- 病历材料：HealthHub 记录、正在服用药物清单（药盒实物最佳）、过敏史、慢性病诊断记录、近期出院小结（discharge summary）。
- 付费：MediSave / MediShield / 私人保险信息（如适用）；Polyclinic 就诊带 **Pioneer Generation / Merdeka Generation 卡**（如适用，可享补贴）。
- 症状记录：起病时间、变化过程、已采取措施、夜间观察记录。
- 沟通模板（英文）："He/She is 72 years old, has hypertension, started having crushing chest pain with sweating at 11pm, lasting 30 minutes so far. Medications: amlodipine. Allergies: none."

## 六、科室/服务 → 就诊准备对照（新加坡常用）

| 目标 | 就诊准备 |
| --- | --- |
| A&E / UCC | 带药物清单、NRIC、过敏史；家属陪同 |
| Polyclinic | HealthHub 预约；是否空腹以诊所指示为准；带 NRIC、旧报告 |
| GP（After-hours） | 先电话确认营业时间；带药盒 |
| Cardiology follow-up（心内随访） | 带近期 BP 记录、既往报告 |
| Endocrinology（内分泌） | 是否空腹以诊所指示为准（勿自行禁食，尤其正用降糖药者）；带血糖记录 |
| Respiratory（呼吸科） | 带既往 CXR/CT；吸烟史 |

## 七、升级信号（通用，写入每张行动卡）

- 症状程度加重、持续更久，或出现任何新的红旗症状。
- 意识、言语、平衡、视力的任何新变化。
- 家属/caregiver 观察到患者"和平时明显不一样"（老年人重症常无典型表现）。
- 任何不确定：升级一级处理——NurseFirst 咨询 → 当晚 UCC/A&E → Call 995。

## 八、边界声明

- 本库只用于分诊和就医指引，不构成诊断或治疗建议。
- 号码与服务以新加坡官方最新公布为准；提交前由团队人工复核一次号码与营业时间表述（见 evidence 清单）。
- 规则与患者实际情况冲突时，一律以更保守（更高一级就医）为准。

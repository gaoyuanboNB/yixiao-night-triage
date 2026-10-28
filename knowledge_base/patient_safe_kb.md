# Patient Safe KB — 患者端安全知识库

版本：SG-PATIENT v2.1（2026-10-08）
定位：**这是唯一进入患者端 RAG 链路的知识库**。只包含四类内容：红旗征象识别、就医路径指引、就诊准备材料、升级条件。
本库经过逐条审查，**不包含**：药物名称、剂量、疗程、手术方案、检查选择、任何治疗决策内容。
（临床参考库 `clinical_reference/` 中的 584 条疾病 Skill 仅用于后台证据审核与医生模式，禁止进入患者问答检索。）

## 一、红旗征象（出现任何一条 = 立即 Call 995）

1. 胸痛、胸闷或压榨感，尤其伴出汗、放射到手臂/下颌、呼吸困难。
2. 面部歪斜、说话不清、一侧手臂或腿无力麻木（卒中征象，记住最后正常时间）。
3. 呼吸困难、喘不上气、说不出完整句子。
4. 叫不应、意识模糊、晕厥、抽搐。
5. 大出血或出血不止；咳血、呕血、黑便。
6. 严重过敏：脸/喉咙肿胀、全身风团伴气促。
7. 疑似药物过量或误服（尤其安眠药、降糖药、心脏病药），或伴嗜睡、呕吐、意识改变。
8. 突发一生中最剧烈的头痛；突发一只眼看不见。
9. 高热伴脖子发硬、意识模糊或不褪色的皮疹。
10. 剧烈腹痛伴腹壁发硬。
11. 任何自伤或轻生表述。
12. 跌倒撞到头部后出现头痛、呕吐、嗜睡（或服用抗凝药者任何头部撞击）。

## 二、分级就医路径（新加坡）

| 引擎分级 | 该做什么 | 时间 |
| --- | --- | --- |
| emergency | **Call 995**，留在患者身边，不要自行驾车 | 立即 |
| high | 先拨 NurseFirst 6262 6262 确认；按指引当晚前往 UCC 或医院 A&E（家属陪同，不要自行驾车） | 当晚 |
| medium | 预约 GP 或 Polyclinic（可用 HealthHub） | 24-48 小时内 |
| low | Telemedicine 咨询或按指标自我观察 | 1-3 天 |
| 信息不足 | **Call NurseFirst 6262 6262**，由护士评估 | 立即（电话） |

夜间（22:00-06:00）提示：非急症但担心 → 先拨 NurseFirst；many after-hours GP clinics 开到深夜，电话确认后前往。

## 三、行动卡四要素（每张行动卡必须齐备）

1. **Do now（现在就做）**：具体到动作，如 "Call 995 now" / "Sit down and rest" / "Check blood sugar if you have a meter"。
2. **Where to go（去哪里）**：场所类型 + 科室 + 时间建议，如 "A&E tonight" / "Polyclinic tomorrow morning, fasting"。
3. **What to bring（带什么）**：NRIC/FIN、正在服用的药盒或药物清单、过敏史、HealthHub/出院小结、手机电量。
4. **When to escalate（何时升级）**：明确的恶化信号，如 "If pain worsens or he becomes drowsy — call 995 immediately"。

每条不超过 20 个英文单词；界面提供中文对照。

## 四、就诊沟通模板（帮助家属向医生描述）

- "He/She is ___ years old, has ___ (conditions)."
- "Tonight at ___ (time), ___ (symptom) started and has lasted ___ ."
- "Medications: ___. Allergies: ___."
- "We already tried ___ , it helped / did not help."

## 五、独居老人附加条目

- medium 及以上：第一项动作加入 "Call your family member, caregiver, or a neighbour now."
- 手机保持畅通；门口解锁；钥匙放在家人知情的位置。
- 记录：把症状变化写在纸上带去医院，避免口头遗漏。

## 六、可对家人说的话（安抚与合规）

- "This app gives directions on where to seek care; the doctor at the clinic/hospital will make the diagnosis."
- "In an emergency, always call 995 first — do not drive yourself."

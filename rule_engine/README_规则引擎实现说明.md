# 紧急风险规则引擎（Emergency Risk Engine）— 实现说明

版本：SG-RULES v2.2（2026-10-08）

> **v2.4**：跌倒三档细分——fall_complicated（剧痛/骨折/无法站立行走）→ high，fall_unspecified → medium 追问，仅显式无伤表述可 low；呼吸词收窄（裸 breathing 不再命中，仅 difficulty/trouble/shortness/cannot breathe/gasping 等）；否定作用域改为"否定词+虚词+症状"，标点与 but/however 截断（denies severe crushing chest pain 正确否定）；vomited once 经 code_overrides 去重，不再同时命中持续呕吐；过敏史支持否定与耐受表达（No penicillin allergy / I tolerate penicillin 不误拦）。回归集 83 例，双引擎 83/83。
> **v2.5**：跌倒撞头表达补充（hit/banged/磕到/头先着地/滑倒等）；抗凝药从跌倒头伤正则移出，改为规则级条件（任何跌倒+抗凝药 → high 新规则 R12-HI-12；头伤+抗凝药仍 → emergency）；bleeding 收窄为严重出血（大出血/出血不止/bleeding heavily 等，轻微牙龈出血不触发）。回归集 93 例，双引擎 93/93。
> **v2.3**：否定词大修——中文紧邻否定（4 字符）与英文否定结构（denies/without/never had a ...）双策略，后向停止词（bleeding has stopped）；生命体征危象拆分：仅"not breathing/no pulse"类否定事实陈述保留豁免，choking/blue lips 可被否定；新增过敏-药物冲突本地拦截（allergy_rules，与 WorkBuddy 端同源）；新增 unresponsive/collapsed/gasping/单次呕吐区分；回归集扩至 70 例，Python 与 JS 镜像 `node parity_test.js` 70/70 对拍一致。
> **v2.2**：规则单一事实源（rules_definition.json，前端 engine.js 自动生成，`node parity_test.js` 50 例对拍一致）；新增 R02-EM-00 生命体征危象（否定豁免）、R02-EM-01a 剧烈胸痛任何年龄；输入 Schema 校验安全降级；真超时控制；全部命中规则留痕。
性质：**确定性代码节点**，不是提示词。本引擎是全系统分级唯一事实来源。

## 1. 为什么必须是代码

评审意见明确指出：如果只用 LLM 提示词判级，"安全闸门"只是答辩概念。本引擎用纯 Python（标准库，无三方依赖）实现，保证：

- 同一输入永远得到同一分级（确定性）；
- LLM 节点收到 `llm_override_allowed=false`，**只能补充升级线索并回传引擎复核，不能降低任何分级**；
- 引擎异常/超时走保守回退（一律按 high 处理，绝不返回 low）。

## 2. 输入输出契约

### 输入
```json
{
  "age": 72,
  "symptom_text": "胸口像压了块石头，出汗很多",
  "symptoms": ["chest_pain_with_sweat"],
  "meds_involved": ["antihypertensive"]
}
```
`symptoms` / `meds_involved` 为结构化代码（上游症状采集 Agent 输出），`symptom_text` 为原始主诉，引擎会用内置文本匹配器补抽代码（结构化代码优先，文本只增不减）。

### 输出
```json
{
  "tier": "emergency",
  "navigation": "call_995",
  "triggered_rules": [{"rule_id": "R02-EM-01", "rule_name": "胸痛伴大汗/放射痛", "evidence": ["..."]}],
  "llm_override_allowed": false,
  "llm_may_escalate_only": true,
  "missing_fields": [],
  "fallback_used": false,
  "rules_version": "SG-RULES v2.2 (2026-10-08)",
  "audit_id": "a1b2c3d4e5f6",
  "latency_ms": 0.21
}
```

tier 取值：`emergency / high / medium / low / insufficient_info`；导航目标固定映射：
call_995 → ucc_or_ed_tonight → gp_or_polyclinic → telemedicine_or_self_monitor → nursefirst_6262_6262。

## 3. 关键策略（评审意见逐条对应）

| 要求 | 实现 |
| --- | --- |
| 信息不足禁止判 low | `R99-II-00`：无命中且信息缺失 → `insufficient_info` → NurseFirst 6262 6262 |
| 冲突优先级 | 规则表按严重度降序，命中多条取第一条，全部留痕 |
| 缺失字段处理 | `missing_fields` 显式返回，参与判级 |
| 超时与失败回退 | 任何异常 → `_fallback()`，tier=high + `fallback_used=true` |
| LLM 不得降级 | `llm_override_allowed=false`（常量），LLM 只能走"升级线索 → 引擎复核" |
| 规则版本号 | 每次输出携带 `rules_version` |
| 审计日志 | `audit_id` + 完整 evidence，可回放 |

## 4. 药物过量分级（RF-007 与 NT-03 冲突的修复）

旧 RF-007 把"降压药加倍"直接判 emergency，与 NT-03 期望冲突。v2.1 拆分为三档：

| 规则 | 条件 | 分级 |
| --- | --- | --- |
| R07-EM-08a | 高危药物（安眠/镇静、阿片、降糖、心脏病、抗凝、精神类）过量，**或**过量伴任何红旗症状（意识改变/抽搐/反复呕吐/呼吸困难） | emergency → 995 |
| R07-EM-08b | 跌倒头部受伤 + 有症状或服用抗凝药 | emergency → 995 |
| R07-HI-08c | 可监测药物（降压等）单次过量且无红旗症状 | high → 当晚 UCC/ED 前先测血压，联系 NurseFirst |

NT-03（降压药加倍+头晕）现在唯一确定地落在 R07-HI-08c = high，与测试用例不再矛盾。

## 5. 红旗规则清单（16 组，不再依赖 7 组关键词）

R02-EM 系列：胸痛（≥50岁或伴大汗）、呼吸困难、卒中征象、意识改变/晕厥/抽搐、大出血/严重过敏/咳血呕血、剧烈腹痛/霹雳头痛/高热颈强/突发失明、自伤表述、严重低血糖；
R07-EM：药物过量两档（见上）；
扩展：R09-R16 覆盖腹痛、头痛、脑膜刺激、自伤、抗凝跌倒、视力、低血糖。

## 6. 测试（实测，非预期文案）

```bash
python run_tests.py
```

最近一次实测：**passed=38, failed=0, contract_broken=0, avg latency 0.23ms, max 4.74ms，fallback 契约 OK**（SG-RULES v2.2，2026-10-08）。

用例覆盖：全部红旗规则正例、药物过量三档、否定词（"否认胸痛""不发烧"）、不确定表达（"不确定是不是多吃"）、口语/错别字变体（"胸口闷闷的""咳出血来了"）、英文输入、冲突症状取高者、空输入/无意义输入、结构化与文本混合输入、回退契约。

## 7. 平台接入（腾讯云 WorkBuddy）

1. 新建"代码节点"（Python 运行时），粘贴 `rule_engine.py` 全文；
2. 节点入口改为平台函数签名，例如：
   ```python
   def main(payload: dict) -> dict:
       from rule_engine import assess
       return assess(payload)
   ```
3. 上游症状采集节点输出 JSON 映射到 payload；下游节点只读 `tier/navigation/audit_id`；
4. 建议同时在代码节点外包一层超时（平台默认超时 2s 即可满足，引擎实测 <5ms）；
5. **禁止**在引擎后再放一个 LLM 节点改写 `tier`；LLM 只允许通过"升级线索节点"输出新的 `symptoms` 代码回传引擎重评。

## 8. 边界与声明

- 文本匹配器是兜底，不是 NLU；正式版应由症状采集 Agent 的结构化 JSON 驱动，文本匹配仅用于对抗性兜底；
- 规则表由临床顾问评审后才可用于真实引导（见 `evidence/README_证明材料清单.md` 中的临床审核项）；
- 引擎输出只是分诊与就医指引，不构成诊断。

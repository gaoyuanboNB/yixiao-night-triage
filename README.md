# 医晓 YiXiao · 老年人夜间智能分诊与就医导航助手

> Healthcare Challenge：智能自我分诊与就医导航 · 场景：新加坡老年人夜间症状分诊
> 规则版本 SG-RULES v2.5 · 本地回归测试 **93/93** 通过（Python 引擎与前端镜像同源对拍一致）

**医晓只回答一个问题：现在该怎么办、去哪里。** 急症第一句永远是 "Call 995 now"；信息不足禁止判低，一律转 NurseFirst 6262 6262；系统只提供分诊与就医指引，不构成诊断、处方或治疗建议。

## 目录结构

```
├── rule_engine/            # 紧急风险规则引擎（核心，确定性判级）
│   ├── rules_definition.json   # 规则单一事实源（v2.5）：症状/药物模式 + 24 条判级规则 + 过敏规则
│   ├── rule_engine.py          # Python 引擎：Schema 校验 · 否定作用域 · 真超时 · 保守回退
│   ├── run_tests.py            # 回归测试运行器（93 例）
│   ├── rules_test_cases.json   # 测试矩阵（急症漏判/否定误报/跌倒三档/过敏拦截/中英混合…）
│   ├── parity_test.js          # 前端镜像引擎与 Python 的跨引擎对拍
│   ├── generate_frontend_engine.py  # 由 JSON 自动生成 patient_ui/engine.js
│   └── README_规则引擎实现说明.md
├── patient_ui/             # 患者端原型（英文优先+中文对照）
│   ├── index.html              # 大字号 · 一步一问 · 固定 CALL 995 · 语音输入 · 朗读 · PDPA 同意页
│   └── engine.js               # ⚠️ 自动生成，勿手改（改 rules_definition.json 后重新生成）
├── prompts/                # 六智能体平台提示词（症状采集/风险引擎/分诊/导航/用药核查/证据审核）
├── knowledge_base/         # 患者安全库 + 导航规则库 + 安全规则库 + clinical_reference（后台隔离）
└── LICENSE                 # Apache-2.0
```

## 快速开始

```bash
# 1) 运行规则引擎回归测试（93 例，含急症漏判/否定误报/跌倒三档/过敏拦截回归）
cd rule_engine
python run_tests.py

# 2) 前后端同源对拍（JS 镜像 vs Python，需 Node.js ≥16）
node parity_test.js

# 3) 打开患者端原型（任选其一）
#    a. 直接双击 patient_ui/index.html
#    b. 本机服务（语音输入体验更完整）
cd .. && python -m http.server 8799 --bind 127.0.0.1
#    浏览器打开 http://127.0.0.1:8799/patient_ui/index.html
```

## 架构一句话

**分级唯一事实来源是确定性代码引擎**：16 组红旗规则 + 药物过量三档 + 跌倒三档 + 过敏冲突拦截；LLM 节点只负责追问与行动卡文案，只能提交"升级线索"回传引擎复评，**永远不能降低分级**（`llm_override_allowed=false`）；信息不足禁止判低，一律转 NurseFirst；引擎异常自动保守回退 high。

规则变更流程：改 `rules_definition.json` → `python rule_engine/generate_frontend_engine.py` 重新生成前端镜像 → `python run_tests.py && node parity_test.js` 全绿后提交。

## 腾讯云 WorkBuddy 部署要点

- `rule_engine.py` 配置为**代码节点**（入口适配 `main(payload)`），实测判定 <1ms，平台 2s 超时余量充足；
- 其余五个节点为 LLM 节点，粘贴 `prompts/` 对应文件；
- 知识库三件套：`knowledge_base/patient_safe_kb.md`（患者主库）、`navigation_rules.md`（导航检索源）、`medical_safety_rules.md`(审核检索源)；`clinical_reference/` 不进入患者检索链路；
- 完整步骤见 `prompts/README_六件套提示词总包.md` 与主提交包 `02_工作流节点设计.md`。

## 安全与边界

- 只提供分诊与就医指引，不构成诊断、处方或治疗建议；
- 急症（16 组红旗规则命中）一律 "Call 995 now"，禁止自行驾车；
- 不推荐具体医院名称、不推荐新药与剂量；过敏冲突直接驳回且不给替代药名；
- PDPA：最小化收集、会话即弃、同意页披露外部模型传输。

## 许可证

[Apache-2.0](LICENSE) · Copyright (c) 2026 医晓团队 YiXiao Team

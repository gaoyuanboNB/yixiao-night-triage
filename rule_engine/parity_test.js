/* 跨引擎一致性对拍：用 Node 运行前端镜像引擎，逐例比对 Python 引擎的实测结果。 */
global.window = global;
const fs = require('fs');
const path = require('path');

const HERE = __dirname;
eval(fs.readFileSync(path.join(HERE, '..', 'patient_ui', 'engine.js'), 'utf8'));
const suite = JSON.parse(fs.readFileSync(path.join(HERE, 'rules_test_cases.json'), 'utf8'));

let passed = 0, failed = 0;
for (const c of suite.cases) {
  const r = TriageEngine.assess(c.input);
  const tierOk = r.tier === c.expected_tier;
  const ruleOk = !c.expect_rule || r.triggered_rules.some(h => h.rule_id === c.expect_rule);
  const allergyOk = c.expect_allergy === undefined || r.allergy_conflict === c.expect_allergy;
  if (tierOk && ruleOk && allergyOk) passed++;
  else {
    failed++;
    console.log(`[MISMATCH] ${c.id}: expected ${c.expected_tier}/${c.expect_rule}, got ${r.tier}/${r.triggered_rules.map(h => h.rule_id).join(',')}`);
  }
  // 契约
  if (r.llm_override_allowed !== false) { failed++; console.log(`[CONTRACT] ${c.id} llm_override_allowed`); }
}
console.log('-'.repeat(50));
console.log(`JS engine (${TriageEngine.build}): passed=${passed} failed=${failed} total=${suite.cases.length}`);
process.exit(failed ? 1 : 0);

# -*- coding: utf-8 -*-
"""规则引擎测试运行器：执行 rules_test_cases.json 全部用例并输出实测统计。

用法：python run_tests.py
输出：passed / failed / total，以及输出契约检查（required keys、llm_override_allowed=False）。
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rule_engine import assess, _fallback, REQUIRED_KEYS  # noqa: E402

HERE = pathlib.Path(__file__).parent


def main() -> int:
    suite = json.loads((HERE / "rules_test_cases.json").read_text(encoding="utf-8"))
    cases = suite["cases"]

    passed = failed = contract_broken = 0
    latencies = []
    for c in cases:
        r = assess(c["input"])
        latencies.append(r.get("latency_ms", 0))

        # 输出契约检查
        if REQUIRED_KEYS - set(r.keys()):
            contract_broken += 1
            print(f"[CONTRACT] {c['id']} 缺少字段: {REQUIRED_KEYS - set(r.keys())}")
        if r["llm_override_allowed"]:
            contract_broken += 1
            print(f"[CONTRACT] {c['id']} llm_override_allowed 必须为 False")

        tier_ok = r["tier"] == c["expected_tier"]
        rule_ok = (c.get("expect_rule") is None) or any(
            h["rule_id"] == c["expect_rule"] for h in r["triggered_rules"]
        )
        allergy_ok = ("expect_allergy" not in c) or (r["allergy_conflict"] == c["expect_allergy"])
        if tier_ok and rule_ok and allergy_ok:
            passed += 1
        else:
            failed += 1
            got_rules = [h["rule_id"] for h in r["triggered_rules"]]
            print(f"[FAIL] {c['id']} {c['label']}: expected {c['expected_tier']}/{c.get('expect_rule')}/allergy={c.get('expect_allergy')}, got {r['tier']}/{got_rules}/allergy={r['allergy_conflict']}")

    # 回退契约：fallback 永不返回 low
    fb = _fallback({"symptom_text": "x"}, reason="unit-test")
    fallback_ok = fb["tier"] == "high" and fb["fallback_used"]
    if not fallback_ok:
        failed += 1
        print("[FAIL] fallback 契约：回退必须为 high 且带标记")

    total = len(cases)
    print("-" * 60)
    print(f"rules_version: {suite['rules_version']}")
    print(f"passed={passed}  failed={failed}  contract_broken={contract_broken}  total={total}")
    print(f"latency avg={sum(latencies)/len(latencies):.2f}ms  max={max(latencies):.2f}ms")
    print(f"fallback contract: {'OK' if fallback_ok else 'BROKEN'}")
    return 0 if (failed == 0 and contract_broken == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())

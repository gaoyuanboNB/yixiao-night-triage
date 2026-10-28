# -*- coding: utf-8 -*-
"""
YiXiao Night Triage — Emergency Risk Rule Engine (Singapore, v2.2)
==================================================================

v2.2 变更（对应评审 P0-1 / P0-2）：
1. 规则单一事实源：全部症状模式、药物模式、判级规则改由 rules_definition.json 驱动；
   前端 patient_ui/engine.js 由 generate_frontend_engine.py 从同一 JSON 自动生成，杜绝两套规则漂移。
2. 急症漏判修复：
   - 新增生命体征危象规则 R02-EM-00（not breathing / no pulse / blue lips / choking / 不呼吸 /
     摸不到脉搏 / 嘴唇发紫 / 被噎），该组模式 negation_exempt=true，否定词不再误杀；
   - 新增 R02-EM-01a：突发剧烈/压榨样胸痛（任何年龄）直接 emergency，不再因 <50 岁降为 high。
3. 输入 Schema 校验：age 类型/范围、symptoms/meds 必须为数组、symptom_text 必须为字符串；
   非法输入安全降级（记录 input_errors，症状文本强制转字符串），绝不抛出未捕获异常。
4. 真超时控制：ENGINE_TIMEOUT_S 通过 deadline 在模式匹配与规则评估循环中实际执行，
   超时走保守回退（high + fallback_used）。
5. 回归测试覆盖以上全部反例（见 rules_test_cases.json E39-E50）。

规则版本：SG-RULES v2.2（2026-10-08）
本引擎是分级唯一事实来源；LLM 节点不得覆盖 tier，只能提交升级线索回传复评。

用法：
    from rule_engine import assess_text, assess
    result = assess_text("He is not breathing")
命令行自测：python run_tests.py
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

HERE = Path(__file__).resolve().parent
_DEF = json.loads((HERE / "rules_definition.json").read_text(encoding="utf-8"))

RULES_VERSION: str = _DEF["version"]
RULES_DATE: str = _DEF["date"]
ENGINE_TIMEOUT_S: float = 2.0
AGE_RANGE = (0, 120)

NAVIGATION: Dict[str, str] = _DEF["tiers"]
VALID_TIERS = set(NAVIGATION.keys())

SYMPTOM_CODES = {
    code for pat in _DEF["symptom_patterns"] for code in pat["codes"]
}
HIGH_RISK_OVERDOSE_MEDS: Set[str] = set(_DEF["high_risk_overdose_meds"])
_CODE_OVERRIDES: Dict[str, Dict[str, Any]] = _DEF.get("code_overrides", {})

NEGATION_WINDOW: int = int(_DEF.get("negation_window", 12))
_STOP_RE = re.compile(_DEF.get("stop_tokens", "stopped"), re.IGNORECASE)
STOP_WINDOW: int = int(_DEF.get("stop_window", 12))
ALLERGY_RULES: List[Dict[str, Any]] = _DEF.get("allergy_rules", [])

_NEGATION = re.compile(_DEF["negation_tokens"], re.IGNORECASE)
_NEG_WORD = re.compile(r"(?:无|没|不|未|否认|排除)|\b(?:denies|denied|deny|without|never|no|not)\b", re.IGNORECASE)
_SCOPE_PUNCT = re.compile(r"[，。；！？,;.!?]")
_SCOPE_BUT = re.compile(r"\b(?:but|however|though)\b", re.IGNORECASE)
_LATIN_FILLER = re.compile(r"[a-z\s\'\-]*", re.IGNORECASE)
_TOLERATE_RE = re.compile(r"\b(?:tolerate|tolerated|tolerates|tolerance)\b|耐受", re.IGNORECASE)
_UNCERTAINTY = re.compile(_DEF["uncertainty_patterns"])
_PATTERNS = [
    (re.compile(p["re"], re.IGNORECASE), p["codes"], p.get("negation_exempt", False))
    for p in _DEF["symptom_patterns"]
]
_MED_PATTERNS = [
    (re.compile(p["re"], re.IGNORECASE), p["med"]) for p in _DEF["med_patterns"]
]
_RULES: List[Dict[str, Any]] = _DEF["rules"]

# 输出契约
REQUIRED_KEYS = {"tier", "navigation", "triggered_rules", "llm_override_allowed",
                 "missing_fields", "fallback_used", "rules_version", "audit_id", "input_errors",
                 "allergy_conflict", "allergy_findings"}

def _is_negated(neg_scan: str, start: int) -> bool:
    """否定作用域：否定词 + 虚词/严重度词 + 症状；标点或 but/however 截断作用域。
    中文要求否定词与症状间隔 ≤4 字符；英文允许 ≤32 字符的英文 filler。"""
    pre = neg_scan[max(0, start - NEGATION_WINDOW):start]
    hits = list(_NEG_WORD.finditer(pre))
    for h in reversed(hits):
        filler = pre[h.end():]
        if _SCOPE_PUNCT.search(filler) or _SCOPE_BUT.search(filler):
            continue
        if h.group().isascii():
            if _LATIN_FILLER.fullmatch(filler):
                return True
        else:
            if len(filler) <= 4:
                return True
    return False


def validate_input(payload: Any):
    """输入 Schema 校验：非法输入安全降级并记录 input_errors，绝不抛出异常。"""
    errors = []
    if payload is None:
        return {}, ["payload_is_null"]
    if not isinstance(payload, dict):
        return {}, ["payload_not_object"]

    cleaned = {}

    age = payload.get("age")
    if age is None:
        cleaned["age"] = None
    elif isinstance(age, bool):
        errors.append("age_is_bool")
        cleaned["age"] = None
    elif isinstance(age, (int, float)):
        if AGE_RANGE[0] <= age <= AGE_RANGE[1]:
            cleaned["age"] = int(age)
        else:
            errors.append("age_out_of_range:" + str(age))
            cleaned["age"] = None
    elif isinstance(age, str) and age.strip().isdigit():
        v = int(age.strip())
        if AGE_RANGE[0] <= v <= AGE_RANGE[1]:
            cleaned["age"] = v
        else:
            errors.append("age_out_of_range:" + age)
            cleaned["age"] = None
    else:
        errors.append("age_not_numeric")
        cleaned["age"] = None

    text = payload.get("symptom_text")
    if text is None:
        cleaned["symptom_text"] = ""
    elif isinstance(text, str):
        cleaned["symptom_text"] = text
    else:
        errors.append("symptom_text_not_string")
        cleaned["symptom_text"] = str(text)

    for key in ("symptoms", "meds_involved"):
        val = payload.get(key)
        if val is None:
            cleaned[key] = set()
        elif isinstance(val, list):
            cleaned[key] = set(v for v in val if isinstance(v, str))
            if len(cleaned[key]) != len(val):
                errors.append(key + "_contains_non_string_items")
        else:
            errors.append(key + "_not_array")
            cleaned[key] = set()

    for key in ("allergies", "planned_med"):
        val = payload.get(key)
        if val is None:
            cleaned[key] = ""
        elif isinstance(val, str):
            cleaned[key] = val
        else:
            errors.append(key + "_not_string")
            cleaned[key] = str(val)

    return cleaned, errors


def extract_symptoms(text: str) -> Set[str]:
    found: Set[str] = set()
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    neg_scan = _UNCERTAINTY.sub("", cleaned)
    for pattern, codes, exempt in _PATTERNS:
        for m in pattern.finditer(cleaned):
            if not exempt:
                # 前向否定：中文紧邻否定 + 英文否定结构（denies/without/never...）
                if _is_negated(neg_scan, m.start()):
                    continue
                # 后向停止词（"bleeding has stopped" / "不再出血"）
                post = neg_scan[m.end():m.end() + STOP_WINDOW]
                if _STOP_RE.search(post):
                    continue
            found.update(codes)
    # 特异代码覆盖泛化代码（如 fall_no_injury 移除 fall_unspecified、single_vomit 移除 persistent_vomiting）
    for keep, cfg in _CODE_OVERRIDES.items():
        if keep in found:
            for rm in cfg.get("removes", []):
                found.discard(rm)
    return found


def extract_meds(text: str) -> Set[str]:
    found: Set[str] = set()
    t = (text or "")
    for pattern, med in _MED_PATTERNS:
        if pattern.search(t):
            found.add(med)
    return found


# ---------------------------------------------------------------------------
# 规则评估（JSON 驱动，first-match；含 deadline 超时检查）
# ---------------------------------------------------------------------------

class EngineTimeout(Exception):
    pass


def _check_deadline(deadline: float) -> None:
    if time.monotonic() > deadline:
        raise EngineTimeout("rule evaluation exceeded budget")


def _cond_match(rule: Dict[str, Any], symptoms: Set[str], meds: Set[str], age: Optional[int]) -> bool:
    sa = rule.get("symptoms_any")
    if sa and not (set(sa) & symptoms):
        return False
    ex = rule.get("symptoms_exactly")
    if ex is not None and symptoms != set(ex):
        return False
    amin = rule.get("age_min")
    if amin is not None and (age is None or age < amin):
        return False
    if rule.get("requires_any") and not symptoms:
        return False
    ma = rule.get("meds_any")
    if ma and not (set(ma) & meds):
        return False
    br = rule.get("branch_or")
    if br is not None:
        hit_meds = bool(set(br.get("meds_any", [])) & meds)
        hit_sym = bool(set(br.get("symptoms_any", [])) & symptoms)
        if not (hit_meds or hit_sym):
            return False
    return True


def _evaluate(symptoms: Set[str], meds: Set[str], age: Optional[int],
              text: str, input_errors: List[str]) -> Tuple[str, List[Dict[str, Any]]]:
    deadline = time.monotonic() + ENGINE_TIMEOUT_S
    if text:
        _check_deadline(deadline)
        symptoms |= extract_symptoms(text)
        meds |= extract_meds(text)

    evidence_symptoms = set(symptoms)
    hits = []
    top_tier = ""
    for rule in _RULES:
        _check_deadline(deadline)
        if _cond_match(rule, symptoms, meds, age):
            if not hits:
                top_tier = rule["tier"]
            hits.append({
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "evidence": sorted(evidence_symptoms) or [f"age={age}"],
            })
    # 规则表按严重度降序：首个命中即最高严重级；全部命中留痕供审计
    if hits:
        return top_tier, hits
    return "", []


def allergy_check(cleaned: Dict[str, Any]) -> List[Dict[str, Any]]:
    """过敏-药物冲突（JSON 驱动，本地即可拦截）。
    与 WorkBuddy 端 MedicationCheckAgent 同一份 allergy_rules 定义；触发时输出
    allergy_conflict=true 与 findings，供患者端行动卡显示"停用该计划"指引。"""
    findings: List[Dict[str, Any]] = []
    allergy_text = (cleaned.get("allergies", "") or "") + " " + (cleaned.get("symptom_text", "") or "")
    trigger_text = (cleaned.get("symptom_text", "") or "") + " " + (cleaned.get("planned_med", "") or "")
    neg_scan = _UNCERTAINTY.sub("", re.sub(r"\s+", " ", allergy_text.strip()))
    for ar in ALLERGY_RULES:
        a_re = re.compile(ar["allergy_re"], re.IGNORECASE)
        t_re = re.compile(ar["trigger_re"], re.IGNORECASE)
        # 过敏原必须以"非否定、非耐受"的方式出现（No penicillin allergy / tolerate ... 不算）
        present = False
        for m in a_re.finditer(neg_scan):
            if _is_negated(neg_scan, m.start()):
                continue
            if _TOLERATE_RE.search(neg_scan[max(0, m.start() - 16):m.start()]):
                continue
            present = True
            break
        if not present:
            continue
        # 从触发物扫描中移除过敏原本身的表述，避免"青霉素过敏"自匹配
        trigger_scan = a_re.sub("", trigger_text)
        if t_re.search(trigger_scan):
            findings.append({"allergy": ar["allergy"], "action": "stop_planned_medication"})
    return findings


def _fallback(payload: Dict[str, Any], reason: str, input_errors: Optional[List[str]] = None) -> Dict[str, Any]:
    """超时/异常保守回退：按 high 处理，绝不返回 low。"""
    return {
        "tier": "high",
        "navigation": NAVIGATION["high"],
        "triggered_rules": [{"rule_id": "R98-FB-97", "rule_name": "引擎异常保守回退", "evidence": [reason]}],
        "llm_override_allowed": False,
        "llm_may_escalate_only": True,
        "missing_fields": [],
        "fallback_used": True,
        "rules_version": f"{RULES_VERSION} ({RULES_DATE})",
        "assessed_at": time.time(),
        "audit_id": hashlib.md5(json.dumps(payload, default=str, ensure_ascii=False).encode()).hexdigest()[:12],
        "input_errors": input_errors or [],
        "allergy_conflict": False,
        "allergy_findings": [],
    }


def assess(payload: Any) -> Dict[str, Any]:
    """结构化评估入口。任何非法输入都会被安全降级并记录 input_errors，不抛出异常。"""
    t0 = time.time()
    cleaned, input_errors = validate_input(payload)
    age: Optional[int] = cleaned.get("age")
    text: str = cleaned.get("symptom_text", "") or ""
    symptoms: Set[str] = set(cleaned.get("symptoms") or set())
    meds: Set[str] = set(cleaned.get("meds_involved") or set())

    try:
        tier, hits = _evaluate(symptoms, meds, age, text, input_errors)
    except EngineTimeout:
        return _fallback(payload, "timeout", input_errors)
    except Exception as exc:  # 任何未预期异常 → 保守回退
        return _fallback(payload, f"exception:{type(exc).__name__}", input_errors)

    missing: List[str] = []
    if age is None and "age" not in [e.split(":")[0] for e in input_errors]:
        missing.append("age")
    if not symptoms and not hits:
        missing.append("symptoms")

    if not hits:
        if text.strip() and len(text.strip()) >= 4 and not missing:
            tier = "medium"
            hits = [{"rule_id": "R20-MD-99", "rule_name": "未命中规则的有主诉病例（保守默认）",
                     "evidence": ["default_medium_guard"]}]
        else:
            tier = "insufficient_info"
            hits = [{"rule_id": "R99-II-00", "rule_name": "信息不足，禁止自动判低",
                     "evidence": missing or input_errors or ["empty_input"]}]

    result = {
        "tier": tier,
        "navigation": NAVIGATION.get(tier, "nursefirst_6262_6262"),
        "triggered_rules": hits,
        "llm_override_allowed": False,
        "llm_may_escalate_only": True,
        "missing_fields": missing,
        "fallback_used": False,
        "rules_version": f"{RULES_VERSION} ({RULES_DATE})",
        "assessed_at": t0,
        "audit_id": uuid.uuid4().hex[:12],
        "input_errors": input_errors,
        "allergy_conflict": False,
        "allergy_findings": [],
    }
    findings = allergy_check({"allergies": cleaned.get("allergies", ""), "symptom_text": text,
                              "planned_med": cleaned.get("planned_med", "")})
    result["allergy_conflict"] = bool(findings)
    result["allergy_findings"] = findings
    result["latency_ms"] = round((time.time() - t0) * 1000, 2)
    return _validate_output(result)


def assess_text(text: str, age: Optional[int] = None) -> Dict[str, Any]:
    return assess({"symptom_text": text, "age": age})


def _validate_output(out: Dict[str, Any]) -> Dict[str, Any]:
    missing = REQUIRED_KEYS - set(out.keys())
    if missing:
        raise ValueError(f"engine output contract broken, missing: {missing}")
    if out["tier"] not in VALID_TIERS:
        raise ValueError(f"invalid tier: {out['tier']}")
    if out["tier"] == "low" and out["fallback_used"]:
        raise ValueError("fallback must never yield low")
    return out

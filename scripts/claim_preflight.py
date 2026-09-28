"""事实来源限定写作的轻量预检。警报只指向待审主张，不自动定稿。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?%?")
SCOPE = ("全国", "所有", "全部", "任何", "普遍", "首次", "必然", "完全", "稳定", "全体", "各地")
PLAN = re.compile(r"明年|次年|下一步|后续将|计划|将研究|将开展|将发布|将推广|将部署|拟于|预计")
STRONG = re.compile(r"证明|证实|决定性|必然|彻底|全面突破|显著|因果|直接政策依据")
EXPLANATION = re.compile(r"区间未跨零|区间没有跨零|区间不跨零|组间差异|显著性|统计学意义")
QUANTIFIER = ("绝大多数情况下", "大多数", "多数", "通常", "部分", "少数", "仅在", "仅对", "至少", "最多")
ORDINAL_GROUP = re.compile(r"(?:前|上述|前述|这)[一二三四五六七八九十两\d]+(?:种|项|类|者)")
CLAUSE_SPLIT = re.compile(r"[，,。！？；;\n]")
NEGATIVE_BEFORE = re.compile(r"(?:未|无|非|不|没有|尚未|尚无|缺少|缺乏|不足以|无法|不可|不得|不宜|不支持|不包含|未见|未给出).{0,14}$")
NEGATIVE_AFTER = re.compile(r".{0,40}(?:不成立|无依据|缺乏依据|未获支持|尚未证实|未证实)")
BLOCKING_SCOPE = ("全国", "各地", "必然", "首次", "普遍", "任何")
ACRONYM = re.compile(r"(?<![A-Za-z])[A-Z]{2,}(?:\d+(?:\.\d+)*)?(?![A-Za-z])")
METHOD_PHRASES = ("随机分配", "随机分组", "实地采集", "前瞻性随访", "全自动", "独立完成")
FORMULAIC = re.compile(r"需要强调|需强调|需要说明|需说明|需要指出|需指出|需要明确|需明确|需要注意|需注意|值得注意|换言之|仍需谨慎|不代表|不意味着|不能解释为|(?:不是|并非).{0,40}?而是|并非|并未|不是")
OPPOSITE_TERMS = (("行政效率", "行政低效"), ("行政效率", "行政效率低下"), ("正相关", "负相关"), ("上升", "下降"), ("增加", "减少"), ("提高", "降低"))
BLOCKING_OPPOSITE_PAIRS = {frozenset(("行政效率", "行政低效")), frozenset(("行政效率", "行政效率低下"))}
RECAP_PREFIX = re.compile(r"^(?:上述|以上|这些|两组|三组|该组|此处).{0,20}?(?:均为|都是|属于|是|为)")
RECAP_CUE = re.compile(r"^(?:(?:需|需要)(?:说明|强调|指出)的是[，,]?\s*)")
MEASURE_TERMS = ("核酸检测阳性率", "置信区间", "样本量", "观察值", "检测率")


def positive_occurrences(value: str, term: str) -> list[str]:
    """返回含目标词、且局部未见否定的短分句；仍需人工判断主张对象。"""
    found = []
    for clause in CLAUSE_SPLIT.split(value):
        clause = clause.strip()
        for match in re.finditer(re.escape(term), clause):
            before = clause[max(0, match.start() - 20):match.start()]
            after = clause[match.end():match.end() + 48]
            if NEGATIVE_BEFORE.search(before) or NEGATIVE_AFTER.match(after):
                continue
            found.append(clause)
    return found


def blocking_candidates(source: str, revision: str) -> list[dict[str, str]]:
    """仅拦截较明确的来源外正面范围词与后续计划；不是事实裁决。"""
    warnings = []
    for term in BLOCKING_SCOPE:
        if positive_occurrences(source, term):
            continue
        for clause in positive_occurrences(revision, term):
            warnings.append({"kind": "scope", "term": term, "clause": clause})
    for match in PLAN.finditer(revision):
        term = match.group(0)
        if positive_occurrences(source, term):
            continue
        for clause in positive_occurrences(revision, term):
            item = {"kind": "future_plan", "term": term, "clause": clause}
            if item not in warnings:
                warnings.append(item)
    for item in opposite_term_candidates(source, revision):
        if frozenset((item["source_term"], item["revision_term"])) in BLOCKING_OPPOSITE_PAIRS:
            warnings.append({"kind": "term_polarity", "term": item["revision_term"], "clause": item["clause"]})
    return warnings


def opposite_term_candidates(source: str, revision: str) -> list[dict[str, str]]:
    """来源与正文呈反向术语时提示复核；不推断该词所指对象。"""
    warnings = []
    for first, second in OPPOSITE_TERMS:
        for source_term, revision_term in ((first, second), (second, first)):
            if source_term not in source or revision_term in source:
                continue
            for clause in positive_occurrences(revision, revision_term):
                warnings.append({"source_term": source_term, "revision_term": revision_term, "clause": clause})
    return warnings


def source_absent_method_candidates(source: str, revision: str) -> list[dict[str, str]]:
    """定位正文新增的技术缩写与方法动作；来源缺词只触发复核。"""
    terms = set(ACRONYM.findall(revision)) - set(ACRONYM.findall(source))
    terms.update(term for term in METHOD_PHRASES if term in revision and not positive_occurrences(source, term))
    warnings = []
    for term in sorted(terms):
        for clause in positive_occurrences(revision, term):
            warnings.append({"term": term, "clause": clause})
    return warnings


def style_candidates(revision: str) -> list[dict[str, str]]:
    """逐处呈现套语与单独否定词候选；真实定义与争论须由编辑判别。"""
    warnings = []
    for match in FORMULAIC.finditer(revision):
        left = max(revision.rfind(mark, 0, match.start()) for mark in "。！？\n") + 1
        right_positions = [revision.find(mark, match.end()) for mark in "。！？\n"]
        right = min((position for position in right_positions if position >= 0), default=len(revision))
        warnings.append({"phrase": match.group(0), "sentence": revision[left:right].strip()})
    sentences = [sentence.strip() for sentence in re.split(r"(?<=[。！？])", revision) if sentence.strip()]
    for index, sentence in enumerate(sentences):
        bare_sentence = RECAP_CUE.sub("", sentence)
        if index == 0 or not RECAP_PREFIX.match(bare_sentence):
            continue
        prior = "".join(sentences[:index])
        for term in MEASURE_TERMS:
            if term not in sentence:
                continue
            already_stated = term in prior
            if term == "核酸检测阳性率":
                already_stated = already_stated or ("核酸检测" in prior and "阳性率" in prior)
            if already_stated:
                warnings.append({"phrase": "重复指标口径候选", "sentence": sentence})
                break
    return warnings


def inspect(source: str, draft: str, revision: str) -> dict:
    """只检查修订正文；来源是用户指定的权威资料，草稿仅用于定位可能漏保留的解释。"""
    source_numbers, revised_numbers = set(NUMBER.findall(source)), set(NUMBER.findall(revision))
    return {
        "novel_number_tokens": sorted(revised_numbers - source_numbers),
        "source_number_tokens_not_in_revision": sorted(source_numbers - revised_numbers),
        "scope_words_absent_from_source": [word for word in SCOPE if word in revision and word not in source],
        "plan_phrases_absent_from_source": [match.group(0) for match in PLAN.finditer(revision) if match.group(0) not in source],
        "strong_words_absent_from_source": [match.group(0) for match in STRONG.finditer(revision) if match.group(0) not in source],
        "supported_explanation_may_be_lost": bool(EXPLANATION.search(draft) and not EXPLANATION.search(revision)),
        "source_quantifiers_absent_from_revision": [word for word in QUANTIFIER if word in source and word not in revision],
        "ordinal_group_references_to_check": [match.group(0) for match in ORDINAL_GROUP.finditer(revision)],
        "source_absent_method_candidates": source_absent_method_candidates(source, revision),
        "opposite_term_candidates": opposite_term_candidates(source, revision),
        "style_candidates": style_candidates(revision),
        "blocking_candidates": blocking_candidates(source, revision),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="UTF-8 JSON，包含 source、draft、revision 字符串")
    parser.add_argument("--output", type=Path, help="可选 JSON 输出路径；省略时打印")
    parser.add_argument("--strict", action="store_true", help="存在高风险候选时输出结果并以状态 2 退出，等待编辑处理")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not all(isinstance(payload.get(key), str) for key in ("source", "draft", "revision")):
        raise ValueError("输入必须包含 source、draft、revision 三个字符串字段")
    result = inspect(payload["source"], payload["draft"], payload["revision"])
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if args.strict and result["blocking_candidates"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

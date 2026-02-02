from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

from ..models import (
    UserInput,
    Program,
    ProgramRecommendation,
    Reason,
    Deadline,
    TodoItem,
)


@dataclass
class Evaluation:
    level: str
    confidence: float
    reasons: List[Reason]
    todo: List[TodoItem]


LlmCallback = Callable[[UserInput, Program], Optional[ProgramRecommendation]]


def recommend_programs(
    user: UserInput,
    programs: List[Program],
    llm_callback: Optional[LlmCallback] = None,
) -> List[ProgramRecommendation]:
    recommendations: List[ProgramRecommendation] = []
    for program in programs:
        if llm_callback:
            llm_result = llm_callback(user, program)
            if llm_result:
                recommendations.append(llm_result)
                continue

        evaluation = _evaluate_program(user, program)
        deadline_ref = 1 if len(program.evidence) > 1 else 0
        deadline = Deadline(date=program.deadline, evidence_ref=deadline_ref if program.deadline else None)
        recommendations.append(
            ProgramRecommendation(
                program_id=program.program_id,
                program_name=program.program_name,
                level=evaluation.level,
                confidence=round(evaluation.confidence, 2),
                reasons=evaluation.reasons,
                deadline=deadline,
                todo=evaluation.todo,
                evidence=program.evidence,
            )
        )

    order = {"high": 0, "medium": 1, "low": 2, "unknown": 3}
    return sorted(recommendations, key=lambda item: (order.get(item.level, 9), -item.confidence))


def _evaluate_program(user: UserInput, program: Program) -> Evaluation:
    eligibility = program.eligibility
    reasons: List[Reason] = []
    todo: List[TodoItem] = []

    total_checks = 0
    matched = 0
    evidence_ref = 0

    def add_check(is_match: bool, ok_text: str, ng_text: str) -> None:
        nonlocal total_checks, matched
        total_checks += 1
        if is_match:
            matched += 1
            if ok_text:
                reasons.append(Reason(text=ok_text, evidence_ref=evidence_ref))
        else:
            if ng_text:
                reasons.append(Reason(text=ng_text, evidence_ref=evidence_ref))

    # Age
    if eligibility.age_min is not None or eligibility.age_max is not None:
        ok = True
        if eligibility.age_min is not None and user.age < eligibility.age_min:
            ok = False
            add_check(
                False,
                "",
                f"年齢が{eligibility.age_min}歳以上に満たないため対象外の可能性。{eligibility.age_min}歳以上で対象になります。",
            )
        if eligibility.age_max is not None and user.age > eligibility.age_max:
            ok = False
            add_check(
                False,
                "",
                f"年齢が{eligibility.age_max}歳以下に収まらないため対象外の可能性。{eligibility.age_max}歳以下で対象になります。",
            )
        if ok:
            add_check(True, "対象年齢に該当する", "")

    # Income
    if eligibility.income_max_yen is not None:
        if user.income_yen <= eligibility.income_max_yen:
            add_check(True, "所得上限に該当する", "")
        else:
            add_check(
                False,
                "",
                f"所得が上限（{eligibility.income_max_yen:,}円）を超えているため対象外の可能性。控除後所得で再確認してください。",
            )

    # Household
    if eligibility.household_min is not None or eligibility.household_max is not None:
        ok = True
        if eligibility.household_min is not None and user.household < eligibility.household_min:
            ok = False
            add_check(
                False,
                "",
                f"世帯人数が{eligibility.household_min}人以上に満たないため対象外の可能性。条件を満たす世帯構成で確認してください。",
            )
        if eligibility.household_max is not None and user.household > eligibility.household_max:
            ok = False
            add_check(
                False,
                "",
                f"世帯人数が{eligibility.household_max}人以下に収まらないため対象外の可能性。住民票の分離条件を確認してください。",
            )
        if ok:
            add_check(True, "世帯条件に該当する", "")

    # Dependents
    if eligibility.dependents_min is not None or eligibility.dependents_max is not None:
        dependents = user.dependents or 0
        ok = True
        if eligibility.dependents_min is not None and dependents < eligibility.dependents_min:
            ok = False
            add_check(
                False,
                "",
                f"扶養人数が{eligibility.dependents_min}人以上に満たないため対象外の可能性。妊娠中の届出など例外条件を確認してください。",
            )
        if eligibility.dependents_max is not None and dependents > eligibility.dependents_max:
            ok = False
            add_check(
                False,
                "",
                f"扶養人数が{eligibility.dependents_max}人以下に収まらないため対象外の可能性。世帯構成の条件を確認してください。",
            )
        if ok:
            add_check(True, "扶養人数の条件に該当する", "")

    # Occupation
    if eligibility.occupation_keywords:
        keywords = eligibility.occupation_keywords
        occupation = user.occupation or ""
        if any(key in occupation for key in keywords):
            add_check(True, "職業条件に合致する", "")
        else:
            add_check(
                False,
                "",
                "職業条件に合致しない可能性。経営者や求職者など対象となる区分で申請できるか確認してください。",
            )

    if total_checks == 0:
        score = 0.0
    else:
        score = matched / total_checks

    if score >= 0.9:
        level = "high"
    elif score >= 0.6:
        level = "medium"
    elif score > 0:
        level = "low"
    else:
        level = "unknown"

    confidence = 0.4 + (0.6 * score)

    # Base TODO from program steps
    todo_ref = 2 if len(program.evidence) > 2 else 0
    for step in program.todo_steps[:3]:
        todo.append(TodoItem(text=step, evidence_ref=todo_ref))

    # Add gray-zone guidance when not high
    if level != "high":
        for guidance in program.gray_zone_guidance[:2]:
            todo.append(TodoItem(text=f"対象条件に近づくため: {guidance}", evidence_ref=todo_ref))

    return Evaluation(level=level, confidence=confidence, reasons=reasons, todo=todo)

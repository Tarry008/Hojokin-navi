from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..models import (
    Deadline,
    Program,
    ProgramRecommendation,
    Reason,
    TodoItem,
    UserInput,
)


@dataclass
class Evaluation:
    eligible: bool
    level: str
    score: float
    matched_checks: int
    total_checks: int
    match_messages: List[str]
    gap_messages: List[str]
    reasons: List[Reason]
    todo: List[TodoItem]


def recommend_programs(
    user: UserInput,
    programs: List[Program],
) -> List[ProgramRecommendation]:
    scored_recommendations: List[tuple[ProgramRecommendation, float]] = []

    for program in programs:
        evaluation = _evaluate_program(user, program)
        deadline = Deadline(date=program.deadline, evidence_ref=None)
        recommendation = ProgramRecommendation(
            program_id=program.program_id,
            program_name=program.program_name,
            eligible=evaluation.eligible,
            level=evaluation.level,
            reasons=evaluation.reasons,
            deadline=deadline,
            todo=evaluation.todo,
            evidence=[],
        )
        scored_recommendations.append((recommendation, evaluation.score))

    order = {"high": 0, "medium": 1, "low": 2}
    sorted_with_score = sorted(
        scored_recommendations,
        key=lambda item: (0 if item[0].eligible else 1, order.get(item[0].level, 9), -item[1]),
    )
    return [item[0] for item in sorted_with_score]


def _evaluate_program(user: UserInput, program: Program) -> Evaluation:
    eligibility = program.eligibility
    reasons: List[Reason] = []
    todo: List[TodoItem] = []
    match_messages: List[str] = []
    gap_messages: List[str] = []

    total_checks = 0
    matched = 0
    evidence_ref = 0

    def add_check(is_match: bool, ok_text: str, ng_text: str) -> None:
        nonlocal total_checks, matched
        total_checks += 1
        if is_match:
            matched += 1
            if ok_text:
                match_messages.append(ok_text)
                reasons.append(Reason(text=ok_text, evidence_ref=evidence_ref))
            return
        if ng_text:
            gap_messages.append(ng_text)
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
    if eligibility.income_min_yen is not None or eligibility.income_max_yen is not None:
        ok = True
        if eligibility.income_min_yen is not None and user.income_yen < eligibility.income_min_yen:
            ok = False
            add_check(
                False,
                "",
                f"所得が下限（{eligibility.income_min_yen:,}円）に達していないため対象外の可能性。",
            )
        if eligibility.income_max_yen is not None and user.income_yen > eligibility.income_max_yen:
            ok = False
            add_check(
                False,
                "",
                f"所得が上限（{eligibility.income_max_yen:,}円）を超えているため対象外の可能性。控除後所得で再確認してください。",
            )
        if ok:
            if eligibility.income_min_yen is not None and eligibility.income_max_yen is not None:
                add_check(True, "所得レンジの条件に該当する", "")
            elif eligibility.income_min_yen is not None:
                add_check(True, "所得下限の条件に該当する", "")
            else:
                add_check(True, "所得上限に該当する", "")

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

    # Gender
    if eligibility.gender_keywords:
        user_gender = (user.gender or "").strip()
        if not user_gender:
            add_check(
                False,
                "",
                f"性別条件（{', '.join(eligibility.gender_keywords)}）の判定に必要な情報が未入力です。",
            )
        elif any(keyword in user_gender for keyword in eligibility.gender_keywords):
            add_check(True, "性別条件に該当する", "")
        else:
            add_check(
                False,
                "",
                f"性別条件（{', '.join(eligibility.gender_keywords)}）に合致しないため対象外の可能性。",
            )

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

    score = (matched / total_checks) if total_checks else 0.0
    eligible = total_checks > 0 and matched == total_checks

    if eligible:
        level = "high"
    elif score >= 0.7:
        level = "medium"
    elif score > 0.3:
        level = "low"
    else:
        level = "low"

    # TODO / evidence are generated by LLM. Keep rule engine focused on eligibility scoring.

    return Evaluation(
        eligible=eligible,
        level=level,
        score=score,
        matched_checks=matched,
        total_checks=total_checks,
        match_messages=match_messages,
        gap_messages=gap_messages,
        reasons=reasons,
        todo=todo,
    )

from __future__ import annotations

from dataclasses import dataclass

from schema import RawSignal


@dataclass
class Opportunity:
    source: str
    source_type: str
    title: str
    url: str
    timestamp: str
    problem_summary: str
    opportunity_summary: str
    target_customer: str
    delivery_type: str
    business_model_guess: str


def _guess_target_customer(text: str) -> str:
    mapping = {
        "clinic": "healthcare clinics",
        "warehouse": "warehouse operators",
        "seller": "ecommerce sellers",
        "agency": "service agencies",
        "real estate": "real estate teams",
        "restaurant": "restaurants",
        "manufacturer": "manufacturers",
        "accounting": "finance/accounting teams",
        "logistics": "logistics operators",
    }
    for key, value in mapping.items():
        if key in text:
            return value
    return "small and mid-size operations teams"


def _guess_delivery_type(text: str) -> str:
    if any(k in text for k in ["monitor", "alert", "dashboard", "report"]):
        return "managed AI operations + reporting"
    if any(k in text for k in ["inbox", "support", "follow-up", "scheduling"]):
        return "agent-run service workflow"
    return "automation setup + monthly agent operations"


def _guess_business_model(text: str) -> str:
    if any(k in text for k in ["lead", "conversion", "sales"]):
        return "performance fee + monthly retainer"
    if any(k in text for k in ["invoice", "payroll", "reconciliation", "compliance"]):
        return "monthly SaaS/ops subscription"
    return "setup fee + recurring operations fee"


def extract_opportunity(signal: RawSignal) -> Opportunity:
    text_blob = f"{signal.title} {signal.text}".lower()
    target = _guess_target_customer(text_blob)
    delivery = _guess_delivery_type(text_blob)
    business_model = _guess_business_model(text_blob)

    problem_summary = (
        f"{target.capitalize()} report a recurring, costly workflow bottleneck: "
        f"{signal.title.strip()}."
    )
    opportunity_summary = (
        f"Deploy AI agents to run/automate the workflow and reduce loss, delay, and labor cost "
        f"for {target}."
    )

    return Opportunity(
        source=signal.source,
        source_type=signal.source_type,
        title=signal.title,
        url=signal.url,
        timestamp=signal.timestamp,
        problem_summary=problem_summary,
        opportunity_summary=opportunity_summary,
        target_customer=target,
        delivery_type=delivery,
        business_model_guess=business_model,
    )
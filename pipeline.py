from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path


BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "data" / "leads.csv"
OUT_DIR = BASE / "output"


@dataclass
class Lead:
    company: str
    domain: str
    industry: str
    employee_count: int
    country: str
    pain_point: str
    persona: str


@dataclass
class EnrichedLead:
    company: str
    domain: str
    industry: str
    country: str
    segment: str
    persona: str
    pain_point: str
    automation_angle: str
    risk_flag: str
    priority_score: int
    llm_prompt: str
    crm_payload: dict
    zapier_webhook_payload: dict


def load_leads(path: Path = DATA_PATH) -> list[Lead]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = csv.DictReader(f)
        return [
            Lead(
                company=row["company"],
                domain=row["domain"],
                industry=row["industry"],
                employee_count=int(row["employee_count"]),
                country=row["country"],
                pain_point=row["pain_point"],
                persona=row["persona"],
            )
            for row in rows
        ]


def segment_lead(lead: Lead) -> str:
    if lead.employee_count >= 500:
        return "mid-market"
    if lead.employee_count >= 200:
        return "growth-stage"
    return "emerging"


def score_lead(lead: Lead, segment: str) -> int:
    score = 40
    if segment == "mid-market":
        score += 25
    elif segment == "growth-stage":
        score += 15
    if lead.industry in {"fintech", "saas", "healthcare"}:
        score += 20
    if "manual" in lead.pain_point or "slow" in lead.pain_point:
        score += 10
    return min(score, 100)


def automation_angle(lead: Lead) -> str:
    industry_angles = {
        "fintech": "automated reconciliation workflows and cleaner payment operations",
        "healthcare": "faster onboarding workflows and reduced operational follow-up",
        "saas": "personalized outbound loops and better CRM data hygiene",
        "logistics": "exception monitoring and automated operational follow-up",
    }
    return industry_angles.get(lead.industry, "workflow automation and operational visibility")


def build_llm_prompt(lead: Lead, segment: str, angle: str) -> str:
    return (
        "Write a concise, professional outbound email under 110 words. "
        f"Target persona: {lead.persona}. Company: {lead.company}. "
        f"Industry: {lead.industry}. Segment: {segment}. Country: {lead.country}. "
        f"Observed pain point: {lead.pain_point}. "
        f"Personalization angle: {angle}. "
        "Avoid unsupported claims. Include one clear call to action."
    )


def enrich(lead: Lead) -> EnrichedLead:
    segment = segment_lead(lead)
    score = score_lead(lead, segment)
    angle = automation_angle(lead)
    risk_flag = "review" if score < 65 else "ready"
    prompt = build_llm_prompt(lead, segment, angle)
    crm_payload = {
        "company": lead.company,
        "domain": lead.domain,
        "segment": segment,
        "industry": lead.industry,
        "country": lead.country,
        "persona": lead.persona,
        "priority_score": score,
        "status": "enriched",
        "risk_flag": risk_flag,
    }
    zapier_payload = {
        "event": "lead.enriched",
        "source": "ai_gtm_automation",
        "company": lead.company,
        "domain": lead.domain,
        "priority_score": score,
        "llm_prompt": prompt,
        "crm_payload": crm_payload,
    }
    return EnrichedLead(
        company=lead.company,
        domain=lead.domain,
        industry=lead.industry,
        country=lead.country,
        segment=segment,
        persona=lead.persona,
        pain_point=lead.pain_point,
        automation_angle=angle,
        risk_flag=risk_flag,
        priority_score=score,
        llm_prompt=prompt,
        crm_payload=crm_payload,
        zapier_webhook_payload=zapier_payload,
    )


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    enriched = [enrich(lead) for lead in load_leads()]
    enriched.sort(key=lambda item: item.priority_score, reverse=True)
    payload = {
        "summary": {
            "total_leads": len(enriched),
            "ready_for_outbound": sum(item.risk_flag == "ready" for item in enriched),
            "needs_review": sum(item.risk_flag == "review" for item in enriched),
            "average_priority_score": round(sum(item.priority_score for item in enriched) / max(1, len(enriched)), 2),
        },
        "leads": [asdict(item) for item in enriched],
    }
    out_path = OUT_DIR / "enriched_leads.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    print(f"Saved CRM/Zapier-ready payloads to {out_path}")


if __name__ == "__main__":
    main()

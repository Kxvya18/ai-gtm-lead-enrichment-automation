# AI GTM Lead Enrichment Automation

AI GTM Lead Enrichment Automation is a compact Python project for lead enrichment and outbound personalization. It takes a small set of structured lead records, evaluates them with simple business rules, generates sales-ready prompt payloads, and exports a clean JSON artifact that can be used by CRM, automation, or LLM workflows.

The project is designed to be easy to inspect, easy to run, and easy to adapt. It does not depend on external libraries, which makes it a good reference implementation for a simple lead-processing pipeline.

## Project Overview

The pipeline reads lead data from a CSV file, calculates a priority score for each record, assigns a segment based on company size, and generates a personalized outreach prompt. The final result is written as JSON so it can be passed directly into downstream tools such as a CRM, a lead routing system, or a webhook-based automation platform.

At a high level, the workflow is:

1. Load leads from `data/leads.csv`.
2. Segment each lead by employee count.
3. Score each lead using industry, segment, and pain-point signals.
4. Generate a concise LLM prompt for outbound email drafting.
5. Build CRM-friendly and webhook-friendly payloads.
6. Save the enriched dataset to `output/enriched_leads.json`.

## What The Output Contains

The generated JSON includes two main parts:

- A summary section with total leads, ready-for-outbound count, review count, and average score.
- A detailed lead list containing the original lead data, calculated segment, priority score, risk flag, CRM payload, and Zapier-style webhook payload.

This makes the output useful both as a demonstration artifact and as a structured handoff format for downstream systems. Because it is generated from the pipeline, it should not be treated as a source file to commit.

## Requirements

- Python 3.10 or newer
- No third-party packages are required

## How To Run

Run the pipeline from the project root:

```bash
python pipeline.py
```

When the script finishes, it prints a short summary to the console and rewrites `output/enriched_leads.json` with the latest enriched records.

## Repository Structure

```text
ai-gtm-lead-enrichment-automation/
├── README.md
├── .gitignore
├── pipeline.py
├── data/
│   └── leads.csv
└── output/
	└── enriched_leads.json
```

## Project Files

- `pipeline.py` contains the full enrichment pipeline, scoring logic, prompt generation, and JSON export.
- `data/leads.csv` contains the sample lead dataset used by the pipeline.
- `output/enriched_leads.json` contains the generated sample output produced by running the script.
- `.gitignore` excludes local caches, virtual environments, logs, and other machine-specific files.

## Data Model

Each lead record includes the following fields:

- `company`
- `domain`
- `industry`
- `employee_count`
- `country`
- `pain_point`
- `persona`

The pipeline expands each record into an enriched object with:

- `segment`
- `automation_angle`
- `risk_flag`
- `priority_score`
- `llm_prompt`
- `crm_payload`
- `zapier_webhook_payload`

## Example Use Case

This project can be used as a simple foundation for:

- outbound sales prioritization
- enrichment and lead routing demos
- prompt generation for sales email workflows
- CRM payload preparation
- webhook-based automation testing

## Notes

- The repository uses only the Python standard library.
- The included output file is reproducible and can be regenerated at any time by rerunning the pipeline.
- If you want a source-only repository, keep `output/` ignored and do not commit the generated JSON file.

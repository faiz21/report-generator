import pytest


@pytest.fixture
def sample_page_template():
    return {
        "system_prompt": "You are a professional report writer.",
        "user_instruction": "Write an executive summary of the plant performance data.",
        "report_format": "## Executive Summary\n\n### Key Findings\n...",
        "extraction_schema": {
            "type": "object",
            "properties": {
                "total_output": {"type": "number"},
                "efficiency_rating": {"type": "string"},
            },
        },
        "sample_data": {},
        "plant_code": "PLT-001",
        "plant_name": "Sample Plant Alpha",
        "plant_description": "A sample power generation plant",
        "page_title": "Executive Summary",
        "page_key": "executive_summary",
        "report_type": "quarterly_review",
    }


@pytest.fixture
def sample_dataset():
    return (
        "Plant Code: PLT-001\n"
        "Plant Name: Sample Plant Alpha\n"
        "Quarter: Q3 2025\n"
        "Total Output: 450 GWh\n"
        "Capacity Factor: 87.2%\n"
        "Availability: 95.1%\n"
        "Forced Outage Rate: 2.3%\n"
        "Heat Rate: 8,250 BTU/kWh\n"
    )

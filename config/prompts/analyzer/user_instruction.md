# Analyze Report Page: {page_title}

## Refined Report
{refined_report}

## Original Instructions
{user_instruction}

## Output Format
Respond in JSON:
```json
{
  "summary": "key takeaway summary grouped by categories",
  "content_score": {
    "overall": 0,
    "outline_alignment": 0,
    "writing_alignment": 0,
    "analysis_score": 0,
    "notes": ["note1", "note2"]
  },
  "extracted_data": {}
}
```

Scores should be 0-100. Notes should contain max 2 items.
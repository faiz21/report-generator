# Validate Report Page: {page_title}

## Generated Report
{raw_report}

## Required Format/Structure
{report_format}

## Original Instructions
{user_instruction}

## Validation Criteria
1. Structure matches required format
2. Heading hierarchy is correct (H1 > H2 > H3)
3. Glossary terms are used consistently
4. Professional tone is maintained
5. All required sections are present
6. Data accuracy and completeness

## Output Format
Respond in JSON:
```json
{
  "compliant_elements": ["list of correct elements"],
  "issues_found": ["list of specific issues"],
  "required_fixes": ["list of fixes needed"],
  "overall_status": "PASS" or "NEEDS_REVISION"
}
```
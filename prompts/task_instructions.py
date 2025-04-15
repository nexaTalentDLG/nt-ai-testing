# prompts/task_instructions.py

TASK_INSTRUCTIONS = {
    "Write a job description": """
We have found that our tools generate the best content when they know more about the specifics you're looking for. Consider using the prompt template below to guide you in creating your materials.

**Role Basics**
- Title: [job title and level (e.g., Senior Software Engineer)]
- Company Information: [Company name and description]
- Location: [work location, including remote options]

**Key Information**
- Primary Purpose: [brief description of the role's main objective]
- Must-Have Requirements: [2-3 critical qualifications or skills]
""",

    "Build Interview Questions": """
We have found that our tools generate the best content when they know more about the specifics you're looking for. Consider using the prompt template below to guide you in creating your materials.

**Role Context**
- Position: [job title and level]
- Key Skills: [2-3 most important skills to assess]
- Experience Level: [entry, mid, senior, etc.]

**Interview Focus**
- Primary Competencies: [key competencies you want to evaluate]
- Specific Scenarios: [any particular situations you want to explore]
""",

    "Create response guides": """
We have found that our tools generate the best content when they know more about the specifics you're looking for. Consider using the prompt template below to guide you in creating your materials.

**Question Context**
- Interview Questions: [list the questions you need guides for]

**Key Criteria**
- Success Indicators: [what would make a response strong]
- Red Flags: [what would make a response concerning]
""",

    "Evaluate candidate responses": """
We have found that our tools generate the best content when they know more about the specifics you're looking for. Consider using the prompt template below to guide you in creating your materials.

**Context**
- Role: [position title and level]
- Questions Asked: [list of questions posed]
- Candidate Responses: [paste the responses to evaluate]

**Focus Areas**
- Key Requirements: [critical skills or competencies to assess]
"""
}
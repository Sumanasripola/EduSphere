from groq import Groq
from app.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def generate_answer(question, context, is_comparison=False):

    base_prompt = """
You are an intelligent assistant.

You are given some information and a question.

Your job is to:
- Understand the question
- Extract relevant information
- Answer clearly and accurately

RULES:
- Use ONLY the provided information
- Do NOT use external knowledge
- Do NOT hallucinate
- Do NOT mention where the data comes from
- Be precise and avoid generic statements
"""

    formatting_rules = """
FORMATTING RULES:

1. Structure the answer clearly using sections when needed.

2. If explanation is needed:
   Use:
   **Explanation**

3. If a table is useful:
   Use:
   **Table**

4. If insights or conclusion are useful:
   Use:
   **Insights**

5. Tables:
   - Use ONLY if it improves clarity
   - Keep proper markdown format
   - Same number of columns in all rows
   - No broken formatting

6. IMPORTANT:
   - Do NOT repeat table data in explanation
   - Explanation should summarize, not duplicate

7. Keep answers clean, readable, and well-structured
"""

    # 🔥 GENERAL INTELLIGENT BEHAVIOR (NOT PDF-SPECIFIC)
    if is_comparison:
        extra_instruction = """
If the question involves comparison:

- First give a short explanation (high-level only)
- Then provide structured comparison (table or bullets)
- Then give a short insight if useful

Choose format based on clarity:
- Table → for structured numeric data
- Bullets → for conceptual comparison

DO NOT force a table.
"""
    else:
        extra_instruction = """
Answer in the most suitable format:

- Explanation → for concepts
- Table → for structured/numeric data
- Bullets → for lists

Choose what improves clarity.

DO NOT force any format unnecessarily.
"""

    prompt = f"""
{base_prompt}

{formatting_rules}

{extra_instruction}

---------------------

Information:
{context}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content
import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = input('AIzaSyCfVkH9UOLAWinEU5z-lwNVA9crbKGvneQ')
genai.configure(api_key=GOOGLE_API_KEY)

def get_input(prompt):
    print(prompt)
    lines = []
    while True:
        line = input()
        if line.strip() == '':
            break
        lines.append(line)
    return '\n'.join(lines)


question = get_input('Enter the question (end with empty line):')
ideal_answer = get_input('Enter the ideal answer (end with empty line):')
student_answer = get_input('Enter the student answer (end with empty line):')


eval_prompt = f"""
You are an expert evaluator and teacher. Your task is to assess a student's answer by comparing it with the ideal answer based on the given question.

Evaluate the student's answer using the following criteria:

1. **Correctness** - Are the facts and reasoning accurate?
2. **Completeness** - Does the answer cover all key points from the ideal answer?
3. **Relevance** - Is the answer focused on the question without going off-topic?
4. **Clarity** - Is the explanation clear and easy to understand?
5. **Structure and Flow** - Is the answer logically organized and well-structured?

Use this grading scale:
- **0-2: Poor** - Many errors or incomplete
- **3-5: Fair** - Some correct information but major issues
- **6-8: Good** - Mostly correct, minor gaps or unclear points
- **9-10: Excellent** - Accurate, complete, and well-explained

### Output Format:
Score: X/10  
Reason: [A concise explanation for the score]  
Suggestions: [Optional — What could be improved]

Question:
{question}

Ideal Answer:
{ideal_answer}

Student Answer:
{student_answer}
"""


def evaluate_answer(prompt):
    model = genai.GenerativeModel('models/gemini-2.5-pro')
    response = model.generate_content(prompt)
    return response.text

result = evaluate_answer(eval_prompt)

print("\n--- Evaluation Result ---")
print(result)

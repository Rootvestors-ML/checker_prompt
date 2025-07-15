from flask import Flask, render_template, request, redirect, url_for, flash
import os
import google.generativeai as genai
import csv
import re
from werkzeug.utils import secure_filename
import tempfile
from PIL import Image

app = Flask(__name__)
app.secret_key = 'b7f2e1c9-4a6d-4e8b-9c2a-7e3f1a2b5c8d'  

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = input('AIzaSyCfVkH9UOLAWinEU5z-lwNVA9crbKGvneQ')
genai.configure(api_key=GOOGLE_API_KEY)

def evaluate_answer(eval_contents):
    model = genai.GenerativeModel('models/gemini-2.5-pro')
    response = model.generate_content(eval_contents)
    return response.text


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    marks = question = ideal_answer = student_answer = suggestions = ''
    llm_score = ''
    if request.method == 'POST':
        marks = request.form.get('marks', '')
        question = request.form.get('question', '')
        ideal_answer = request.form.get('ideal_answer', '')
        student_answer = request.form.get('student_answer', '')
        suggestions = request.form.get('suggestions', '')

        # Handle file uploads
        files = {}
        for field in ['question', 'ideal_answer', 'student_answer']:
            file = request.files.get(f'{field}_file')
            if file and file.filename:
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[-1].lower()
                temp = tempfile.NamedTemporaryFile(delete=False, suffix='.'+ext)
                file.save(temp.name)
                files[field] = (temp, ext)
            else:
                files[field] = (None, None)

        # Prepare contents for Gemini
        eval_contents = [
            f"""
You are a strict and professional examiner. Your task is to compare a student's answer with the ideal answer and provide a detailed, rubric-based evaluation.

Evaluate based on the following criteria (each out of 10):

1. **Correctness** - Are the facts accurate?
2. **Completeness** - Are all key points included?
3. **Relevance** - Is the answer focused on the question?
4. **Clarity** - Is it well-written and understandable?
5. **Structure** - Is the answer logically organized?

Be strict. Avoid being overly generous or lenient.

---

### Desired Output Format (Use this structure exactly):

Marks:  
Correctness: X/10  
Completeness: X/10  
Relevance: X/10  
Clarity: X/10  
Structure: X/10  
**Final Score: X/{marks}**

---

# Reasoning:

1. Knowledge Understanding:
Comment on the depth of conceptual understanding shown in the answer.

2. Use of Technical or Key Terms: 
Mention if important subject-specific terms were missing or well-used.

3. Coverage of Key Points:
Which key parts of the ideal answer were included or missing?

4. Clarity & Expression: 
Was the answer well-phrased, concise, and readable?

---

# Suggestions for Improvement:
Give 2-3 bullet points suggesting what the student can do to improve the answer next time.

---

# Now Evaluate the Following:
"""
        ]
        # For each field, add text and/or file
        for field, label in zip(['question', 'ideal_answer', 'student_answer'], ['Question', 'Ideal Answer', 'Student Answer']):
            text = locals()[field]
            file_obj, ext = files[field]
            if text:
                eval_contents.append(f"**{label}:**\n{text}")
            if file_obj:
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    img = Image.open(file_obj.name)
                    eval_contents.append(img)
                elif ext == 'pdf':
                    with open(file_obj.name, 'rb') as f:
                        eval_contents.append({"mime_type": "application/pdf", "data": f.read()})
                file_obj.close()
        if suggestions:
            eval_contents.append(f"**Custom Notes (if any):**\n{suggestions}")
        result = evaluate_answer(eval_contents)
        match = re.search(r'Score:\s*(\d+)', result)
        if match:
            llm_score = match.group(1)
    return render_template('index.html', result=result, marks=marks, question=question, ideal_answer=ideal_answer, student_answer=student_answer, suggestions=suggestions, llm_score=llm_score)

@app.route('/review', methods=['POST'])
def review():
    question = request.form.get('question', '')
    ideal_answer = request.form.get('ideal_answer', '')
    student_answer = request.form.get('student_answer', '')
    llm_score = request.form.get('llm_score', '')
    user_marks = request.form.get('user_marks', '')
    user_review = request.form.get('user_review', '')
    marks = request.form.get('marks', '')
    llm_reasoning_rating = request.form.get('llm_reasoning_rating', '')
    llm_marks_rating = request.form.get('llm_marks_rating', '')
    llm_suggestions_rating = request.form.get('llm_suggestions_rating', '')

    csv_file = 'results.csv'
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['question', 'ideal_answer', 'student_answer', 'llm_marks', 'user_marks', 'user_review', 'marks', 'llm_reasoning_rating', 'llm_marks_rating', 'llm_suggestions_rating'])
        writer.writerow([question, ideal_answer, student_answer, llm_score, user_marks, user_review, marks, llm_reasoning_rating, llm_marks_rating, llm_suggestions_rating])
    flash('Review submitted and saved!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

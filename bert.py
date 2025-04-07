from flask import *
import google.generativeai as genai
import PyPDF2
import os
import textwrap
import re

# Initialize Flask application
app = Flask(__name__)

# Google Gemini API Key
GOOGLE_API_KEY = 'AIzaSyAdbPNd0d037Wad2-DZ8PKPzidNJ4H6anE'
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = None
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        model = genai.GenerativeModel('gemini-1.5-flash')
        break

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

# Function to generate questions from the text
def generate_questions_from_text(text):
    context_prompt = f"""
        Generate 5 multiple-choice question based on the following text. Each question should have 4 options, and one should be correct. Provide the output in the following structured format:

        Question1:
        - Question: <question_text>
        - Options: 
            a) <option_a>
            b) <option_b>
            c) <option_c>
            d) <option_d>
        - Correct Answer: <correct_answer>

        Text: {text}
    """
    
    response = model.generate_content(context_prompt)
    print("Model Response:")
    print(response.text)  # Print the raw response to inspect the format

    # Parse the response text into a structured dictionary
    question_dict = {}

    questions = []
    question_pattern = re.compile(
        r'Question\d+:\s*- Question:\s*(.*?)\s*- Options:\s*a\)\s*(.*?)\s*b\)\s*(.*?)\s*c\)\s*(.*?)\s*d\)\s*(.*?)\s*- Correct Answer:\s*(\w)', 
        re.DOTALL
    )
    
    matches = question_pattern.findall(response.text)
    for match in matches:
        question_data = {
            'question': match[0].strip(),
            'options': {
                'a': match[1].strip(),
                'b': match[2].strip(),
                'c': match[3].strip(),
                'd': match[4].strip()
            },
            'correct_answer': match[5].strip()
        }
        questions.append(question_data)

    # print(questions[0])
    
    # # Regular expression to extract the question, options, and correct answer
    # matchs = re.search(r'Question1:\s*- Question:\s*(.*?)\s*- Options:\s*a\)\s*(.*?)\s*b\)\s*(.*?)\s*c\)\s*(.*?)\s*d\)\s*(.*?)\s*- Correct Answer:\s*(\w\))\s*(.*?)\s*', response.text, re.DOTALL)
    
    # for match in matchs:
    #     # Extract the question and options
    #     question_dict['question'] = match.group(1).strip()
    #     question_dict['options'] = {
    #         'a': match.group(2).strip(),
    #         'b': match.group(3).strip(),
    #         'c': match.group(4).strip(),
    #         'd': match.group(5).strip()
    #     }
        
    #     # Capture both the letter and the text of the correct answer
    #     correct_answer_letter = match.group(6)  # e.g., 'c)'
        
        
    #     # Combine the letter and the answer text correctly
    #     correct_answers = f"{correct_answer_letter}"
    #     correct_answer=correct_answers.split(")")
    #     # Assign the correct answer to the dictionary
    #     question_dict['correct_answer'] = correct_answer[0]

    #     print(question_dict['correct_answer'],'////////////////////////////////')
    # else:
    #     print("No match found in the response.")
    
    return questions

def upload_pdf(files):
    text = extract_text_from_pdf(files)
    
    # Generate questions based on the extracted text
    question = generate_questions_from_text(text)
    return question


# upload_pdf("static/odf.pdf")
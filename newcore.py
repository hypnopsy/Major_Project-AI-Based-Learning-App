from pyexpat import model
from flask import *
import PyPDF2
import os
import textwrap
import re
from transformers import (
    AutoTokenizer, 
    AutoModelForQuestionAnswering, 
    BertConfig,
    logging as transformers_logging
)
import torch
import atexit

# Configure transformers logging
transformers_logging.set_verbosity_error()

# Initialize Flask application
app = Flask(__name__)

# Initialize BERT model and tokenizer with proper configuration
try:
    config = BertConfig.from_pretrained(
        'bert-large-uncased-whole-word-masking-finetuned-squad',
        output_hidden_states=False,
        output_attentions=False
    )
    
    tokenizer = AutoTokenizer.from_pretrained(
        'bert-large-uncased-whole-word-masking-finetuned-squad',
        use_fast=True
    )
    
    bert_model = AutoModelForQuestionAnswering.from_pretrained(
        'bert-large-uncased-whole-word-masking-finetuned-squad',
        config=config
    )
    
    # Move model to GPU if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    bert_model = bert_model.to(device)
    bert_model.eval()
    
except Exception as e:
    print(f"Error initializing BERT model: {str(e)}")
    raise Exception("Failed to initialize BERT model")

# Clean up function for gRPC
def cleanup():
    try:
        torch.cuda.empty_cache()
    except:
        pass

# Register cleanup function
atexit.register(cleanup)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        
        if not text.strip():
            raise ValueError("Extracted text is empty")
            
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        raise Exception("Failed to process PDF file")

def validate_answer_with_bert(question, options, context):
    try:
        best_score = -float('inf')
        best_answer = None
        
        for option_key, option_text in options.items():
            inputs = tokenizer(
                question,
                option_text + ". " + context,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            )
            
            # Move inputs to same device as model
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = bert_model(**inputs)
                start_scores = outputs.start_logits.squeeze()
                end_scores = outputs.end_logits.squeeze()
                score = torch.max(start_scores) + torch.max(end_scores)
                
                if score > best_score:
                    best_score = score
                    best_answer = option_key
        
        return best_answer
    except Exception as e:
        print(f"Error in BERT validation: {str(e)}")
        return None

# Function to generate questions from the text
def generate_questions_from_text(text):
    try:
        if not text or len(text.strip()) < 100:
            raise ValueError("Text is too short to generate questions")
            
        context_prompt = f"""
            Generate 5 multiple-choice questions based on the following text. Each question should have 4 short options, and one should be correct. Provide the output in the following structured format:

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
            question_text = match[0].strip()
            options = {
                'a': match[1].strip(),
                'b': match[2].strip(),
                'c': match[3].strip(),
                'd': match[4].strip()
            }
            
            # Use BERT to validate/correct the answer
            bert_answer = validate_answer_with_bert(question_text, options, text)
            
            question_data = {
                'question': question_text,
                'options': options,
                'correct_answer': bert_answer  # Use BERT-validated answer
            }
            questions.append(question_data)

        if not questions:
            raise ValueError("No questions could be generated")
            
        return questions
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        raise Exception("Failed to generate questions")

def upload_pdf(files):
    try:
        text = extract_text_from_pdf(files)
        questions = generate_questions_from_text(text)
        
        if not questions:
            raise Exception("No questions were generated")
            
        return {
            "success": True,
            "questions": questions
        }
    except Exception as e:
        error_message = str(e)
        print(f"Error in upload_pdf: {error_message}")
        return {
            "success": False,
            "error": "Could not generate MCQs. Please try again with a different PDF file."
        }

# Add basic route for error handling
@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({
        "success": False,
        "error": "Error Processing PDF. Please try again with a different PDF file."
    }), 500

# upload_pdf("static/odf.pdf")
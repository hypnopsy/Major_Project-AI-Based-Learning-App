from flask import *
from bert import *
from admin import *

main = Flask(__name__,template_folder='templates')


@main.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST' and 'sub' in request.form:
        if 'pdf_file' not in request.files:
            return "No file part in the request", 400
        
        pdf_file = request.files['pdf_file']

        if pdf_file.filename == '':
            return "No file selected", 400
        
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            # Extract text from the uploaded PDF
            extracted_text = extract_text_from_pdf(pdf_file)

            # Generate questions from the extracted text
            questions = generate_questions_from_text(extracted_text)

            # For demonstration, print the generated questions (or handle as needed)
            print(questions)

            # Render the questions or send them as a response
            return render_template('bert.html', questions=questions)

    return render_template('bert.html')


if __name__ == '__main__':
    main.run(debug=True)

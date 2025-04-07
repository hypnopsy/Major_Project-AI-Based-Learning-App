import time
import re
import os
import PyPDF2
import google.generativeai as genai
from langchain_chroma import Chroma  # Updated import
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyAdbPNd0d037Wad2-DZ8PKPzidNJ4H6anE"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize embedding function globally
embedding_function = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

def clean_text(text):
    """Cleans extracted text by removing metadata, tables, diagrams, and exercises."""
    unwanted_patterns = [
        r"Downloaded from .*? by .*?",
        r"Author[:].*",
        r"www\..*?\.com",
        r"\d{2,4}[-/]\d{2}[-/]\d{2,4}",
        r"(?i)table of contents.*?\n",
        r"(?i)acknowledg(e|ement)s.*?\n",
        r"(?i)copyright .*?\n",
        r"(?i)terms of use.*?\n",
        r"(?i)figure\s\d+[:]?.*",
        r"(?i)page\s\d+",
        r"(?i)illustration\s\d+[:]?.*",
        r"(?i)table\s\d+[:]?.*",
        r"\s{3,}",
        r"[-–]{5,}",
        r"\.{5,}",
        r"\n\s*\n",
    ]

    for pattern in unwanted_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text.strip()

def retrieve_and_generate_mcqs(pdf_collection, embedding_func, query, min_chunks=10, top_k=20):
    try:
        vectorstore = Chroma(
            persist_directory=pdf_collection, 
            embedding_function=embedding_func,
            collection_metadata={"hnsw:space": "cosine"}  # Add metadata for better matching
        )
        total_docs = vectorstore._collection.count()
        
        if total_docs < 1:
            raise ValueError("No documents found in collection")
            
        top_k = min(top_k, total_docs)
        search_results = vectorstore.similarity_search_with_score(query, k=top_k)
        
        # Improved chunk filtering
        relevant_chunks = []
        for doc, score in search_results:
            if score > 0.5 and doc.page_content and len(doc.page_content.strip()) > 50:
                relevant_chunks.append(doc.page_content)

        if len(relevant_chunks) < min_chunks:
            relevant_chunks = [doc[0].page_content for doc in search_results[:min_chunks]]
            
        if not relevant_chunks:
            raise ValueError("No relevant content found")

        context_text = "\n\n".join(relevant_chunks)

        # Enhanced Gemini Prompt for MCQ Generation
        gemini_prompt = """
        Generate 5 multiple-choice questions based on the following text. 
        Each question must follow this exact format:

        Q1. Question text here?
        A) First option
        B) Second option
        C) Third option
        D) Fourth option
        Correct Answer: A

        Content to analyze:
        {context_text}
        
        Important:
        - Keep questions clear and simple
        - Ensure exactly one correct answer
        - Use A, B, C, D format strictly
        """

        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(gemini_prompt)
        
        return response.text if response and hasattr(response, "text") else ""
    except Exception as e:
        print(f"Error in retrieve_and_generate_mcqs: {str(e)}")
        return ""

def format_mcq_output(mcq_content):
    """Formats the MCQ content for clean display."""
    # Split into sections
    sections = re.split(r"\*\*Section \d+: .*?\*\*", mcq_content)
    sections = [s.strip() for s in sections if s.strip()]
    
    formatted_output = []
    section_number = 1
    
    for section in sections:
        # Extract title
        title_match = re.search(r"(.*?)\n", section)
        title = title_match.group(1) if title_match else f"Section {section_number}"
        
        # Format content and questions
        content = section.replace(title, "").strip()
        
        formatted_output.append(f"\n{'='*50}")
        formatted_output.append(f"Section {section_number}: {title}")
        formatted_output.append(f"{'='*50}\n")
        formatted_output.append(content)
        formatted_output.append("\n")
        
        section_number += 1
    
    return "\n".join(formatted_output)

def upload(pdf_path):
    try:
        start_time = time.time()
        
        if not os.path.exists(pdf_path):
            raise Exception("PDF file not found")

        # Process PDF
        loader = PyPDFLoader(pdf_path)
        loaded_docs = loader.load()
        filtered_docs = loaded_docs[5:] if len(loaded_docs) > 5 else loaded_docs
        cleaned_docs = [clean_text(doc.page_content) for doc in filtered_docs]
        
        # Add validation for minimum text length
        if not cleaned_docs or not any(doc.strip() for doc in cleaned_docs):
            raise ValueError("No valid text content found in PDF")

        # Improved text splitting with error handling
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ".", "?", "!"],
            chunk_size=800,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False
        )
        
        combined_text = "\n".join(cleaned_docs)
        if len(combined_text.strip()) < 100:
            raise ValueError("PDF content too short")
            
        split_docs = text_splitter.split_text(combined_text)
        
        if not split_docs:
            raise ValueError("Failed to split text into chunks")
        
        # Setup ChromaDB
        pdf_collection_name = f"./chroma_db_{os.path.basename(pdf_path).replace('.pdf', '')}"
        vectorstore = Chroma.from_texts(
            split_docs,
            embedding_function,
            persist_directory=pdf_collection_name
        )
        
        print(f"Stored {vectorstore._collection.count()} text chunks in ChromaDB!")
        
        # Generate MCQs
        mcq_content = retrieve_and_generate_mcqs(
            pdf_collection_name, 
            embedding_function,
            query="Generate educational content and questions"
        )
        
        # Parse content into questions
        questions = []
        section_pattern = re.compile(
            r'Q\d+\.\s*(.*?)\n'
            r'A\)\s*(.*?)\n'
            r'B\)\s*(.*?)\n'
            r'C\)\s*(.*?)\n'
            r'D\)\s*(.*?)\n'
            r'Correct Answer:\s*([A-D])',
            re.DOTALL
        )
        
        matches = section_pattern.findall(mcq_content)
        for match in matches:
            question_data = {
                'question': match[0].strip(),
                'options': {
                    'a': match[1].strip(),
                    'b': match[2].strip(),
                    'c': match[3].strip(),
                    'd': match[4].strip()
                },
                'correct_answer': match[5].lower()
            }
            if all(question_data.values()):  # Ensure no empty values
                questions.append(question_data)
        
        print(f"\nExecution Time: {round(time.time() - start_time, 2)} seconds")
        return {"success": True, "questions": questions}
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return {
            "success": False,
            "error": "Could not generate MCQs. Please try again with a different PDF file."
        }

if __name__ == "__main__":
    # Test the function with a sample PDF
    result = upload(r"D:\PROJECTS\TOC-H\updations\Solve ai\AI-Question_&_Answers-WEB\file-sample_150kB.pdf")
    print(result)
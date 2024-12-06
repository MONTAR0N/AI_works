import os
from dotenv import load_dotenv
import PyPDF2
import pikepdf
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def convert_pdf_to_text(pdf_path):
    try:
        # First attempt with pikepdf to repair the PDF
        with pikepdf.open(pdf_path) as pdf:
            # Save to a temporary file
            temp_path = pdf_path + "_temp.pdf"
            pdf.save(temp_path)
        
        # Now read with PyPDF2
        with open(temp_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            
        # Clean up temporary file
        os.remove(temp_path)
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None

def main():
    # Get the current directory and build paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    manuales_dir = os.path.join(current_dir, "manuales")
    # Add path for output directory
    output_dir = os.path.join(current_dir, "manuales convertidos")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all PDF files in the manuales directory
    pdf_files = [f for f in os.listdir(manuales_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in manuales directory")
        return
        
    print(f"Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file}")
        pdf_path = os.path.join(manuales_dir, pdf_file)
        text = convert_pdf_to_text(pdf_path)
        
        if text:
            print(f"Successfully converted {pdf_file}")
            # Save each PDF's text to a separate file in the output directory
            output_filename = os.path.join(output_dir, f"output_{os.path.splitext(pdf_file)[0]}.txt")
            with open(output_filename, "w", encoding='utf-8') as text_file:
                text_file.write(text)
        else:
            print(f"Failed to convert {pdf_file}")

if __name__ == "__main__":
    main() 
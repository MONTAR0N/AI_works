import os
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import ConfigDict

# Load environment variables
load_dotenv()

class Config:
    protected_namespaces = ()

class Port(BaseModel):
    type: str = Field(..., description="Type of port (e.g., USB, HDMI, Ethernet)")
    quantity: int = Field(..., description="Number of ports of this type")

class ComputerSpecs(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_name: str = Field(..., description="Computer model name/number")
    max_memory: str = Field(..., description="Maximum supported RAM memory")
    processor_info: str = Field(..., description="CPU/Processor information")
    storage_capacity: str = Field(..., description="Maximum storage capacity")
    ports: List[Port] = Field(..., description="List of available ports")
    operating_system: Optional[str] = Field(None, description="Supported operating system(s)")
    additional_features: Optional[List[str]] = Field(None, description="Any additional notable features")

def extract_specs_from_text(client: OpenAI, text: str) -> ComputerSpecs:
    """Extract structured computer specifications from text using OpenAI."""
    
    # If text is too long, take first 15000 characters
    text = text[:15000]
    
    # Create a system message that includes the expected structure
    system_message = """You are a technical expert that extracts computer specifications from technical documentation.
Extract all relevant hardware specifications into a JSON with the following structure. IMPORTANT: processor_info and operating_system must be single strings, not lists or objects:
{
    "model_name": "Computer model name/number",
    "max_memory": "Maximum supported RAM memory",
    "processor_info": "Full processor description as a single string",
    "storage_capacity": "Maximum storage capacity",
    "ports": [
        {"type": "port type (e.g., USB, HDMI)", "quantity": number_of_ports}
    ],
    "operating_system": "All supported operating systems as a single string",
    "additional_features": ["feature1", "feature2"]
}"""

    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    
    # Parse the response into our Pydantic model
    response_text = completion.choices[0].message.content
    return ComputerSpecs.model_validate_json(response_text)

def main():
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Get the current directory and build paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(current_dir, "manuales convertidos")
    output_dir = os.path.join(current_dir, "manuales json")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all text files in the input directory
    text_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    
    if not text_files:
        print("No text files found in 'manuales convertidos' directory")
        return
    
    print(f"Found {len(text_files)} text files to process:")
    for text_file in text_files:
        print(f"Processing: {text_file}")
        
        # Read the input file
        input_path = os.path.join(input_dir, text_file)
        with open(input_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
        
        try:
            # Extract structured information
            specs = extract_specs_from_text(client, text_content)
            
            # Save to JSON file
            output_filename = os.path.splitext(text_file)[0] + '.json'
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json_file.write(specs.model_dump_json(indent=2))
            
            print(f"Successfully processed {text_file}")
            
        except Exception as e:
            print(f"Error processing {text_file}: {e}")

if __name__ == "__main__":
    main()

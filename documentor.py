import os
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL=os.getenv("OPENAI_MODEL")
OPENAI_ORG=os.getenv("OPENAI_ORG")
OPENAI_PROJ=os.getenv("OPENAI_PROJ")
OPENAI_KEY=os.getenv("OPENAI_KEY")
ROOT_FOLDER=os.getenv("ROOT_FOLDER")
DEST_FOLDER=os.getenv("DEST_FOLDER")


client = OpenAI(
  organization=OPENAI_ORG,
  project=OPENAI_PROJ,
  api_key=OPENAI_KEY
)

# Supported file extensions
supported_extensions = ['.py', '.ts']  # Add more as needed

def generate_documentation(code_content, file_path):
    """Generate documentation using OpenAI API for the given code content."""
    prompt = f"You are a documentation creator of code. Generate detailed documentation for the given code in markdown format:"
    response = client.chat.completions.create(
        model=OPENAI_MODEL,  # You can use different models like gpt-4
        messages=[
                {
                    "role": "system",
                    "content": f"{prompt}"
                },
                {
                    "role": "user",
                    "content": code_content
                }
            ]
        #max_tokens=500  # Adjust based on your needs
    )
    return response.choices[0].message.content

def process_file(file_path, root_folder):
    """Read the code from the file and generate corresponding documentation."""
    with open(file_path, 'r', encoding='utf-8') as file:
        code_content = file.read()

    # Generate documentation for the code
    documentation = generate_documentation(code_content, file_path)

    # Define the relative path from the root folder
    relative_path = os.path.relpath(file_path, root_folder)
    
    # Create corresponding path in the documentation folder
    documentation_path = os.path.join(DEST_FOLDER, relative_path)
    documentation_path = os.path.splitext(documentation_path)[0] + '.md'  # Save as .md file

    # Ensure the directory for the markdown file exists
    os.makedirs(os.path.dirname(documentation_path), exist_ok=True)

    # Write documentation to markdown file
    with open(documentation_path, 'w', encoding='utf-8') as md_file:
        md_file.write(f"# Documentation for {relative_path}\n\n")
        md_file.write(documentation)

def scan_project_directory(root_folder):
    """Recursively scan the project directory and process each supported file."""
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if any(file.endswith(ext) for ext in supported_extensions):
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}...")
                process_file(file_path, root_folder)

# Start scanning the root folders and generating documentation

if os.path.exists(ROOT_FOLDER):
    scan_project_directory(ROOT_FOLDER)
else:
    print(f"Root folder {ROOT_FOLDER} does not exist.")

print("Documentation generation complete.")

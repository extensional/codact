import argparse
import subprocess
import sys
import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key='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')

def get_python_project_structure(start_path=".", skip_dirs=None):
    no_add_dirs = ['node_modules', 'public', 'dev_env']
    if skip_dirs is None:
        skip_dirs = set(no_add_dirs)
    else:
        skip_dirs = set(skip_dirs)

    structure = []
    start_path = Path(start_path).resolve()

    for root, dirs, files in os.walk(start_path):
        # Remove directories we want to skip
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]

        for file in files:
            if not file.startswith('.'):  # Skip hidden files
                file_path = Path(root) / file
                relative_path = file_path.relative_to(start_path)
                structure.append(str(relative_path))

    return sorted(structure)

def get_file_contents(file_name):
    try:
        with open(file_name, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"Error: File '{file_name}' not found."
    except Exception as e:
        return f"Error reading file '{file_name}': {str(e)}"

def analyze_with_openai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes code and provides insights."},
                {"role": "user", "content": f"{prompt}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"
    
def install_package(package_name):
    try:
        subprocess.check_call(['pip', 'install', package_name])
        print(f"Successfully installed {package_name}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}. Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Description of your CLI tool")
    subparsers = parser.add_subparsers(dest='command', help="command to run")

    install_parser = subparsers.add_parser('install', help="Install Python packages using pip.")
    install_parser.add_argument('library_name', help="Library to install and integrate")
    parser.add_argument('-p', '--prompt', help="What feature of the library do you want to integrate")
    parser.add_argument('-f', '--files', help="Files where you want these changes to be integrated at")

    args = parser.parse_args()
    print(f'{args.prompt} {args.files}')
    if args.command == 'install':
            install_package(args.library_name)
            print("Library installed")
    else:
        parser.print_help()
    # current_path = os.getcwd()
    # print(f"Project structure for: {current_path}")
    # structure = get_python_project_structure(start_path=current_path, skip_dirs=['.venv', 'node_modules, public, dist, dev_env'])
    # print(structure)
    # content = get_file_contents(args.files)
    # dependencies = 
    # print(f"Contents of {'requirements.txt'}:")
    # print(content)
    # # pass package json, pass content of file, structured prompt
    prompt = f'Generate code for my python project to integrate {args.library_name} library. Add a REST endpoint to process payment requests using stripe. Respond with code only.'
    analysis = analyze_with_openai(prompt)
    print(analysis)
    # update local files


if __name__ == "__main__":
    main()
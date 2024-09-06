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


def replace_file_content(filename, new_content):
    ignore_dirs = ['.venv']
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        if filename in files:
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'w') as file:
                    file.write(new_content)
                print(f"File '{filename}' found and content replaced successfully.")
                return True
            except IOError as e:
                print(f"Error writing to file '{filename}': {e}")
                return False

    print(f"File '{filename}' not found in the current directory or its subdirectories.")
    return False

def main():
    parser = argparse.ArgumentParser(description="Description of your CLI tool")
    subparsers = parser.add_subparsers(dest='command', help="command to run")

    install_parser = subparsers.add_parser('install', help="Install Python packages using pip.")
    install_parser.add_argument('library_name', help="Library to install and integrate")
    parser.add_argument('-p', '--prompt', help="What feature of the library do you want to integrate")
    parser.add_argument('-f', '--files', help="Files where you want these changes to be integrated at")

    args = parser.parse_args()
    print(f'{args.install} {args.prompt} {args.files}')
    install_package(args.install)
    current_path = os.getcwd()
    print(f"Project structure for: {current_path}")
    structure = get_python_project_structure(start_path=current_path, skip_dirs=['.venv', 'node_modules, public, dist, dev_env'])
    print(structure)
    content = get_file_contents('requirements.txt')
    print(f"Contents of {'requirements.txt'}:")
    print(content)
    # pass package json, pass content of file, structured prompt
    prompt = f'I have a python project with and I want to integrate {args.install} into it. {args.prompt}. This is my project structure : \n {structure} \n and requirements.txt : {content}'
    analysis = analyze_with_openai(prompt)
    print(analysis)
    replace_file_content("", "");
    # update local files


if __name__ == "__main__":
    main()
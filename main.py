import argparse
import sys
import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key='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')

def get_nodejs_project_structure(start_path=".", skip_dirs=None):
    if skip_dirs is None:
        skip_dirs = set(['node_modules', 'public'])
    else:
        skip_dirs = set(skip_dirs).union({'node_modules', 'public'})

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

def analyze_with_openai(content, prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes code and provides insights."},
                {"role": "user", content: f"{prompt}\n\nHere's the content:\n\n{content}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Description of your CLI tool")
    parser.add_argument('library', help="Library to integrate")
    parser.add_argument('-p', '--prompt', help="What feature of the library do you want to integrate")
    parser.add_argument('-f', '--files', help="Files where you want these changes to be integrated at")

    args = parser.parse_args()
    print(f'{args.library} {args.prompt} {args.files}')
    current_path = os.getcwd()
    print(f"Project structure for: {current_path}")
    structure = get_nodejs_project_structure(start_path=current_path, skip_dirs=['.venv', 'node_modules, public, dist'])
    print(structure)

    print()
    print()
    content = get_file_contents('package.json')
    print(f"Contents of {'package.json'}:")
    print(content)
    # pass package json, pass content of file, structured prompt
    analysis = analyze_with_openai(content, args.prompt)
    print(analysis)
    # update local files


if __name__ == "__main__":
    main()
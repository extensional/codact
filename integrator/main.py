import argparse
import subprocess
import sys
import os
from pathlib import Path
from openai import OpenAI
from bs4 import BeautifulSoup
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

def get_docs(page_url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(page_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        page_source = driver.page_source

        soup = BeautifulSoup(page_source, "html.parser")
        text = soup.get_text()
        all_text = " ".join(text.split())

        driver.quit()
        return all_text
    except Exception as e:
        logging.error(f"Error in get_docs: {e}")
        return None
    

def run_code(run_cmd):
    try:
        cmd_result = subprocess.run(run_cmd.split(), check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
        print("RUNNING INTO ERRORS: ", error_message)
        print(f"Debugging script ...")
        print(run_cmd.split()[-1])
        file_content = get_file_contents(run_cmd.split()[-1])
        debug_prompt = f'This is my code: {file_content}. Debug this error: {error_message}'
        ai_response = analyze_with_openai(debug_prompt)
        print("TRY THIS SOLUTION TO FIX IT:")
        print(ai_response)

def main():
    parser = argparse.ArgumentParser(description="Description of your CLI tool")
    subparsers = parser.add_subparsers(dest='command', help="command to run")

    install_parser = subparsers.add_parser('install', help="Install Python packages using pip.")
    install_parser.add_argument('package_name', help="Library to install and integrate")
    install_parser.add_argument('-p', '--prompt', help="What feature of the library do you want to integrate")
    install_parser.add_argument('-f', '--file', help="File where you want these changes to be integrated into")

    debug_parser = subparsers.add_parser('debug', help="Debug your code")
    debug_parser.add_argument('-r', '--run', help="Command to run for debugging")

    args = parser.parse_args()
    if args.command == 'install':

        print(f'DEBUG: {args.package} {args.prompt} {args.file}')

        pypi_url = "https://pypi.org/project/" + args.package_name
        package_docs = get_docs(pypi_url)
        install_package(args.package_name)

        current_path = os.getcwd()
        # structure = get_python_project_structure(start_path=current_path, skip_dirs=['.venv', 'node_modules, public, dist, dev_env'])
        # print(structure)
        content = get_file_contents(args.file)
        prompt = f'I have a python project and I want to integrate {args.package_name} into it. Respond with code only. This is the documentation for {args.package_name} : {package_docs}. {args.prompt}. This is my current code: {content}'
        analysis = analyze_with_openai(prompt)
        print(analysis)
        # replace_file_content(args.file, "HELLO THERE!")

    elif args.command == 'debug':
        run_code(args.run)


if __name__ == "__main__":
    main()
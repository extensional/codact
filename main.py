import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Description of your CLI tool")
    parser.add_argument('action', help="Action to perform")
    parser.add_argument('-n', '--name', help="Name to use")
    parser.add_argument('-c', '--count', type=int, default=1, help="Number of times to perform the action")
    # docUrl, code files in context, where do u want to add it or create a new file for it,
    # detect the local file changes
    args = parser.parse_args()




if __name__ == "__main__":
    main()
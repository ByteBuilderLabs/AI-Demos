import json
import subprocess
import sys


def main():
    payload = json.loads(sys.stdin.read())
    file_path = payload.get("tool_input", {}).get("file_path", "")

    if not file_path.endswith(".py"):
        sys.exit(0)

    result = subprocess.run(
        ["python", "-m", "ruff", "check", file_path], capture_output=True, text=True
    )

    if result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()

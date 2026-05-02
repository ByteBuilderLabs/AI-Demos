import os
from anthropic import Anthropic
from github import Github
from schema import Review

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO_NAME = os.environ["GITHUB_REPOSITORY"]
PR_NUMBER = int(os.environ["PR_NUMBER"])

claude = Anthropic(api_key=ANTHROPIC_API_KEY)
gh = Github(GITHUB_TOKEN)


def get_pr_diff(repo_name: str, pr_number: int):
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    files = []
    for f in pr.get_files():
        if f.patch and f.status != "removed":
            files.append({"filename": f.filename, "patch": f.patch})
    return pr, files


def run_review(files: list) -> Review:
    diff = "\n\n".join(f"=== {f['filename']} ===\n{f['patch']}" for f in files)
    prompt = (
        "Review this PR diff. Flag security, complexity, missing tests, and bugs. "
        "Return empty findings if code is fine.\n\nDiff:\n" + diff
    )
    resp = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
        tools=[
            {
                "name": "submit_review",
                "description": "Submit findings",
                "input_schema": Review.model_json_schema(),
            }
        ],
        tool_choice={"type": "tool", "name": "submit_review"},
    )
    tool_use = next(b for b in resp.content if b.type == "tool_use")
    return Review.model_validate(tool_use.input)


def post_review(pr, review: Review):
    if not review.findings:
        pr.create_issue_comment(f"AI Review: {review.summary}\n\nNo issues found.")
        return
    pr.create_issue_comment(
        f"AI Review: {review.summary}\n\nFound {len(review.findings)} issue(s)."
    )
    commit = list(pr.get_commits())[-1]
    for f in review.findings:
        body = f"**[{f.severity.upper()}] {f.category}**\n\n{f.message}\n\n*Suggestion:* {f.suggestion}"
        try:
            pr.create_review_comment(
                body, commit, f.file_path, line=f.line, side="RIGHT"
            )
        except Exception as e:
            print(f"Skipped {f.file_path}:{f.line} - {e}")


def main():
    pr, files = get_pr_diff(REPO_NAME, PR_NUMBER)
    if not files:
        print("No reviewable files in this PR.")
        return
    review = run_review(files)
    post_review(pr, review)
    print(f"Posted {len(review.findings)} review comment(s).")


if __name__ == "__main__":
    main()

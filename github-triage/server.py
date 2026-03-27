import os
from dotenv import load_dotenv
from github import Github
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("github-triage")
gh = Github(os.getenv("GITHUB_TOKEN"))
repo = gh.get_repo(os.getenv("GITHUB_REPO"))


@mcp.tool()
def fetch_issues(state: str = "open", limit: int = 50) -> list[dict]:
    """Fetch GitHub issues from the repository."""
    issues = repo.get_issues(state=state)[:limit]
    return [
        {
            "number": i.number,
            "title": i.title,
            "body": i.body or "",
            "labels": [l.name for l in i.labels],
            "author": i.user.login,
        }
        for i in issues
    ]


@mcp.tool()
def label_issue(issue_number: int, labels: list[str]) -> str:
    """Apply labels to a GitHub issue."""
    issue = repo.get_issue(issue_number)
    for name in labels:
        try:
            repo.get_label(name)
        except:
            repo.create_label(name, color="0075ca")
    issue.set_labels(*labels)
    return f"Labels {labels} applied to #{issue_number}"


@mcp.tool()
def post_comment(issue_number: int, comment: str) -> str:
    """Post a comment on a GitHub issue."""
    issue = repo.get_issue(issue_number)
    issue.create_comment(comment)
    return f"Comment posted on #{issue_number}"


if __name__ == "__main__":
    mcp.run()

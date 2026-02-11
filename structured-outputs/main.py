from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI()
MODEL = "gpt-4o"


class ExtractedJob(BaseModel):
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    salary_min: int | None = Field(default=None, description="Minimum salary in USD")
    salary_max: int | None = Field(default=None, description="Maximum salary in USD")
    skills: list[str] = Field(description="Required technical skills")
    is_remote: bool = Field(description="Whether the position is remote")


def extract_job(raw_text: str) -> ExtractedJob:
    response = client.responses.parse(
        model=MODEL,
        input=[
            {"role": "system", "content": "Extract job posting details."},
            {"role": "user", "content": raw_text},
        ],
        text_format=ExtractedJob,
    )

    if response.output_parsed is None:
        print(f"Model refused: {response.output_text}")
        return None

    return response.output_parsed


if __name__ == "__main__":
    posting = """
    We're hiring a Senior Backend Engineer at Acme Corp!
    Salary: $140,000 - $180,000/year. Remote OK.
    Must know Python (5+ yrs), PostgreSQL, and Docker.
    Experience with Kubernetes is a plus.
    """

    result = extract_job(posting)

    if result:
        print(result.model_dump_json(indent=2))

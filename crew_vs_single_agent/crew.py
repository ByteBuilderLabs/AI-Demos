from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
import tools

llm = LLM(model="anthropic/claude-sonnet-5")


@tool("read_file")
def read_file_tool(path: str) -> str:
    """Read a source doc and return its text."""
    return tools.read_file(path)


@tool("write_file")
def write_file_tool(path: str, content: str) -> str:
    """Save the final report to a path."""
    return tools.write_file(path, content)


@tool("verify")
def verify_tool(path: str) -> str:
    """Score the report against the rubric. Returns PASS, or FAIL with missing fields."""
    return tools.verify(path)


def build_crew() -> Crew:
    planner = Agent(
        role="Planner",
        goal="Plan how to turn the source docs into one complete report.",
        backstory="You break the work into clear steps before anyone writes anything.",
        llm=llm,
        tools=[read_file_tool],
        verbose=False,
    )

    extractor = Agent(
        role="Extractor",
        goal="Pull every required field out of the source docs.",
        backstory="You read carefully and miss nothing the rubric asks for.",
        llm=llm,
        tools=[read_file_tool],
        verbose=False,
    )

    assembler = Agent(
        role="Assembler",
        goal="Assemble the extracted fields into the final report and write it.",
        backstory="You turn raw fields into one clean, readable document.",
        llm=llm,
        tools=[write_file_tool],
        verbose=False,
    )

    reviewer = Agent(
        role="Reviewer",
        goal="Verify the report passes the rubric and fix whatever fails.",
        backstory="Nothing ships until verify comes back PASS.",
        llm=llm,
        tools=[read_file_tool, write_file_tool, verify_tool],
        verbose=False,
    )

    docs = r".\docs\brief.md and .\docs\notes.md"
    out = r".\out\report.md"

    plan = Task(
        description=f"Read {docs}. Plan a report covering title, summary, owner, deadline, and risks.",
        expected_output="A short plan listing what to extract and how to structure the report.",
        agent=planner,
    )

    extract = Task(
        description=f"Using the plan, read {docs} and extract title, summary, owner, deadline, and risks.",
        expected_output="Each required field with its value, pulled from the docs.",
        agent=extractor,
        context=[plan],
    )

    assemble = Task(
        description=f"Assemble the extracted fields into one markdown report and write it to {out}.",
        expected_output=f"Confirmation the report was written to {out}.",
        agent=assembler,
        context=[extract],
    )

    review = Task(
        description=f"Read {out}, call verify on it, and fix any missing fields until verify returns PASS.",
        expected_output="A report at the output path that passes the rubric.",
        agent=reviewer,
        context=[assemble],
    )

    return Crew(
        agents=[planner, extractor, assembler, reviewer],
        tasks=[plan, extract, assemble, review],
        process=Process.sequential,
        verbose=False,
    )

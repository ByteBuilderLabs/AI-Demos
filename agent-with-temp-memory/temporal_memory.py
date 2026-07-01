import asyncio
import logging
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

load_dotenv()

# Neo4j logs a harmless "index already exists" error on every rerun. Mute it.
logging.getLogger("graphiti_core.driver.neo4j_driver").setLevel(logging.CRITICAL)


class Person(BaseModel):
    """A user the agent keeps memory about."""

    role: str | None = Field(None, description="The person's job or role, if mentioned")


class City(BaseModel):
    """A city or place where a person lives."""


async def main():
    graphiti = Graphiti(
        os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
        os.environ.get("NEO4J_USER", "neo4j"),
        os.environ.get("NEO4J_PASSWORD", "password"),
    )
    await graphiti.build_indices_and_constraints()

    jan = await graphiti.add_episode(
        name="loc_jan",
        episode_body="Alice lives in London.",
        source=EpisodeType.text,
        source_description="profile update",
        reference_time=datetime(2025, 1, 10, tzinfo=timezone.utc),
        entity_types={"Person": Person, "City": City},
    )
    print(f"First episode extracted {len(jan.nodes)} entities, {len(jan.edges)} edges.")

    jun = await graphiti.add_episode(
        name="loc_jun",
        episode_body="Alice lives in Tokyo.",
        source=EpisodeType.text,
        source_description="profile update",
        reference_time=datetime(2025, 6, 20, tzinfo=timezone.utc),
        entity_types={"Person": Person, "City": City},
    )
    print(
        f"Second episode extracted {len(jun.nodes)} entities, {len(jun.edges)} edges."
    )

    results = await graphiti.search("Where does the user live?")
    for edge in results:
        print(f"Fact:       {edge.fact}")
        print(f"  valid_at:   {edge.valid_at}")
        print(f"  invalid_at: {edge.invalid_at}")

    await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())

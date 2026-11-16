
from typing import Literal

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import (
    ToolError,
    ResourceNotFoundError,
)

from database import get_db
from models import (
    search_jobs_db,
    add_application_db,
    list_applications_db,
    update_application_db,
)


# Create the MCP server
mcp = MCPServer("PlaceMate")


# --------------------------------------------------
# TOOL 1: Search jobs
# --------------------------------------------------

@mcp.tool()
def search_jobs(keyword: str = "", location: str = "") -> list[dict]:
    """Search available placement jobs by keyword and location."""

    jobs = search_jobs_db(keyword, location)

    return jobs


# --------------------------------------------------
# TOOL 2: Add a job application
# --------------------------------------------------

@mcp.tool()
def add_application(student_name: str, job_id: int) -> dict:
    """Add a student's application for an available job."""

    if not student_name.strip():
        raise ToolError("Student name cannot be empty.")

    application = add_application_db(student_name.strip(), job_id)

    if application is None:
        raise ToolError(f"No job found with ID {job_id}.")

    return application


# --------------------------------------------------
# TOOL 3: List application history
# --------------------------------------------------

@mcp.tool()
def list_applications(student_name: str) -> list[dict]:
    """List all job applications belonging to a student."""

    if not student_name.strip():
        raise ToolError("Student name cannot be empty.")

    applications = list_applications_db(student_name.strip())

    return applications


# --------------------------------------------------
# TOOL 4: Update application status
# --------------------------------------------------

@mcp.tool()
def update_status(
    application_id: int,
    status: Literal[
        "applied",
        "shortlisted",
        "interview",
        "offer",
        "rejected"
    ]
) -> dict:
    """Update the status of an existing job application."""

    application = update_application_db(application_id, status)

    if application is None:
        raise ToolError(
            f"No application found with ID {application_id}."
        )

    return application


# --------------------------------------------------
# RESOURCE: Read a job by ID
# --------------------------------------------------

@mcp.resource("jobs://{job_id}")
def get_job(job_id: int) -> dict:
    """Retrieve complete job information using its ID."""

    with get_db() as conn:
        job = conn.execute(
            "SELECT * FROM jobs WHERE id = ?",
            (job_id,)
        ).fetchone()

    if job is None:
        raise ResourceNotFoundError(
            f"No job found with ID {job_id}."
        )

    return dict(job)


# --------------------------------------------------
# PROMPT: Interview preparation
# --------------------------------------------------

@mcp.prompt()
def interview_prep(job_title: str, company: str) -> str:
    """Generate an interview preparation prompt for a placement."""

    return f"""
    Help me prepare for an interview for the position of
    {job_title} at {company}.

    Please provide:

    1. Important technical topics to study.
    2. Frequently asked interview questions.
    3. Python and SQL coding questions if relevant.
    4. Practical scenario-based questions.
    5. HR interview questions.
    6. A short mock interview with answers and explanations.

    Keep the preparation suitable for an entry-level candidate.
    """


# --------------------------------------------------
# START THE SERVER
# --------------------------------------------------

if __name__ == "__main__":
    mcp.run()

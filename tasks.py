from crewai import Task
from tools import  search_tool, apply_tool,login_tool
from agents import Apply_agent, Webscrapingagent

scrape_task = Task(
    description=(
        "Login into the user's account using login tool and scrape top 5 internships"
    ),
    expected_output= "Successfull login and 5 scraped internships",
    tools=[login_tool,search_tool],
    output_file="webdata.json",
    async_execution=False,  
    agent=Webscrapingagent
)

Apply_task = Task(
    description = (
    "Go to the links extracted by the scrape task, and open each job. "
    "For every listing, answer any required questions or write the cover letter if prompted, "
    "upload the resume, submit the application, and show successful uploads."
),
    expected_output="JSON list of jobs where resume gets uploaded successfully.",
    tools=[apply_tool],
    agent=Apply_agent,
    context=[scrape_task],
    output_file="Applied.json",
    async_execution=False,
)


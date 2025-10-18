from agents import Webscrapingagent
from crewai import Task
from tools import search_tool, file_read_tool, apply_tool,login_tool
from agents import Filter_agent, Apply_agent

scrape_task = Task(
    description=(
        "Login into the user's account using login tool"
        "Scrape Internshala for Machine Learning, Data Science, and AI internships using search tool. "
        "Return the details of the internship including a valid link of the internship."
    ),
    expected_output="JSON list of internships with details.",
    tools=[login_tool,search_tool],
    agent=Webscrapingagent,
    output_file="webdata.json",
    async_execution=False,  
)

filter_task = Task(
    description=(
        "Read 'skills.txt' and rank internships based on relevance to resume keywords and skill."
    ),
    expected_output="JSON list of ranked jobs with similarity scores.",
    tools=[file_read_tool],
    agent=Filter_agent,
    context=[scrape_task],  
    output_file="ranked.json",
    async_execution=False,
)


resume_path="Rishita_Sharma.pdf"
Apply_task = Task(
    description=(
        f"Go to the link in ranked.json, and open the job. "
        f"For each listing, upload '{resume_path} and submit'. "
        "Show successful uploads"
    ),
    expected_output="JSON list of jobs where resume gets uploaded successfully.",
    tools=[apply_tool],
    agent=Apply_agent,
    context=[filter_task],
    output_file="Applied.json",
    async_execution=False,
)


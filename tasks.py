from agents import Webscrapingagent
from crewai import Task
from tools import search_tool, apply_tool, file_read_tool
from agents import Filter_agent, Apply_agent

scrape_task = Task(
    description=(
        "Scrape Internshala for Machine Learning, Data Science, and AI internships. "
        "Extract job title, company, location, stipend, duration, and link."
    ),
    expected_output="JSON list of internships with details.",
    tools=[search_tool],
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


# resume_path="Rishita_Sharma.pdf"
# Apply_task = Task(
#     description=(
#         "Login into internshala account using the credentials. "
#         f"Use 'ranked.json' to apply to internships. "
#         f"For each listing, open the application link and upload '{resume_path}'. "
#         "Show the whole automation procces"
#     ),
#     expected_output="JSON list of jobs where resume gets uploaded successfully.",
#     tools=[apply_tool],
#     agent=Apply_agent,
#     context=[filter_task],
#     output_file="Applied.json",
#     async_execution=False,
# )


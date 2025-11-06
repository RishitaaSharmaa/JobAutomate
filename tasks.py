from crewai import Task
from tools import  search_tool, file_read_tool, apply_tool,login_tool
from agents import Apply_agent, Webscrapingagent
# from agents import Filter_agent

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
skills="skills.txt"
interns="internships.json"
# filter_task = Task(
#     description=(
#         f"Read {skills} and the internships from {interns} and rank them based on relevance to resume keywords and skill."
#     ),
#     expected_output="JSON list of ranked jobs with similarity scores.",
#     tools=[file_read_tool],
#     agent=Filter_agent,
#     output_file="ranked.json",
#     async_execution=False,
# )

resume_path="Rishita_Sharma.pdf"
Apply_task = Task(
    description=(
        "Go to the links in webdata.json, and open the job. "
        "For each listing, upload and submit the resume. "
        "Show successful uploads"
    ),
    expected_output="JSON list of jobs where resume gets uploaded successfully.",
    tools=[apply_tool],
    agent=Apply_agent,
    context=[scrape_task],
    output_file="Applied.json",
    async_execution=False,
)


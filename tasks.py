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
        "Read 'skills.txt' and rank internships based on relevance to resume keywords and skills."
    ),
    expected_output="JSON list of ranked jobs with similarity scores.",
    tools=[file_read_tool],
    agent=Filter_agent,
    context=[scrape_task],  
    output_file="ranked.json",
    async_execution=False,
)

Apply_task = Task(
    description=(
        "Use 'ranked.json' to apply to internships by opening application links "
        "and submitting 'Rishita_Sharma.pdf'. If direct submission fails, write a short, professional email."
    ),
    expected_output="JSON list of successfully applied jobs.",
    tools=[apply_tool],
    agent=Apply_agent,
    context=[filter_task],
    output_file="Applied.json",
    async_execution=False,
)


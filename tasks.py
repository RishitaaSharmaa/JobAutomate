from agents import Webscrapingagent
from crewai import Task
from tools import search_tool, pdf_tool, apply_tool
from agents import Filter_agent, Apply_agent

scrape_task = Task(
    description=(
        "Scrape the Internshala website and extract detailed information about internship opportunities. "
        "Focus on finding job titles, company names, locations, stipends, duration, and application links. "
        "Look for machine learning, data science, and AI related internships specifically."
    ),
    expected_output="A structured list of internship opportunities with job titles, company names, locations, stipends, duration, and application links",
    tools=[search_tool],
    agent=Webscrapingagent,
    output_file="webdata.json"
)

filter_task = Task(
    description=(
        "Read and analyze the resume from the PDF file (Rishita_Sharma.pdf). "
        "Compare the scraped jobs against the resume content, focusing on technical skills, "
        "experience, and education mentioned in the resume. "
        "Calculate similarity scores based on matching keywords, required skills, and relevance. "
        "Rank the jobs from highest to lowest similarity score with detailed explanations."
    ),
    expected_output="List of jobs according to their ranks in json format",
    tools=[pdf_tool],
    agent=Filter_agent,
    context=[scrape_task],
    output_file="ranked.json"
)

Apply_task= Task(
    description=(
        "Use the ranked job list from 'ranked.json' and automatically apply to each job. "
        "Read the application links, open them, and upload the resume (Rishita_Sharma-1.pdf). "
        "If direct submission isn't possible, generate a professional application email or message. "
        "Ensure every job application is customized and properly formatted."
    ),
    expected_output="List of jobs successfully applied in a json format",
    tools=[apply_tool],
    agent= Apply_agent,
    context=[filter_task],
    output_file="Applied.json"
)
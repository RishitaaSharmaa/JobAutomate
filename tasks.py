from agents import Webscrapingagent
from crewai import Task
from tools import search_tool

scrape_task = Task(
    description=(
        "Scrape the Internshala website and extract detailed information about internship opportunities. "
        "Focus on finding job titles, company names, locations, stipends, duration, and application links. "
        "Look for machine learning, data science, and AI related internships specifically."
    ),
    expected_output="A structured list of internship opportunities with job titles, company names, locations, stipends, duration, and application links",
    tools=[search_tool],
    agent=Webscrapingagent
)

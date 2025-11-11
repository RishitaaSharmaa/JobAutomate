from crewai import Crew, Process
from agents import Apply_agent, Webscrapingagent
from tasks import scrape_task

from tasks import Apply_task

crew = Crew(
    agents=[Webscrapingagent, Apply_agent],
    tasks=[scrape_task, Apply_task],
    
    process=Process.sequential,
    verbose=True,  
    cache=True,
    max_rpm=100,
    share_crew=True
)

result = crew.kickoff()
print(result)
        

from crewai import Crew, Process
from agents import Webscrapingagent
from tasks import scrape_task

crew = Crew(
    agents=[Webscrapingagent],
    tasks=[scrape_task],
    process=Process.sequential,
    verbose=True,  
    cache=True,
    max_rpm=100,
    share_crew=True
)

result = crew.kickoff()
print(result)
        

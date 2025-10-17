from crewai import Crew, Process
from agents import Webscrapingagent, Filter_agent
# from agents import Apply_agent
from tasks import scrape_task, filter_task
# from tasks import Apply_task

crew = Crew(
    agents=[Webscrapingagent, Filter_agent],
    tasks=[scrape_task, filter_task],
    
    process=Process.sequential,
    verbose=True,  
    cache=True,
    max_rpm=100,
    share_crew=True
)

result = crew.kickoff()
print(result)
        

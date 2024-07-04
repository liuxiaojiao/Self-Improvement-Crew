from crewai import Task
from textwrap import dedent
from tools.top_voice_scraper_curator_tools import TopVoiceScraperCuratorTools
from crewai_tools import SerperDevTool

class Briefing_Tasks():
    def __init__(self, top_voice_source):
        self.top_voice_source = top_voice_source

    def innovation_research(self, agent):
        return Task(description=dedent(f'''
            Conduct a comprehensive analysis of the latest advancements in AI in 2024 through online search. Identify key trends, breakthrough technologies, and potential industry impacts. 
            Your final answer MUST deliver a detailed report on AI emerging trends and innovations. 
            {self.__tip_section()}'''),
            expected_output=("Full analysis report in bullet points"),
            tools=[SerperDevTool()],
            agent=agent)
  
    def top_voice_curation(self, agent):
        return Task(description=dedent(f'''
            Scrape the articles authored by leading voices from AI top voice source - deeplearning.ai, extracting key findings and trends related to AI development and its industrial applications.
            Your final deliverable MUST be a concise overview of the most important thoughts and developments in AI. 
            {self.__tip_section()}

            AI top voice source: {self.top_voice_source}'''),
            expected_output=("Full analysis report in bullet points"),
            tools=[TopVoiceScraperCuratorTools()],
            agent=agent) 

    def content_generation(self, agent):
        return Task(description=dedent(f'''
            Using the insights provided from previous steps, develop an engaging blog post that highlights the most significant trends and advancements in AI development and industrial application. 
            Your post should be informative yet accessible, catering to a tech-savvy audience.
            Your final deliverable MUST clearly present the latest trends and advancements in AI development and industrial application. 
            {self.__tip_section()}'''),
            expected_output=("Detailed full blog post of at least 5 paragraphs"),
            agent=agent) 

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100!"

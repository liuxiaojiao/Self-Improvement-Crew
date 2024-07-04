# Description: This script is used to extract course information from the provided URLs in the course_info.xlsx file.
# The script uses the CrewAI platform to create a crew of agents and tasks to extract the course information.
# env: CourseRecCrew (Python 3.10)
# python run dl_course_inventory.py

import pandas as pd
import json
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool
from crewai import Agent, Task, Crew
from pydantic import BaseModel
from textwrap import dedent
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
# Create the llm
llm_35_turbo = ChatOpenAI(api_key=openai_api_key, model='gpt-3.5-turbo')
scrape_tool = ScrapeWebsiteTool()


class DLCourseRecAgents():
    def scraper(self):
        return Agent(
            role="Senior Software Engineer",
            goal="Complete amazing web scraping job and extracting information required for online learning students.",
            tools = [scrape_tool],
            verbose=True,
            backstory=(
                '''As a Senior Software Engineer, your prowess in scraping web content and extracting
                course information based on instructions is unmatched. 
                Your skills help people get cleaned and structured results for online learning students.'''
                    ),
            max_iter=3,
            llm=llm_35_turbo,
        )

class CourseDetails(BaseModel):
        Title: str 
        Category: str 
        URL: str 
        Level: str 
        Length: str 
        Instructor: str 
        Highlights: str 
        Content: str 
        Syllabus: str 
        Audience: str 
        Skills: str

class DLCourseRecTasks():
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $100 commission!"

    def scraping_task(self, agent, url, category):
        return Task(
            description=dedent(
            f"""
            Scrape the course information from the provided URL below
            to extract the course level ,length, instructor, highlights, content, syllabus, audience and skills according to the category below.

            Here are the instructions to help you locate the highlights, content, syllabus and skills sections for each category. ALWAYS remember to output the entire detailed original content. 
            DO NOT summarize or revise the content.
            
            For "Short Course" category:
            The highlights: should come from the entire content before "What youll learn in this course" ,
            The content: pull the entire content after "What youll learn in this course" and before "Who should join",
            The syllabus: please create a learning plan based on the content,
            The skills: important keywords extracted from the highlights and goal, such as model names, programmging language, framework, methods or techniques. 
            
            For "Course" category:
            The highlights: should come from the entire content right after "What you will learn" and before "skills you will gain",
            The content: pull the detailed entire content related to course description,
            The syllabus: should come from the entire content after "Syllabus" and before 'Instructors',
            The skills: should come from the entire content after "skills you will gain". 

            For "Specialization" category:
            The highlights: should come from the entire content after "What youll get from this course" ,
            The content: should come from the entire content after "Syllabus",
            The skills: should come from the entire content after "skills you will gain" or "concepts you will learn". 

            
            Output in a json format. Use the exact keys as mentioned below:
            Title, Category, URL, Level, Length, Instructor, Highlights, Content, Syllabus, Audience, Skills.
            
            {self.__tip_section()}
    
            URL: {url}
            Category: {category}
            """),
            agent=agent,
            expected_output=("A json format"),
            output_json=CourseDetails
        )

class DLCourseRecCrew:
    def __init__(self, url, category):
        self.url = url
        self.category = category

    def run(self):
        # Define your custom agents and tasks in agents.py and tasks.py
        agents = DLCourseRecAgents()
        tasks = DLCourseRecTasks()

        scraper_agent = agents.scraper()
        scraping_task = tasks.scraping_task(
            scraper_agent,
            self.url,
            self.category,
        )

        crew = Crew(
            agents=[scraper_agent],
            tasks=[scraping_task],
            verbose=False,
        )

        result = crew.kickoff()
        return result


if __name__ == "__main__":
    print("## Welcome to Course Recommendation Crew")
    print("-------------------------------")

    inventory = pd.read_excel('course_info.xlsx')
    df = pd.DataFrame(columns = inventory.columns)

    for url in inventory['URL']:
        course_inputs = {
            'course_url': url,
            'course_category': inventory[inventory['URL'] == url]['Category'].values[0]
        }
  
        res = DLCourseRecCrew(
            url = course_inputs['course_url'], 
            category = course_inputs['course_category']).run()
        
        df_temp = pd.DataFrame.from_dict(json.loads(res), orient='index').T
        df = pd.concat([df, df_temp])

    df.to_excel('output/deeplearning_course_info_extracted.xlsx', index=False)
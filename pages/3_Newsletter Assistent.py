from crewai import Agent, Task, Crew
from pydantic import BaseModel
from textwrap import dedent
from briefing_agents import Briefing_Agents
from briefing_tasks import Briefing_Tasks
import os
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool
import pandas as pd
import json
import streamlit as st

from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
llm_35_turbo = ChatOpenAI(api_key=openai_api_key, model='gpt-3.5-turbo')


class Briefing_Crew():
    def __init__(self, top_voice_source):
        self.top_voice_source = top_voice_source

    def run(self):
        agents = Briefing_Agents()
        tasks = Briefing_Tasks(self.top_voice_source)

        innovation_researcher_agent = agents.innovation_researcher()
        top_voice_curator_agent = agents.top_voice_curator()
        content_strategist_agent = agents.content_strategist()

        innovation_research_task = tasks.innovation_research(innovation_researcher_agent)
        top_voice_curation_task = tasks.top_voice_curation(top_voice_curator_agent)
        content_generation_task = tasks.content_generation(content_strategist_agent)

        crew = Crew(
            agents=[innovation_researcher_agent, top_voice_curator_agent,  content_strategist_agent],
            tasks=[innovation_research_task, top_voice_curation_task, content_generation_task],
            verbose=True
        )

        result = crew.kickoff()
        return result


if __name__ == "__main__":
    st.subheader('Welcome to Trend Briefing Crew -- Help you to find the latest events and news in the tech world!')
    st.text('')
    st.text('')

    user_inputs = {'top_voice_source': 'deeplearning.ai'}

    newsletter_result = Briefing_Crew(top_voice_source = user_inputs['top_voice_source']).run()
    print(newsletter_result)
    # Save the output to a .txt file
    with open(f'output/briefing_newsletter.txt', 'w') as f:
        f.write(newsletter_result)

    # Output a list of meetup events based on the user's location and category
    topics_input = st.text_area(label='What trending topics would you like to learn about:', 
                                    height=2, 
                                    placeholder='For example, Data Science, Machine Learning, AI...')

    timeframe_input = st.text_area(label='Which timeframe are you searching for the events:', 
                                    height=2, 
                                    placeholder='For example, July 2024...')
    
    user_inputs_dict = {
            'topics': topics_input,
            'timeframe': timeframe_input
        }
    
    agent = Agent(
                role='Principal Event Researcher',
                goal='Do amazing online research about the events searching',
                backstory='''You are a Principal Researcher at a big company and your job is to 
                find recent online events related to given topics. ''',
                allow_delegation=False,
                llm=llm_35_turbo
            )

    task = Task(
        agent=agent,
        description=dedent(f'''
        Search online and find the 7-9 online events that will be organized in the timeframe below and are related to the given topics below.
        You will need to provide a detailed report on the events found. MAKE SURE to include the name, date, URL and brief description of the event.

        Output every event in a json format. Use the exact keys as mentioned below:
        Title, Date, URL, Content                
        Topics: {user_inputs_dict['topics']}
        Timeframe: {user_inputs_dict['timeframe']}
        '''),
        tools=[SerperDevTool()],
        expected_output=('detailed event lists in json format.')
    )
    
    st.write('We will help you to generate trending newsletter and search events based on the topics and timeframe you provide.')
    
    col1, col2 = st.columns(2) 
    st.empty()

    generate_newsletter = col1.button('Generate Trending Newsletter')
    if generate_newsletter:
        with open(f'output/briefing_newsletter.txt','r') as file:
            newsletter = file.read()
        st.download_button(label='Download Newsletter', data=newsletter, file_name='briefing_newsletter.txt', mime='text/plain')
    
    generate_event = col2.button('Generate List of Events to Attend')
    if generate_event:
        event_list_result = task.execute()
        res = json.loads(event_list_result)
        df = pd.DataFrame(res)
        df.to_csv('output/events_list.csv', index=False)

        event_df = pd.read_csv('output/events_list.csv')
        st.dataframe(event_df)

        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('latin')

        event_csv = convert_df(event_df)
        st.download_button(label = 'Download Events List', 
                            data = event_csv,
                            file_name = 'events_list.csv',
                            mime = 'text/csv')
        generate_event=False
  
    
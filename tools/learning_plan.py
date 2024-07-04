import pandas as pd
import json
import os
from textwrap import dedent
from langchain_openai import ChatOpenAI
from crewai_tools import BaseTool
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from crewai import Agent, Task, Crew
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
llm_35_turbo = ChatOpenAI(api_key=openai_api_key, model='gpt-3.5-turbo') # Loading GPT-3.5-turbo model


class LearningPlan():
    def __init__(self):
        pass
    
    def run(self, user_inputs):
        '''
        Generate personalized learning plan based on selected courses and users schedule/preferences
        '''

        if 'selected_course_list' not in user_inputs:
            raise KeyError("The 'selected_course_list' key is missing from user_inputs")
    
        course_inventory = pd.read_csv('inputs/course_inventory.csv', encoding="latin")
        # user_inputs_dict = {
        #     'selected_course_list': ['AI for Everyone','AI Agentic Design Patterns with AutoGen','Multi AI Agent Systems with crewAI'],
        #     'schedule': '5-7 hours per week',
        #     'notes': 'I am interested in learning more about AI and how to build my own AI agent.'
        # }
        
        course_plan_df = self.build_learning_schedule(user_inputs_dict = user_inputs, course_inventory_df=course_inventory)
        course_plan_df.to_excel('output/course_learning_plan.xlsx', index=False)
        course_plan_df.to_csv('output/course_learning_plan.csv', index=False)

    def build_learning_schedule(self, user_inputs_dict, course_inventory_df):
        
        selected_course = course_inventory_df[course_inventory_df['Title'].isin(user_inputs_dict['selected_course_list'])]
        
        plan_df = pd.DataFrame(columns = selected_course.columns)

        for i in range(len(selected_course)):
            learning_plans = selected_course.iloc[i].to_dict()

            agent = Agent(
                role='Lead Learning Architect',
                goal='Design a comprehensive and effective learning schedule that exceeds expectations.',
                backstory='''As a Lead Learning Architect at a prominent online learning company, you possess in-depth knowledge of 
                    online courses, including their highlights, content, and syllabus. Your expertise lies in creating detailed and 
                    tailored learning schedules that align with students' individual learning plans and time availability. 
                    Your role involves leveraging this knowledge to craft learning experiences that optimize student engagement and success.''',
                allow_delegation=False,
                llm=llm_35_turbo
            )

            task = Task(
                agent=agent,
                description=dedent(f'''
                Review the provided course syllabus below thoroughly. 
                Customize a detailed online learning schedule to align with user's unique needs, learning schedule and preference.
                For 'Short Course' category which has 1 hour length of course, the learning schedule should be designed to be completed within 3-4 days. Otherwise, the learning schedule should be designed based on the syllabus.
                Please take into account the user's notes to design the learning schedule.
                Consider any specific requirements or preferences mentioned by the user in the notes.

                Course Content: {selected_course.iloc[i]}
                Learning Schedule: {user_inputs_dict['schedule']}
                User Notes: {user_inputs_dict['notes']}

                Output the detailed learning schedule in bullet points with the number of days.
                '''),
                expected_output=("Clear online course learning schedule in bullet points")
            )

            plan_results = task.execute()
            learning_plans['Plan'] = plan_results

            df_temp = pd.DataFrame.from_dict(learning_plans, orient='index').T
            plan_df = pd.concat([plan_df, df_temp])

        return plan_df


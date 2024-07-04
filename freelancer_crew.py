from crewai import Crew, Task, Agent
from crewai_tools import ScrapeWebsiteTool, DOCXSearchTool
from freelancer_agents import Freelancer_Agents
from freelancer_tasks import Freelancer_Tasks
from langchain.chat_models import ChatOpenAI
from textwrap import dedent
import tempfile
import textract
import os
import streamlit as st
import docx2txt

from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
llm_35_turbo = ChatOpenAI(api_key=openai_api_key, model='gpt-3.5-turbo')

class Freelancer_Crew():
    def __init__(self, resume_input, personal_writeup_input, jd_url_input):
        self.resume_input = resume_input
        self.personal_writeup_input = personal_writeup_input  
        self.personal_writeup_doc = docx2txt.process(uploaded_personal_writeup)
        self.resume_doc = docx2txt.process(uploaded_resume)
        self.jd_url = jd_url_input 
        self.semantic_search_resume = DOCXSearchTool(docx=resume_input)
        self.jd_scraping_tool = ScrapeWebsiteTool(website_url=self.jd_url)

    def run(self):
        agents = Freelancer_Agents(self.resume_input, self.jd_url)
        tasks = Freelancer_Tasks(self.resume_input, self.personal_writeup_input, self.jd_url)

        researcher_agent = agents.researcher()
        profiler_agent = agents.profiler()
        resume_strategist_agent = agents.resume_strategist()
        cover_letter_strategist_agent = agents.cover_letter_strategist()
        interview_preparer_agent = agents.interview_preparer()

        research_task = tasks.research_task(researcher_agent)
        profile_task = tasks.profile_task(profiler_agent)
        resume_strategy_task = tasks.resume_strategy_task(resume_strategist_agent)
        cover_letter_strategy_task = tasks.cover_letter_strategy_task(cover_letter_strategist_agent)
        interview_preparation_task = tasks.interview_preparation_task(interview_preparer_agent)

        crew = Crew(
            agents=[researcher_agent, profiler_agent, resume_strategist_agent, cover_letter_strategist_agent, interview_preparer_agent],
            tasks=[research_task, profile_task, resume_strategy_task, cover_letter_strategy_task, interview_preparation_task],
            verbose=True
        )

        results = crew.kickoff()
        return results


if __name__ == "__main__":
    st.subheader('Welcome to Freelancer Crew -- Resume and Cover letter Builder!')
    st.write('Please upload your personal write-up, resume and job description link.')
    st.write('We assist on updating resumes, cover letters and interview preparation questions, based on qualifications on job descriptions.')
    st.text('')
    st.text('')

    uploaded_resume = st.file_uploader('Step 1: Upload your resume:', 
                                   accept_multiple_files = False, 
                                   type=['.txt', 'docx', '.pdf'])
    upload_resume = st.button('Upload Resume')
    if upload_resume:
        st.session_state['upload_resume'] = uploaded_resume
        st.write('Resume successfully uploaded.')

        save_path = os.path.join("streamlit/", uploaded_resume.name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_resume.getbuffer())
        upload_resume = False
    st.text('')
    st.text('')

    st.write('Personal write-up may contain information about your expertise, interests and experience that are not included in the resume')
    uploaded_personal_writeup = st.file_uploader('Step 2: Upload your personal writeup:', 
                                                accept_multiple_files = False, 
                                                type=['.txt', 'docx', '.pdf'])
    upload_personal_writeup = st.button('Upload Personal Writeup')
    if upload_personal_writeup:
        st.session_state['uploaded_personal_writeup'] = uploaded_personal_writeup
        st.write('Personal writeup successfully uploaded.')

        save_path = os.path.join("streamlit/", uploaded_personal_writeup.name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_personal_writeup.getbuffer())
        upload_personal_writeup = False
    st.text('')
    st.text('')

    jd_url_input = st.text_area(label='Step 3: Enter the URL of the job you are applying for:', 
                                height=2, 
                                placeholder='Paste the job description link/URL here...')

    st.text('')
    st.text('')
    
    # user_inputs = {'personal_writeup': uploaded_personal_writeup,
    #         'resume': uploaded_resume,
    #         'jd_url': jd_url_input}

    st.write('Ready for updating resume, cover letter and preparing interview questions.')
    start = st.button('Start!')
    if start:
        st.write('Processing now....')
        print('Starting Agentic Workflow!!!!!!!!!')
        resume_path = os.path.join("streamlit/", uploaded_resume.name)
        personal_writeup_path = os.path.join("streamlit/", uploaded_personal_writeup.name)

        Freelancer_Crew(resume_path, personal_writeup_path, jd_url_input).run()
        print('####################################')
        print('Agentic Workflow finished!!!!!!!!!!!')
        start=False

    st.text('')
    st.text('')
    col1, col2, col3 = st.columns([1,1,1]) 

    generate_resume = col1.button('1 - Generate Resume')

    if generate_resume: 
        with open('output/updated_resume.md', 'r') as file:
            resume_output = file.read()
        st.download_button('Download Resume', resume_output, file_name = 'updated_resume.txt', mime = 'text')

    generate_cover_letter = col2.button('2 - Generate Cover Letter')
    if generate_cover_letter: 
        with open('output/coverletter.md', 'r') as file:
            cover_letter_output = file.read()
        st.download_button('Download Cover Letter', cover_letter_output, file_name = 'coverletter.txt', mime = 'text')

    generate_interview = col3.button('3 - Generate Interview Preparation Materials')
    if generate_interview:
        with open('output/interview_preparation_materials.txt', 'r') as file:
            interview_preparation_output = file.read()
        st.download_button('Download Interview Preparation', interview_preparation_output, file_name = 'interview_preparation_materials.txt', mime = 'text')
        
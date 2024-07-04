from crewai import Task
from textwrap import dedent
from datetime import date
import docx2txt


class Freelancer_Tasks():
    def __init__(self, resume_input, personal_writeup_input, jd_url_input):
        # self.personal_writeup = textract.process(personal_writeup_input)
        # self.resume = textract.process(resume_input)
        self.jd_url = jd_url_input 
        self.personal_writeup = docx2txt.process(personal_writeup_input)
        self.resume = docx2txt.process(resume_input)

    def research_task(self, agent):
        return Task(description=dedent(f'''
            Analyze the provided job description to extract key skills, experiences and qualifications required, based on 
            the following job descriptions URL.
            {self.__tip_section()}

            Job description URL: {self.jd_url}
            '''),
            expected_output=("A structured list of job requirements, including necessay skills, qualifications and experiences."),
            agent=agent)
  
    def profile_task(self, agent):
        return Task(description=dedent(f'''
            Compile a detailed personal and professional profile by combining the personal write-up and resume below. 
            Utilize tools to extract and synthesize information from these sources on personal education, previous profressional experiences and skills.
            {self.__tip_section()}

            Personal writeup: {self.personal_writeup}
            Resume: {self.resume}
            '''),
            expected_output=("A comprehensive profile document that includes skills, project experiences, contributions, \
                                and capabilities to solve business problems."),
            agent=agent)

    def resume_strategy_task(self, agent):
        return Task(description=dedent(f'''
            Using the profile and job requirements obtained from previous tasks, tailor the resume to highlight the most relevant areas. 
            Employ tools to adjust and enhance the resume content. Make sure this is the best resume even but 
            don't make up any information. Update the work experience, skills and education. All to better reflect the 
            candidates abilities and how it matches the job posting.
            {self.__tip_section()}
            '''),
            expected_output=("An updated resume that effectively highlights the candidate's qualifications and experiences relevant to the job."),
            output_file='output/updated_resume.md',
            agent=agent) 
    
    def cover_letter_strategy_task(self, agent):
        return Task(description=dedent(f'''
            Using the profile, job requirements obtained from previous tasks, and the udpated resume to write a cover letter to apply the position within 4 paragraphs. 
            Make sure to emphasize the candidate's strengths but don't make up any information, and reflect the candidates abilities and how it matches the job posting.
            {self.__tip_section()}
            '''),
            expected_output=("A cover letter that effectively highlights the candidate's qualifications and experiences relevant to the job."),
            output_file='output/coverletter.md',
            agent=agent) 
  
    def interview_preparation_task(self, agent):
        return Task(description=dedent(f'''
            Create a set of potential interview questions and talking points based on the latest updated resume and job requirements. 
            Utilize tools to generate relevant questions and discussion points. Make sure to use these question and talking points to help 
            the candidate highlight the main points of the resume and how it matches the job posting. 
            {self.__tip_section()}
            '''),
            expected_output=("A document containing key questions and talking points that the candidate should prepare for the interview."),
            output_file='output/interview_preparation_materials.txt',
            agent=agent) 

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100!"

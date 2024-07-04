from crewai import Crew, Task, Agent
# from crewai_tools import ScrapeWebsiteTool, DOCXSearchTool
from langchain.chat_models import ChatOpenAI
from textwrap import dedent
import pandas as pd
import os
import streamlit as st
from tools.course_recommendation import CourseRecommendation
from tools.learning_plan import LearningPlan

from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
llm_35_turbo = ChatOpenAI(api_key=openai_api_key, model='gpt-3.5-turbo')


if __name__ == "__main__":
    st.subheader('Welcome to Course Recommendation Crew -- Find the course to learn!')
    # st.write('Please upload your profile to generate your learning profile.')
    st.text('')
    st.text('')

    # uploaded_profile = st.file_uploader('Step 1: Upload your profile:', 
    #                                accept_multiple_files = False, 
    #                                type=['.txt', 'docx', '.pdf', '.csv'])
    # upload_profile = st.button('Upload Profile')
    # if upload_profile:
    #     st.session_state['upload_profile'] = uploaded_profile
    #     st.write('Personal profile successfully uploaded.')
    #     upload_profile = False
    # st.text('')
    # st.text('')

    recommend = st.button('Recommend Courses for Data Science and Deep Learning!')
    if recommend:
        st.write('Processing now....')
        print('Starting Course Recommendation !!!!!!!!!')
        CourseRecommendation().run()
        print('####################################')
    
        course_rec = pd.read_excel('output/deeplearning_course_recommendation.xlsx')
        course_rec_list = course_rec['title'].tolist()
        print(course_rec_list)

        st.markdown('Here are recommended courses....')
        st.dataframe(course_rec)
        
        st.session_state['course_rec'] = course_rec
        st.session_state['course_rec_list'] = course_rec_list
       
        st.empty()
    
    if 'course_rec' not in st.session_state:
        st.empty()
    else:
        st.write('You can select the courses for yourself based on recommendation list.')
        
        course_rec_list = st.session_state['course_rec_list']
        if not recommend:
            course_rec = st.session_state['course_rec']
            st.dataframe(course_rec)
        selected_option = st.multiselect("Which of the following courses would you like to learn?",
                            course_rec_list,
                            max_selections=3,
                            placeholder="Select the course(s)...",
        )
        st.write("Your selected courses:", selected_option)
        print(selected_option)

        schedule = st.text_area(label='What does your learning schedule look like:', 
                                    height=2, 
                                    placeholder='Put how many hours per week that you can learn here...')

        notes = st.text_area(label='What else do you want us to know:', 
                                    height=2, 
                                    placeholder='Put your personal notes here...')
        
        # user_inputs = {
        #     'user_id':101,
        #     'selected_course_list': ['AI for Everyone','AI Agentic Design Patterns with AutoGen','Multi AI Agent Systems with crewAI'],
        #     'schedule': '5-7 hours per week',
        #     'notes': 'I am interested in learning more about AI and how to build my own AI agent.'
        # }
        
        user_inputs = {
            'selected_course_list': selected_option,
            'schedule': schedule,
            'notes': notes
        }

        print(user_inputs)

        st.text('')
        st.text('')

        st.write('Generate Learning Plan - Ready for generating your personal learning schedule.')
        create = st.button('Create Learning Plan!')
        if create:
            st.write('Processing now....')
            print('Start Creating Learning Plan!!!!!!!!!')
            LearningPlan().run(user_inputs)
            print('####################################')

            # with open('output/course_learning_plan_0625.csv', 'r', encoding='latin') as f:
            #     plan_df = f.read()

            plan_df = pd.read_csv('output/course_learning_plan.csv')

            output_df = plan_df[['Title','URL','Skills','Plan']]
            st.dataframe(output_df)

            @st.cache_data
            def convert_df(df):
                return df.to_csv(index=False).encode('latin')

            plan_csv = convert_df(plan_df)

            st.download_button(label = 'Download Learning Plan', 
                               data = plan_csv,
                               file_name = 'course_learning_plan.csv',
                               mime = 'text/csv')
            create=False
            

            
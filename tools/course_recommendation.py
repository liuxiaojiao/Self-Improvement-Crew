import pandas as pd
import json
import os
from langchain_openai import ChatOpenAI
from crewai_tools import BaseTool
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.retrievers import BM25Retriever, EnsembleRetriever

from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
llm_35_turbo = ChatOpenAI(api_key=openai_api_key, model='gpt-3.5-turbo') # Loading GPT-3.5-turbo model


class CourseRecommendation():
    def __init__(self):
        pass

    def run(self, file_path='inputs/course_inventory.csv', user_profile_path='inputs/user_profile.csv'):
        '''
        Select courses from inventory and recommend the top 10 most relevant courses to match users' profile/preferences.
        '''
        loader = CSVLoader(file_path=file_path, encoding="latin")
        data = loader.load()

        vectordb = self.build_vectordb(data)

        user_profile = pd.read_csv(user_profile_path, encoding="latin")
        results = self.get_recommendations(data, vectordb, 10, user_profile)['result']
        res = json.loads(results)
        print(res)
    
        df = pd.DataFrame(columns = res['recommended_courses'][0].keys())
        
        for k in res['recommended_courses']:
            df_temp = pd.DataFrame.from_dict(k, orient='index').T
            df = pd.concat([df, df_temp])
        df.to_excel('output/deeplearning_course_recommendation.xlsx', index=False)
        print('file saved !!!!!!!')

        return df

    def build_vectordb(self, docs):
        embeddings = OpenAIEmbeddings()
        # Alternative Approach: HuggingFace embeddings:bge-large
        # model_name = 'BAAI/bge-large-en'
        # # model_kwargs = {'device': 'cpu'}
        # # encode_kwargs = {'normalize_embeddings': True}
        # embeddings = HuggingFaceEmbeddings(model_name=model_name)
        vectordb = FAISS.from_documents(docs, embeddings)
        index_folder_path = 'output/faiss_index'
        index_name = 'faiss_0'
        if len(os.listdir(index_folder_path)) == 0:
            print('Creating FAISS index...')
            vectordb.save_local(index_folder_path, index_name)
        else: 
            print('Loading FAISS index....')
            vectordb = FAISS.load_local(index_folder_path, embeddings, index_name, allow_dangerous_deserialization=True)
        return vectordb

    def get_recommendations(self, docs, db, k, user_profile):
        faiss_retirever = db.as_retriever(search_kwargs={'k': k}, search_type='mmr')
        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k=k
        retriever = EnsembleRetriever(retrievers=[faiss_retirever, bm25_retriever], weights=[0.5, 0.5])
        
        template = '''
        You are given the full course inventory in the Deep Learning domain. The inventory context includes course level, length, highlights, 
        content, syllabus, audience and skills of a list of courses. 
        Based on the detailed course info, recommend the top 10 most relevant courses that fit the user's overall profile and preferences. 

        Make sure to recommend the course based on the following:
        Find the appropriate level of course that matches with user's skill level. 
        Find the course with highlights or content that cover or relevant to user's 'skills to learn' and 'practice areas'. 
        Find the course by taking 'personal notes' into accounts. 
        
        Course Inventory: {context}
        User Profile: {user_profile}

        Remember to provide the detailed reasons why you recommend these courses for the user. 
        Output the recommended courses information as well as the reasons for recommending the courses in json format with the following keys:
        'title', 'category', 'URL', 'level', 'reasons'. 
        '''

        rec_chain_prompt = PromptTemplate(template = template,
                                        input_variables = ['context', 'question'],
                                        partial_variables = {'user_profile': user_profile})

        rec_chain = RetrievalQA.from_chain_type(
            llm = llm_35_turbo, 
            retriever = retriever, 
            chain_type_kwargs={"prompt": rec_chain_prompt}
        )

        question = "What are the top 10 courses do you recommend the user to learn, and why is that?"
        result = rec_chain({"query": question})

        return result




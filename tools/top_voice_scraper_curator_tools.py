'''
Scrape webpage content from the deeplearning.ai blog
Summarize the major findings from Andrew's newsletters.
'''

import pandas as pd
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from crewai import Agent, Task
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from crewai_tools import BaseTool

# Load the .env file
load_dotenv()
# Get the OPENAI_API_KEY
openai_api_key = os.getenv('OPENAI_API_KEY')
# Create the llm
llm_35_turbo = ChatOpenAI(api_key=openai_api_key, model='gpt-3.5-turbo') # Loading GPT-3.5-turbo model


class TopVoiceScraperCuratorTools(BaseTool):
    name: str = 'deeplearning.ai top voice scraping and summarization tool'
    description: str = ('A tool to scrape and summarize the articles authored by leading voices from AI top voice source - deeplearning.ai.\
                        extracting key findings and trends related to AI development and its industrial applications. ')

    def generate_webpage_url_list(self, webpage_url):
        '''
        Get a list of webpages to scrape
        '''
        webpage_url_list = [webpage_url]
        for index in range(1, 3):
            webpage_url_list.append(f"https://www.deeplearning.ai/the-batch/tag/letters/page/{index}/")
        
        return webpage_url_list

    def generate_article_urls(self,webpage_url):
        '''
        get article's URL from the webpage
        '''
        # Send a GET request to the page
        response = requests.get(webpage_url)

        # Parse the page content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all article elements
        articles = soup.find_all('div', class_='p-6 flex flex-col items-start h-full')

        articles_title = []
        articles_urls = []

        # Loop through each article
        for article in articles:
            title = article.find('h2').text
            link = article.find('a')['href']
        
            articles_title.append(title)
            articles_urls.append('https://deeplearning.ai' + link)

        articles_urls_dict = {'title': articles_title, 'url': articles_urls}

        return articles_urls_dict

    def generate_article_content(self,article_url):
        '''
        Get the article content from its URL
        '''
        # Send a GET request to the page
        response = requests.get(article_url)

        # Parse the page content
        soup = BeautifulSoup(response.content, 'html.parser')

        def has_prose_in_class(html_tag):
            return html_tag.name == 'div' and html_tag.has_attr('class') and 'prose' in ' '.join(html_tag['class'])

        # Find the article content
        article_content_div = soup.find(has_prose_in_class)

        # Extract the text from the div
        article_body = article_content_div.get_text()

        return article_body
    
    # @tool('deeplearning.ai top voice scraping and summarization')
    def _run(self, top_voice_source: str) -> str:
        '''
        Scrape the articles authored by leading voices from AI top voice source - deeplearning.ai, \
        extracting key findings and trends related to AI development and its industrial applications. \
        Your final deliverable MUST be a concise overview of the most important thoughts and developments in AI.
        '''
        if 'deeplearning.ai' in top_voice_source:
            webpage = "https://www.deeplearning.ai/the-batch/tag/letters/"
        else:
            print('deeplearning.ai webpage not provided')

        webpage_url_list = self.generate_webpage_url_list(webpage_url=webpage)

        df_list = []

        for webpage_url in webpage_url_list:
            articles_urls_dict = self.generate_article_urls(webpage_url)

            article_content_list = []
            for article_url in articles_urls_dict['url']:
                article_content = self.generate_article_content(article_url)
                article_content_list.append(article_content)
            
            articles_urls_dict['content'] = article_content_list

            # Convert the dictionary to a dataframe and append it to the list
            df = pd.DataFrame(articles_urls_dict)
            df_list.append(df)
        
        # Concatenate all the dataframes in the list
        final_df = pd.concat(df_list, ignore_index=True)
        dt_today = datetime.now().strftime("%Y%m%d")
        final_df.to_excel('output/deeplearning_ai_articles.xlsx', index=False, sheet_name=dt_today)
        print("Total number of articles extracted : ", final_df.shape[0])

        important_findings = []
        for chunk in final_df['content'].head(15):
            
            agent = Agent(
                role='Principal Researcher',
                goal='Do amazing research and summaries based on the content you are working with',
                backstory="You're a Principal Researcher at a big company and your job is to summarize the trends and advancements in AI development and industrial application from articles authored by AI top voices. \
                List out the most important trends or insights from them.",
                allow_delegation=False,
                llm=llm_35_turbo
            )

            task = Task(
                agent=agent,
                description=f'Distill the content below into elegantly presented and digestible insights, \
                Return the most significant trends and advancements in AI development and industrial application.\n\nCONTENT\n----------\n{chunk}',
                expected_output=("Full analysis report in bullet points"),
            )

            findings = task.execute()
            important_findings.append(findings)s

        # Save the output to a .txt file
        with open('output/important_findings_AI_top_voice.txt', 'w') as f:
            for finding in important_findings:
                f.write(finding + '\n')

        return "\n\n".join(important_findings)

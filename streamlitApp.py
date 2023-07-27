import os
from dotenv import find_dotenv, load_dotenv 
import requests 
import json
from langchain import LLMChain, PromptTemplate 
from langchain.document_loaders import PlaywrightURLLoader
from langchain.text_splitter import CharacterTextSplitter 
from langchain.chat_models import ChatOpenAI
import streamlit as st

load_dotenv(find_dotenv())
SERPAPI_API_KEY = os.getenv("SERP_API_KEY")

def search (query):
    url = "https://google.serper.dev/search"
    payload = json.dumps ({
        "q": query
    })
    headers = {
        'X-API-KEY': SERPAPI_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = response.json()

    print("search results: ", response_data)
    return response_data

# 2. llm to choose the best articles, and return urls
def find_best_article_urls(response_data, query) :
    # turn json into string
    response_str = json.dumps(response_data)
    # create llm to choose best articles
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=.7)
    template = """You are a world class journalist & researcher, you are extremely good at find most relevant articles to certain topic;
    {response_str}
    Above is the list of search results for the query {query}.
    Please choose the best 3 articles from the list, return ONLY an array of the urls, do not include anything else; return ONLY an array of the urls, do not include anything else"""
    prompt_template = PromptTemplate(input_variables=["response_str", "query"], template=template)
    article_picker_chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True)
    urls = article_picker_chain.predict(response_str=response_str, query=query)
    # convert string to list
    url_list = json.loads(urls)
    print (url_list)
    return url_list

# 3. get content for each article from urls and make summaries
def get_content_from_urls(urls):
    print("Getting content from urls...")
    # loader = UnstructuredURLLoader(urls=urls)
    loader = PlaywrightURLLoader(urls=urls, remove_selectors=["header", "footer"])
    data = loader.load()
    print(data)
    return data

def summarise(data, query):
    print("Summarising content...")
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=3000, chunk_overlap=200, length_function=len)
    text = text_splitter.split_documents(data)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=.7)
    template = """
    {text}
    You are a world class journalist, and you will try to summarise the text above in order to create a twitter thread about {query}
    Please follow all of the following rules:
    1/ Make sure the content is engaging, informative with good data
    2/ Make sure the content is not too long, it should be no more than 3-5 tweets
    3/ The content should address the {query} topic very well
    4/ The content needs to be viral, and get at least 1000 likes
    5/ The content needs to be written in a way that is easy to read and understand
    6/ The content needs Jo give audience actionable advice & insights too
    SUMMARY:
    """
    prompt_template = PromptTemplate(input_variables=["text", "query"], template=template)
    summariser_chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True)

    summaries = []
    for chunk in enumerate(text):
        summary = summariser_chain.predict(text=chunk, query=query)
        summaries. append (summary)

    print (summaries)
    return summaries

# 4. Turn summarization into twitter thread
def generate_thread(summaries, query):
    print("Generating twitter thread...")
    summaries_str = str(summaries)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=.7)
    template = """
    {summaries_str}
    You are a world class journalist & twitter influencer, text above is some context about {query} Please write a viral twitter thread about {query} using the text above, and following all rules below:
    1/ The thread needs to be engaging, informative with good data
    The thread needs to be around than 3-5 tweets
    3/ The thread needs to address the {query} topic very well
    4/ The thread needs to be viral, and get at least 1000 likes
    5/ The thread needs to be written in a way that is easy to read and understand
    6/ The thread needs to give audience actionable advice & insights too
    TWITTER THREAD:
    """
    prompt_template = PromptTemplate(input_variables=["summaries_str", "query"], template=template)
    twitter_thread_chain = LLMChain (llm=llm, prompt=prompt_template, verbose=True)
    twitter_thread = twitter_thread_chain.predic(summaries_str=summaries_str, query=query)
    print (twitter_thread)
    return twitter_thread

def main():
    st.set_page_config(page_title="Autonomous researcher - Twitter threads", page_icon=":bird:")
    st.header("Autonomous researcher - Twitter threads :bird:")
    query = st.text_input ("Topic of Twitter thread")
                            
    if query:
        print (query)
        st.write("Generating twitter thread for: ", query)
        
        search_results = search(query)
        urls = find_best_article_urls(search_results, query)
        data = get_content_from_urls(urls)
        summaries = summarise(data, query)
        thread = generate_thread(summaries, query)
        with st.expander("search results"):
            st.info(search_results)
        with st.expander("best urls"):
            st.info(urls)
        with st.expander("data"):
            st.info(data)
        with st.expander ("summaries"):
            st.info(summaries)
        with st.expander ("thread"):
            st.info(thread)

if __name__ == '__main__':
    main()
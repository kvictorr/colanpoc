import os
from pathlib import Path
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_core.tools import Tool
from langchain_classic.agents import initialize_agent, AgentExecutor, create_react_agent
from langchain_classic.agents.agent_types import AgentType
from langchain_classic import hub
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

OPENAI_API_KEY = "your api key"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
GPT_MODEL = "gpt-4"
uploaded_file = st.session_state["input_file"]
file_name = uploaded_file.name
file_path = Path(file_name)
temp_file = "./temp.pdf"
loader = None
print("File Ext: " + file_path.suffix)
if ".pdf" == file_path.suffix.lower(): 
    with open(temp_file, "wb") as file:
        file.write(uploaded_file.getvalue())
    loader = PyPDFLoader(temp_file)
elif ".txt" == file_path.suffix.lower():
    temp_file = "./temp.txt"
    with open(temp_file, "wb") as file:
        file.write(uploaded_file.getvalue())
    loader = TextLoader(temp_file)
documents = loader.load_and_split()
print("Number of pages loaded:", len(documents))
embeddings = OpenAIEmbeddings()
# Create a ChromaDB vectorstore
vector_db = Chroma.from_documents(documents, embeddings)
print("Number of documents in the vectorstore:", len(vector_db))
retriever = vector_db.as_retriever()
# Create the question-answer chain
my_llm = ChatOpenAI(model=GPT_MODEL, temperature=0.7, max_tokens=4096)  # use GPT-4 model
qa_chain = RetrievalQA.from_chain_type(
        llm=my_llm,
        retriever=retriever,
        return_source_documents=True
    ) 
# Wrap RetrievalQA as a Tool
rag_tool = Tool(
        name="RAGRetriever",
        func=lambda q: qa_chain.invoke(q),
        description="Useful for answering questions from internal documents"
    )
    

class RoutingAgent():
   
    def interact(question):
        # Create the question-answer chain
        my_llm = ChatOpenAI(model=GPT_MODEL, temperature=0.2, max_tokens=4096)  # use GPT-4 model
        static_prompt = question + ". Classify the previous sentence using the following strategy. " + \
            "If the sentence is related to summary, respond with single word Summary. " + \
            "If the sentence contains the word sentiment, respond with single word Sentiment. " + \
            "Otherwise, respond with single word Question. document refers to the first statement. "
        
        try:
            # 4. Run the prompt
            response = my_llm.invoke(static_prompt)
            #print(response.content)
            print("Classification: ", response.content)
            if len(response.content) > 0:
                match str(response.content):
                    case 'Summary': return SummaryAgent.interact(question)
                    case 'Sentiment': return SentimentAgent.interact(question)
        except Exception  as e:
            print(e)
        return BaseAgent.interact(question)

class BaseAgent():
    
    def interact(question):
       
        prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a knowledgeable assistant with access to the enterprise knowledge base.
            Your retrieval strategy:
            1. When a user asks a question, search the context for relevant information
            2. Document refers to the context
            3. Input refers to the context
            4. Source refers to the context
            5. Content refers to the context
            6. Provide brief answer to the question based on the information available in the context
            7. Do not include any information from general knowledge base outside the context
            8. If you cannot find the answer in the knowledge base, say I do not have answer for this question."""),
                
                ("human", "{input}"),
               MessagesPlaceholder(variable_name="agent_scratchpad"),
               MessagesPlaceholder(variable_name="tool_names", optional=True),
               MessagesPlaceholder(variable_name="tools", optional=True)
            ])
        # Initialize LangChain Agent with the Tool
        agent = initialize_agent(
            tools=[rag_tool],
            llm=my_llm,
            prompt=prompt,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        print("Base Agent Generating Response : " + question)
        try:
            # 4. Run the Agent
            response = agent.invoke(question + " in the document. document, content, input, source refer to the context")
            #print(response)
            print("Answer:", response['output'])
            if len(response['output']) > 0:
                return response['output']
        except Exception  as e:
            print(e)
        return "Sorry! I couldn't find answer for your question at this time. Please try with detailed information."

class SummaryAgent():
    
    def interact(question):
       
        prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a knowledgeable assistant with access to the enterprise knowledge base.
            Your retrieval strategy:
            1. When a user asks a question, search the context for relevant information
            2. Document refers to the context
            3. Input refers to the context
            4. Source refers to the context
            5. Content refers to the context
            6. Provide brief summary of the information available in the context not exceeding 100 words
            7. Do not include any information from general knowledge base outside the context
            8. If you cannot find the answer in the knowledge base, say I do not have answer for this question."""),
                
                ("human", "{input}"),
               MessagesPlaceholder(variable_name="agent_scratchpad"),
               MessagesPlaceholder(variable_name="tool_names", optional=True),
               MessagesPlaceholder(variable_name="tools", optional=True)
            ])
        # Initialize LangChain Agent with the Tool
        agent = initialize_agent(
            tools=[rag_tool],
            llm=my_llm,
            prompt=prompt,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        #agent = create_react_agent(llm=my_llm, tools=[rag_tool], prompt=prompt)
        print("Summary Agent Generating Response : " + question)
        try:
            # 4. Run the Agent
            response = agent.invoke("Write summary of the document. document refers to the context")
            print("Answer:", response['output'])
            if len(response['output']) > 0:
                return response['output']
        except Exception  as e:
            print(e)
        return "Sorry! I couldn't find answer for your question at this time. Please try with detailed information."

class SentimentAgent():
    
    def interact(question):
       
        prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a knowledgeable assistant with access to the enterprise knowledge base.
            Your retrieval strategy:
            1. When a user asks a question, search the context for relevant information
            2. Document refers to the context
            3. Find out overall sentiment of the information available in the context
            4. Give two examples for positive sentiments from the context
            5. Give two examples for negative sentiments from the context
            6. Do not include any information from general knowledge base outside the context
            7. If the context does not have any sentiment, say Neutral."""),
                
                ("human", "{input}"),
               MessagesPlaceholder(variable_name="agent_scratchpad"),
               MessagesPlaceholder(variable_name="tool_names", optional=True),
               MessagesPlaceholder(variable_name="tools", optional=True)
            ])
        # Initialize LangChain Agent with the Tool
        agent = initialize_agent(
            tools=[rag_tool],
            llm=my_llm,
            prompt=prompt,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        #agent = create_react_agent(llm=my_llm, tools=[rag_tool], prompt=prompt)
        print("Sentiment Agent Generating Response : " + question)
        try:
            # 4. Run the Agent
            response = agent.invoke("Fetch sentiment from the document. document refers to the context")
            print("Answer:", response['output'])
            if len(response['output']) > 0:
                return response['output']
        except Exception  as e:
            print(e)
        return "Sorry! I couldn't find answer for your question at this time. Please try with detailed information."

import os
import json
from news_extractor import NewsExtractor
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer 

class MarketAnalyser:
    def __init__(self, groq_api_key: str = None, model_name: str = "llama3-8b-8192"):
        # Initialize the components required for processing
        self.news_extractor = NewsExtractor()
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.model_name = model_name
        self.llm = ChatGroq(groq_api_key=self.groq_api_key, model_name=self.model_name)
        self.embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    def fetch_news_data(self, query: str, limit: int = 20) -> list:
        """Fetch news articles based on the query."""
        news_data = self.news_extractor.get_news_data(query=query, limit=limit)
        news_articles = json.loads(news_data)
        return news_articles
    
    def prepare_documents(self, news_articles: list) -> list:
        """Convert news articles into a list of LangChain Document objects."""
        documents = [
            Document(
                page_content=f"Title: {article['title']}\nSnippet: {article['snippet']}\nSource: {article['source']}\nDate: {article['date']}"
            )
            for article in news_articles
        ]
        return documents
    
    def split_documents(self, documents: list) -> list:
        """Split documents into smaller chunks for efficient processing."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=0)
        doc_splits = splitter.split_documents(documents)
        return doc_splits
    
    def create_vector_store(self, doc_splits: list):
        """Create a vector store for document retrieval using HuggingFace embeddings."""
        vectorstore = Chroma.from_documents(doc_splits, self.embedding_model)
        return vectorstore
    
    def summarize_market_trends(self, doc_splits: list) -> str:
        """Summarize the market trends based on the provided document splits."""
        # Define the prompt for summarization
        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a market research assistant. Based on the following news snippets, provide a summary of market trends."),
            ("human", "{text}")
        ])
        
        # Combine document splits into a single input
        summary_input = "\n".join([doc.page_content for doc in doc_splits])
        
        # Create a chain using the prompt and the model
        chain = summary_prompt | self.llm
        
        # Invoke the chain to get the summarized response
        response = chain.invoke({"text": summary_input})
        return response.content

    def analyze_market(self, query: str, limit: int = 20) -> str:
        """Main method to fetch news, prepare documents, and summarize the market trends."""
        # Step 1: Fetch news data
        news_articles = self.fetch_news_data(query=query, limit=limit)
        
        # Step 2: Prepare documents from the fetched news articles
        documents = self.prepare_documents(news_articles)
        
        # Step 3: Split the documents into chunks for processing
        doc_splits = self.split_documents(documents)
        
        # Step 4: Summarize market trends based on the documents
        summary = self.summarize_market_trends(doc_splits)
        
        return summary

# Example usage:
if __name__ == "__main__":
    # Example of using the MarketAnalyser class
    analyser = MarketAnalyser()
    market_summary = analyser.analyze_market(query="AI market trends", limit=20)
    print("Market Research Summary:\n", market_summary)

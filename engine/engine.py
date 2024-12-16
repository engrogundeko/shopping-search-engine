import os
from getpass import getpass
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.vectorstores import FAISS
from langchain.retrievers import BM25Retriever, EnsembleRetriever

class QuerySearchEngine:
    def __init__(self, contents: List[str], speed: "fast" | "balanced" | "quality"):
        self.contents = contents
        self.speed = speed
        os.environ['HUGGINGFACEHUB_API_TOKEN'] = hf_token
        self.hf_model_name = hf_model_name
        self.hf_token = hf_token

        # Initialize components
        self.documents = self._load_documents()
        self.text_splits = self._chunk_documents()
        self.vectorstore = self._initialize_vectorstore()
        self.ensemble_retriever = self._initialize_ensemble_retriever()

    def _load_documents(self):
        documents = []
        for file in os.listdir(self.dataset_path):
            loader = TextLoader(os.path.join(self.dataset_path, file))
            documents.extend(loader.load())
        return documents

    def _chunk_documents(self):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
        return text_splitter.split_documents(self.documents)

    def _initialize_vectorstore(self):
        embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=self.hf_token, model_name=self.hf_model_name
        )
        return FAISS.from_documents(self.text_splits, embeddings)

    def rerank(self)  :
        ...

    def _initialize_ensemble_retriever(self):
        retriever_vectordb = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        keyword_retriever = BM25Retriever.from_documents(self.text_splits)
        keyword_retriever.k = 5
        return EnsembleRetriever(
            retrievers=[retriever_vectordb, keyword_retriever], weights=[0.5, 0.5]
        )

    def search_by_query(self, query):
        """Search for documents relevant to a specific query."""
        docs_rel = self.ensemble_retriever.get_relevant_documents(query)
        return docs_rel

    def search_by_keyword(self, keyword):
        """Search for documents containing a specific keyword."""
        keyword_matches = [doc for doc in self.text_splits if keyword.lower() in doc.page_content.lower()]
        return keyword_matches

# Example usage
if __name__ == "__main__":
    dataset_path = '/content/drive/MyDrive/Tech_news_dataset/dataset_news/'
    hf_model_name = 'BAAI/bge-base-en-v1.5'
    hf_token = getpass("Enter Hugging Face token: ")

    engine = QuerySearchEngine(dataset_path, hf_model_name, hf_token)

    query = "How many cafes were closed in 2004 in China?"
    relevant_docs = engine.search_by_query(query)
    print("Relevant documents for query:")
    for doc in relevant_docs:
        print(doc.page_content)

    keyword = "net cafes"
    keyword_docs = engine.search_by_keyword(keyword)
    print("\nDocuments containing keyword:")
    for doc in keyword_docs:
        print(doc.page_content)

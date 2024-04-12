from flask import Flask, request, jsonify
from pymongo import MongoClient
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.document_loaders import DirectoryLoader
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import AzureChatOpenAI
from flask_cors import CORS
from azure.storage.blob import BlobServiceClient
import key_param
import openai
import os
import datetime

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = key_param.OPENAI_API_KEY
OPENAI_API_BASE = key_param.OPENAI_API_BASE
OPENAI_API_VERSION = key_param.OPENAI_API_VERSION

PDF_PATH = r'C:\Users\Hp\Downloads\sample pdf.pdf'
CHUNK_SIZE = 500

client = MongoClient(key_param.MONGO_URI)
dbName = "PDFQuery"
pdfCollectionName = "PDFVectors"
conversationCollectionName = "Conversations"
pdfCollection = client[dbName][pdfCollectionName]
conversationCollection = client[dbName][conversationCollectionName]

class PDFDocument:
    def __init__(self, text, metadata=None):
        self.page_content = text
        self.metadata = metadata if metadata else {}

embeddings = OpenAIEmbeddings(openai_api_key=key_param.openai_api_key)

def query_data(query):
    docs = vectorStore.similarity_search(query, K=1)
    llm = AzureChatOpenAI(deployment_name="InternModel", openai_api_key=OPENAI_API_KEY,
                          openai_api_base=OPENAI_API_BASE, openai_api_version=OPENAI_API_VERSION)

    retriever = vectorStore.as_retriever()
    qa = RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=retriever)
    retriever_output = qa.run(query)
    return retriever_output

class CharacterTextSplitter:
    def __init__(self, chunk_size):
        self.chunk_size = chunk_size

    def split_text(self, text):
        chunks = [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]
        return chunks

pdf_text = ""
with open(PDF_PATH, 'rb') as file:
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

text_splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE)
chunked_texts = text_splitter.split_text(pdf_text)

pdf_documents = [PDFDocument(chunk) for chunk in chunked_texts]

vectorStore = MongoDBAtlasVectorSearch.from_documents(pdf_documents, embeddings, collection=pdfCollection)

# Azure Blob container connection details

storage_account_key = key_param.storage_account_key
storage_account_name = key_param.storage_account_name
connection_string = key_param.connection_string
container_name = key_param.container_name

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        if file:
            # Upload the file to Azure Blob Storage
            blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
            container_client = blob_service_client.get_container_client(container_name)
            blob_client = container_client.upload_blob(name=file.filename, data=file.stream)

            # Return the URL of the uploaded file
            return jsonify({'url': blob_client.url}), 200
        else:
            return jsonify({'error': 'No file provided in the request'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        message = data['message']
        response = query_data(message)
        return jsonify({'answer': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

    # # Set user_id to 1
    # user_identifier = 1

    # # Sample conversation_id and session_id
    # conversation_id = 123456
    # session_id = 67891

    # # Store chat message in the Conversations collection
    # chat_document = {
    #     "user_id": user_identifier,
    #     "timestamp": datetime.datetime.now(),
    #     "conversation_id": conversation_id,
    #     "session_id": session_id,
    #     "user_query": message,
    #     "chatbot_response": response,
    #     "success": True, 
    #     "execution_time": 0 
    # }
    # conversationCollection.insert_one(chat_document)


    # Return the response as before


@app.route('/store_chat_history', methods=['POST'])
def storeChatHistory():
    try:
        data = request.get_json()
        # message = data['message']
        # user_identifier=data['user_id']
        # conversation_id =data['conversation_id']
        # session_id=data['session_id']
    
    # Set user_id to 1
        user_identifier = 1

    # Sample conversation_id and session_id
        message="What is machine learning"
        conversation_id = 123456
        session_id = 67891
        response="machine learning"
        # response = query_data(message)

    # Store chat message in the Conversations collection
        chat_document = {
             "user_id": user_identifier,
             "timestamp": datetime.datetime.now(),
             "conversation_id": conversation_id,
             "session_id": session_id,
             "user_query": message,
             "chatbot_response": response,
             "success": True, 
             "execution_time": 0 
              }
        
        
        conversationCollection.insert_one(chat_document)
        print(f'Backend response',chat_document)
        return jsonify({'answer': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

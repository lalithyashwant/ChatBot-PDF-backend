PDF Query Chatbot

Overview

This is a Flask-based AI-powered chatbot that allows users to query PDF documents using Natural Language Processing (NLP) and vector search techniques. The application integrates with MongoDB Atlas Vector Search, OpenAI, and Azure Blob Storage to process documents and return relevant responses based on user queries.

Features:
Upload PDF files to Azure Blob Storage.

Extract and split text from PDFs for efficient retrieval.

Vectorize and store document chunks using MongoDB Atlas Vector Search.

Query PDFs using OpenAI's embeddings and LLM-based retrieval.

Store conversation history in MongoDB.

Tech Stack:
Backend: Flask, OpenAI, LangChain, PyPDF2

Database: MongoDB Atlas (Vector Search)

Cloud Services: Azure Blob Storage, Azure OpenAI

Libraries: LangChain, PyMongo, Flask-CORS


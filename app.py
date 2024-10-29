import streamlit as st
from dotenv import load_dotenv
import pickle
from streamlit_extras.add_vertical_space import add_vertical_space
import PyPDF2  # Make sure to install this package
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from langchain.llms import OpenAI  # Import OpenAI
from langchain.chains.question_answering import load_qa_chain
import os

# Load environment variables


# Set the title for the sidebar
with st.sidebar:
    st.title('PDF Chat App')   
    st.markdown('''
        ## About
        This app is an LLM-powered chatbot using:
        - [Streamlit](https://streamlit.io)
        - [LangChain](https://langchain.readthedocs.io)
        - [OpenAI](https://openai.com)
    ''')
    
    add_vertical_space(5)  # Adds vertical space for better layout
    st.write('Made by Shrey Sharma')

# Main content area
st.title("Welcome to the PDF Chat App!")
st.write("Upload your PDF document to start chatting.")

def main():
    pdf = st.file_uploader("Upload your PDF", type='pdf')
    load_dotenv()
    

    if pdf is not None:
        st.write(pdf.name)
        
        # Read the PDF file
        pdf_reader = PyPDF2.PdfReader(pdf)
        text = ""
        
        # Extract text from each page
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"  # Add new line for better formatting
        
        st.write(text)  # Display the extracted text
        
        # Split the extracted text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text=text)

        # Vector store name based on the PDF file name
        store_name = pdf.name[:-4]  # Remove the file extension

        # Check if the embeddings file exists
        if os.path.exists(f"{store_name}.pkl"):
            with open(f"{store_name}.pkl", "rb") as f:
                vector_store = pickle.load(f)
                st.write('Embedding loaded from the disk')
        else:
            # Create embeddings and vector store
            embeddings = OpenAIEmbeddings()
            vector_store = FAISS.from_texts(chunks, embedding=embeddings)

            # Save the embeddings to a pickle file
            with open(f"{store_name}.pkl", "wb") as f:
                pickle.dump(vector_store, f)

        # Accept user questions/query
        query = st.text_input("Ask questions about your PDF file:")

        if query:
            docs = vector_store.similarity_search(query=query, k=3)
            llm = OpenAI(temperature=0)  # Fixed parameter name
            chain = load_qa_chain(llm=llm, chain_type="stuff")
            
            # Get the answer from the QA chain
            answer = chain.run(input_documents=docs, question=query)
            
            # Display the answer
            st.write("Answer:")
            st.write(answer)

if __name__ == '__main__':
    main()

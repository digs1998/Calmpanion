import os
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings  # Corrected the embedding class
from utils.prompt_templates import PromptTemplates
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from utils.model_handler import ModelHandler

def setup_database():
    db_path = './chroma_db'

    # Define embedding function correctly
    embedding_function = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

    if not os.path.exists(db_path):
        # Load PDF documents
        loader = DirectoryLoader(
            "/Users/Lenovo/Desktop/Education/TranquiliChat/utils",
            glob="*.pdf",
            loader_cls=PyPDFLoader
        )
        docs = loader.load()

        # Split text into smaller chunks for better embedding retrieval
        txt_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        txts = txt_splitter.split_documents(docs)

        # Create Chroma database
        call_db = Chroma.from_documents(txts, embedding_function, persist_directory=db_path)
        call_db.persist()
    else:
        # Load existing database
        call_db = Chroma(persist_directory=db_path, embedding_function=embedding_function)

    return call_db


def setup_qachain(call_db, model_type=None):
    # Retrieve documents from the database
    retrieve = call_db.as_retriever(search_kwargs={"k": 3})
    
    # Load prompt template
    prompt_template = PromptTemplates.get_templates().get("Stress and Mental Wellbeing Support")
    PROMPT = PromptTemplate(template=prompt_template, input_variables=['context', 'question'])

    # Initialize the model (Llama or Mistral) based on the input argument
    if model_type == "Mistral":
        # Initialize Mistral AI (make sure `model_handler` is defined properly)
        model_handler = ModelHandler()
        llm = model_handler.initialize_mistral()
    elif model_type == "Llama":
        # Initialize Llama model (make sure `initialize_llama` is implemented)
        model_handler = ModelHandler()
        llm = model_handler.initialize_llama()  # You may need to modify the `initialize_llama` method if required
    else:
        raise ValueError("Invalid model_type specified. Choose either 'mistral' or 'llama'.")

    # Set up QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # You can modify this based on your use case
        retriever=retrieve,
        chain_type_kwargs={"prompt": PROMPT}
    )
    return qa_chain
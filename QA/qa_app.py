import streamlit as st
# from langchain.document_loaders import TextLoader
# from langchain.document_loaders import PyPDFLoader
# from langchain.chains import RetrievalQA
# from langchain.indexes import VectorstoreIndexCreator
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import Chroma
# from langchain.chat_models import ChatOpenAI
from llama_index import download_loader, GPTSimpleVectorIndex
import urllib.request
import urllib.parse
import os

os.environ['OPENAI_API_KEY'] = st.secrets['OPEN_AI_KEY'] 

# chat = ChatOpenAI(model_name='gpt-3.5-turbo')


try:
    os.mkdir('book')
    os.mkdir('index')
except:
    pass

url = "https://ia802800.us.archive.org/11/items/crossingthechasm_202002/Crossing%20the%20Chasm.pdf"

@st.cache
def get_book(url):
    # Parse the URL
    parsed_url = urllib.parse.urlparse(url)
    # Extract the path from the parsed URL
    path = parsed_url.path
    # Use os.path to get the file name from the path
    file_name = os.path.basename(path)
    # Unquote the file name to convert %20 to spaces and handle other special characters
    pdf = urllib.parse.unquote(file_name)
    urllib.request.urlretrieve(url, "book/"+pdf)
    return pdf


# # load document with LangChain
# @st.cache
# def load_doc(pdf):
#     loader = PyPDFLoader("book/"+pdf)
#     documents = loader.load()
#     # split the documents into chunks
#     text_splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=0)
#     texts = text_splitter.split_documents(documents)
#     # select which embeddings we want to use
#     embeddings = OpenAIEmbeddings()
#     # create the vectorestore to use as the index
#     db = Chroma.from_documents(texts, embeddings)
#     # expose this index in a retriever interface
#     retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":3})
#     # create a chain to answer questions 
#     qa = RetrievalQA.from_chain_type(
#     llm=chat, chain_type="stuff", retriever=retriever, return_source_documents=True)
#     return qa

# load document with LLaMa Index
@st.cache
def load_doc(pdf):
    PDFReader = download_loader("PDFReader")
    loader = PDFReader()
    documents = loader.load_data(pdf)
    index = GPTSimpleVectorIndex.from_documents(documents)
    return index

def load_index(file):
    # load from disk
    index = GPTSimpleVectorIndex.load_from_disk(file)
    return index


st.title("🤖 Question Answering on Book")
st.header("📖 Crossing the Chasm")

try:
    pdf = get_book(url)
except Exception as e:
    print(f"Error downloading PDF file: {e}")

# list = os.listdir('book')
# l = st.selectbox("Select Book",list)
# qa = load_doc(pdf)

file = 'index\index.json'
index = load_index(file)
# index = load_doc(pdf)

query = st.text_area('Query',"what is Vendor-Oriented Pricing?")
if st.button('Answer'):
    # res = qa({"query": query})
    res = index.query(query)
    st.write(res.response)
    st.write("### Sources:")
    st.write(res.get_formatted_sources().replace('>',''))
    # st.write(res['result'])
    # st.write(res['source_documents'].dict()['metadata']['source'])
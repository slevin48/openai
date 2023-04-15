import streamlit as st
from llama_index import download_loader, GPTSimpleVectorIndex, LLMPredictor, ServiceContext
from langchain.chat_models import ChatOpenAI
import urllib.request
import urllib.parse
import os

os.environ['OPENAI_API_KEY'] = st.secrets['OPEN_AI_KEY'] 
llm_predictor = LLMPredictor(llm=ChatOpenAI(model_name="gpt-3.5-turbo"))
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

try:
    os.mkdir('book')
    os.mkdir('index')
except:
    pass

url = "https://ia802800.us.archive.org/11/items/crossingthechasm_202002/Crossing%20the%20Chasm.pdf"

@st.cache_data
def get_book(url):
    # Parse the URL
    parsed_url = urllib.parse.urlparse(url)
    # Extract the path from the parsed URL
    path = parsed_url.path
    # Use os.path to get the file name from the path
    file_name = os.path.basename(path)
    # Unquote the file name to convert %20 to spaces and handle other special characters
    pdf = urllib.parse.unquote(file_name)
    urllib.request.urlretrieve(url, os.path.join('book',pdf))
    return pdf

# load document with LLaMa Index
def load_doc(pdf):
    PDFReader = download_loader("PDFReader")
    loader = PDFReader()
    documents = loader.load_data(pdf)
    index = GPTSimpleVectorIndex.from_documents(documents,service_context=service_context)
    return index

def load_index(file):
    # load from disk
    index = GPTSimpleVectorIndex.load_from_disk(file)
    return index


st.title("🤖 Question Answering on Book")
st.header("📖 Crossing the Chasm")

src = st.radio('Source',['full','chapter7'],index=1)
if src == 'full':
    try:
        pdf = get_book(url)
    except Exception as e:
        print(f"Error downloading PDF file: {e}")
    file = os.path.join('index','index-full.json')
elif src == 'chapter7':
    pdf = 'Crossing the Chasm-202-217.pdf'
    file = os.path.join('index','index-202-217.json')

# list = os.listdir('book')
# l = st.selectbox("Select Book",list)


if os.path.exists(file):
    index = load_index(file)
    print(f'Using existing index: {file}')
else:
    index = load_doc(os.path.join('book',pdf))
    # save index to file
    index.save_to_disk(file)
    print(f'Creating and saving index: {file}')

query = st.text_area('Query',"what is Vendor-Oriented Pricing?")
if st.button('Answer'):
    res = index.query(query)
    st.write(res.response)
    # st.write("### Sources:")
    with st.expander('Sources:'):
        # st.write(res.get_formatted_sources().replace('>',''))
        st.write(res.source_nodes[0].node.get_text())
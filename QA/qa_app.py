import streamlit as st
from llama_index import download_loader, GPTSimpleVectorIndex, LLMPredictor, ServiceContext
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import urllib.request
import urllib.parse
import os, boto3, json

s3_bucket = 'book48'
s3_client = boto3.client('s3',aws_access_key_id = st.secrets["aws"]["aws_access_key_id"],
                    aws_secret_access_key = st.secrets["aws"]["aws_secret_access_key"])

os.environ['OPENAI_API_KEY'] = st.secrets['OPEN_AI_KEY'] 
chat = ChatOpenAI(model_name="gpt-3.5-turbo")
llm_predictor = LLMPredictor(llm=chat)
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

try:
    os.mkdir('book')
    os.mkdir('index')
except:
    pass

url = "https://www.impromptubook.com/wp-content/uploads/2023/03/impromptu-rh.pdf"

def llm(prompt):
    res = chat([HumanMessage(content=prompt)])
    return res.dict()['content']

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
    index = GPTSimpleVectorIndex.load_from_disk(file,service_context=service_context)
    return index

def change_prompt(prompt):
    st.session_state.prompt = prompt


st.title("🤖 Question Answering on Book")
st.header("📖 Impromptu")

src = st.radio('Source',['full','chapter1'],index=1)
if src == 'full':
    try:
        pdf = get_book(url)
    except Exception as e:
        print(f"Error downloading PDF file: {e}")
    file = 'index/index-impromptu.json'
elif src == 'chapter1':
    pdf = 'impromptu-chap1.pdf'
    file = 'index/index-impromptu-chap1.json'
# s3_client.download_file(s3_bucket, object_name,file_name)
s3_client.download_file(s3_bucket,file, file)

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

if 'prompt' not in st.session_state:
    st.session_state.prompt = "what is the opinion of the author?"

query = st.text_area('Query',value=st.session_state.prompt)
if st.button('Answer'):
    res = index.query(query)
    st.write(res.response)
    # st.write("### Sources:")
    with st.expander('Sources:'):
        # st.write(res.get_formatted_sources().replace('>',''))
        st.write(res.source_nodes[0].node.get_text())
    st.write('Follow-up questions:')
    follow_up = f'''
    Provide a list of of 3 follow-up questions the initial query and the result associated. 
    Here is the initial query:
    {query}
    Here is the result associated:
    {res.response}
    Format the output as a JSON file with a list of the 3 follow-up questions in a field called follow-up
    '''
    q2 = llm(follow_up)
    jason = json.loads(q2)
    # st.write(jason)

    for element in jason['follow-up']:
        st.button(element, on_click=change_prompt, args=(element,))
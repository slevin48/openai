import streamlit as st
import pandas as pd
import os
from selenium import webdriver

def get_result(id):
    with open(f'problems/problem{id}/gpt-3.5-turbo/result.txt','r') as f:
        return f.read()

def get_status(result):
    if result == 'passed':
        return '✅' # :check_mark:
    elif result == 'failed':
        return '❌' # :cross_mark:

def remove_element(lst):
    removed_elements = []
    for element in lst:
        if element.endswith("Test.m"):
            lst.remove(element)
            removed_elements.append(element)
    # lst.remove('result.txt')
    return removed_elements

def get_file_extension(filename):
    _, extension = os.path.splitext(filename)
    return extension

def auth():
    driver = webdriver.Chrome()
    # Autenticate to Mathworks Account
    url = "https://www.mathworks.com/login"
    driver.get(url)
    return driver

st.sidebar.title('Cody 4 LLM')

# if st.sidebar.button('Login to Cody'):
#     driver = auth()
#     st.session_state.driver = driver

# p = [f'Problem {i+1} {get_status(get_result(i))}' for i in range(49)]
id = st.sidebar.radio('Problem', range(1,48), format_func=lambda i: f'Problem {i} {get_status(get_result(i))}')
# id = 1

st.header(f'Problem {id} {get_status(get_result(id))}')

st.subheader('Prompt')
with open(f'problems/problem{id}/prompt.txt','r') as f:
    prompt = f.read()
st.write(prompt)

# st.subheader('Template')
# with open(f'problems/problem{id}/template.txt','r') as f:
#     template = f.read()
#     template = template.split('\n1')[0]
# st.write(f'''```matlab
#          {template}
#          ''')


sol = os.listdir(f'problems/problem{id}/gpt-3.5-turbo')
sol.reverse()
r = remove_element(sol)
# st.write(sol)
# sel = st.selectbox('Select file',sol)
for s in sol:
    if s.endswith(".m"):
        st.subheader('Solution')
        with open(f'problems/problem{id}/gpt-3.5-turbo/{s}','r') as f:
            solution = f.read()
        st.write(f'''```matlab
            {solution}
            ''')
    if s.endswith(".csv"):
        st.subheader('Test Results')
        tests = pd.read_csv(f'problems/problem{id}/gpt-3.5-turbo/{s}')
        st.table(tests)

if st.checkbox('Show test cases'):
    st.subheader('Test Cases')
    with open(f'problems/problem{id}/gpt-3.5-turbo/{r[0]}','r') as f:
        test = f.read()
    st.write(f'''```matlab
        {test}
        ''')

if st.button('Open Cody Problem', type='primary'):
    if 'driver' not in st.session_state:
        driver = auth()
        st.session_state.driver = driver
        st.write('Authenticate and click again')
        
    else:
        url = f"https://www.mathworks.com/matlabcentral/cody/problems/{id}"
        driver = st.session_state['driver']
        driver.get(url)

# st.write(st.session_state)
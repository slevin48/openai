# %% Cody 4 LLM
import os, openai, tomli, matlab.engine, re, time
from selenium import webdriver
from selenium.webdriver.common.by import By

with open('secrets.toml','rb') as f:
    toml_dict = tomli.load(f)
openai.api_key = toml_dict['OPEN_AI_KEY']

eng = matlab.engine.start_matlab()

n = 58463 # number of problems

def extract_function_name(matlab_code):
    patterns = [
        r"function\s+\w+\s*=\s*(\w+)\(",
        r"function\s+\w+\s*=\s*(\w+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, matlab_code)
        if match:
            return match.group(1)  # Return the captured function name
        else:
            pattern = r"function\s+\[(\w+(\s+\w+)*)\]\s*=\s*(\w+)\("
            match = re.search(pattern, matlab_code)
            if match:
                return match.group(3)
    return None  # Return None if no match found
# %% Get Cody Problems with Selenium
driver = webdriver.Chrome()
# Autenticate to Mathworks Account ydebray@mathworks.com
url = "https://www.mathworks.com/login"
driver.get(url)

# %% Solve Cody Problems with GPT-3.5-turbo and test with MATLAB

# for id in range(50,n+1):
id = 1
try:
    os.mkdir(f'problems/problem{id}')
    os.mkdir(f'problems/problem{id}/gpt-3.5-turbo')
    print(f'Problem {id}')

    url = f"https://www.mathworks.com/matlabcentral/cody/problems/{id}/solutions/new"
    driver.get(url)
    time.sleep(10)

    css_selector = "[aria-labelledby='learnerProblemDescriptionAriaInfo']"
    prompt = driver.find_element(by=By.CSS_SELECTOR, value=css_selector).text
    with open(f'cody/problem{id}/prompt.txt','w') as f:
        f.write(prompt)

    css_selector2 = "[aria-labelledby='learnerSolutionEditorAriaInfo']"
    template = driver.find_element(by=By.CSS_SELECTOR, value=css_selector2).text
    with open(f'problems/problem{id}/template.txt','w') as f:
        f.write(template)

    function_name = extract_function_name(template)
    # print(function_name)
    if function_name is None:
        raise Exception("No function name found in the template")

    css_selector3 = "[aria-labelledby='learnerRunYourSolutionEditorAriaInfo']"
    scratchpad = driver.find_element(by=By.CSS_SELECTOR, value=css_selector3).text
    with open(f'problems/problem{id}/scratchpad.txt','w') as f:
        f.write(scratchpad)

    for e in driver.find_elements(by=By.CLASS_NAME,value="problem_test_parent"):
        e.click()

    css_selector4 = "[aria-labelledby='learnerSubmissionResultsAriaInfo']"
    testcases = driver.find_element(by=By.CSS_SELECTOR, value=css_selector4).text
    testsuite = [t.split('\n1')[0].replace('%%\n',f'%% test {i+1}\n') for i,t in enumerate(testcases.split('Test Code:\n')[1:])]
    # save the test suite in the directory
    with open(f'problems/problem{id}/gpt-3.5-turbo/{function_name}Test.m', 'w') as f:
        f.write('\n'.join(testsuite))

    # Solve with GPT-3.5-turbo
    messages = [
                {"role": "system", "content": "You are a helpful assistant that solves coding problems in MATLAB. reply only with the MATLAB code, without formatting or chit chat. Format the result as a function"}, 
                {"role": "user", "content": "This is the problem statement:\n"+prompt+"\n Integrate the result in the following function:\n"+template},
                ]


    res = openai.ChatCompletion.create(messages=messages, model="gpt-3.5-turbo")
    solution = res['choices'][0]['message']['content']
    # print(solution)
    print(f'Problem {id} solved')

    with open(f'problems/problem{id}/gpt-3.5-turbo/{function_name}.m','w') as f:
        f.write(solution)

    # Test code with MATLAB
    eng.cd(f'problems/problem{id}/gpt-3.5-turbo')
    # execute the test suite
    results = eng.runtests()
    rt = eng.table(results)
    eng.writetable(rt,function_name+".csv",nargout=0)
    eng.workspace['rt'] = rt
    eng.evalc("fileID = fopen('result.txt', 'w');if any(rt.Passed == false); fprintf(fileID, 'failed'); else; fprintf(fileID, 'passed'); end;fclose(fileID);")
    status = eng.evalc("if any(rt.Passed == false); disp('failed'); else; disp('passed'); end;")
    print(f'Problem {id} tested: {status}')
    eng.cd('../../..')
except:
    print(f'Problem {id} failed')
    pass

# %%
eng.exit()
driver.quit()


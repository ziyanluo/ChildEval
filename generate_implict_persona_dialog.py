import math
from copy import deepcopy
import json
import sys
import os
import json
import random
import requests
import time
import re


wf = open(sys.argv[1],'w',encoding="utf-8")
sys_prompts = open("./prompts/prompt_chinese_persona_dialog.txt").read() + "\n"

def parse_preference_and_question(input_string):
    pattern = r'<偏好>\s*(.*?)\s*</偏好>'  # \s* 匹配可能的空白字符
    match = re.search(pattern, input_string, re.DOTALL)
    if match:
        preference = match.group(1).strip()  # 去除前后空白字符
    else:
        preference= ''
    pattern = r'<主题>\s*(.*?)\s*</主题>'  # \s* 匹配可能的空白字符
    match = re.search(pattern, input_string, re.DOTALL)
    if match:
        subject = match.group(1).strip()  # 去除前后空白字符
    else:
        subject= ''
    pattern = r'<对话>\s*(.*?)\s*</对话>'  # \s* 匹配可能的空白字符
    match = re.search(pattern, input_string, re.DOTALL)
    if match:
        question = match.group(1).strip()  # 去除前后空白字符
    else:
        question= ''
    
    return preference,subject,question


def test_qwen_openai_api(obj, text):
    request_headers = {
        'content-type': 'application/json',
    }
    data = {
        # "model":"Qwen2.5-3B",
        "model":"Qwen2.5-72B-Instruct",
        "messages":[
            {"role":"system","content":"你是一个擅长模拟儿童与智能助理进行对话的系统。"},
            {"role": "user", "content": text},
        ],
        "temperature":0.8,
        "top_p":0.9,
        "max_tokens":10240,
    }
    url = "http://localhost:8000/v1/chat/completions"
    response=requests.post(url,json=data,headers=request_headers)
    if response.status_code == 200:
        try:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    data = json.loads(decoded_line)
                    result = data["choices"][0]["message"]["content"]
                    print(f"\nresult:{result}")
                    #print('********************************************')
                    obj['task_dialog'] = result
                    wf.write(json.dumps(obj,ensure_ascii=False)+ "\n")
                    wf.flush()
                    return result
                    
            return ""
        except:
            return ""
    else:
        print("请求失败，状态码:", response.status_code)
        print("响应:", response.text)
        return ""

i = 0
for line in sys.stdin:
    i = i+1
    objs = json.loads(line.strip())
    preference,topic,question= parse_preference_and_question(objs['task'])
    n  = random.randint(6, 10)
    objs['n-round'] = n
    persona = objs['en_child']
    prompt = sys_prompts.replace("{preference}",preference)
    prompt = prompt.replace("{persona}",persona)
    prompt = prompt.replace("{topic}",topic)
    prompt = prompt.replace("{n}",str(n))
    print(f"preference:{preference}")
    print(f"topic:{topic}")
    print(f"question:{question}")
    print(f"persona:{persona}")
    print(f"n:{n}")
    
    #print(prompt)
    result = test_qwen_openai_api(objs, prompt)
    time.sleep(1)


      
      

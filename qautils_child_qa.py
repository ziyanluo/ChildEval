import math
from copy import deepcopy
import json
import sys
import os
import json
import random
import requests
import time

wf = open(sys.argv[2],'w',encoding="utf-8")
inputfile  = sys.argv[1]
start = int(sys.argv[3])
sys_prompts = open("./prompts/prompt_chinese_persona_question.txt").read() + "\n"





def test_qwen_openai_api(obj, text):
    #app_code = "your code"
    request_headers = {
        'content-type': 'application/json',
        #'Authorization': 'Bearer ' + app_code
    }
    data = {
        "model":"Qwen2.5-72B-Instruct",
        "messages":[
            {"role":"system","content":"You are a persona assistant for children."},
            {"role": "user", "content": text},
        ],
        "temperature":0.9,
        "top_p":0.9,
        "max_tokens":1024,
        #"extra_body":{"repetition_penalty": 1.5,}
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
                    #print(f"result:{result}")
                    #print('********************************************')
                    if result.startswith('<task>'):
                      obj['qa'] = result

                      wf.write(json.dumps(obj,ensure_ascii=False)+ "\n")
                      wf.flush()
                      return result
                    
                    else:
                        return ''
                    
            return ""
        except:
            return ""
    else:
        print("请求失败，状态码:", response.status_code)
        print("响应:", response.text)
        return ""

num_samples = 15
samples = []
topics =['艺术启蒙-音乐','艺术启蒙-舞蹈','艺术启蒙-绘画手工','认知探索-科技','认知探索-科学','认知探索-自然',\
'认知探索-教育','运动饮食-户外','运动饮食-饮食',\
'语言发展-故事','语言发展-阅读','语言发展-语言',\
'社会情感-游戏','社会情感-互动']
i = 0
with open(inputfile, "r", encoding="utf-8") as f:
        for line in f:
          if i <= start:
               i = i +1
               continue

          objs = json.loads(line.strip())
          persona = "persona:"+objs['qa'].strip()
          prompt = sys_prompts.replace("{persona}",persona)
          topic = "topic:"+random.choice(topics)
          prompt = prompt.replace("{topic}",topic)
          obj ={}
          obj['en_child'] = objs['qa'].strip()
          obj['topic'] = random.choice(topics)
          print(f"en_child {obj['en_child']}")
          print('***************************')
          if  len(samples) < num_samples:
               num_samples = len(samples)
          if num_samples >0:
              samples_random=random.sample(samples,num_samples)
              topic_string = '\n'.join(samples_random)
              prompt  += topic_string
          #print(f"prompt:{prompt}")
          obj['prompt'] = prompt
          result = test_qwen_openai_api(obj, prompt)
          if result != '':
              samples.append(result)
          i = i +1
          if i % 300 == 0:
            print(f"index == {i}")
          time.sleep(1)

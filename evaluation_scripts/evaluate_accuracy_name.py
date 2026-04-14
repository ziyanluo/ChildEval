#encoding=utf8
import json
import os
import requests
import argparse
import time
import re

from tqdm import tqdm
from bs4 import BeautifulSoup


def parse_explanation_and_answer(input_string):
    # Create a BeautifulSoup object
    soup = BeautifulSoup(input_string, "html.parser")

    # Find the explanation tag and extract its content
    explanation_tag = soup.find("explanation")
    explanation = explanation_tag.text.strip() if explanation_tag else ""

    # Find the answer tag and extract its content
    answer_tag = soup.find("answer")
    answer = answer_tag.text.strip() if answer_tag else ""

    return explanation, answer

def parse_preference_and_answer(input_string):
    # Create a BeautifulSoup object
    soup = BeautifulSoup(input_string, "html.parser")

    # Find the preference tag and extract its content
    preference_tag = soup.find("preference")
    preference = preference_tag.text.strip() if preference_tag else ""

    # Find the answer tag and extract its content
    answer_tag = soup.find("answer")
    answer = answer_tag.text.strip() if answer_tag else ""

    return preference, answer

def parse_prompt(prompts):
    user_contents = re.findall(r'<\|im_start\|>user\n(.*?)<\|im_end\|>', prompts, re.DOTALL)
    if len(user_contents)  < 2:
          print(f"the format is error in {prompts}")
    user_prefernce = user_contents[0]
    question = user_contents[-1]
     
    '''
    for i, content in enumerate(user_contents, 1):
        print(f"User 内容 {i}: {content.strip()}")
    '''
    return user_prefernce,question
def test_qwen_openai_api( messages):
    #app_code = "eydddd***"
    request_headers = {
        'content-type': 'application/json',
        #'Authorization': 'Bearer ' + app_code
    }
    # {"role":"system","content":"You are a child persona assistant."},
    data = {
        "model":"Qwen2.5-72B-Instruct",
        "messages":messages,
        "temperature":0.8,
        "top_p":0.9,
        "max_tokens":1024,
        #"extra_body":{"repetition_penalty": 3,}
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
                    print(f"result:{result}")
                    print('********************************************')
                    return result
            return ""
        except:
            return ""
    else:
        print("请求失败，状态码:", response.status_code)
        print("响应:", response.text)
        return ""

def main():
    parser = argparse.ArgumentParser(description="eval")
    parser.add_argument("--model", type=str, default="jiutian")
    parser.add_argument("--turn", type=int, default=3)
    parser.add_argument("--loc", type=int, default=10)
    parser.add_argument("--line_nums", type=int, default=-1)
    parser.add_argument("--infile", type=str)
    parser.add_argument("--outfile", type=str)
    parser.add_argument("--task", type=str, default="zero-shot")
    #json key for assistant generations
    parser.add_argument("--key", type=str, default="generations")
    parser.add_argument("--pretrained", type=str, default="yes")
    parser.add_argument(
        "--method",
        type=str,
        default="single_pref_remind",
    )
    parser.add_argument("--debug", action="store_false")
    args = parser.parse_args()

    try:
        max_tokens = 100
        generation_file = args.infile #f"data_inner/chinese_child/gen/test_{args.turn}.json"
        #generation_file = f"test_test10_qwen_short.json"
        print(f"input_file:{generation_file}")
        save_file = args.outfile #f"inference_result_eval_model_qwen_ori{args.turn}_{args.task}_short.json"
        generation_data = []
        existing_eval_data =[]
        with open(generation_file, "r", encoding='utf-8') as f:
            for i, line in enumerate(f):
                #Continue from previous run in case of API failures during generation,defult generation from start
                if i < args.line_nums:
                    continue
                generation_data.append(json.loads(line.strip()))
      
        print(f"generation_data length: {len(generation_data)}")
        if os.path.isfile(save_file):
            print(f"{save_file} already exists, skipping generation...")
            return
        else:
            existing_eval_data = generation_data
        wf = open(save_file, "w", encoding='utf-8')
        for task_id, task in enumerate(tqdm(existing_eval_data)):
            if "evaluation_error_analysis" in task:
                analysis = task["evaluation_error_analysis"]
                if (
                    "acknow" in analysis
                    and "violate" in analysis
                    and "hallucinate" in analysis
                    and "helpful" in analysis
                    and "adaption" in analysis
                    and "interaction" in analysis
                    and "development" in analysis
                    and "engagement" in analysis
                ):
                    print("already task_id", task_id)
                    continue
            #preference, question = parse_prompt(task['prompt'])
            
            #preference = task['prompt']
            preference = task["preference"]
            question = task["question"]

            if args.key not in task:
                 print(f"no {args.key} in task")
                 continue
            if not isinstance(task[args.key], str):
                 print(f"{task[args.key]}")
                 continue
            
            end_generation = task[args.key]
            system_prompt = """You are a helpful assistant in evaluating an AI assistant's reponse. You should be fair and strict and follow the user's instruction"""
            BASE_DIR = f"./error_type"
            file_dict = {
                "acknow": "check_acknowledge.txt",
                "violate": "check_violation.txt",
                "hallucinate": "check_hallucination.txt",
                "helpful": "check_helpful.txt",
                "adaption": "check_emotionadaption.txt",
                "interaction": "check_interaction.txt",
                "development": "check_development.txt",
                "engagement": "check_engagement.txt"
            }

            eval_message_texts = []
            for metric_name, file_name in file_dict.items():
                file_path = os.path.join(BASE_DIR, file_name)
                with open(file_path, "r") as f:
                    eval_message_texts.append([metric_name, f.read()])
            if "evaluation_error_analysis" in task:
                error_check = task["evaluation_error_analysis"]
            else:
                error_check = {}
            for idx, (metric, eval_message_text) in enumerate(eval_message_texts):
                print('***************')
                print(f"metric: {metric}")
                print('***************')
                if metric in error_check:
                    continue
                if metric in["acknow","adaption","interaction","development","engagement"]:
                    eval_message_text = eval_message_text.replace("{end_generation}", end_generation)
                    eval_message_text = eval_message_text.replace("{question}", question)
                elif metric == "violate" or metric == "helpful":
                    eval_message_text = eval_message_text.replace("{preference}", preference)
                    eval_message_text = eval_message_text.replace("{question}", question)
                    eval_message_text = eval_message_text.replace("{end_generation}", end_generation)
                elif metric == "hallucinate":
                    if 'acknow' not in error_check:
                        continue
                    extracted_pref = error_check["acknow"]["extract_pref"]
                    eval_message_text = eval_message_text.replace("{preference}", preference)
                    eval_message_text = eval_message_text.replace("{assistant_restatement}", extracted_pref)
                eval_message = [{"role": "system", "content": system_prompt},{"role": "user", "content": eval_message_text}]
                print('eval_message *****************************************')
                print(f"question: {question}  \nresult:{end_generation}")
                print('*******************************************************')
                eval_response = test_qwen_openai_api(eval_message)
                #print(f'eval response:{eval_message}')
                time.sleep(1)
                #eval_response = generate_message(client, model_id, system_prompt, eval_message, max_tokens)["content"][
                #    0
                #]["text"]
                
                error_check[metric] = {}
                if metric != "acknow":
                    explanation, answer = parse_explanation_and_answer(eval_response)
                    error_check[metric]["explanation"] = explanation
                    error_check[metric]["answer"] = answer
                else:
                    extract_preference, answer = parse_preference_and_answer(eval_response)
                    error_check[metric]["answer"] = answer
                    error_check[metric]["extract_pref"] = extract_preference
                print(error_check)
            
            task["evaluation_error_analysis"] = error_check
            existing_eval_data[task_id] = task
            task['index'] = task_id
            wf.write(json.dumps(task,ensure_ascii=False)+ "\n")
            wf.flush()
            
        print("done!", args.model, save_file)
    except Exception as e:
        print(e)



if __name__ == "__main__":
    main()

import streamlit as st
import openai
import re
import os
import requests
import json
from PIL import Image
from io import BytesIO
import time
import gpt_prompt

openai.api_key = os.getenv('OPENAI_API_KEY')
mj_api_key = os.getenv('MJ_API_KEY')

@st.cache_data
def imagine(prompt):
    headers = {
    'Authorization': f'Bearer {mj_api_key}',
    'Content-Type': 'application/json'
    }

    url = "https://api.thenextleg.io/v2/imagine"

    payload_image = json.dumps({
    "msg": prompt,
    "ref": "",
    "webhookOverride": "", 
    "ignorePrefilter": "false"
    })

    def check_task_status(url):  # 这里添加 url 参数
        while True:
            response_result = requests.request("GET", url, headers=headers)
            if response_result.status_code == 200:
                json_response = json.loads(response_result.text)
                progress = json_response['progress']
                if progress == 100:
                    return json_response["response"]['imageUrl']
            else:
                st.write(f"Request failed, status code: {response_result.status_code}")
            time.sleep(3)

    attempts = 0
    max_attempts = 3
    while attempts <= max_attempts:
        time.sleep(3)
        messageId = None
        response_image = requests.request("POST", url, headers=headers, data=payload_image)
        if response_image.status_code == 200:
            messageId = response_image.json().get('messageId')

        url_with_id = f"https://api.thenextleg.io/v2/message/{messageId}?expireMins=2"
        
        if messageId:
            img_url = check_task_status(url_with_id)
            if img_url is not None and img_url != '':
                return img_url
            else:
                attempts += 1
    raise ValueError("Unable to get valid image URL after multiple attempts")

def main():

    if 'all_prompt_lists' not in st.session_state:
        st.session_state['all_prompt_lists'] = [None] * 1000
    
    if 'all_selected_lists' not in st.session_state:
        st.session_state['all_selected_lists'] = [None] * 1000

    if 'init_prompt' not in st.session_state:
        st.session_state['init_prompt'] = ""

    if 'count' not in st.session_state:
        st.session_state['count'] = 1

    if 'choices' not in st.session_state:
        st.session_state['choices'] = [None] * 1000

    if 'img_cache' not in st.session_state:
        st.session_state['img_cache'] = {}
    
    if 'keyword_mat' not in st.session_state:
        st.session_state['keyword_mat'] = None

    st.title("Genjourney:dna:")

    option = st.radio('**Choose a Midjourney mode:**', ('Midjourney Model V5.2', 'Niji Model V5'))

    st.session_state['init_prompt'] = st.text_input("**Enter your initial prompt**")
    if st.button("**Generate prompts & images**", key="init_list_button"):
        prompt_mat, keyword_mat = gpt_prompt.generate(st.session_state['init_prompt'], 5)
        st.session_state['keyword_mat'] = keyword_mat
        st.session_state['all_prompt_lists'][0] = prompt_mat

    if st.session_state['all_prompt_lists'][0] is not None:
        st.write("**Initial generated prompts:**")
        for i in range(5):
            prompt = gpt_prompt.list2str(st.session_state['all_prompt_lists'][0][i], option)
            st.write(i + 1, prompt)

            img = st.session_state['img_cache'].get(prompt)
            if img is None:
                img = imagine(prompt)
                st.session_state['img_cache'][prompt] = img
            st.write(img)
            st.image(img)

        for i in range(st.session_state['count']):
            container = st.container()
            prompt_mat = st.session_state['all_prompt_lists'][i]
            selected_nums = container.multiselect(f"**Select two prompts as parent prompts**", range(1, 6), key=f"multi_select_{i}")
            rate_list = []
            if len(selected_nums) == 2:
                selected_prompts = [prompt_mat[selected_nums[0] - 1], prompt_mat[selected_nums[1] - 1]]

                subject_rate = st.slider('rate the subject', min_value=0, max_value=10, key=f"slider_subject_{i}")
                style_rate = st.slider('rate the style', min_value=0, max_value=10, key=f"slider_style_{i}")
                color_rate = st.slider('rate the color', min_value=0, max_value=10, key=f"slider_color_{i}")
                angle_rate = st.slider('rate the angle', min_value=0, max_value=10, key=f"slider_angle_{i}")
                light_rate = st.slider('rate the light', min_value=0, max_value=10, key=f"slider_light_{i}")
                renderer_rate = st.slider('rate the renderer', min_value=0, max_value=10, key=f"slider_renderer_{i}")
                rate_list = [subject_rate, style_rate, color_rate, angle_rate, light_rate, renderer_rate]

            if len(selected_nums) == 2 and st.button(f"**Generate child prompts & images**", key=f"button_{i}"):
                st.session_state['choices'][i] = selected_prompts
                child_prompts = gpt_prompt.genetic(selected_prompts[0], selected_prompts[1], rate_list=rate_list, keyword_mat=st.session_state['keyword_mat'])
                st.session_state['all_prompt_lists'][i+1] = child_prompts
                st.session_state['all_selected_lists'][i] = selected_prompts
                if i + 1 == st.session_state['count']:
                    st.session_state['count'] += 1
                    st.experimental_rerun()
            
            if st.session_state['choices'][i] is not None:
                st.write(f"**Your selcetion from Generation {i}:**")
                for j in range(2):
                    st.write(j + 1, gpt_prompt.list2str(st.session_state['all_selected_lists'][i][j], option))
                st.write("\n")
                st.write(f"**Generation {i + 1}:**")
                for j in range(5):
                    prompt = gpt_prompt.list2str(st.session_state['all_prompt_lists'][i + 1][j], option)
                    st.write(j + 1, prompt)

                    img = st.session_state['img_cache'].get(prompt)
                    if img is None:
                        img = imagine(prompt)
                        st.session_state['img_cache'][prompt] = img
                    st.write(img)
                    st.image(img)
                    
    if st.button(':violet[**Try another initial prompt**]:leftwards_arrow_with_hook:', key="refresh"):
        st.session_state['all_prompt_lists'] = [None] * 1000
        st.session_state['all_selected_lists'] = [None] * 1000
        st.session_state['init_prompt'] = ""
        st.session_state['count'] = 1
        st.session_state['choices'] = [None] * 1000
        st.session_state['img_cache'] = {}
        st.session_state['keyword_mat'] = None
        st.experimental_rerun()

if __name__ == '__main__':
    main()
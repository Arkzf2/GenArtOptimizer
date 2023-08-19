import streamlit as st
import openai
import os
import requests
import json
from PIL import Image
from io import BytesIO
import time
import numpy as np
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

    def check_task_status(url):
        while True:
            response_result = requests.request("GET", url, headers=headers)
            if response_result.status_code == 200:
                json_response = json.loads(response_result.text)
                progress = json_response['progress']
                if progress == 100:
                    return json_response["response"]['imageUrl'], json_response["response"]['imageUrls']
            else:
                st.write(f"Request failed, status code: {response_result.status_code}")
            time.sleep(3)

    attempts = 0
    max_attempts = 3
    while attempts <= max_attempts:
        time.sleep(1)
        messageId = None
        response_image = requests.request("POST", url, headers=headers, data=payload_image)
        if response_image.status_code == 200:
            messageId = response_image.json().get('messageId')

        url_with_id = f"https://api.thenextleg.io/v2/message/{messageId}?expireMins=2"
        
        if messageId:
            img_url, img_urls = check_task_status(url_with_id)
            if img_url is not None and img_url != '':
                return img_url, img_urls
            else:
                attempts += 1
    raise ValueError("Unable to get valid image URL after multiple attempts")

# get session state
if 'init_prompt' not in st.session_state:
    st.session_state.init_prompt = ''
if 'prompts' not in st.session_state:
    st.session_state.prompts = []
if 'prompt_history' not in st.session_state:
    st.session_state.prompt_history = []
if 'images' not in st.session_state:
    st.session_state.images = []
if 'single_images' not in st.session_state:
    st.session_state.single_images = []
if 'blender_images' not in st.session_state:
    st.session_state.blender_images = []
if 'blender_urls' not in st.session_state: 
    st.session_state.blender_urls = []
if 'image_history' not in st.session_state:
    st.session_state.image_history = []
if 'single_image_history' not in st.session_state:
    st.session_state.single_image_history = []
if 'selection_history' not in st.session_state:
    st.session_state.selection_history = []
if 'selected_images' not in st.session_state:
    st.session_state.selected_images = []
if 'scores' not in st.session_state:
    st.session_state.scores = []
if 'round_count' not in st.session_state:
    st.session_state.round_count = 0
if 'keyword_mat' not in st.session_state:
    st.session_state.keyword_mat = None

st.title("Genjourney:dna:")

# choose the mj mode
option = st.radio('**Choose a Midjourney mode:**', ('Midjourney Model V5.2', 'Niji Model V5'))
mutate_rate = st.radio('**Set the mutate rate:**', ('Low', 'Medium', 'High'))

# input init prompt and generate prompts of generation 0
st.session_state.init_prompt = st.text_input("**Enter your initial prompt**", value=st.session_state.init_prompt)

if st.button("**Generate prompts & images**"):

    prompt_mat, keyword_mat = gpt_prompt.generate(st.session_state['init_prompt'], 5)
    st.session_state.keyword_mat = keyword_mat
    st.session_state.prompts = prompt_mat

if np.size(st.session_state.prompts) > 0:
    # show the lastest images
    st.markdown("# Current Images")

    image_list = []
    single_image_list = []

    

    for i in range(len(st.session_state.prompts)):
        prompt = gpt_prompt.list2str(st.session_state.prompts[i], option)

        if len(st.session_state.blender_urls) > 0:
            for url in st.session_state.blender_urls:
                prompt = ' ' + url + ' ' + prompt

        st.write(i+1)
        img, single_imgs = imagine(prompt)
        st.image(img, caption=prompt)
        for j in range(4):
            st.write(f"U{j+1}: {single_imgs[j]}")
        image_list.append(img)
        single_image_list.append(single_imgs)

    st.session_state.images = image_list
    st.session_state.single_images = single_image_list

    # # multi-thread
    # def get_image(prompt):
    #     img = imagine(prompt)
    #     return img, prompt

    # # results = []
    # # with ThreadPoolExecutor(max_workers=5) as executor:
    # #     futures = [executor.submit(get_image, gpt_prompt.list2str(prompt, option)) for prompt in st.session_state.prompts]
    # #     progress_bar = st.progress(0)
    # #     for i, future in enumerate(as_completed(futures)):
    # #         results.append(future.result())
    # #         progress_bar.progress((i+1) / len(futures))

    # # for i, (img, prompt) in enumerate(results, start=1):
    # #     st.image(img, caption=f"{i}. {prompt}")

    # with ThreadPoolExecutor(max_workers=5) as executor:
    #     futures = [executor.submit(get_image, gpt_prompt.list2str(prompt, option)) for prompt in st.session_state.prompts]
    #     progress_bar = st.progress(0)
    #     results = []
    #     for i, future in enumerate(as_completed(futures)):
    #         img, prompt = future.result()
    #         results.append((img, prompt))
    #         progress_bar.progress((i + 1) / len(futures))
    #     progress_bar.progress(1.0)

    # image_list = []
    # for i, (img, prompt) in enumerate(results, start=1):
    #     st.write(f"{i}. {prompt}")
    #     st.image(img, caption=prompt)
    #     image_list.append(img)

    # st.session_state.images = image_list

    with st.form(key='my_form'):

        # let user to choose images to blend
        # option_mapping = {'1️⃣ U1': [0,0], '1️⃣ U2': [0,1], '1️⃣ U3': [0,2], '1️⃣ U4': [0,3],
        #               '2️⃣ U1': [1,0], '2️⃣ U2': [1,1], '2️⃣ U3': [1,2], '2️⃣ U4': [1,3],
        #               '3️⃣ U1': [2,0], '3️⃣ U2': [2,1], '3️⃣ U3': [2,2], '3️⃣ U4': [2,3],
        #               '4️⃣ U1': [3,0], '4️⃣ U2': [3,1], '4️⃣ U3': [3,2], '4️⃣ U4': [3,3],
        #               '5️⃣ U1': [4,0], '5️⃣ U2': [4,1], '5️⃣ U3': [4,2], '5️⃣ U4': [4,3]}

        # blend = st.multiselect('Pick the image(s) if you want to blend it(them) into next generation',
        #         ['1️⃣ U1', '1️⃣ U2', '1️⃣ U3', '1️⃣ U4',
        #         '2️⃣ U1', '2️⃣ U2', '2️⃣ U3', '2️⃣ U4',
        #         '3️⃣ U1', '3️⃣ U2', '3️⃣ U3', '3️⃣ U4',
        #         '4️⃣ U1', '4️⃣ U2', '4️⃣ U3', '4️⃣ U4',
        #         '5️⃣ U1', '5️⃣ U2', '5️⃣ U3', '5️⃣ U4'],
        #         key=f"multiselect_{i}_st.session_state.round_count")

        # blender_urls = []
        # for option in blend:
        #     i = option_mapping[option][0]
        #     j = option_mapping[option][1]
        #     url = st.session_state.single_images[i][j]
        #     blender_urls.append(url)
        
        # st.session_state.blender_images = blender_urls

        st.session_state.blender_images = st.multiselect('Pick the image(s) if you want to blend it(them) into next generation',
            ['1️⃣ U1', '1️⃣ U2', '1️⃣ U3', '1️⃣ U4',
            '2️⃣ U1', '2️⃣ U2', '2️⃣ U3', '2️⃣ U4',
            '3️⃣ U1', '3️⃣ U2', '3️⃣ U3', '3️⃣ U4',
            '4️⃣ U1', '4️⃣ U2', '4️⃣ U3', '4️⃣ U4',
            '5️⃣ U1', '5️⃣ U2', '5️⃣ U3', '5️⃣ U4'],
            key=f"multiselect_{i}_st.session_state.round_count")

        if len(st.session_state.blender_images) > 3:
            st.warning('Please select no more than three images to blend')
        elif len(st.session_state.blender_images) >= 0:
            # let user to choose two prompts as parent prompts
            st.session_state.selected_images = st.multiselect('Select two prompts as parent prompts', range(1, 6), key=f"select_{st.session_state.round_count}")
            # let user to rate the art styles
            if st.session_state.selected_images:
                if len(st.session_state.selected_images) != 2:
                    st.warning('Please select exactly two images and set scores for them.')
                else:
                    subject_rate = st.slider('rate the subject', min_value=0, max_value=10, value=5, key=f"slider_subject_{st.session_state.round_count}_{i}")
                    style_rate = st.slider('rate the style', min_value=0, max_value=10, value=5, key=f"slider_style_{st.session_state.round_count}_{i}")
                    color_rate = st.slider('rate the color', min_value=0, max_value=10, value=5, key=f"slider_color_{st.session_state.round_count}_{i}")
                    angle_rate = st.slider('rate the angle', min_value=0, max_value=10, value=5, key=f"slider_angle_{st.session_state.round_count}_{i}")
                    light_rate = st.slider('rate the light', min_value=0, max_value=10, value=5, key=f"slider_light_{st.session_state.round_count}_{i}")

                    st.session_state.scores = [subject_rate, style_rate, color_rate, angle_rate, light_rate]
        
        # submit button
        submit_button = st.form_submit_button(label='Submit for Next Generation')

    if submit_button:
        if len(st.session_state.selected_images) != 2:
            st.warning('Please select exactly two images and set scores for them.')
        else:
            # store history
            st.session_state.prompt_history.append(st.session_state.prompts)
            st.session_state.image_history.append(st.session_state.images)
            st.session_state.single_image_history.append(st.session_state.single_images)
            st.session_state.selection_history.append(st.session_state.selected_images)

            # generate prompts of next generation
            prompt_A = st.session_state.prompts[st.session_state.selected_images[0]-1]
            prompt_B = st.session_state.prompts[st.session_state.selected_images[1]-1]
            st.session_state.prompts = gpt_prompt.genetic(prompt_A, prompt_B, st.session_state.scores, st.session_state.keyword_mat, mutate_rate)
            
            option_mapping = {'1️⃣ U1': [0,0], '1️⃣ U2': [0,1], '1️⃣ U3': [0,2], '1️⃣ U4': [0,3],
                              '2️⃣ U1': [1,0], '2️⃣ U2': [1,1], '2️⃣ U3': [1,2], '2️⃣ U4': [1,3],
                              '3️⃣ U1': [2,0], '3️⃣ U2': [2,1], '3️⃣ U3': [2,2], '3️⃣ U4': [2,3],
                              '4️⃣ U1': [3,0], '4️⃣ U2': [3,1], '4️⃣ U3': [3,2], '4️⃣ U4': [3,3],
                              '5️⃣ U1': [4,0], '5️⃣ U2': [4,1], '5️⃣ U3': [4,2], '5️⃣ U4': [4,3]}
    
            blender_urls = []
            for option in st.session_state.blender_images:
                i = option_mapping[option][0]
                j = option_mapping[option][1]
                url = st.session_state.single_images[i][j]
                blender_urls.append(url)
            st.session_state.blender_urls = blender_urls

            # increase round count
            st.session_state.round_count += 1

            # clear selection and scores
            st.session_state.blender_images = []
            st.session_state.selected_images = []
            st.session_state.scores = []

    # show history and selection on sidebar
    if st.session_state.image_history:
        st.sidebar.markdown("# History")
        for i, (past_images, selected) in enumerate(zip(st.session_state.image_history, st.session_state.selection_history)):
            st.sidebar.markdown(f"## Generation {i}")
            for idx, img in enumerate(past_images):
                prompt = gpt_prompt.list2str(st.session_state.prompt_history[i][idx], option)
                caption = prompt + (f" - Selected" if (idx+1) in selected else "")
                st.sidebar.image(img, caption=caption)
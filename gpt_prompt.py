import openai
import os
import re
import numpy as np
import time
import requests
import json

openai.api_key = os.getenv('OPENAI_API_KEY')

def get_completion(prompt, model='gpt-3.5-turbo'):
    messages = [{'role': 'user', 'content': prompt}]
    
    max_retries = 5
    retry_delay = 10

    for i in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=1.0,
            )
            return response['choices'][0]['message']['content']

        except Exception as e:

            if i < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                print(f"Failed after {max_retries} attempts. Please try again later.")
                break

def text2list(text):
    l = re.split('\d+\.', text.strip())
    l = [prompt.strip() for prompt in l if prompt]
    return l

def subject(init_prompt, n=30):

    prompt = f"""

    Now you should act as a image prompt advisor for an AI art image generator Midjourney.
    Midjourney can generate art images given the text prompt.
    "prompt" refers to a short text phrase used to generate images. The Midjourney Bot breaks down the words and phrases in the prompt into smaller units called tokens. These tokens can be compared with its training data and then used to generate an image. This means that, no matter what the sentence structure is, Midjourney will first decompose long sentences and then generate the final image through a "black box algorithm" for multiple tokens. Therefore, the significance of word order becomes less important.
    Midjourney does not understand grammar, sentence structure, or words like humans do. In many cases, more specific synonyms are more effective. For example, you can replace "big" with words like "huge" or "massive". Reduce the use of words where possible. Using fewer words means that the impact of each word is more powerful. Use commas, parentheses, and conjunctions to help organize your thoughts, but be aware that Midjourney does not reliably interpret them. Midjourney Bot does not distinguish between upper and lower case.

    Based on the intial prompt I provide: {init_prompt}, you need to generate 5 descriptive expansion keyword phrases to add details and the phrases should be seperated by comma.
    Expansion phrases should be developed based on the theme content, that is to frame the content of the art image or what is the people/animal/object doing or the surrounding environment (A clear description will make the image generation effect better).

    The length of all tokens should be no more than 20.

    Try not to use prepositional phrases because Midjourney Bot does not understand them very well.

    The final prompt should follow the following structure:
    <init_prompt>, <keyword1>, <keyword2>, <keyword3>, <keyword4>, <keyword5>

    Generate {n} different prompts and list your prompts as follows:
    1. <prompt1>
    2. <prompt2>
    ...
    {n}. <prompt{n}>

    """

    lst = []
    while len(lst) != 30:
        response = get_completion(prompt)
        lst = text2list(response)

    return lst

def modifier_generator(init_prompt, modifier, examples, n=30):

    prompt = f"""

    Examples of {modifier} keyword can be such as: {examples}, etc.

    Refer to the given examples, you need to generate {n} {modifier} keywords for the theme of: {init_prompt}.

    If {modifier} keyword is mationed in the initial prompt: {init_prompt}, then your generation should be very similar to the mentioned {modifier}.

    Ensure your result is not limitted by the given examples.

    Following the rules above, list only the generated keywords as follows:
    1. <{modifier}1>
    2. <{modifier}2>
    ...
    {n}. <{modifier}{n}>

    """

    lst = []
    while len(lst) != 30:
        response = get_completion(prompt)
        lst = text2list(response)

    return lst

def visual_art_style(init_prompt):

    modifier = "visual art style"

    examples = "cyberpunk, futuristic, Rococo, ink painting, 1900s anime, Pixar, surrealism, Chinese painting, Renaissance style, minimalist style, graffiti style, gothic style, Fauvism, 3d, cinematic, photorealistic, industrial, architectural sketching"

    lst = modifier_generator(init_prompt, modifier, examples)

    return lst

def artist_style(init_prompt):

    modifier = "artist"

    examples = "Junji Ito, H.R. Ford, Jhon Berkey, Studio Ghibli, Alphonso Mucha, Yoneyama Mai, Krenz Cushart, Sandra Chevrier, Van Gogh, Guanzhong Wu, Baishi Qi, Sam Toft, WLOP"

    lst = modifier_generator(init_prompt, modifier, examples)

    return lst

def color_style(init_prompt):

    modifier = "color"

    examples = "Macarons, Muted tones, black and white, laser candy paper color, maple red, neon shades, ivory white, red and black tones, rose gold, crystal blue"

    lst = modifier_generator(init_prompt, modifier, examples)

    return lst

def perspective_style(init_prompt):

    modifier = "composition perspective"

    examples = "close-up, panoramic view, simulated cemera, faceshot, full body, perspective, datail shot, side perspective, three views, product view, top-down perspective, fisheyelens, macrolens"

    lst = modifier_generator(init_prompt, modifier, examples)

    return lst

def light_style(init_prompt):

    modifier = "lighting effect"

    examples = "cinematic light, intense backlight, soft lighting, soft moon light, studio lighting, crepuscular ray, volumetric lighting, front lighting, hard lighting, rainbow halo, glow in the dark, rim lighting"

    lst = modifier_generator(init_prompt, modifier, examples)

    return lst

def rendering_style(init_prompt):

    modifier = "rendering quality"

    examples = "subpixel sampling, Arnold renderer, V-ray renderer, C4D renderer, Unreal Engine, Blender renderer, 4k, 3DCG, Octane renderer, architectural visualisation, DOF"

    lst = modifier_generator(init_prompt, modifier, examples)

    return lst

def list2str(prompt_l, midorniji=''):

    prompt = ''
    for i in range(7):
        prompt += f'{prompt_l[i]}, '
    prompt = prompt.rstrip()
    if prompt[-1] == ',':
        prompt = prompt[:-1]
    if midorniji == 'Midjourney Model V5.2':
        prompt += ' --v 5.2'
    if midorniji == 'Niji Model V5':
        prompt += ' --niji 5'
    
    return prompt

def generate(init_prompt, n=5):
    
    subject_list = subject(init_prompt)
    visual_art_style_list = visual_art_style(init_prompt)
    artist_style_list = artist_style(init_prompt)
    color_style_list = color_style(init_prompt)
    perspective_style_list = perspective_style(init_prompt)
    light_style_list = light_style(init_prompt)
    rendering_style_list = rendering_style(init_prompt)

    keyword_mat = np.array([subject_list, visual_art_style_list, artist_style_list, color_style_list, perspective_style_list, light_style_list, rendering_style_list])

    prompt_mat = np.empty((n, 7), dtype='<U200')

    for i in range(n):
        for j in range(7):
            id = np.random.randint(0, 20)
            prompt_mat[i, j] = keyword_mat[j, id]

    return prompt_mat, keyword_mat

def mutate(prompt, keyword, mat):

    index = prompt.index(keyword)

    new_keyword = keyword
    while new_keyword == keyword:
        id = np.random.randint(0, 20)
        new_keyword = mat[index, id]
    prompt[index] = new_keyword

    return prompt

def cross(prompt_A, prompt_B):
    
    prompt_child = []
    for i in range(len(prompt_A)):
        index = np.random.randint(0, 2)
        if index == 0:
            keyword = prompt_A[i]
        else:
            keyword = prompt_B[i]
        prompt_child.append(keyword)
    
    return prompt_child

def genetic(prompt_A, prompt_B, rate_list, keyword_mat, mutate_rate):
    m = 0.2
    if mutate_rate == 'high':
        m = 0.1
    elif mutate_rate == 'medium':
        m = 0.15
    elif mutate_rate == 'low':
        m = 0.3

    prompt_list = []

    subject_rate = np.exp(-m * rate_list[0])
    style_rate = np.exp(-m * rate_list[1])
    color_rate = np.exp(-m * rate_list[2])
    angle_rate = np.exp(-m * rate_list[3])
    light_rate = np.exp(-m * rate_list[4])

    for i in range(5):
        
        prompt_child = cross(prompt_A, prompt_B)

        subject_mutate = np.random.choice(np.array([0, 1]), p=np.array([subject_rate, 1-subject_rate]))
        style_mutate = np.random.choice(np.array([0, 1]), p=np.array([style_rate, 1-style_rate]))
        color_mutate = np.random.choice(np.array([0, 1]), p=np.array([color_rate, 1-color_rate]))
        angle_mutate = np.random.choice(np.array([0, 1]), p=np.array([angle_rate, 1-angle_rate]))
        light_mutate = np.random.choice(np.array([0, 1]), p=np.array([light_rate, 1-light_rate]))

        mutate_list = [subject_mutate, style_mutate, color_mutate, angle_mutate, light_mutate]

        if mutate_list[0] == 1:
            prompt_child = mutate(prompt_child, prompt_child[0], keyword_mat)
        if mutate_list[1] == 1:
            num = np.random.randint(0, 6)
            if num == 0:
                prompt_child = mutate(prompt_child, prompt_child[1], keyword_mat)
            elif num == 1:
                prompt_child = mutate(prompt_child, prompt_child[2], keyword_mat)
            elif num == 2:
                prompt_child = mutate(prompt_child, prompt_child[6], keyword_mat)
            elif num == 3:
                prompt_child = mutate(prompt_child, prompt_child[1], keyword_mat)
                prompt_child = mutate(prompt_child, prompt_child[2], keyword_mat)
            elif num == 3:
                prompt_child = mutate(prompt_child, prompt_child[1], keyword_mat)
                prompt_child = mutate(prompt_child, prompt_child[6], keyword_mat)
            elif num == 4:
                prompt_child = mutate(prompt_child, prompt_child[2], keyword_mat)
                prompt_child = mutate(prompt_child, prompt_child[6], keyword_mat)
            else:
                prompt_child = mutate(prompt_child, prompt_child[1], keyword_mat)
                prompt_child = mutate(prompt_child, prompt_child[2], keyword_mat)
                prompt_child = mutate(prompt_child, prompt_child[6], keyword_mat)
        if mutate_list[2] == 1:
            prompt_child = mutate(prompt_child, prompt_child[3], keyword_mat)
        if mutate_list[3] == 1:
            prompt_child = mutate(prompt_child, prompt_child[4], keyword_mat)
        if mutate_list[4] == 1:
            prompt_child = mutate(prompt_child, prompt_child[5], keyword_mat)

        prompt_list.append(prompt_child)
    
    return prompt_list
# Genjourney 🧬

## A Text-to-Image Prompt Optimization System Based on Interactive Genetic Algorithm and Large Language Models

Genjourney is an interactive web application developed using the Python-based Streamlit library, designed for optimizing textual prompts of Midjourney. It can be accessed and utilized via the following URL: https://genjourney.streamlit.app/ 🔗.

### Local Deployment

Genjourney is designed to support local deployment. To achieve this, one may clone the repository. After ensuring all the libraries listed in the "requirements.txt" are installed, execute the following command in the repository's directory:

```
streamlit run app.py
```
Please note that an active internet connection is still required for its operation.

For local deployment, it is imperative to configure two environment variables: OPENAI_API_KEY for the OpenAI API and MJ_API_KEY for the Midjourney API, provided by The Next Leg (https://www.thenextleg.io/). Ensure these are set in advance.

![Alt text](1692868276126.png)
## Plz email me if the API key is NO LONGER AVAILABLE (ucapfz0@ucl.ac.uk). ##

### Workflow of Genjourney
The workflow of this system is delineated as follows:

    a) The user provides an initial prompt.

    b) Based on the initial prompt, the system formulates a prompt modifier matrix with potential combinations amounting to 30^7.

    c) The system randomly constructs an initial population of structured prompts, with a population size of five, from the prompt modifier matrix.

    d) The user then selects two prompts corresponding to the images that best align with their aesthetic preferences from the current population, offering feedback from five aesthetic dimensions.

    e) Using user feedback as a measure, the system determines the fitness of the current population. Subsequent crossover and mutation operations are performed to produce the next generation of prompts.

Steps d and step e are repeatedly undertaken until the resultant image aligns with the user's aesthetic criteria.

Moreover, to enhance the user's creative experience, we integrated the 'blend' feature from Midjourney, allowing users to amalgamate desirable images from the offspring with textual prompts.

### Components in Genjourney
The Genjourney application, grounded on our proposed prompt optimization algorithm, encompasses components as depicted in Figure 3.7:

    Model Selection: Within Genjourney, users have access to two of Midjourney's latest models: “Midjourney Model V5.2” and “Niji Model V5”.

    Mutation Rate Mode Selection: Depending on their requirements, users can opt between three mutation rate modes: “low,” “medium,” and “high”.

    Initial Prompt Input: Users can articulate their concepts by feeding them into Genjourney as initial prompts.

    Current Generation Display: The primary interface showcases the present generation of prompt populations along with their corresponding images. Additionally, each image set is accompanied by links to its sub-images for user download convenience.

    User-driven Interactive Genetics: Following each population generation, users can pinpoint the prompt of the image that best resonates with them. This selected two prompts serve as the parent prompts. Users then provide aesthetic feedback based on the five dimensions delineated in Section 3.2.4. Genjourney then translates this into a fitness measure for the population, perpetuating its evolution.

    Blend Feature: Should users desire, they can meld the prompts of up to three images from the current generation with the chosen parent prompts.

    Historical Log: All previously generated offspring populations are catalogued under the 'History' section on the page's left, with indicators specifying if they were selected.

### Experiments

"prompt_diversity.ipynb", "user.ipynb" and "target_similarity.ipynb" are for experiments. Detailed setup is mentioned in the report.
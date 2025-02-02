from langchain_openai import ChatOpenAI
#from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os,dotenv
from langchain_core.prompts import PromptTemplate 


dotenv.load_dotenv()

default_headers={"Authorization" : os.environ["BODHI_LLM_GATEWAY_TOKEN"]}

# Initialize OpenAI with Langchain and default headers
openai_api = ChatOpenAI(
    model="gpt-4o",
    default_headers=default_headers,
    max_tokens= 256,
    seed= 42,
    stream= False,
    temperature= 0,
    top_p= 1
)

def get_course_recommendations(QA_res, available_courses):
    """
    Use OpenAI to get course recommendations based on user responses.
    
    Parameters:
    - QA_res (str): User's responses to questions.
    - available_courses (list): List of available courses.
    
    Returns:
    - list: Recommended courses.
    """
    template = """
    You only answer in the format ['course to learn1', 'course to learn2', ...].
    Based on the answers for the below questions,
    which of these topics should the user learn {available_courses}?
    This is in the perspective of the user for your context.
    {QA_res}
    """
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o", default_headers={"Authorization" : os.environ["BODHI_LLM_GATEWAY_TOKEN"]})
    llm_chain = prompt | llm 
    response = llm_chain.invoke({"QA_res":QA_res, "available_courses":available_courses})
    
    # Evaluate the response to convert it into a list
    recommended_courses = eval(response.content)
    print("Recommended Courses:", recommended_courses)
    return recommended_courses

def generate_description(course_name):
    """
    Generate a description for a course using OpenAI.
    
    Parameters:
    - course_name (str): The name of the course.
    
    Returns:
    - str: Generated description.
    """
    # prompt_template = PromptTemplate(
    #     input_variables=["course_name"],
    #     template="Generate a description for a video whose title is {course_name}."
    # )
    # chain = LLMChain(llm=openai_api, prompt=prompt_template)
    # description = chain.run(course_name=course_name)
    template="Generate a description for a video whose title is {course_name}."
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o", default_headers={"Authorization" : os.environ["BODHI_LLM_GATEWAY_TOKEN"]})
    llm_chain = prompt | llm 
    description = llm_chain.invoke({"course_name":course_name})
    return description.content

def generate_course_overview(question):
    """
    Generate a brief overview for a course topic.
    
    Parameters:
    - question (str): The course topic.
    
    Returns:
    - str: Generated overview.
    """
    # prompt_template = PromptTemplate(
    #     input_variables=["question"],
    #     template=(
    #         "Provide a brief overview of the topic (your entire response should be in about 15 words): {question}"
    #     )
    # )
    # chain = LLMChain(llm=openai_api, prompt=prompt_template)
    # overview = chain.run(question=question)
    # return overview
    template="Provide a brief overview of the topic (your entire response should be in about 15 words): {question}"
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o", default_headers={"Authorization" : os.environ["BODHI_LLM_GATEWAY_TOKEN"]})
    llm_chain = prompt | llm 
    overview = llm_chain.invoke({"question":question})
    return overview.content

def generate_course_paragraph(title):
    """
    Generate a detailed paragraph for a course title.
    
    Parameters:
    - title (str): The course title.
    
    Returns:
    - str: Generated paragraph.
    """
    # prompt_template = PromptTemplate(
    #     input_variables=["title"],
    #     template=(
    #         "Write an extremely detailed paragraph on {title}. Make it very understandable and well formatted."
    #     )
    # )
    
    # chain = LLMChain(llm=openai_api, prompt=prompt_template)
    # paragraph = chain.run(title=title)
    # return paragraph
#     import requests

#     url = "https://bodhi-llm-gateway-hackathon.api.sandbox.psbodhi.live//api/openai/chat/completions"

#     payload = {
#     "model": "gpt-4o",
#     "messages": [
#         {
#             "role": "system",
#             "content": "You are a helpful assistant"
#         },
#         {
#             "role": "user",
#             "content": f"Write an extremely detailed paragraph on {title}. Make it very understandable and well formatted."
#         }
#     ],
#     "max_tokens": 256,
#     "seed": 42,
#     "stream": False,
#     "temperature": 0,
#     "top_p": 1
# }
#     headers = {
#     "authorization": os.environ["BODHI_LLM_GATEWAY_TOKEN"],
#     "content-type": "application/json"
#     }

#     response = requests.post(url, json=payload, headers=headers)
#     json_data=response.json()

#     return json_data['choices'][0]['message']['content']
    template="Write an extremely detailed paragraph on {title}. Make it very understandable and well formatted."
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o", default_headers={"Authorization" : os.environ["BODHI_LLM_GATEWAY_TOKEN"]})
    llm_chain = prompt | llm 
    overview = llm_chain.invoke({"title": title})
    return overview.content

def generate_course_quiz(paragraph):
    """
    Generate a quiz based on a course paragraph.
    
    Parameters:
    - paragraph (str): The course paragraph.
    
    Returns:
    - list: Generated quiz in the specified format.
    """
    # prompt_template = PromptTemplate(
    #     input_variables=["paragraph"],
    #     template=(
    #         "{paragraph}\nFrom the above paragraph, generate a quiz of this format:\n"
    #         "[\n"
    #         "    {\n"
    #         "        'question': question_statement,\n"
    #         "        'options': [option1, option2, option3, option4]\n"
    #         "    },\n"
    #         "    ...\n"
    #         "] Each question should contain a single correct answer."
    #     )
    # )
    
    # chain = LLMChain(llm=openai_api, prompt=prompt_template)
    # quiz = chain.run(paragraph=paragraph)
    # template = """
    # {paragraph}
    # From the above paragraph, generate a quiz of this format:
    # [
    #     {
    #         '{{question_statement}}': question_statement,
    #         options: [option1, option2, option3, option4]
    #     },
    #     ...
    # ] Each question should contain a single correct answer.
    # """
    template=(
            "{paragraph}\nFrom the above paragraph, generate a quiz of this format:\n"
            "[\n"
            "    (\n"
            "        'question': question_statement,\n"
            "        'options': [option1, option2, option3, option4]\n"
            "    ),\n"
            "    ...\n"
            "] Each question should contain a single correct answer."
            "DO NOT say Here’s a quiz based on the provided paragraph:"
        )

    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o", default_headers={"Authorization" : os.environ["BODHI_LLM_GATEWAY_TOKEN"]})
    llm_chain = prompt | llm 
    quiz = llm_chain.invoke({"paragraph":paragraph})

    print(quiz.content)
    print(eval(quiz.content))
    try:
        return eval(quiz.content)
    except:
        return None

def fetch_relevant_video(question):
    """
    Fetch a relevant YouTube video link for a course topic.
    
    Parameters:
    - question (str): The course topic.
    
    Returns:
    - str: YouTube video link.
    """
    # prompt_template = PromptTemplate(
    #     input_variables=["question"],
    #     template=(
    #         "Find a YouTube video link that best explains the topic. The video link should be of the format "
    #         "https://www.youtube.com/watch?v=[video_code]: {question}"
    #     )
    # )
        
    # chain = LLMChain(llm=openai_api, prompt=prompt_template)
    # video_link = chain.run(question=question)
    # return video_link

    template="""
            Find a YouTube video link that best explains the topic. The video link should be of the format 
            https://www.youtube.com/watch?v=[video_code]: {question}
        """
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o", default_headers={"Authorization" : os.environ["BODHI_LLM_GATEWAY_TOKEN"]})
    llm_chain = prompt | llm 
    video_link = llm_chain.invoke({"question":question})
    return video_link.content

def grade_quiz(quiz, user_answers):
    """
    Grade a quiz based on user answers.
    
    Parameters:
    - quiz (list): The quiz questions and options.
    - user_answers (list): The user's answers.
    
    Returns:
    - tuple: Grade percentage, number of correct answers, total questions.
    """
    # prompt_template = PromptTemplate(
    #     input_variables=["quiz", "user_answers"],
    #     template=(
    #         "{quiz}\n{user_answers}\nHere are the questions, followed by their answers. "
    #         "Return the count of how many questions are correct in this format:\n"
    #         "[{'score': no_of_correct_answers:int, 'total_questions': total_questions:int}]"
    #     )
    # )
    
    # chain = LLMChain(llm=openai_api, prompt=prompt_template)
    # response = chain.run(quiz=quiz, user_answers=user_answers)

    template="""
            {quiz}\n{user_answers}\nHere are the questions, followed by their answers. 
            Return the count of how many questions are correct in this format:\n
            [{'score': no_of_correct_answers:int, 'total_questions': total_questions:int}]
        """
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o", default_headers={"Authorization" : os.environ["BODHI_LLM_GATEWAY_TOKEN"]})
    llm_chain = prompt | llm 
    response = llm_chain.invoke({"quiz":quiz, "user_answers":user_answers})     
    response = eval(response.content)
    score = response[0]['score']
    total_questions = response[0]['total_questions']
    grade = (score / total_questions) * 100
    return grade, score, total_questions

def create_custom_course(question, user_id, db):
    """
    Create a custom course and update the user's enrolled courses.
    
    Parameters:
    - question (str): The course topic.
    - user_id (str): The user's ID.
    - db: The database instance.
    
    Returns:
    - dict: The new course details.
    """
    if question is None:
        raise ValueError("Question cannot be None")
    
    course_title = question.title()
    overview = generate_course_overview(question)
    video_link = fetch_relevant_video(question)
    
    new_course = {
        "title": course_title,
        "description": overview,
        "type": "video",
        "link": video_link
    }
    
    user_data = db.child("users").child(user_id).get().val()
    enrolled_courses = user_data.get('enrolled_courses', [])
    enrolled_courses.append(new_course)
    db.child("users").child(user_id).update({'enrolled_courses': enrolled_courses})
    
    return new_course

def is_finance_related(topic):
    """
    Determine if a topic is finance-related.
    
    Parameters:
    - topic (str): The topic to assess.
    
    Returns:
    - bool: True if finance-related, False otherwise.
    """
    # prompt_template = PromptTemplate(
    #     input_variables=["topic"],
    #     template="Is the following topic related to finance? Answer with 'Yes' or 'No': {topic}"
    # )
    
    # chain = LLMChain(llm=openai_api, prompt=prompt_template)
    # response = chain.run(topic=topic)
    # print(response)
    # return response.strip().lower() == "yes"
    template="Is the following topic related to finance? Answer with 'Yes' or 'No': {topic}"
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o", default_headers={"Authorization" : os.environ["BODHI_LLM_GATEWAY_TOKEN"]})
    llm_chain = prompt | llm 
    response = llm_chain.invoke({"topic":topic}) 
    print(response.content) 
    return response.content.strip().lower() == "yes"


def is_asking_to_create_course(user_input):
    """
    Determine if the user is asking to create a course.
    
    Parameters:
    - user_input (str): The user's input.
    
    Returns:
    - bool: True if asking to create a course, False otherwise.
    """
    # prompt_template = PromptTemplate(
    #     input_variables=["user_input"],
    #     template="Is the user asking to create a course in the following statement? Answer with 'Yes' or 'No': {user_input}"
    # )
    
    # chain = LLMChain(llm=openai_api, prompt=prompt_template)
    # response = chain.run(user_input=user_input)
    # print("create course")
    # return response.strip().lower() == "yes"

    template="Is the user asking to create a course in the following statement? Answer with 'Yes' or 'No': {user_input}"
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o", default_headers={"Authorization" : os.environ["BODHI_LLM_GATEWAY_TOKEN"]})
    llm_chain = prompt | llm 
    response = llm_chain.invoke({"user_input":user_input}) 
    print(f"create course - {response.content}")
    return response.content.strip().lower() == "yes"


def generate_teaching_response(question):
    """
    Generate a detailed teaching response for a question.
    
    Parameters:
    - question (str): The question to answer.
    
    Returns:
    - str: The teaching response.
    """
    # prompt_template = PromptTemplate(
    #     input_variables=["question"],
    #     template="Answer the following question in detail as if you are teaching finance to a beginner: {question}"
    # )
    
    # chain = LLMChain(llm=openai_api, prompt=prompt_template)
    # response = chain.run(question=question)
    # return response
    template="Answer the following question in detail as if you are teaching finance to a beginner: {question}"
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o", default_headers={"Authorization" : os.environ["BODHI_LLM_GATEWAY_TOKEN"]})
    llm_chain = prompt | llm 
    response = llm_chain.invoke({"question":question}) 
    return response.content

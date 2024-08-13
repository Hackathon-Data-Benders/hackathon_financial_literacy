from huggingface_hub import InferenceClient
from api_keys import ai_key

client = InferenceClient(
        "meta-llama/Meta-Llama-3-8B-Instruct",
        token=ai_key,
    )

def get_course_recommendations(QA_res, available_courses):
    global client

    recommended_courses = ""

    for message in client.chat_completion(
            messages=[{"role": "user", "content": f"""You only answer in the format ["courses to learn1", "course to learn2"... ] 
                Based off the answers for the below questions, 
                which of these topics should the user learn {available_courses}. 
                This is in the perspective of the user for your context\n"""+QA_res}],
            max_tokens=500,
            stream=True,
    ):
        recommended_courses += (message.choices[0].delta.content)

    print(recommended_courses)
    print(eval(recommended_courses))

    return eval(recommended_courses)

def generate_description(course_name):
    global client
    for message in client.chat_completion(
            messages=[{"role": "user", "content": f"""Generate a description for a video whose title is {course_name}"""}],
            max_tokens=500,
            stream=True,
    ):
        description += (message.choices[0].delta.content)

    return description

# print(output)

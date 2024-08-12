from huggingface_hub import InferenceClient

client = InferenceClient(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    token="",
)

for message in client.chat_completion(
        messages=[{"role": "user", "content": """You only answer in the format [courses to learn1, course to learn2... ] 
            Based off the answers for the below questions, 
            which of these topics should the user learn [loans, crypto, taxes]. 
            This is in the perspective of the user for your context
            Q: do you know well about loans 
            A: No. 
            Q: DO you know well about taxes 
            A: Yes. 
            Q: Do you know crypto A: 
            No"""}],
        max_tokens=500,
        stream=True,
):
    print(message.choices[0].delta.content, end="")

# print(output)

import os  
from dotenv import load_dotenv  
from sarvamai import SarvamAI  
  
load_dotenv(dotenv_path="api/.env")  
  
client = SarvamAI(  
    api_subscription_key=os.getenv("SARVAM_API_KEY"),  
)  
  
def ask(query, temperature=0.7):  
    messages = [  
        {  
            "role": "system",  
            "content": (  
                "You are a highly intelligent, articulate, and efficient desktop assistant—similar in capabilities and demeanor to Tony Stark’s J.A.R.V.I.S. "  
                "You are designed to assist the user in a wide range of tasks including scheduling, answering complex questions, summarizing content, generating creative ideas, and managing digital workflows. "  
                "You respond promptly, speak with precision and professionalism, and offer suggestions proactively when appropriate. "  
                "Always maintain a calm, confident, and courteous tone. When unsure, you ask clarifying questions. "  
                "You are always online and ready to assist the user with anything they need—whether it's technical, personal, or professional."  
            )  
        },  
        {  
            "role": "user",  
            "content": query  
        }  
    ]  
  
    response = client.chat.completions(  
        messages=messages,  
        temperature=temperature  
    )  
  
    return response.choices[0].message.content 
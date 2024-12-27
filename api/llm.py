from gradio_client import Client
import sys
import io

def compute(query):
    sys.stdout = io.StringIO()
    
    client = Client("prakhardoneria/artifix")
    result = client.predict(
        message=query,
        api_name="/predict"
    )
    
    sys.stdout = sys.__stdout__
    
    return result
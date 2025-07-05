import api.wikipedia as wiki
import datetime
import api.sarvam as sarvam

def handle(query):

    if not query or not isinstance(query, str):
        return "Invalid query. Please provide a valid string."

    query = query.lower().strip()

    if 'who is' in query:
        query = query.replace("who is", "").strip()
        return wiki.wiki(query)

    elif 'the time' in query:
        str_time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"The time is {str_time}."

    elif 'love' in query:
        return 'Love is that for which a person can wait for years, holding onto the pain and hope.'

    else:
        try:
            response = sarvam.ask(query)
            return response
        except Exception as e:
            print(f"Error handling query: {e}")
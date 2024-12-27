import api.llm as ai
import api.wikipedia as wiki
import api.gemini as gemini
import datetime

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

    elif any(phrase in query for phrase in ['explain', 'what do', 'how can']):
        return gemini.ask(query)

    else:
        try:
            ans = ai.compute(query)
            return ans
        except Exception as e:
            return f"Error while processing query: {str(e)}"

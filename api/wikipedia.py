import wikipedia

def wiki(query):
    query = query.replace("who is", "").strip()
    if not query:
        return "Please specify whom you'd like to know about."
    try:
        results = wikipedia.summary(query, sentences=2)
        return f"According to Wikipedia: {results}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"The query is ambiguous. Suggestions: {', '.join(e.options)}"
    except wikipedia.exceptions.PageError:
        return "No matching Wikipedia page was found."
    except Exception as e:
        return f"An error occurred while fetching information: {str(e)}"
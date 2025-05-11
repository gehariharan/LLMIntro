from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, GROQ_MODEL_NAME

llm_groq = ChatGroq(model_name=GROQ_MODEL_NAME, api_key=GROQ_API_KEY)

# Create an instance of DDGS first
ddgs = DDGS()

# Call the news method on the instance with correct parameters and handle rate limiting
try:
    test = ddgs.news(keywords="Latest Gold and silver metal news", region='us-in', timelimit='d')
    print("Successfully retrieved news")
except RatelimitException as e:
    print(f"Rate limit exceeded: {e}")
    print("DuckDuckGo has rate-limited your request. Try again later or use a different search provider.")

def news_analyzer(style, query):
  text = ""
  try:
    r = DDGS().news(query, region='us-en')
    for article in r:
      text +=  article.get('title')+ "\n"+ article.get('body')+"\n\n"

    if not text:
      return "No news articles found. Please try a different query or try again later."

    prompt = "Give a detailed news analysis in this style: "+style+". You will be given news items to analyze and apply that style. Here is the user question" + query + \
              "\n\n. The news items are : " + text

    #print(prompt)
    return llm_groq.invoke(prompt).content
  except RatelimitException as e:
    return f"Rate limit exceeded: {e}. DuckDuckGo has rate-limited your request. Try again later or use a different search provider."
  except Exception as e:
    return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    # Set defaults
    newstopic = input("Enter the news topic you want to know more about (default: Today's news): ") or "Today's news"
    stylechoice = input("Enter the style in which you would like to read the news (default: CNN News Anchor): ") or "CNN News Anchor"
    print(f"Here is the latest update about: {newstopic} \n")
    print(news_analyzer(f"Write in the style of {stylechoice}", newstopic))


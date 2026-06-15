from ddgs import DDGS
import json

def websearch(query:str="") -> str:
    try:
        with DDGS() as ddgs:
            results = [item for item in ddgs.text(query, max_results=5)]
            return json.dumps(results)
    except Exception as e:
        return json.dumps({"error":f"Failed to perform websearch: {str(e)}"})
    
if __name__ == "__main__":
    while True:
        uInput = input("Search query: ")
        if not uInput:
            continue
        results = websearch(query=uInput)
        print(results)

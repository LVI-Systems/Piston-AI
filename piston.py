import json
from openai import OpenAI
from pathlib import Path
import platform
import threading
import sys
import time
from tools import websearch, currentWeather
from datetime import datetime, date

if platform.system() in ("Darwin", "Linux"):
    import readline
else:
    pass

def spinner(spinner_event):
    frames = ["/", "-", "\\", "|"]
    idx = 0

    while not spinner_event.is_set():
        sys.stdout.write(f"\r{frames[idx]}")
        sys.stdout.flush()
        idx += 1
        if idx > 3:
            idx = 0
        time.sleep(0.08)

def askPiston(message=""):
    sysPrompt = f"""You are Piston AI, a useful voiced or typed AI assistant. Stay friendly.
    The current time is {datetime.now()}.
    Use the provided live web search results to find the most up-to-date information, and prioritize official release notes or recent news dates over older discussions.
    In every message, if the user's request or answer is fulfilled, you MUST append "[CLOSE]" into the end of the message. if the message is not fulfilled, append "[LISTEN]" to the end of the message.
    """
    spinnerStopped = False
    stopSpinner = threading.Event()
    spinnerAnimation = threading.Thread(target=spinner, daemon=True, args=(stopSpinner,))
    spinnerAnimation.start()

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="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",
    )

    messages = readHistory()
    payload = {
        "role":"user",
        "content":message
    }
    if not messages:
        messages.append({
            "role":"system",
            "content":sysPrompt
        })
    messages.append(payload)

    tools = [{
        "type":"function",
        "function": {
            "name":"web_search",
            "description":"Look up real-time information, news, or facts on the live internet. DO NOT use this tool for general conversation, scheduling, internal math, or when the user's request can be handled using local logic or the current time context.",
            "parameters":{
                "type":"object",
                "properties":{
                    "query": {"type":"string", "description":"The search keyword to look up on the web"},
                    "required":["query"]
                }
            }
        }
    },{
        "type":"function",
        "function": {
            "name":"current_weather",
            "description":"use this tool only when the user EXPLICITELY talks about the weather.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }]

    completion = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=1,
        top_p=0.95,
        max_tokens=8192,
        stream=True
    )

    full_response = ""
    tool_calls = []

    for chunk in completion:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if not spinnerStopped:
            stopSpinner.set()
            spinnerAnimation.join()
            spinnerStopped  = True
            print("\r", end="", flush=True)
            print(end="", flush=True)
        if delta.content is not None:
            print(delta.content, end="", flush=True)
            full_response += delta.content
        if delta.tool_calls:
            for tool_call in delta.tool_calls:
                idx = tool_call.index
                fname = tool_call.function.name
                tool_call_id = tool_call.id

                if len(tool_calls) <= idx:
                    tool_calls.append(
                        {
                            "id":tool_call_id,
                            "type":"function",
                            "function": {
                                "name": tool_call.function.name, "arguments":""
                            }
                        }
                    )

                if tool_call.function.arguments:
                    tool_calls[idx]["function"]["arguments"] += tool_call.function.arguments

    if tool_calls:
        for tool_call in tool_calls:
            fname = tool_call["function"]["name"]
            rawArgs = tool_call["function"]["arguments"] or "{}"
            fargs = json.loads(rawArgs)
            tool_call_id = tool_call["id"]

            if fname == "web_search":
                print("Searching the web...")
                results = websearch.websearch(query=fargs.get("query"))
            elif fname == "current_weather":
                print("Fetching weather...")
                results = currentWeather.main()

        messages.append({
            "role":"tool",
            "tool_call_id":tool_call_id,
            "name":fname,
            "content":results
        })
        secCompletion = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=messages,
            temperature=1,
            top_p=0.95,
            max_tokens=8192,
            stream=True
        )
        full_response = ""
        for chunk in secCompletion:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if not spinnerStopped:
                stopSpinner.set()
                spinnerAnimation.join()
                spinnerStopped = True
            if delta.content is not None:
                print(delta.content, end="", flush=True)
                full_response += delta.content
    if full_response.strip().endswith("[LISTEN]"):
        numberOfCharToBeRemoved = 8
        listen = True
    elif full_response.strip().endswith("[CLOSE]"):
        numberOfCharToBeRemoved = 7
        listen = False
    else:
        numberOfCharToBeRemoved = 0
        listen = False
    
    full_response = full_response[:-numberOfCharToBeRemoved]
    
    print('')
    messages.append({
        "role":"assistant",
        "content":full_response
    })
    writeHistory(messages)
    return full_response, listen
    
def readHistory(path="data/history.json"):
    Path(path).touch()
    with open(path, "r") as f:
        try:
            history = json.load(f)
            if not isinstance(history, list):
                history = []
        except:
            with open(path, "w") as fw:
                json.dump([], fw, indent=4)
            history = []
    return history

def writeHistory(historyArray=[], path="data/history.json"):
    if historyArray is None:
        historyArray=[]
    if not Path(path).exists():
        Path(path).touch()
    
    with open(path, "w") as f:
        try:
            json.dump(historyArray, f, indent=4)
        except:
            json.dump([], f, indent=4)

if __name__ == "__main__":
    while True:
        uInput = input("Ask anything> ")
        if not uInput.strip():
            continue
    
        askPiston(uInput)

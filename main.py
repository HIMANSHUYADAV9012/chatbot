from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json

app = FastAPI()

# 🔹 CORS allow (frontend से connect के लिए)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production में अपनी domain डालो
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Gemini API Key
GEMINI_API_KEY = "AIzaSyC-0CdxgA7G5l6nvVSQEp4rgR9beSvQk9Y"
GEMINI_ENDPOINT = "https://api.generativeai.google.com/v1beta2/models/text-bison-001:generateText"

# 🔹 Load FollowersHub JSON data
with open("followershub_data.json", "r", encoding="utf-8") as f:
    site_data = json.load(f)

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
    except Exception:
        return {"reply": "Error: Invalid JSON received."}

    user_message = data.get("message", "").strip()
    if not user_message:
        return {"reply": "Please type a message."}

    # 🔹 Context: FollowersHub data
    context = f"""
FollowersHub Data:
{json.dumps(site_data, ensure_ascii=False, indent=2)}
"""

    # 🔹 Gemini API request payload
    payload = {
        "prompt": f"""
Tu FollowersHub ka smart AI assistant hai.
- User Hindi, Hinglish ya English mein baat kar sakta hai.
- Har message ko same language mein reply de.
- Hamesha FollowersHub ke JSON data se hi answer de.
- Agar user unrelated baat kare, politely bol: "Maaf kijiye, ye information abhi available nahi hai."

Context:
{context}

User: {user_message}
""",
        "temperature": 0.7,
        "maxOutputTokens": 500
    }

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(GEMINI_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
            resp_json = response.json()
            reply = resp_json.get("candidates", [{}])[0].get("content", "Maaf kijiye, response nahi aaya.")
            return {"reply": reply}

    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

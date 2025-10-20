from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import re
import random
import time
from typing import Dict, List, Optional
import datetime

# ------------------ Load Data ------------------
with open("followershub_data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

# ------------------ Enhanced Greetings & Responses ------------------
GREETINGS = {
    "hi": ["Hey there! 👋 How can I help you with your social media growth today?", 
           "Hi! Welcome to FollowersHub! Ready to boost your Instagram? 🚀",
           "Hello! Great to see you here! What can I do for you? 😊"],
    
    "hello": ["Hello! 👋 Looking to grow your Instagram presence?", 
              "Hi there! Excited to help you with followers, views, or verification!"],
    
    "hey": ["Hey! What's on your mind today? 💭", 
            "Hey there! How's your social media journey going? 😄"],
    
    "good morning": ["Good morning! 🌞 Perfect time to grow your Instagram!", 
                     "Morning! Hope you're having an amazing day! Ready to boost your account?"],
    
    "good evening": ["Good evening! 🌇 Great time to plan your social media growth!", 
                     "Evening! How can I make your Instagram better today? 😎"],
    
    "how are you": ["I'm doing great! Thanks for asking 😊 How about you? What brings you to FollowersHub today?", 
                    "Awesome as always! Ready to help you grow 📈 How's your day going?"],
}

# Natural follow-up questions
FOLLOW_UPS = {
    "greeting": [
        "By the way, are you looking for followers, views, or the blue tick?",
        "What would you like to know about our services?",
        "Is there a specific package you're interested in?",
        "How can I help improve your Instagram today?"
    ],
    "general": [
        "Would you like me to suggest the best package for your needs?",
        "Need help choosing the right service?",
        "Want to know about our current offers?",
        "Should I show you our most popular packages?"
    ]
}

# ------------------ Conversation Memory ------------------
conversation_memory = {}

def get_user_context(user_id: str) -> Dict:
    """Get or create user conversation context"""
    if user_id not in conversation_memory:
        conversation_memory[user_id] = {
            "last_message": "",
            "last_intent": "",
            "mentioned_services": [],
            "conversation_count": 0,
            "last_active": datetime.datetime.now(),
            "user_name": None
        }
    return conversation_memory[user_id]

def update_user_context(user_id: str, message: str, intent: str):
    """Update user conversation context"""
    context = get_user_context(user_id)
    context["last_message"] = message
    context["last_intent"] = intent
    context["conversation_count"] += 1
    context["last_active"] = datetime.datetime.now()
    
    # Track mentioned services
    services = ["followers", "views", "blue tick", "verify", "reels", "story"]
    for service in services:
        if service in message.lower():
            if service not in context["mentioned_services"]:
                context["mentioned_services"].append(service)

# ------------------ Advanced Response Generator ------------------
class AdvancedResponseGenerator:
    def __init__(self):
        self.package_synonyms = {
            "followers": ["followers", "fans", "audience", "subscribers", "people"],
            "views": ["views", "watchers", "viewers", "visibility", "watch time"],
            "likes": ["likes", "reactions", "engagement"],
            "blue tick": ["blue tick", "verification", "verified", "badge", "authentic"],
            "story": ["story", "stories", "story views"],
            "reels": ["reels", "reel views", "video views"]
        }
    
    def detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        intents = {
            "greeting": any(word in message_lower for word in ["hi", "hello", "hey", "good morning", "good evening"]),
            "pricing": any(word in message_lower for word in ["price", "cost", "how much", "₹", "rs"]),
            "packages": any(word in message_lower for word in ["package", "plan", "service", "offer"]),
            "technical": any(word in message_lower for word in ["how", "what", "when", "where", "why", "can i"]),
            "trust": any(word in message_lower for word in ["trust", "safe", "secure", "legit", "real", "genuine"]),
            "support": any(word in message_lower for word in ["help", "support", "contact", "problem", "issue"]),
            "payment": any(word in message_lower for word in ["payment", "pay", "money", "transaction", "failed"]),
            "refund": any(word in message_lower for word in ["refund", "return", "cancel", "money back"]),
            "policy": any(word in message_lower for word in ["policy", "term", "privacy", "condition"]),
            "service_type": any(any(syn in message_lower for syn in syns) for syns in self.package_synonyms.values())
        }
        
        for intent, detected in intents.items():
            if detected:
                return intent
        return "general"
    
    def generate_natural_response(self, intent: str, message: str, user_context: Dict) -> str:
        """Generate natural, human-like responses"""
        
        # Add thinking delay for realism
        time.sleep(0.5)
        
        if intent == "greeting":
            greeting = random.choice(GREETINGS.get(
                next((k for k in GREETINGS if k in message.lower()), "hi")
            ))
            follow_up = random.choice(FOLLOW_UPS["greeting"])
            return f"{greeting} {follow_up}"
        
        elif intent == "pricing":
            return "Let me check our current prices for you! 💰 Our packages start from just ₹110 and go up to ₹1749, depending on what you need. Which service are you looking for - followers, views, or verification?"
        
        elif intent == "packages":
            return self._handle_packages_query(message)
        
        elif intent == "trust":
            t = DATA["trust"]
            trust_responses = [
                f"{t['icon']} {t['message']} We've helped thousands of users grow their Instagram safely!",
                f"{t['icon']} Absolutely trusted! {t['message']} and we maintain 100% safety standards.",
                f"{t['icon']} {t['message']} Your account security is our top priority! 🔒"
            ]
            return random.choice(trust_responses)
        
        elif intent == "payment":
            return self._handle_payment_query(message)
        
        elif intent == "service_type":
            return self._handle_service_specific(message)
        
        else:
            return self._handle_general_query(message, user_context)
    
    def _handle_packages_query(self, message: str) -> str:
        """Handle package-related queries"""
        found_packages = []
        message_lower = message.lower()
        
        for pkg in DATA["packages"]:
            if (pkg["type"] in message_lower or 
                str(pkg["price"]) in message_lower or 
                pkg["title"].lower() in message_lower or 
                any(word in message_lower for word in ["package", "plan", "service"])):
                found_packages.append(pkg)
        
        if found_packages:
            response = "I found these perfect packages for you! 📦\n\n"
            for p in found_packages[:3]:  # Show max 3 packages
                emoji = "🔥" if p["popular"] else "⭐"
                discount = " 💰 Discount Available!" if p["discount"] else ""
                response += f"• {p['title']} - ₹{p['price']}\n  {p['desc']}{emoji}{discount}\n\n"
            
            response += "Which one catches your eye? Or should I suggest the best option for your needs? 😊"
            return response
        else:
            return "Let me show you our most popular packages! 🔥\n\n• 10K Followers - ₹300 (Most Popular!)\n• 20K Story Views - ₹299\n• Blue Tick Verification - ₹299\n\nWhich service interests you most?"
    
    def _handle_payment_query(self, message: str) -> str:
        """Handle payment-related queries"""
        if any(word in message.lower() for word in ["failed", "problem", "issue", "not working"]):
            payment_data = DATA["responses"]["paymentFailed"]
            responses = [
                f"😔 {payment_data['response']} Don't worry, your money is safe!",
                f"⚠️ {payment_data['response']} We'll make sure you get your refund quickly!",
                f"🔧 {payment_data['response']} Our team is on it to resolve this for you!"
            ]
            return random.choice(responses)
        else:
            return "For payments, we accept all major UPI apps, credit/debit cards, and net banking. 💳 Which package are you interested in?"
    
    def _handle_service_specific(self, message: str) -> str:
        """Handle specific service queries"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in self.package_synonyms["followers"]):
            return "Great choice! 👥 Followers are essential for growth. Our followers are real, active, and permanent. We have packages from 5K to 100K followers. Which size are you thinking?"
        
        elif any(word in message_lower for word in self.package_synonyms["views"]):
            return "Awesome! 📹 Views boost your visibility and engagement. We offer story views and reels views with high retention rates. Which type are you looking for?"
        
        elif any(word in message_lower for word in self.package_synonyms["blue tick"]):
            return "Excellent! ✅ The blue tick adds instant credibility. Our verification service helps you get that prestigious badge. Want me to tell you more about the process?"
        
        else:
            return self._handle_packages_query(message)
    
    def _handle_general_query(self, message: str, user_context: Dict) -> str:
        """Handle general queries with context awareness"""
        
        # Check for specific known queries first
        if "term" in message.lower():
            return f"📜 {DATA['responses']['terms']}"
        
        elif "privacy" in message.lower():
            return f"🔒 {DATA['responses']['privacy']}"
        
        elif "refund" in message.lower():
            return f"💸 {DATA['responses']['refund']}"
        
        elif "faq" in message.lower():
            faqs = DATA["responses"]["faq"]
            response = "Here are answers to common questions: ❓\n\n"
            for i, faq in enumerate(faqs[:3], 1):  # Show only 3 FAQs
                response += f"{i}. {faq['question']}\n   {faq['answer']}\n\n"
            response += "Did that answer your question? 😊"
            return response
        
        elif "contact" in message.lower() or "support" in message.lower():
            contact_responses = [
                "📞 You can reach us through our Contact page or DM our official Instagram handle @FollowersHub. We're here to help!",
                "💬 Need help? Contact us through our website or Instagram @FollowersHub. We usually reply within minutes!",
                "👋 We'd love to help! Reach out on our Contact page or Instagram @FollowersHub for quick support."
            ]
            return random.choice(contact_responses)
        
        elif "about" in message.lower() or "followershub" in message.lower():
            return f"🎯 {DATA['description']}\n\n💡 Note: {DATA['note']}"
        
        else:
            # Context-aware fallback
            if user_context["mentioned_services"]:
                last_service = user_context["mentioned_services"][-1]
                return f"Regarding {last_service}, is there something specific you'd like to know? Or shall I tell you about our best {last_service} packages? 😊"
            else:
                fallbacks = [
                    "I'd love to help! Could you tell me a bit more about what you're looking for? 🤔",
                    "Hmm, I want to make sure I give you the right info. Are you thinking about followers, views, or verification? 💭",
                    "Let me help you better! What aspect of Instagram growth are you most interested in? 📈",
                    "I'm here to help with your Instagram growth! What would you like to achieve - more followers, better engagement, or verification? 🎯"
                ]
                return random.choice(fallbacks)

# ------------------ Initialize App ------------------
app = FastAPI()
response_generator = AdvancedResponseGenerator()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Enhanced Chat Endpoint ------------------
@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        message = body.get("message", "").strip()
        user_id = body.get("user_id", "default_user")  # In production, use actual user auth
        
        if not message:
            return {"reply": "Hello! 👋 How can I help you with FollowersHub today?"}
        
        # Get user context
        user_context = get_user_context(user_id)
        
        # Detect intent and generate response
        intent = response_generator.detect_intent(message)
        reply = response_generator.generate_natural_response(intent, message, user_context)
        
        # Update user context
        update_user_context(user_id, message, intent)
        
        return {"reply": reply}
        
    except Exception as e:
        # Natural error response
        error_responses = [
            "Oops! 😅 Something went wrong on my end. Could you try again?",
            "Sorry about that! 🤖 Technical glitch. Mind repeating your question?",
            "My circuits are a bit fuzzy right now! 🔌 Could you rephrase that?"
        ]
        return {"reply": random.choice(error_responses)}

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "FollowersHub AI Chatbot is running! 🚀"}

# Clear old conversations (optional cleanup endpoint)
@app.delete("/clear-conversations")
async def clear_old_conversations():
    global conversation_memory
    now = datetime.datetime.now()
    # Remove conversations older than 24 hours
    conversation_memory = {
        user_id: context for user_id, context in conversation_memory.items()
        if (now - context["last_active"]).total_seconds() < 86400
    }
    return {"message": "Old conversations cleared"}

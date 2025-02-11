from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai

# IMPORTANT: Disclaimer - Clearly state the limitations
DISCLAIMER = "This chatbot is for informational purposes only and DOES NOT provide medical advice. Consult a healthcare professional for any health concerns."


import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# ✅ Set your Gemini API Key
GEMINI_API_KEY = os.getenv("MEDCHATBOT_API_KEY")  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# Load Gemini model
model = genai.GenerativeModel("gemini-pro")


# ✅ Trusted medical references
TRUSTED_SOURCES = {
    "symptoms": "https://www.webmd.com/a-to-z-guides/symptom-checker",
    "medications": "https://www.mayoclinic.org/drugs-supplements",
    "diseases": "https://www.cdc.gov/diseasesconditions/index.html",
    "first aid": "https://www.redcross.org/get-help/how-to-prepare-for-emergencies/first-aid.html",
    "nutrition": "https://www.hsph.harvard.edu/nutritionsource/",
    "mental health": "https://www.who.int/health-topics/mental-health",
    "vaccines": "https://www.cdc.gov/vaccines/index.html",
    "exercise": "https://www.healthline.com/health/fitness-exercise",
    "hygiene": "https://www.cdc.gov/healthywater/hygiene/index.html",
    "lifestyle": "https://www.hsph.harvard.edu/nutritionsource/healthy-lifestyle/",
    "aging": "https://www.nia.nih.gov/health",
    "wellness": "https://www.medicalnewstoday.com/categories/wellness",
    "cold": "https://www.mayoclinic.org/diseases-conditions/common-cold",
    "flu": "https://www.cdc.gov/flu/index.html",
    "allergies": "https://www.aaaai.org/",
    "diabetes": "https://www.diabetes.org/",
    "heart disease": "https://www.heart.org/en/health-topics",
    "respiratory": "https://www.lung.org/",
    "digestive": "https://www.gastro.org/",
    "cardiovascular": "https://www.heart.org/en/health-topics",
    "nervous system": "https://www.ninds.nih.gov/",
    "blood tests": "https://www.labtestsonline.org.uk/",
    "MRI": "https://www.radiologyinfo.org/en/info.cfm?pg=bodymr",
    "CT scan": "https://www.radiologyinfo.org/en/info.cfm?pg=abdoct",
    "X-ray": "https://www.radiologyinfo.org/en/info.cfm?pg=geninfo",
    "pregnancy": "https://www.acog.org/",
    "menstruation": "https://www.plannedparenthood.org/learn/health-and-wellness/menstruation",
    "fertility": "https://www.reproductivefacts.org/",
    "prostate health": "https://www.pcf.org/",
    "acne": "https://www.aad.org/public/diseases/acne",
    "eczema": "https://nationaleczema.org/",
    "hair loss": "https://www.aad.org/public/diseases/hair-loss",
    "skincare": "https://www.skincare.org/",
    "stress": "https://www.mentalhealth.org.uk/a-to-z/s/stress",
    "anxiety": "https://www.nimh.nih.gov/health/topics/anxiety-disorders",
    "depression": "https://www.psychiatry.org/patients-families/depression",
    "therapy": "https://www.psychologytoday.com/us/therapists"
}

def chatbot_home(request):
    """Render chatbot home page with disclaimer."""
    return render(request, "chatbot/chatbot.html", {"disclaimer": DISCLAIMER})

def chatbot_response(request):
    """Handle chatbot queries and return JSON response."""
    user_input = request.GET.get("message", "").strip().lower()

    if not user_input:
        return JsonResponse({"error": "No message provided"}, status=400)

    # ✅ Check if input is related to medical topics
    if not is_medical_query(user_input):
        return JsonResponse({
            "response": "I can only answer health-related queries. Please ask about symptoms, nutrition, or first aid!"
        })

    try:
        # ✅ Add context for better responses
        prompt = f"You are a medical chatbot. Provide factual, non-diagnostic health information. {user_input}"
        response = model.generate_content(prompt)
        bot_response = response.text.strip()

        # ✅ Sanitize and filter unsafe content
        bot_response = sanitize_response(bot_response)

        # ✅ Add trusted references for credibility
        reference = get_medical_reference(user_input)
        if reference:
            bot_response += f"\n🔗 **For more information:** {reference}"

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {e}"}, status=500)

    return JsonResponse({"response": bot_response})

def is_medical_query(text):
    """Check if the query is health-related using AI model."""
    prompt = f"Does the following text relate to general health or medical information? Reply 'yes' or 'no'.\n\nText: {text}"
    response = model.generate_content(prompt).text.strip().lower()
    return response == "yes"


def sanitize_response(text):
    """Filter sensitive or unsafe medical terms."""
    blacklist = ["diagnosis", "prescription", "surgery", "treatment", "cure"]
    for word in blacklist:
        text = text.replace(word, "[REDACTED]")
    return text

def get_medical_reference(text):
    """Get a relevant medical reference based on query."""
    for topic, link in TRUSTED_SOURCES.items():
        if topic in text:
            return link
    return None





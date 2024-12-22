from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Store user sessions
user_sessions = {}

# Predefined questions and responses
questions = {
    "start": "Hello! What symptom are you experiencing? (e.g., fever, cough, headache, sore throat, nausea)",
    "fever_q1": "Have you measured your temperature? Is it above 100.4°F (38°C)? (yes/no)",
    "fever_q2": "Are you experiencing chills or body aches? (yes/no)",
    "cough_q1": "Are you coughing frequently? (yes/no)",
    "cough_q2": "Do you have any chest pain or difficulty breathing? (yes/no)",
    "headache_q1": "Is the headache severe and persistent? (yes/no)",
    "headache_q2": "Do you feel nauseous or sensitive to light? (yes/no)",
    "sore_throat_q1": "Is your throat painful when swallowing? (yes/no)",
    "sore_throat_q2": "Do you have swollen tonsils or white patches in your throat? (yes/no)",
    "nausea_q1": "Are you vomiting? (yes/no)",
    "nausea_q2": "Do you also have diarrhea or abdominal cramps? (yes/no)",
}

diagnoses = {
    "fever_yes_yes": {"diagnosis": "Your symptoms strongly suggest influenza or another viral infection that causes systemic symptoms.","advice": "Get plenty of rest, drink fluids, and manage the fever with acetaminophen or ibuprofen if necessary. Seek medical care if your fever persists beyond 3 days, worsens, or is accompanied by shortness of breath."},
    "fever_yes_no": {"diagnosis": "A measured fever without additional symptoms could indicate a developing illness such as a urinary tract infection or an early viral infection.",  "advice": "Monitor your symptoms closely. Stay hydrated and rest. If new symptoms appear or the fever does not improve in 48–72 hours, consult a healthcare provider."},
    "fever_no_yes": {"diagnosis": "Chills and body aches without a fever could point to the early stages of a viral illness, muscle strain, or even dehydration.", "advice": "Ensure you are staying hydrated and resting. Consider taking a warm shower to ease the chills. If additional symptoms, such as fever or fatigue, develop, follow up with a doctor."},
    "fever_no_no": None,
    "cough_yes_yes": {"diagnosis": "This might indicate bronchitis or pneumonia.", "advice": "You should consult a doctor. Stay hydrated and avoid cold air."},
    "cough_yes_no": {"diagnosis": "You may have a common cold or mild respiratory infection.", "advice": "Stay hydrated, rest, and consider cough syrup if needed."},
    "cough_no_yes": {"diagnosis": "You might have mild throat irritation or an allergy.", "advice": "Avoid irritants and consider anti-allergy medication."},
    "cough_no_no": None,
    "headache_yes_yes": {"diagnosis": "This could be a migraine.", "advice": "Avoid bright lights, rest, and take pain relief medication if necessary. Consult a doctor if persistent."},
    "headache_yes_no": {"diagnosis": "This might be a tension headache.", "advice": "Relax, avoid stress, and consider over-the-counter pain relief."},
    "headache_no_yes": {"diagnosis": "This might be a sinus-related headache.", "advice": "Stay hydrated and consider a decongestant. Consult a doctor if needed."},
    "headache_no_no": None,
    "sore_throat_yes_yes": {"diagnosis": "You might have strep throat.", "advice": "Consult a doctor for a proper diagnosis. You may need antibiotics."},
    "sore_throat_yes_no": {"diagnosis": "This could be a viral sore throat.", "advice": "Gargle with warm salt water and stay hydrated. Monitor your symptoms."},
    "sore_throat_no_yes": {"diagnosis": "This might be throat irritation or an allergy.", "advice": "Avoid irritants and stay hydrated. Use throat lozenges if needed."},
    "sore_throat_no_no": None,
    "nausea_yes_yes": {"diagnosis": "You might have food poisoning or a stomach virus.", "advice": "Stay hydrated, rest, and avoid solid food until symptoms improve. Consult a doctor if it persists."},
    "nausea_yes_no": {"diagnosis": "This might be mild nausea due to stress or an upset stomach.", "advice": "Sip on ginger tea or clear fluids. Avoid heavy meals."},
    "nausea_no_yes": {"diagnosis": "This might be a sign of mild indigestion.", "advice": "Eat light meals and avoid spicy or greasy foods."},
    "nausea_no_no": None,
}

def initialize_user_session(user_id):
    """Reset or initialize the user's session."""
    user_sessions[user_id] = {"state": "start", "symptom": None}


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower().strip()
    user_id = request.json.get('user_id', 'default')

    # Debugging logs for tracking
    app.logger.debug(f"User Message: {user_message}, User ID: {user_id}")

    # Ensure the user has an active session or handle restart
    if user_message == "restart" or user_id not in user_sessions:
        initialize_user_session(user_id)  # Reset the session
        return jsonify({"response": questions["start"]})  # Send the initial message

    # Retrieve the current session
    session = user_sessions[user_id]
    state = session["state"]
    symptom = session["symptom"]

    # Main state handling logic
    if state == "start":
        for key in questions:
            if key.startswith(user_message):
                session["state"] = f"{user_message}_q1"
                session["symptom"] = user_message
                return jsonify({"response": questions[f"{user_message}_q1"]})
        return jsonify({"response": questions["start"]})  # If no symptom matches, repeat initial question.

    elif f"{symptom}_q1" in state:
        if user_message in ["yes", "no"]:
            session[state] = user_message
            session["state"] = f"{symptom}_q2"
            return jsonify({"response": questions[f"{symptom}_q2"]})
        return jsonify({"response": f"Please answer yes or no. {questions[f'{symptom}_q1']}"})

    elif f"{symptom}_q2" in state:
        if user_message in ["yes", "no"]:
            session[state] = user_message
            key = f"{symptom}_{session.get(f'{symptom}_q1')}_{user_message}"
            diagnosis = diagnoses.get(key)
            initialize_user_session(user_id)  # Reset for a new symptom
            if diagnosis:
                return jsonify({"response": f"Diagnosis: {diagnosis['diagnosis']} Advice: {diagnosis['advice']} "
                                            f"If you have another symptom, type 'restart' to start over."})
            else:
                return jsonify({"response": "I'm not sure about your symptoms. Please consult a doctor. "
                                            "Type 'restart' to discuss another symptom."})
        return jsonify({"response": f"Please answer yes or no. {questions[f'{symptom}_q2']}"})


def initialize_user_session(user_id):
    """Initialize or reset the user session."""
    user_sessions[user_id] = {"state": "start", "symptom": None}


if __name__ == "__main__":
    app.run(debug=True)
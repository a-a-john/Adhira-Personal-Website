# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import json, os, time

# Load environment variables
load_dotenv()

# Initialize OpenAI client (modern API)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Flask app setup
app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app)

@app.route("/")
def index():
    return app.send_static_file("index.html")

# Load portfolio data once at startup
with open("data/portfolio.json", "r") as f:
    portfolio_data = json.load(f)

@app.route("/api/ask", methods=["POST"])
def ask():
    try:
        user_input = request.json.get("message")
        print("User message:", user_input)

        if not user_input:
            return jsonify({"reply": "No message received."}), 400

        # --- Moderation Check ---
        mod = client.moderations.create(
            model="omni-moderation-latest",
            input=user_input
        )
        if mod.results[0].flagged:
            return jsonify({"reply": "Please keep questions professional."}), 400

        # --- System Prompt ---
        system_prompt = (
        "You are a professional assistant who answers questions about Adhira John's portfolio. "
        "Adhira John is a third-year Computer Science student with experience in research, software development, "
        "and creative technology projects. Use only the provided data for reference. "
        "If the question is about a specific topic or project, mention only the most directly related experiences. "
        "Avoid repeating general background information unless necessary. "
        "Adopt a confident but natural tone — clear, professional, and conversational. "
        "Highlight skills and achievements with understated confidence, not excessive praise."
    )


        context = json.dumps(portfolio_data)

        # --- Chat Completion Call ---
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Answer the question strictly using only the relevant parts of the data.\n\nQuestion: {user_input}\n\nData: {context}"}
                ],
                temperature=0.7,
                max_tokens=400
            )
        except Exception as api_err:
            # Retry once if we hit rate limits
            if "429" in str(api_err):
                print("Rate limit hit, retrying after 2 seconds...")
                time.sleep(2)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Question: {user_input}\n\nData: {context}"}
                    ],
                    temperature=0.7,
                    max_tokens=400
                )
            else:
                raise api_err

        answer = response.choices[0].message.content
        return jsonify({"reply": answer})

    except Exception as e:
        print("Error:", e)
        if "429" in str(e):
            return jsonify({"reply": "I'm getting too many requests right now — please try again in a moment."}), 429
        if "401" in str(e):
            return jsonify({"reply": "Invalid or expired API key. Please check your .env file."}), 401
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

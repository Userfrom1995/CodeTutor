from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from groq import Groq

app = Flask(__name__)
CODE_DIRECTORY = 'volume'

# Create the Groq client with API key
client = Groq(api_key="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")

# Initial system prompt
system_prompt = {
    "role": "system",
    "content": (
        "You are a helpful assistant who uses the Socratic method to teach students. "
        "First, ask the user what they want to learn about programming. Then guide them through the topic "
        "by asking thought-provoking questions to encourage deep understanding. Keep your answers concise "
        "and focused on questions that lead the user to figure things out for themselves."
    )
}

# Initialize chat history
chat_history = [system_prompt]


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat_with_groq():
    try:
        # Get the user's message from the request
        data = request.json
        user_message = data.get('prompt')

        if not user_message:
            return jsonify({"error": "No user input provided"}), 400

        # Append the user's message to chat history
        chat_history.append({"role": "user", "content": user_message})

        # Get response from Groq API
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=chat_history,
            max_tokens=150,
            temperature=1.0
        )

        # Extract the assistant's reply
        assistant_reply = response.choices[0].message.content

        # Append the assistant's reply to the chat history
        chat_history.append({"role": "assistant", "content": response.choices[0].message.content})

        # Return the response to the frontend
        return jsonify({"response": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/load_file/<language>')
def load_file(language):
    file_mapping = {
        'python': 'main.py',
        'javascript': 'main.js',
        'cpp': 'main.cpp',
        'java': 'main.java',
        'c': 'main.c'
    }

    file_name = file_mapping.get(language)
    if file_name:
        file_path = os.path.join(CODE_DIRECTORY, file_name)
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return content, 200
        except Exception as e:
            return f'Error reading file: {str(e)}', 500
    return 'File not found', 404


if __name__ == '__main__':
    app.run(debug=True)

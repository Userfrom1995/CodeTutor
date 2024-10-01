from flask import Flask, request, jsonify, render_template
import os
from groq import Groq
import docker
from flask_socketio import SocketIO, emit
from threading import Thread
from flask_cors import CORS

app = Flask(__name__)
socketio = SocketIO(app)
client = docker.from_env()
CODE_DIRECTORY = 'volume'  # Directory where your code files are stored
MAIN_CONTAINER_ID = "c99ebdf3a5f9"
# Create the Groq client with API key
client = Groq(api_key="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")
CORS(app, resources={r"/*": {"origins": "https://5000-userfrom1995-codetutor-4jawtjmljtv.ws-us116.gitpod.io/"}})

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

@socketio.on('start_terminal')
def handle_start_terminal():
    """Attach to the container and start a shell session."""
    try:
        container = client.containers.get(MAIN_CONTAINER_ID)
        
        # Create a shell session inside the container (interactive terminal)
        exec_id = client.api.exec_create(container.id, 'bash', stdin=True, tty=True)
        exec_stream = client.api.exec_start(exec_id, stream=True, tty=True)

        # Stream the terminal output in a separate thread
        thread = Thread(target=stream_terminal_output, args=(exec_stream,))
        thread.start()

        emit('terminal_output', {'output': 'Started terminal session\n'})
    except Exception as e:
        emit('terminal_output', {'output': f"Error: {str(e)}\n"})

@socketio.on('input_command')
def handle_input_command(data):
    """Send user input to the container's terminal."""
    command = data.get('command', '')
    try:
        container = client.containers.get(MAIN_CONTAINER_ID)

        # Execute the command inside the running container's terminal session
        exec_id = client.api.exec_create(container.id, f'bash -c "{command}"', stdin=True, tty=True)
        exec_stream = client.api.exec_start(exec_id)
        emit('terminal_output', {'output': exec_stream.decode('utf-8')})
    except Exception as e:
        emit('terminal_output', {'output': f"Error: {str(e)}\n"})

def stream_terminal_output(exec_stream):
    """Continuously stream the terminal output from the container."""
    for output in exec_stream:
        socketio.emit('terminal_output', {'output': output.decode('utf-8')})


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


# Route to load code files based on the selected language
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

        # Check if the file exists, create it if it doesn't
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w') as file:
                    file.write("")  # Create an empty file
            except Exception as e:
                return f'Error creating file: {str(e)}', 500

        # Read the file and return its content
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return content, 200
        except Exception as e:
            return f'Error reading file: {str(e)}', 500

    return 'File not found', 404


# Route to save code from the editor to the appropriate file
@app.route('/save_code', methods=['POST'])
def save_code():
    data = request.get_json()

    # Determine which language was selected
    language = data['language']
    
    # Get the updated code from the request
    updated_code = data['code']

    # Map the language to the appropriate file
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

        # Ensure the file exists, create it if not
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w') as file:
                    file.write("")  # Create an empty file
            except Exception as e:
                return jsonify({'error': f'Error creating file: {str(e)}'}), 500

        # Write the updated code to the file
        try:
            with open(file_path, 'w') as code_file:
                code_file.write(updated_code)
            return jsonify({'message': 'Code saved successfully'}), 200
        except Exception as e:
            return jsonify({'error': f'Error writing file: {str(e)}'}), 500

    return jsonify({'error': 'Invalid language selected'}), 400


if __name__ == '__main__':
    socketio.run(app, debug=True)
    app.run(debug=True)

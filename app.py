from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Sample text content - in production this could come from a database
    sample_text = [
        "Welcome to the interactive text reader.",
        "This is a progressive text display system.",
        "You can control the speed and navigation.",
        "Try using the spacebar to pause/resume.",
        "Type 'commencer' in the command box to begin."
    ]
    return render_template('index.html', text_content=sample_text)

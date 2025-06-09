from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, DevOps World! This is my CI/CD Pipeline!"

if __name__ == '__main__':
    # Bind to 0.0.0.0 to make it accessible from outside the container
    app.run(debug=True, host='0.0.0.0', port=5000)

Chatbot Platform – Software Engineer Intern Assignment



Overview:

This project is a minimal chatbot platform built for an intern assignment. It supports user sign up/login, project creation, and chatting with an AI bot through the Gemini API.

Features:

1.Users can register, log in, and log out securely using Flask-Login and hashed passwords.
2.Every user can create one or more chatbot projects.
3.In each project, users can send prompts and receive AI responses powered by Google Gemini.
4.Routes are protected so only logged-in users can access their projects and chat.
5.Designed for easy scaling; add more features like chat history or file uploads as needed.

Architecture:

Backend: Python (Flask micro-framework)
Database: SQLite for users, projects, and prompts
Authentication: Flask-Login
AI Chat: Google Gemini API (using the free text-bison-001 model)
Frontend: HTML forms rendered by Flask

For a detailed system design and diagram, see design.pdf included in this repository.



Setup and Running:

1.Clone or Download This Repository
2.Install Required Python Packages



text:(terminal)
pip install google-generativeai flask flask-login flask-sqlalchemy



Set Your Gemini API Key:

Open app.py
Find the line:

genai.configure(api\_key="YOUR\_API\_KEY")
Replace "YOUR\_API\_KEY" with the actual API key from Google AI Studio.
Run the Application

text:(terminal)
python app.py



Access in Your Web Browser:

text:
http://127.0.0.1:5000/



Use the signup page to create a new user.
Log in, create a project, and start chatting.












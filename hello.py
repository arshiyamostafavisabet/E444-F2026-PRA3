import re
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, flash, request, jsonify
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = StringField('What is your UofT Email address?', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        if 'utoronto' in form.email.data.lower():
            session['email'] = form.email.data
            return redirect(url_for('chat_page'))
        else:
            session['email'] = None
            flash('Please enter a valid UofT email address!')
            return redirect(url_for('index'))
        
    return render_template(
        'index.html', 
        form=form, 
        name=session.get('name'), 
        email=session.get('email'),
        current_time=datetime.utcnow()
    )

@app.route('/chat_page', methods=['GET'])
def chat_page():
    if not session.get('email'):
        flash('Please log in with a valid UofT email first!')
        return redirect(url_for('index'))
    return render_template('chat.html', name=session.get('name'))

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get("message", "")
    msg_lower = message.lower()
    
    # Initialize memory dictionary in Flask session if not present
    if 'chat_memory' not in session:
        session['chat_memory'] = {}
        
    memory = session['chat_memory']

    # Memory Store Rule 1: "My name is [Name]"
    name_match = re.search(r"my name is (\w+)", msg_lower)
    if name_match:
        extracted_name = name_match.group(1).capitalize()
        memory['user_name'] = extracted_name
        session.modified = True  # Tell Flask the session dictionary was updated
        return jsonify({"reply": f"Nice to meet you, {extracted_name}!"})

    # Memory Store Rule 2: "I like [Thing]" or "My favorite [Thing] is [Value]"
    like_match = re.search(r"i like (\w+)", msg_lower)
    if like_match:
        thing = like_match.group(1)
        memory['liked_item'] = thing
        session.modified = True
        return jsonify({"reply": f"Got it! I will remember that you like {thing}."})

    # Memory Recall Rule 1: "What is my name?"
    if "what is my name" in msg_lower:
        if 'user_name' in memory:
            return jsonify({"reply": f"Your name is {memory['user_name']}."})
        elif session.get('name'):
            return jsonify({"reply": f"Your name is {session.get('name')}."})
        else:
            return jsonify({"reply": "I don't know your name yet!"})

    # Memory Recall Rule 2: "What do I like?"
    if "what do i like" in msg_lower:
        if 'liked_item' in memory:
            return jsonify({"reply": f"You told me earlier that you like {memory['liked_item']}!"})
        else:
            return jsonify({"reply": "You haven't told me what you like yet."})

    # Default Responses
    if "hello" in msg_lower or "hi" in msg_lower:
        reply = f"Hello {session.get('name', '')}!"
    else:
        reply = "I don't understand."
        
    return jsonify({"reply": reply})

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()  # Clears all session data (memory + user info)
    flash('You have been logged out and your session memory has been cleared.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
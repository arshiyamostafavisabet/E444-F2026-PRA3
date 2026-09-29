from datetime import datetime
from flask import Flask, render_template
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = StringField('What is your UofT Email address?', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        old_email = session.get('email')
        
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        if old_email is not None and old_email != form.email.data:
            flash('Looks like you have changed your email!')
            
        session['name'] = form.name.data
        
        # Check if email is a UofT address
        if 'utoronto' in form.email.data.lower():
            session['email'] = form.email.data
        else:
            session['email'] = None
            flash('Please enter a valid UofT email address!')

        return redirect(url_for('index'))
        
    return render_template('index.html', form=form, name=session.get('name'), email=session.get('email'))

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template_string, request, session, redirect, url_for
import datetime

# Create the Flask application
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=1)
app.secret_key = '848fb6eec6c8caa1b564e3a16e80305ef4586018060acab712788f9bc3098500'

@app.route('/set_email', methods=['GET', 'POST'])
def set_email():
    if request.method == 'POST':
        # Save the form data to the session object
        session['email'] = request.form['email_address']
        return redirect(url_for('get_email'))

    return """
        <form method="post">
            <label for="email">Enter your email address:</label>
            <input type="email" id="email" name="email_address" required />
            <button type="submit">Submit</button>
        </form>
    """

@app.route('/get_email')
def get_email():
    if 'email' in session:
        return render_template_string("<h1>Welcome {{ session['email'] }}!</h1>")
    else:
        return render_template_string("<h1>Welcome! Please enter your email <a href='{{ url_for('set_email') }}'>here.</a></h1>")

@app.route('/delete_email')
def delete_email():
    # Clear the email stored in the session object
    session.pop('email', default=None)
    return '<h1>Session deleted!</h1>'

if __name__ == '__main__':
    app.run()

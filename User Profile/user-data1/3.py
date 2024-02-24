from flask import *
from LoginRadius import LoginRadius as LR
from flask import Flask, redirect, url_for
from flask import Flask, redirect, url_for, request

app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRETKEY"

LR.API_KEY = "API Key"
LR.API_SECRET = "API Secret"
loginradius = LR()


@app.route("/")
def index():
    return "Hello World!"


LR_AUTH_PAGE = "https://{APP_NAME}.hub.loginradius.com/auth.aspx?action={AUTH_ACTION}&return_url={RETURN_URL}"


@app.route('/register')
def register():
    # Assuming LR_AUTH_PAGE is a string with a placeholder for formatting
    LR_AUTH_PAGE = "https://example.com/{}?return_url={}"
    return redirect(LR_AUTH_PAGE.format("register", request.host_url))


@app.route('/login')
def login():
    # Assuming LR_AUTH_PAGE is a variable representing the login/register page URL
    LR_AUTH_PAGE = "/auth/login"
    return redirect(LR_AUTH_PAGE)


if __name__ == "__main__":
    app.run(debug=True, port=809)

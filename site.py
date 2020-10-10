from flask import Flask, request, redirect, render_template

from oauth import Oauth

app = Flask(__name__)

@app.route("/", methods=["get"])
def index():
    return redirect(Oauth.discord_login_url)
@app.route("/login")
def login():
    if request.args.get("error") == "access_denied":
        return f'error access_denied'
    code = request.args.get("code")
    at = Oauth.get_access_token(code)

    user_json = Oauth.get_user_json(at)
    gj = Oauth.get_guild_json(at)
    if user_json.get('message') == '401: Unauthorized':
        return redirect(Oauth.discord_login_url)
    username, usertag = user_json.get("username"), user_json.get("discriminator")
    for gj in s:
        return '<div class="card"><img src='Oauth.get_server_avatar_url(s.get('id'))'></div>'


# RUN
if __name__  == "__main__":
    app.run(debug=True)

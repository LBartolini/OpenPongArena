from flask import Flask

app = Flask(__name__, template_folder='../templates',
			static_folder='../static')

app.debug = DEV
app.secret_key = b'(\xfe\x8b\x081\xb1\x06\x1b#O\xe4r'  # used to encrypt session

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.errorhandler(404)
def page_not_found(e):
    return "<p>Error 404 Page not Found!</p>"
    #return render_template('error404.html', title="Ops...")

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=6006)
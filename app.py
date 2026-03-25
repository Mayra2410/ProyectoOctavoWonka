from flask import Flask, render_template
from proveedores.routes import proveedores

app = Flask(__name__)

app.register_blueprint(proveedores)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)

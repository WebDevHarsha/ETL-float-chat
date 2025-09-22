from flask import Flask
from flask_cors import CORS
from routes.query_routes import query_bp
# from etl import run_etl
from config import NC_FILE

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

# Register blueprints
app.register_blueprint(query_bp)

if __name__ == "__main__":
    # run_etl(NC_FILE)  
    app.run(host="0.0.0.0", port=5001, debug=True)

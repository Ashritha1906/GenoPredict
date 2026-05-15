from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from ml_model import DiseasePredictor
from database import DatabaseManager
import os
import json

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)  # Enable CORS for frontend connection

# Initialize ML Model
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "final_genomic_dataset.csv")
predictor = DiseasePredictor(data_path=DATA_FILE)

if os.path.exists(DATA_FILE):
    print("Loading ML model with dataset...")
    predictor.load_and_prepare_data()
else:
    print(f"Warning: Dataset not found at {DATA_FILE}.")

# Load Local NCBI Dataset (JSON)
NCBI_DATA_PATH = os.path.join(os.path.dirname(__file__), "ncbi_data.json")
NCBI_DATASET = {}

if os.path.exists(NCBI_DATA_PATH):
    print(f"Loading local NCBI dataset from {NCBI_DATA_PATH}...")
    with open(NCBI_DATA_PATH, 'r') as f:
        NCBI_DATASET = json.load(f)
else:
    print(f"Warning: Local NCBI dataset not found at {NCBI_DATA_PATH}. Run generate_json.py first.")

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online", 
        "message": "Bioinformatics Disease Prediction API is running",
        "model_loaded": predictor.df is not None
    })

@app.route('/predict', methods=['POST'])
def predict_disease():
    data = request.json
    if not data or 'symptoms' not in data:
        return jsonify({"error": "Please provide 'symptoms' in the request body"}), 400
    user_input = data['symptoms']
    top_n = data.get('limit', 3)
    results = predictor.predict(user_input, top_n=top_n)
    return jsonify(results)

@app.route('/disease-details', methods=['GET'])
def disease_details():
    disease_name = request.args.get('name')
    if not disease_name:
        return jsonify({"error": "Please provide a disease 'name'"}), 400
    details = predictor.get_disease_details(disease_name)
    return jsonify(details)

@app.route('/more-details', methods=['GET'])
def more_details():
    disease_name = request.args.get('disease')
    if not disease_name:
        return jsonify({"error": "Disease name is required"}), 400

    # Clean the name for lookup (ML model often uses underscores or specific casing)
    clean_name = disease_name.replace('_', ' ').strip()
    
    # Try direct lookup
    data = NCBI_DATASET.get(clean_name)
    
    # Try case-insensitive lookup if not found
    if not data:
        for key in NCBI_DATASET:
            if key.lower() == clean_name.lower():
                data = NCBI_DATASET[key]
                break
    
    if not data:
        # Return empty arrays with structure to prevent frontend crashes
        return jsonify({
            "genes": [],
            "variants": [],
            "conditions": []
        })

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

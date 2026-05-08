from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from ml_model import DiseasePredictor
from database import DatabaseManager
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)  # Enable CORS for frontend connection

# Initialize ML Model
# Update the path to match where the combined CSV will be
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "final_genomic_dataset.csv")

predictor = DiseasePredictor(data_path=DATA_FILE)

# Attempt to load data on startup
if os.path.exists(DATA_FILE):
    print("Loading ML model with dataset...")
    predictor.load_and_prepare_data()
else:
    print(f"Warning: Dataset not found at {DATA_FILE}. Run data_processor.py first.")

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online", 
        "message": "Bioinformatics Disease Prediction API is running",
        "model_loaded": predictor.df is not None
    })

@app.route('/ui', methods=['GET'])
def ui():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_disease():
    """
    Step 3, 4, 5: Predict disease based on natural language symptoms or gene mutations
    Expects JSON: {"symptoms": "feeling tired, low hemoglobin, gene HBB"}
    """
    data = request.json
    if not data or 'symptoms' not in data:
        return jsonify({"error": "Please provide 'symptoms' in the request body"}), 400
        
    user_input = data['symptoms']
    
    # Optional limit parameter
    top_n = data.get('limit', 3)
    
    results = predictor.predict(user_input, top_n=top_n)
    return jsonify(results)

@app.route('/disease-details', methods=['GET'])
def disease_details():
    """
    Get detailed information about a specific disease.
    Query param: ?name=Thalassemia
    """
    disease_name = request.args.get('name')
    if not disease_name:
        return jsonify({"error": "Please provide a disease 'name' as a query parameter"}), 400
        
    details = predictor.get_disease_details(disease_name)
    return jsonify(details)

@app.route('/gene-search', methods=['GET'])
def gene_search():
    """
    Search for a specific gene and get associated diseases and variations.
    Query param: ?gene=BRCA1
    """
    gene_name = request.args.get('gene')
    if not gene_name:
        return jsonify({"error": "Please provide a 'gene' name as a query parameter"}), 400
        
    info = predictor.search_genes(gene_name)
    return jsonify(info)

@app.route('/admin/init-db', methods=['POST'])
def initialize_database():
    """
    Admin endpoint to set up MySQL database and import data.
    Expects JSON: {"host": "localhost", "user": "root", "password": ""}
    """
    data = request.json or {}
    host = data.get('host', 'localhost')
    user = data.get('user', 'root')
    password = data.get('password', '')
    
    if not os.path.exists(DATA_FILE):
        return jsonify({"error": f"Dataset not found at {DATA_FILE}. Cannot import."}), 404
        
    db = DatabaseManager(host=host, user=user, password=password)
    
    if not db.connect():
        return jsonify({"error": "Failed to connect to MySQL server. Check credentials."}), 500
        
    db.create_tables()
    success = db.import_csv_to_db(DATA_FILE)
    db.close()
    
    if success:
        return jsonify({"message": "Database initialized and data imported successfully!"})
    else:
        return jsonify({"error": "Failed to import data into database."}), 500

if __name__ == '__main__':
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

# Bioinformatics Disease Prediction Web Application - Backend

This backend is built using Flask, Scikit-learn, Pandas, and MySQL. It processes genetic data and uses an NLP model (TF-IDF) to predict diseases based on symptoms or gene mutations.

## Folder Structure
```
backend/
├── app.py                  # Main Flask application and API routes
├── data_processor.py       # Script to combine CSVs and add 'disease' column
├── database.py             # Database connection, table creation, and CSV import logic
├── ml_model.py             # TF-IDF NLP logic, data loading, and disease predictions
├── requirements.txt        # Python dependencies
└── README.md               # Documentation
```

## Setup Instructions

### 1. Install Dependencies
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Prepare the Data (Steps 1 & 2)
If you have individual disease CSVs, you need to combine them. 
Open `data_processor.py` and modify the paths in the `__main__` block to point to your raw data folder.
Then run:
```bash
python data_processor.py
```
This will generate `final_genomic_dataset.csv`. (If you already have `final_genomic_dataset.csv` in the root folder, you can skip this step).

### 3. Setup MySQL Database (Step 6)
Ensure your MySQL server is running (e.g., via XAMPP or local install).
Open `database.py` and verify the credentials (host='localhost', user='root', password='').
Run the script to create the database, tables, and import the CSV data:
```bash
python database.py
```
*Alternatively, you can start the Flask app and use the `/admin/init-db` POST endpoint.*

### 4. Start the Flask Backend (Steps 3, 4, 5, 7, 8)
Run the server:
```bash
python app.py
```
The server will start on `http://localhost:5000`. It will automatically load the NLP model using the `final_genomic_dataset.csv`.

## API Endpoints (Step 7)

- `GET /` : Health check.
- `POST /predict` : Predicts disease based on symptoms or mutations.
  - Body: `{"symptoms": "feeling tired, HBB gene mutation"}`
- `GET /disease-details?name=Thalassemia` : Get details, prevalence, and treatment for a specific disease.
- `GET /gene-search?gene=BRCA1` : Search for a specific gene to find associated diseases and variations.
- `POST /admin/init-db` : Initialize database and import data (requires JSON body with db credentials).

## Connecting with Frontend (Step 8)
The backend is configured with `Flask-CORS`, meaning it's ready to accept requests from your future HTML/CSS/JS frontend website on a different port.

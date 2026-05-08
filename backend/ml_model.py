import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class DiseasePredictor:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        
        # Disease Knowledge Mapping: Simplified for general users
        self.disease_info = {
            "thalassemia": {
                "causes": "Passed down from parents through genes. It makes the body produce less healthy blood (hemoglobin).",
                "prevention": "Check with a doctor before marriage. Simple blood tests for couples can help understand the risk for children."
            },
            "sickle cell disease": {
                "causes": "An inherited problem where blood cells change shape and get stuck in blood vessels, causing pain.",
                "prevention": "Couples should get screened before having children. Early check-ups help manage the condition better."
            },
            "sickle_cell": {
                "causes": "An inherited problem where blood cells change shape and get stuck in blood vessels, causing pain.",
                "prevention": "Couples should get screened before having children. Early check-ups help manage the condition better."
            },
            "glucose-6-phosphate dehydrogenase deficiency": {
                "causes": "A genetic condition where the body lacks a special chemical that protects red blood cells.",
                "prevention": "Stay away from certain foods like fava beans and some medicines. Always tell your doctor about this condition."
            },
            "g6pd": {
                "causes": "A genetic condition where the body lacks a special chemical that protects red blood cells.",
                "prevention": "Stay away from certain foods like fava beans and some medicines. Always tell your doctor about this condition."
            },
            "breast cancer": {
                "causes": "Changes in certain genes (like BRCA) that can be passed down in families.",
                "prevention": "Regular check-ups and mammograms. Eating healthy and staying active also helps reduce the risk."
            },
            "breast_cancer": {
                "causes": "Changes in certain genes (like BRCA) that can be passed down in families.",
                "prevention": "Regular check-ups and mammograms. Eating healthy and staying active also helps reduce the risk."
            },
            "parkinson's disease": {
                "causes": "Brain cells that control movement slowly stop working. It can be caused by genes or aging.",
                "prevention": "Exercise regularly and eat a balanced diet. Early visits to a brain specialist (neurologist) are helpful."
            },
            "parkinsons": {
                "causes": "Brain cells that control movement slowly stop working. It can be caused by genes or aging.",
                "prevention": "Exercise regularly and eat a balanced diet. Early visits to a brain specialist (neurologist) are helpful."
            },
            "hemophilia": {
                "causes": "A condition passed from parents where the blood doesn't clot properly after an injury.",
                "prevention": "Genetic testing for families. Be careful to avoid accidents that cause heavy bleeding."
            },
            "familial hypercholesterolemia": {
                "causes": "High cholesterol that runs in the family because of a gene problem.",
                "prevention": "Start heart-healthy habits early, like low-fat food and regular exercise. Regular blood tests are important."
            },
            "fh": {
                "causes": "High cholesterol that runs in the family because of a gene problem.",
                "prevention": "Start heart-healthy habits early, like low-fat food and regular exercise. Regular blood tests are important."
            },
            "cystic fibrosis": {
                "causes": "A gene problem passed from parents that makes the body produce thick mucus in the lungs.",
                "prevention": "Genetic testing for parents. Early treatment and special lung exercises can keep the body healthy."
            },
            "cystic_fibrosis": {
                "causes": "A gene problem passed from parents that makes the body produce thick mucus in the lungs.",
                "prevention": "Genetic testing for parents. Early treatment and special lung exercises can keep the body healthy."
            },
            "hypertrophic cardiomyopathy": {
                "causes": "A condition where the heart muscle gets too thick, often because of family genes.",
                "prevention": "Heart check-ups for family members. Avoid very heavy exercise if you have this condition."
            },
            "hcm": {
                "causes": "A condition where the heart muscle gets too thick, often because of family genes.",
                "prevention": "Heart check-ups for family members. Avoid very heavy exercise if you have this condition."
            },
            "hereditary anemia": {
                "causes": "Blood problems that are passed down from parents to children.",
                "prevention": "Good nutrition and regular check-ups with a blood doctor (hematologist)."
            },
            "hereditary_anemia": {
                "causes": "Blood problems that are passed down from parents to children.",
                "prevention": "Good nutrition and regular check-ups with a blood doctor (hematologist)."
            }
        }
        
        # Organ Mapping
        self.organ_map = {
            "thalassemia": "Blood / Bone Marrow",
            "sickle cell disease": "Blood",
            "sickle_cell": "Blood",
            "glucose-6-phosphate dehydrogenase deficiency": "Blood",
            "g6pd": "Blood",
            "breast cancer": "Breast",
            "breast_cancer": "Breast",
            "parkinson's disease": "Brain",
            "parkinsons": "Brain",
            "hemophilia": "Blood",
            "familial hypercholesterolemia": "Heart",
            "fh": "Heart",
            "cystic fibrosis": "Lungs",
            "cystic_fibrosis": "Lungs",
            "hypertrophic cardiomyopathy": "Heart",
            "hcm": "Heart",
            "hereditary anemia": "Blood",
            "hereditary_anemia": "Blood"
        }

    def load_and_prepare_data(self):
        try:
            self.df = pd.read_csv(self.data_path)
            
            # Create a combined features column for NLP matching
            # Assuming columns: gene_id, gene_name, condition, variation, protein_change, consequence, location, review_status, disease
            
            # Handle potential NaN values
            cols_to_combine = ['gene_name', 'condition', 'variation', 'protein_change', 'consequence', 'disease']
            for col in cols_to_combine:
                if col in self.df.columns:
                    self.df[col] = self.df[col].fillna('')
            
            # Create a searchable text column
            # We focus on conditions, variations, genes, and recovery/region
            self.df['search_text'] = self.df['condition'].astype(str) + " " + \
                                     self.df['variation'].astype(str) + " " + \
                                     self.df['gene_name'].astype(str) + " " + \
                                     self.df['disease'].astype(str)
            
            # Map common symptoms to search text so user inputs like "fatigue" or "fever" will match
            # Keys MUST match the unique diseases in the CSV ('breast_cancer', 'cystic_fibrosis', 'fh', 'g6pd', 'hcm', 'hemophilia', 'hereditary_anemia', 'parkinsons', 'sickle_cell', 'thalassemia')
            symptom_mapping = {
                "thalassemia": "fatigue pale skin weakness anemia tired exhaustion dizzy dizzy breathless bone deformities dark urine",
                "sickle cell disease": "pain infections fatigue swelling anemia tired crisis vision problems delayed growth frequent infections",
                "glucose-6-phosphate dehydrogenase deficiency": "jaundice fatigue pale skin dark urine tired yellowing eyes rapid heart rate shortness of breath trigger",
                "breast cancer": "lump pain breast tissue swelling redness skin changes discharge nipple inversion",
                "parkinson's disease": "tremor stiffness slow movement balance shaking rigid muscles posture changes speech writing changes",
                "hemophilia": "bleeding joint pain bruising blood nosebleeds prolonged bleeding tight joints swelling",
                "familial hypercholesterolemia": "chest pain cholesterol xanthomas heart attack fatty deposits family history high lipids angina",
                "cystic fibrosis": "cough lung infection shortness of breath wheezing salty skin poor growth greasy stools mucus",
                "hypertrophic cardiomyopathy": "shortness of breath chest pain fainting heart murmur palpitations rapid heartbeat dizziness syncope",
                "hereditary anemia": "fatigue weakness pale skin tired lethargy shortness of breath irregular heartbeats cold hands feet"
            }
            
            def add_symptoms(disease_name):
                if pd.isna(disease_name):
                    return ""
                disease_key = str(disease_name).lower().strip()
                return symptom_mapping.get(disease_key, "")
                
            self.df['symptoms'] = self.df['disease'].apply(add_symptoms)
            self.df['search_text'] = self.df['search_text'] + " " + self.df['symptoms']
            
            # Fit TF-IDF
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df['search_text'])
            print(f"Model loaded with {len(self.df)} records.")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def predict(self, user_input, top_n=3):
        if self.df is None or self.tfidf_matrix is None:
            return {"error": "Model not loaded"}

        clean_input = user_input.strip().lower()

        # Step 1: Check if user input matches gene_name column
        exact_matches = self.df[self.df['gene_name'].astype(str).str.lower() == clean_input]
        
        # Step 2: If no gene match, check variation column
        if exact_matches.empty:
            exact_matches = self.df[self.df['variation'].astype(str).str.lower() == clean_input]

        # Step 3: If gene/mutation match is found, return the results
        if not exact_matches.empty:
            results = []
            seen_diseases = set()
            for _, row in exact_matches.iterrows():
                disease_name = row.get('disease', 'Unknown')
                
                if disease_name.lower() not in seen_diseases:
                    seen_diseases.add(disease_name.lower())
                    
                    disease_key = disease_name.lower().strip()
                    match = {
                        "disease": disease_name,
                        "confidence_score": 100.0,
                        "related_genes": row.get('gene_name', 'N/A'),
                        "mutation_info": f"Variation: {row.get('variation', 'N/A')} | Protein Change: {row.get('protein_change', 'N/A')} | Consequence: {row.get('consequence', 'N/A')} | Condition: {row.get('condition', 'N/A')} | Review Status: {row.get('review_status', 'N/A')}",
                        "prevalence_in_india": row.get('region', 'Data not available'),
                        "recovery_treatment": row.get('recovery', 'Consult a healthcare professional'),
                        "affected_organ": self.organ_map.get(disease_key, "General / Multiple"),
                        "causes": self.disease_info.get(disease_key, {}).get("causes", "Information not available"),
                        "prevention": self.disease_info.get(disease_key, {}).get("prevention", "Information not available")
                    }
                    results.append(match)
                    
                    if len(results) >= top_n:
                        break
            return results

        # Step 4: Fallback to existing NLP model if no exact match is found
        # Transform user input
        user_vector = self.vectorizer.transform([user_input])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(user_vector, self.tfidf_matrix).flatten()
        
        # Get top matches (fetch more to allow filtering duplicates)
        top_indices = similarities.argsort()[-top_n*10:][::-1]
        
        results = []
        seen_diseases = set()
        
        for idx in top_indices:
            score = similarities[idx]
            if score > 0.05:  # Threshold to avoid irrelevant matches
                row = self.df.iloc[idx]
                disease_name = row.get('disease', 'Unknown')
                
                # Only add one representative result per disease to avoid duplicates
                if disease_name.lower() not in seen_diseases:
                    seen_diseases.add(disease_name.lower())
                    
                    disease_details = self.disease_info.get(disease_name.title(), {})
                    
                    disease_key = disease_name.lower().strip()
                    match = {
                        "disease": disease_name,
                        "confidence_score": round(score * 100, 2),
                        "related_genes": row.get('gene_name', 'N/A'),
                        "mutation_info": f"Variation: {row.get('variation', 'N/A')} | Protein Change: {row.get('protein_change', 'N/A')} | Consequence: {row.get('consequence', 'N/A')} | Condition: {row.get('condition', 'N/A')} | Review Status: {row.get('review_status', 'N/A')}",
                        "prevalence_in_india": row.get('region', 'Data not available'),
                        "recovery_treatment": row.get('recovery', 'Consult a healthcare professional'),
                        "affected_organ": self.organ_map.get(disease_key, "General / Multiple"),
                        "causes": self.disease_info.get(disease_key, {}).get("causes", "Information not available"),
                        "prevention": self.disease_info.get(disease_key, {}).get("prevention", "Information not available")
                    }
                    results.append(match)
                    
                    # Stop once we have top_n distinct diseases
                    if len(results) >= top_n:
                        break
                
        if not results:
            return {"message": "No strong matches found. Please try providing more specific symptoms or mutation names."}
            
        return results

    def get_disease_details(self, disease_name):
        # Return information for a specific disease
        details = self.disease_info.get(disease_name.title())
        if details:
            # Get some sample genes associated with this disease from the dataset
            if self.df is not None:
                genes = self.df[self.df['disease'].str.lower() == disease_name.lower()]['gene_name'].unique()[:5].tolist()
                details['associated_genes'] = genes
            return details
        return {"error": "Disease not found"}
        
    def search_genes(self, gene_name):
        if self.df is None:
            return {"error": "Model not loaded"}
            
        matches = self.df[self.df['gene_name'].str.lower() == gene_name.lower()]
        if not matches.empty:
            # Return summarized info
            diseases = matches['disease'].unique().tolist()
            variations = matches['variation'].unique()[:10].tolist()
            return {
                "gene": gene_name.upper(),
                "associated_diseases": diseases,
                "common_variations": variations
            }
        return {"error": "Gene not found"}

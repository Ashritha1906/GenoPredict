import os
import glob
import pandas as pd

# Step 1 & 2: Combine CSVs and add 'disease' column
def combine_csv_datasets(data_folder, output_file="final_genomic_dataset.csv"):
    """
    Reads all CSV files from the given folder, extracts disease name from file name,
    and combines them into one final CSV.
    """
    csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {data_folder}")
        return None

    combined_df = pd.DataFrame()
    
    for file_path in csv_files:
        # Avoid reading an already combined file if it exists in the same folder
        if "final_genomic_dataset" in file_path:
            continue
            
        try:
            df = pd.read_csv(file_path)
            
            # Extract disease name from file name (e.g., "Thalassemia.csv" -> "Thalassemia")
            file_name = os.path.basename(file_path)
            raw_disease_name = os.path.splitext(file_name)[0].lower()
            
            # Map of known short forms to full forms
            mapping = {
                'fh': 'Familial Hypercholesterolemia',
                'g6pd': 'Glucose-6-Phosphate Dehydrogenase Deficiency',
                'hcm': 'Hypertrophic Cardiomyopathy',
                'breast_cancer': 'Breast Cancer',
                'cystic_fibrosis': 'Cystic Fibrosis',
                'hemophilia': 'Hemophilia',
                'hereditary_anemia': 'Hereditary Anemia',
                'parkinsons': "Parkinson's Disease",
                'sickle_cell': 'Sickle Cell Disease',
                'thalassemia': 'Thalassemia'
            }
            
            disease_name = mapping.get(raw_disease_name, raw_disease_name.replace("_", " ").title())
            
            # Add disease column
            df['disease'] = disease_name
            
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            print(f"Processed: {file_name} -> Disease: {disease_name}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    if not combined_df.empty:
        # Save to final dataset
        combined_df.to_csv(output_file, index=False)
        print(f"\\nSuccessfully combined {len(csv_files)} files into {output_file}!")
        print(f"Total records: {len(combined_df)}")
        return output_file
    else:
        print("No data could be combined.")
        return None

if __name__ == "__main__":
    # Example usage: assuming raw CSVs are in a folder named 'raw_data'
    # Adjust path as necessary.
    combine_csv_datasets("../raw_data", "../final_genomic_dataset.csv")

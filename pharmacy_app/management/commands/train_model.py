from django.core.management.base import BaseCommand
import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from pharmacy_app.models import Medicine

def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9 ]', '', text).strip().lower()

class Command(BaseCommand):
    help = "Train the medicine recommendation AI model"

    def handle(self, *args, **kwargs):
        self.stdout.write("🔄 Training AI model...")

        # Fetch medicine data from the database
        medicines = Medicine.objects.values_list("medicine_name", "short_composition1", "short_composition2")
        
        medicine_data = []
        compositions = []
        
        for med in medicines:
            name, comp1, comp2 = med
            comp1 = clean_text(comp1)
            comp2 = clean_text(comp2) if comp2 else ""
            
            # Store medicine details
            medicine_data.append({"medicine_name": name, "short_composition1": comp1, "short_composition2": comp2})
            
            # Use only the first composition if the second composition exists
            composition_text = comp1 if comp2 else f"{comp1} {comp2}".strip()
            compositions.append(composition_text)
        
        # Train TF-IDF model
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(compositions)
        
        # Save trained models
        joblib.dump(vectorizer, "vectorizer.pkl")
        joblib.dump(tfidf_matrix, "tfidf_matrix.pkl")
        joblib.dump(medicine_data, "medicine_data.pkl")
        
        self.stdout.write(self.style.SUCCESS("✅ AI model trained and saved successfully!"))

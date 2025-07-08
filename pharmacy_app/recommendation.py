import joblib
import re

# Clean the input text by removing unwanted characters and normalizing the text
def clean_text(text):
    """Cleans and normalizes the text but keeps numbers."""
    return re.sub(r'[^a-zA-Z0-9+ ]', '', text).strip().lower()

# Load trained model and data
try:
    medicine_data = joblib.load("medicine_data.pkl")
    print("Model and data loaded successfully!")
except Exception as e:
    print(f"Error loading model or data: {e}")
    
def recommend_medicines(test_medicine):
    """Returns alternative medicines based on the same active ingredients."""

    # Normalize input name
    test_medicine = clean_text(test_medicine)
    print(f"🔍 Searching for: {test_medicine}")

    # 🔍 Find medicine by partial matching
    matched_medicine = next(
        (med for med in medicine_data if test_medicine in clean_text(med["medicine_name"])),
        None
    )

    if not matched_medicine:
        print("⚠️ Medicine not found in database.")
        return []

    # Normalize the composition
    comp1 = matched_medicine.get("short_composition1", "").strip()
    comp2 = matched_medicine.get("short_composition2", "").strip()
    target_composition = " + ".join(filter(None, [comp1, comp2]))  # Join only non-empty values
    print(f"🧪 Found Composition: {target_composition}")

    # **Find Alternative Medicines**
    alternative_medicines = [
        med for med in medicine_data
        if " + ".join(filter(None, [med.get("short_composition1", ""), med.get("short_composition2", "")])) == target_composition
        and clean_text(med["medicine_name"]) != test_medicine
    ]

    recommendations = [
        {"name": med["medicine_name"], "composition": target_composition, "similarity": 100}
        for med in alternative_medicines
    ]

    print(f"✅ Alternative Medicines Found: {recommendations}")
    return recommendations

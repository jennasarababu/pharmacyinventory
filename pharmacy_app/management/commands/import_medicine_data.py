import csv
from django.core.management.base import BaseCommand
from pharmacy_app.models import Medicine

class Command(BaseCommand):
    help = "Import medicine data from CSV"

    def handle(self, *args, **kwargs):
        file_path = "final_cleaned_medicine_inventory.csv"  # Update with actual file path
        batch_size = 10000  # Adjust based on performance
        medicines = []

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                medicines.append(
                    Medicine(
                        medicine_name=row["Name"],
                        short_composition1=row["short_composition1"],
                        short_composition2=row.get("short_composition2", ""),
                        price=row.get(" Unit Price", None),
                    )
                )
                if len(medicines) >= batch_size:
                    Medicine.objects.bulk_create(medicines)
                    medicines = []  # Reset list

            if medicines:  # Insert remaining data
                Medicine.objects.bulk_create(medicines)

        self.stdout.write(self.style.SUCCESS("Medicine data imported successfully!"))

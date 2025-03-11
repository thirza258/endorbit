import os
import pandas as pd
from aihandler.models import Product
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Import recipe data from a CSV file"

    def handle(self, *args, **kwargs):
        # Get the absolute path of the script
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Correct path to the CSV file
        file_path = os.path.join(base_dir, "data", "dataset.csv")

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        dataset = pd.read_csv(file_path) 

        for _, row in dataset.iterrows():
            Product.objects.create(
                product_url=row["product_url"],
                product_name=row["product_name"],
                retail_price=row["retail_price"],
                image=None,
                description=row["description"],
                product_rating=None,
                brand=row["brand"]
            )
            
        self.stdout.write(self.style.SUCCESS("Data inserted successfully!"))
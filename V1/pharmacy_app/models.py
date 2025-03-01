from django.db import models
from django.utils import timezone
import uuid

class Supplier(models.Model):
    """Model for pharmaceutical suppliers"""
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
        
class Purchase(models.Model):
    """Main model for pharmacy purchases"""
    
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)
    purchase_date = models.DateField(default=timezone.now)
    
    # Product details
    hsn = models.CharField(max_length=20, help_text="Harmonized System Nomenclature code")
    name = models.CharField(max_length=200)
    batch = models.CharField(max_length=50)
    expiry = models.DateField()
    
    # Quantity and pricing
    quantity = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit in ₹")
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Discount percentage")
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="GST percentage")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total amount in ₹")
    
    # Status and relations
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchases')
    
    # Metadata
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='purchases_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-purchase_date', 'name']
        
    def __str__(self):
        return f"{self.name} - {self.batch}"
    
    def save(self, *args, **kwargs):
        # Calculate amount if not provided
        if not self.amount:
            base_amount = self.quantity * self.rate
            discount_amount = base_amount * (self.discount / 100)
            subtotal = base_amount - discount_amount
            gst_amount = subtotal * (self.gst / 100)
            self.amount = subtotal + gst_amount
            
        # Update status based on expiry date
        today = timezone.now().date()
        days_to_expiry = (self.expiry - today).days
        
        
            
        super().save(*args, **kwargs)

class PurchaseDocument(models.Model):
    """Model for storing documents related to purchases"""
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=[
        ('Invoice', 'Invoice'),
        ('Delivery Note', 'Delivery Note'),
        ('Quality Certificate', 'Quality Certificate'),
        ('Other', 'Other')
    ])
    file = models.FileField(upload_to='purchase_documents/')
    notes = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.document_type} for {self.purchase}"
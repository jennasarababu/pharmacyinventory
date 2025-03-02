from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
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
    invoice_number = models.CharField(max_length=50, unique=True)
    purchase_date = models.DateField(default=timezone.now)
    product_name = models.CharField(max_length=200)
    batch = models.CharField(max_length=50)
    expiry = models.DateField()
    quantity = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit in ₹")
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Discount percentage")
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="GST percentage")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total amount in ₹")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchases')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='purchases_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-purchase_date', 'product_name']

    def __str__(self):
        return f"{self.product_name} - {self.batch}"

    def save(self, *args, **kwargs):
        if not self.amount:
            base_amount = self.quantity * self.rate
            discount_amount = base_amount * (self.discount / 100)
            subtotal = base_amount - discount_amount
            gst_amount = subtotal * (self.gst / 100)
            self.amount = subtotal + gst_amount
        super().save(*args, **kwargs)

class Billing(models.Model):
    """Model for managing billing transactions"""
    bill_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    billing_date = models.DateTimeField(default=timezone.now)
    items = models.ManyToManyField(Purchase, related_name='bills')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Discount on total bill")
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="GST on total bill")
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    payment_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Cancelled', 'Cancelled')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bill {self.bill_id} - {self.customer_name}"

    def save(self, *args, **kwargs):
        subtotal = sum(item.amount for item in self.items.all())
        discount_amount = subtotal * (self.discount / 100)
        subtotal_after_discount = subtotal - discount_amount
        gst_amount = subtotal_after_discount * (self.gst / 100)
        self.final_amount = subtotal_after_discount + gst_amount
        super().save(*args, **kwargs)

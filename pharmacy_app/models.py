from django.db import models

from django.utils import timezone

class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="Supplier Name")
    gst_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Supplier GST")
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contact Person")
    contact_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Contact Number")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"


class Invoice(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('cash', 'Cash'),
        ('credit', 'Credit'),
        ('bank-transfer', 'Bank Transfer'),
        ('check', 'Check'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('partial', 'Partial'),
    ]
    
    BILL_STATUS_CHOICES = [
        ('draft', 'DRAFT'),
        ('paid', 'PAID'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Invoice No.")
    invoice_date = models.DateField(default=timezone.now, verbose_name="Invoice Date")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='invoices')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    additional_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='cash')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    bill_status = models.CharField(max_length=20, choices=BILL_STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_number

    class Meta:
        ordering = ['-invoice_date']
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=200)
    batch = models.CharField(max_length=50, blank=True, null=True)
    expiry = models.DateField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} ({self.invoice.invoice_number})"

    class Meta:
        verbose_name = "Invoice Item"
        verbose_name_plural = "Invoice Items"
        
    def save(self, *args, **kwargs):
        # Calculate amount if not already set
        if not self.amount:
            subtotal = self.quantity * self.rate
            discount_amount = (subtotal * self.discount_percentage) / 100
            after_discount = subtotal - discount_amount
            tax_amount = (after_discount * self.tax_percentage) / 100
            self.amount = after_discount + tax_amount
            
        super().save(*args, **kwargs)

from django.contrib.auth.models import User  # Import the User model

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Medicine_supplier(models.Model):
    supplier = models.CharField(max_length=50)
    InvoiceNo = models.CharField(max_length=50)
    InvoiceDate = models.DateField()
    SupplierGST = models.CharField(max_length=50)
    Address = models.CharField(max_length=50)
    ContactPerson = models.CharField(max_length=50)
    ContactNumber = models.PositiveIntegerField()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medicine_suppliers")  # <-- CHANGED related_name
    hsn = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    batch = models.CharField(max_length=50)
    expiry = models.DateField()
    quantity = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=5, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.batch})"

class Purchase(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Expiring Soon', 'Expiring Soon'),
        ('Expired', 'Expired'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchase_records")  # <-- CHANGED related_name
    hsn = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    batch = models.CharField(max_length=50)
    expiry = models.DateField()
    quantity = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=5, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.batch})"
    

class Inventory(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]

    inventory_id = models.BigAutoField(primary_key=True)
    hsn = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    batch = models.CharField(max_length=50)
    expiry_date = models.DateField()
    stock = models.PositiveIntegerField()
    threshold = models.PositiveIntegerField()
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.name} - {self.batch}"

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventories"

class BillDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bill_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Bill {self.bill_number} - {self.total_amount}"

class BillDetailItems(models.Model):
    bill = models.ForeignKey(BillDetails, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.quantity} x {self.price}"
    
class Medicine(models.Model):
    medicine_name = models.CharField(max_length=255)
    short_composition1 = models.TextField()
    short_composition2 = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.medicine_name
from django.db import models
from django.contrib.auth.models import User

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent to Supplier'),
        ('received', 'Received'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order #{self.id} - {self.get_status_display()}"

class PurchaseOrderItem(models.Model):
    order = models.ForeignKey(PurchaseOrder, related_name="items", on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=100)
    batch = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    supplier_email = models.EmailField()

    def __str__(self):
        return f"{self.medicine_name} ({self.batch}) - {self.quantity}"



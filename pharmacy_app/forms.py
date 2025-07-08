from django import forms
from .models import Supplier, Invoice, InvoiceItem

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'gst_number', 'address', 'contact_person', 'contact_number']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make name required
        self.fields['name'].required = True
        
        # Add placeholders to match HTML
        self.fields['name'].widget.attrs.update({
            'placeholder': 'Enter supplier name',
            'id': 'supplier-name'
        })
        self.fields['gst_number'].widget.attrs.update({
            'placeholder': 'Enter GST number',
            'id': 'supplier-gst'
        })
        self.fields['address'].widget.attrs.update({
            'placeholder': 'Enter supplier address',
            'id': 'supplier-address',
            'rows': 2
        })
        self.fields['contact_person'].widget.attrs.update({
            'placeholder': 'Enter contact person',
            'id': 'contact-person'
        })
        self.fields['contact_number'].widget.attrs.update({
            'placeholder': 'Enter contact number',
            'id': 'contact-number'
        })


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'invoice_date', 'payment_type', 
            'payment_status', 'bill_status', 'notes',
            'subtotal', 'tax_total', 'additional_discount',
            'shipping', 'grand_total'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Required fields
        self.fields['invoice_number'].required = True
        self.fields['invoice_date'].required = True
        
        # Add placeholders to match HTML
        self.fields['invoice_number'].widget.attrs.update({
            'id': 'invoice-no',
            'placeholder': 'Enter invoice number'
        })
        self.fields['invoice_date'].widget.attrs.update({
            'id': 'invoice-date'
        })
        self.fields['payment_type'].widget.attrs.update({
            'id': 'payment-type'
        })
        self.fields['payment_status'].widget.attrs.update({
            'id': 'payment-status'
        })
        self.fields['notes'].widget.attrs.update({
            'id': 'notes',
            'rows': 3,
            'placeholder': 'Additional notes or terms'
        })
        self.fields['additional_discount'].widget.attrs.update({
            'id': 'additional-discount',
            'min': 0
        })
        self.fields['shipping'].widget.attrs.update({
            'id': 'shipping',
            'min': 0,
            'step': 0.01
        })


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = [
            'item_name', 'batch', 'expiry', 'quantity',
            'rate', 'discount_percentage', 'tax_percentage', 'amount'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # All fields from InvoiceItem model
        self.fields['item_name'].widget.attrs.update({
            'class': 'item-name',
            'placeholder': 'Search item...'
        })
        self.fields['batch'].widget.attrs.update({
            'class': 'batch',
            'placeholder': 'Batch'
        })
        self.fields['expiry'].widget.attrs.update({
            'class': 'expiry'
        })
        self.fields['quantity'].widget.attrs.update({
            'class': 'qty',
            'min': 1,
            'value': 1
        })
        self.fields['rate'].widget.attrs.update({
            'class': 'rate',
            'min': 0,
            'step': 0.01,
            'value': 0.00
        })
        self.fields['discount_percentage'].widget.attrs.update({
            'class': 'discount',
            'min': 0,
            'max': 100,
            'value': 0
        })
        self.fields['tax_percentage'].widget.attrs.update({
            'class': 'tax',
            'min': 0,
            'max': 100,
            'value': 0
        })
        self.fields['amount'].widget.attrs.update({
            'class': 'amount',
            'readonly': True,
            'value': 0.00
        })


# Formset for handling multiple invoice items
InvoiceItemFormSet = forms.inlineformset_factory(
    Invoice, 
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
    can_delete=True
)
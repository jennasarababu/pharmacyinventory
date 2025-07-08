import os
from django.core.mail import EmailMessage
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_invoice_pdf(order):
    filename = f"invoice_order_{order.id}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, filename)

    c = canvas.Canvas(filepath, pagesize=letter)
    c.drawString(100, 750, f"Invoice for Order #{order.id}")
    c.drawString(100, 730, f"Date: {order.created_at.strftime('%Y-%m-%d')}")
    
    y_position = 700
    for item in order.items.all():
        c.drawString(100, y_position, f"{item.medicine_name} - Batch {item.batch} - Qty: {item.quantity}")
        y_position -= 20

    c.save()
    return filepath

def send_order_email(order, pdf_path):
    subject = f"Order #{order.id} - Invoice"
    message = "Please find the attached invoice for your order."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [item.supplier_email for item in order.items.all()]

    email = EmailMessage(subject, message, email_from, recipient_list)
    email.attach_file(pdf_path)
    email.send()

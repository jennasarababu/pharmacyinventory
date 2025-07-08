from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q, Sum, Avg, Max  # Import Q for complex queries, Sum for aggregation, Avg for average calculation, and Max for aggregation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from torch import cosine_similarity
from .models import Medicine_supplier, Supplier, Invoice, InvoiceItem, Purchase, Inventory, BillDetails, BillDetailItems
from .forms import SupplierForm, InvoiceForm, InvoiceItemFormSet
import json
import logging
import datetime
from pharmacy_app.models import Purchase, Supplier, Inventory, BillDetailItems

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    total_stock = Inventory.objects.aggregate(total_stock=Sum('stock'))['total_stock'] or 0
    total_sales = BillDetailItems.objects.aggregate(total_sales=Sum('total'))['total_sales'] or 0
    total_purchase_amount = Purchase.objects.aggregate(total_purchase=Sum('amount'))['total_purchase'] or 0
    context = {
        'total_stock': total_stock,
        'total_sales': total_sales,
        'total_purchase_amount': total_purchase_amount,
    }
    return render(request, 'dashboard.html', context)

def purchase(request):
    return render(request, 'purchase.html')

def sales(request):
    return render(request, 'sales.html')
    

def reports(request):
    return render(request, 'reports.html')

def inventory(request):
    return render(request, 'inventory.html')

def purchase_report(request):
    return render(request, 'purchase_report.html')

def new_purchase(request):
    return render(request, 'new_purchase.html')

def billing_view(request):
    return render(request, 'billing.html')

def customer_bill(request):
    return render(request, 'customer_bill.html')
# In views.py
def recommendation_page(request):
    return render(request, 'recommendation_page.html')  # Or whatever your template path is
@login_required

def purchase_history(request):
    suppliers = list(Medicine_supplier.objects.all().values())  # Fetch all supplier records
    return render(request, "purchase_history.html", {"suppliers": suppliers})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'signup.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('dashboard')
    
    return render(request, 'signup.html')


@login_required
def add_purchase(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            logging.info(f"Received data: {data}")
            purchase = Purchase.objects.create(
                user=request.user,
                hsn=data['hsn'],
                name=data['name'],
                batch=data['batch'],
                expiry=data['expiry'],
                quantity=data['quantity'],
                rate=data['rate'],
                discount=data['discount'],
                gst=data['gst'],
                amount=data['amount'],
                supplier=data['supplier']
            )

            inventory, created = Inventory.objects.get_or_create(
                batch=data['batch'],
                name=data['name'],
                defaults={
                    'hsn': data['hsn'],
                    'expiry_date': data['expiry'],
                    'stock': data['quantity'],
                    'threshold': 10,
                    'mrp': data['rate'],
                    'status': 'active'
                }
            )

            if not created:
                inventory.stock += data['quantity']
                inventory.save()


            return JsonResponse({"message": "Purchase added successfully!"}, status=201)

        except Exception as e:
            logging.info("This is an info message")
            logging.error("An error occurred", exc_info=True)
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_inventory(request):
    inventory_items = list(Inventory.objects.values())
    return JsonResponse({'inventory': inventory_items}, safe=False)

@login_required
def get_purchases(request):
    purchases = list(Purchase.objects.filter(user=request.user).values())
    return JsonResponse({"purchases": purchases}, safe=False)
@csrf_exempt
@login_required
def add_supplier(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            medicine_supplier = Medicine_supplier.objects.create(
                supplier=data['Supplier'],
                InvoiceNo=data['InvoiceNo'],
                InvoiceDate=data['InvoiceDate'],
                SupplierGST=data['SupplierGST'],
                Address=data['Address'],
                ContactPerson=data['ContactPerson'],
                ContactNumber=data['ContactNumber'],
                user=request.user,
                hsn=data['hsn'],
                name=data['name'],
                batch=data['batch'],
                expiry=data['expiry'],
                quantity=data['quantity'],
                rate=data['rate'],
                discount=data.get('discount', 0),
                gst=data['gst'],
                amount=data['amount']
            )

            return JsonResponse({"message": "Supplier and purchase saved successfully!", "id": medicine_supplier.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def invoice_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            supplier_name = data.get('supplierName')
            invoice_number = data.get('invoiceNumber')

            if not supplier_name or not invoice_number:
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            supplier, created = Supplier.objects.get_or_create(name=supplier_name)
            invoice = Invoice.objects.create(invoice_number=invoice_number, supplier=supplier)

            return JsonResponse({'success': True, 'invoice_id': invoice.id})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        item_formset = InvoiceItemFormSet(request.POST, prefix='items')
        
        if supplier_form.is_valid() and invoice_form.is_valid() and item_formset.is_valid():
            try:
                with transaction.atomic():
                    supplier = supplier_form.save()
                    invoice = invoice_form.save(commit=False)
                    invoice.supplier = supplier
                    invoice.save()
                    
                    items = item_formset.save(commit=False)
                    for item in items:
                        item.invoice = invoice
                        item.save()
                    
                    messages.success(request, 'Invoice saved successfully!')
                    return redirect('invoice_detail', pk=invoice.pk)
            except Exception as e:
                messages.error(request, f'Error saving invoice: {str(e)}')
                
    else:
        supplier_form = SupplierForm(prefix='supplier')
        invoice_form = InvoiceForm(prefix='invoice', initial={
            'invoice_number': f'INV-{datetime.datetime.now().strftime("%y%m%d%H%M%S")}',
            'invoice_date': datetime.date.today(),
        })
        item_formset = InvoiceItemFormSet(prefix='items')
    
    products = [
        {'name': 'Paracetamol 500mg', 'rate': 10.50, 'tax': 5},
        {'name': 'Amoxicillin 250mg', 'rate': 15.75, 'tax': 5},
        {'name': 'Cough Syrup 100ml', 'rate': 85.00, 'tax': 12},
        {'name': 'Vitamin C 500mg', 'rate': 120.00, 'tax': 5},
        {'name': 'Ibuprofen 400mg', 'rate': 12.50, 'tax': 5},
        {'name': 'Bandage Roll', 'rate': 35.00, 'tax': 18},
        {'name': 'Thermometer Digital', 'rate': 250.00, 'tax': 18},
        {'name': 'Hand Sanitizer 500ml', 'rate': 150.00, 'tax': 18}
    ]
    
    context = {
        'supplier_form': supplier_form,
        'invoice_form': invoice_form,
        'item_formset': item_formset,
        'products_json': json.dumps(products),
    }
    
    return render(request, 'billing.html', context)

def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    context = {
        'invoice': invoice,
        'items': invoice.items.all(),
    }
    return render(request, 'invoice_detail.html', context)

def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-created_at')
    context = {
        'invoices': invoices,
    }
    return render(request, 'invoice_list.html', context)

@require_POST
def fetch_supplier(request):
    supplier_name = request.POST.get('name')
    
    try:
        supplier = Supplier.objects.get(name__iexact=supplier_name)
        data = {
            'success': True,
            'id': supplier.id,
            'name': supplier.name,
            'gst_number': supplier.gst_number or '',
            'address': supplier.address or '',
            'contact_person': supplier.contact_person or '',
            'contact_number': supplier.contact_number or '',
        }
    except Supplier.DoesNotExist:
        data = {'success': False, 'message': 'Supplier not found'}
    except Exception as e:
        data = {'success': False, 'message': str(e)}
        
    return JsonResponse(data)

@require_POST
def product_search(request):
    query = request.POST.get('query', '')
    
    products = [
        {'name': 'Paracetamol 500mg', 'rate': 10.50, 'tax': 5},
        {'name': 'Amoxicillin 250mg', 'rate': 15.75, 'tax': 5},
        {'name': 'Cough Syrup 100ml', 'rate': 85.00, 'tax': 12},
        {'name': 'Vitamin C 500mg', 'rate': 120.00, 'tax': 5},
        {'name': 'Ibuprofen 400mg', 'rate': 12.50, 'tax': 5},
        {'name': 'Bandage Roll', 'rate': 35.00, 'tax': 18},
        {'name': 'Thermometer Digital', 'rate': 250.00, 'tax': 18},
        {'name': 'Hand Sanitizer 500ml', 'rate': 150.00, 'tax': 18}
    ]
    
    filtered_products = [p for p in products if query.lower() in p['name'].lower()]
    
    return JsonResponse({'products': filtered_products})

@require_POST
def search_inventory(request):
    data = json.loads(request.body)
    query = data.get('query', '').strip()

    if query:
        results = Inventory.objects.filter(
            Q(name__icontains=query)
        ).values('inventory_id', 'name', 'batch', 'stock', 'mrp')
        return JsonResponse({'results': list(results)}, safe=False)
    return JsonResponse({'results': []}, safe=False)

@csrf_exempt
@require_POST
def finalize_bill(request):
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        total_amount = 0

        # Create a new bill
        bill = BillDetails.objects.create(
            user=request.user,
            bill_number=f"BILL-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            total_amount=0  # Placeholder, will update later
        )

        # Add items to the bill and update inventory
        for item in items:
            inventory = Inventory.objects.get(inventory_id=item['id'])
            if inventory.stock < item['quantity']:
                return JsonResponse({'error': f"Insufficient stock for {inventory.name} (Batch: {inventory.batch})"}, status=400)
            inventory.stock -= item['quantity']
            inventory.save()

            item_total = item['quantity'] * inventory.mrp
            total_amount += item_total

            BillDetailItems.objects.create(
                bill=bill,
                name=inventory.name,
                quantity=item['quantity'],
                price=inventory.mrp,
                total=item_total
            )

        # Update the total amount in the bill
        bill.total_amount = total_amount
        bill.save()

        return JsonResponse({'message': 'Bill finalized and stock updated successfully!', 'bill_id': bill.id}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def download_bill(request):
    try:
        bill_id = request.GET.get('bill_id')
        bill = get_object_or_404(BillDetails, id=bill_id)
        items = bill.items.all()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="bill_summary.pdf"'

        # Create the PDF
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "MediPharm Billing Summary")
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 70, f"Date: {bill.created_at.strftime('%Y-%m-%d')}")
        p.drawString(50, height - 90, f"Bill ID: {bill.bill_number}")
        p.drawString(50, height - 110, f"Customer: {bill.user.username}")

        # Table Header
        p.setFont("Helvetica-Bold", 12)
        y = height - 150
        p.drawString(50, y, "Name")
        p.drawString(200, y, "Quantity")
        p.drawString(300, y, "Price")
        p.drawString(400, y, "Total")
        p.line(50, y - 5, 500, y - 5)

        # Table Rows
        p.setFont("Helvetica", 12)
        y -= 30
        for item in items:
            p.drawString(50, y, item.name)
            p.drawString(200, y, str(item.quantity))
            p.drawString(300, y, f"₹{item.price:.2f}")
            p.drawString(400, y, f"₹{item.total:.2f}")
            y -= 20
            if y < 50:  # Add a new page if space is insufficient
                p.showPage()
                p.setFont("Helvetica", 12)
                y = height - 50

        # Grand Total
        p.setFont("Helvetica-Bold", 12)
        p.drawString(300, y - 20, "Grand Total:")
        p.drawString(400, y - 20, f"₹{bill.total_amount:.2f}")

        # Footer
        p.setFont("Helvetica", 10)
        p.drawString(50, 30, "Thank you for shopping with MediPharm!")

        p.save()
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def sales_report(request):
    total_sales = BillDetailItems.objects.aggregate(total=Sum('total'))['total'] or 0
    total_orders = Purchase.objects.count()  # Count the number of rows in the Purchase table
    total_bill_orders = BillDetailItems.objects.count()  # Count the number of rows in the BillDetailItems table
    average_order_value = Purchase.objects.aggregate(avg_amount=Avg('amount'))['avg_amount'] or 0  # Calculate average amount

    # Find the best-selling item
    best_selling_item = (
        BillDetailItems.objects.values('name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')
        .first()
    )
    best_selling_item_name = best_selling_item['name'] if best_selling_item else "N/A"
    best_selling_item_quantity = best_selling_item['total_quantity'] if best_selling_item else 0

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_bill_orders': total_bill_orders,  # Add this to the context
        'average_order_value': round(average_order_value, 2),  # Round to 2 decimal places
        'best_selling_item_name': best_selling_item_name,
        'best_selling_item_quantity': best_selling_item_quantity,
    }
    return render(request, 'reports.html', context)


from django.shortcuts import render
from django.http import JsonResponse
import json

from django.shortcuts import render
from django.http import JsonResponse
from pharmacy_app.recommendation import medicine_data

def recommendation_page(request):
    return render(request, "recommendation_page.html")

def get_recommendations(request):
    medicine_name = request.GET.get("medicine_name", "").strip().lower()
    
    if not medicine_name:
        return JsonResponse({"error": "Medicine name is required"}, status=400)

    # Find the matched medicine
    matched_medicine = next(
        (med for med in medicine_data if medicine_name in med["medicine_name"].lower()),
        None
    )

    if not matched_medicine:
        return JsonResponse({"results": []})  # No match found

    # Find alternatives with the same composition
    target_composition = {matched_medicine["short_composition1"].strip(), matched_medicine.get("short_composition2", "").strip()}
    alternative_medicines = [
        {"name": med["medicine_name"]}
        for med in medicine_data
        if {med.get("short_composition1", "").strip(), med.get("short_composition2", "").strip()} == target_composition
        and med["medicine_name"] != matched_medicine["medicine_name"]
    ]

    return JsonResponse({"results": alternative_medicines})


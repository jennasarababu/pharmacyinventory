from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

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
def dashboard(request):
    return render(request, 'dashboard.html')
def purchase(request):
    return render(request, 'purchase.html')
def sales(request):
    return render(request, 'sales.html')
def report(request):
    return render(request, 'reports.html')
def inventory(request):
    return render(request, 'inventory.html')
def purchase_report(request):
    return render(request, 'purchase_report.html')
def new_purchase(request):
    return render(request, 'new_purchase.html')
from django.shortcuts import render

def billing_view(request):
    return render(request, 'billing.html')
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.core.paginator import Paginator
# from django.db.models import Q
# from .models import PurchaseRecord, Supplier
# from .forms import PurchaseRecordForm

# def purchase(request):
#     # Initialize variables
#     form = None
#     purchases = PurchaseRecord.objects.all().order_by('-created_at')
#     search_query = request.GET.get('search', '')
    
#     # Handle search
#     if search_query:
#         purchases = purchases.filter(
#             Q(name__icontains=search_query) | 
#             Q(batch__icontains=search_query) | 
#             Q(hsn__icontains=search_query) |
#             Q(supplier__name__icontains=search_query)
#         )
    
#     # CREATE operation
#     if request.method == 'POST' and 'create' in request.POST:
#         form = PurchaseRecordForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Purchase record created successfully!')
#             return redirect('purchase')
    
#     # UPDATE operation
#     elif request.method == 'POST' and 'update' in request.POST:
#         purchase_id = request.POST.get('purchase_id')
#         purchase_obj = get_object_or_404(PurchaseRecord, id=purchase_id)
#         form = PurchaseRecordForm(request.POST, instance=purchase_obj)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Purchase record updated successfully!')
#             return redirect('purchase')
    
#     # DELETE operation
#     elif request.method == 'POST' and 'delete' in request.POST:
#         purchase_id = request.POST.get('purchase_id')
#         purchase_obj = get_object_or_404(PurchaseRecord, id=purchase_id)
#         purchase_obj.delete()
#         messages.success(request, 'Purchase record deleted successfully!')
#         return redirect('purchase')
    
#     # EDIT operation (get form for editing)
#     elif 'edit' in request.GET:
#         purchase_id = request.GET.get('edit')
#         purchase_obj = get_object_or_404(PurchaseRecord, id=purchase_id)
#         form = PurchaseRecordForm(instance=purchase_obj)
#         # Pass the ID for the update operation
#         edit_id = purchase_id
#     else:
#         # For CREATE operation (empty form)
#         form = PurchaseRecordForm()
#         edit_id = None
    
#     # Pagination
#     paginator = Paginator(purchases, 8)  # Show 8 purchases per page
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     # Context data for the template
#     context = {
#         'form': form,
#         'purchases': page_obj,
#         'suppliers': Supplier.objects.all(),
#         'search_query': search_query,
#         'edit_id': edit_id
#     }
    
#     return render(request, 'purchase.html', context)


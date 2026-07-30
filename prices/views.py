import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from .models import Product
from .forms import ProductForm, UserEmailForm
from .forms import ProductForm, EmployeeCreationForm

# ----- Public Home -----
def home(request):
    products = Product.objects.all()
    products = products.order_by('?')
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    context = {
        'products': products,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'home.html', context)

# ----- Login (email only) -----
def login_view(request):
    if request.user.is_authenticated:
        return redirect('prices:dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:
            # Authenticate using username=email (since we set username=email)
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('prices:dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('prices:home')

# ----- Dashboard -----
@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('prices:staff_dashboard')
    else:
        return redirect('prices:employee_dashboard')

# ----- Employee Dashboard -----
@login_required
def employee_dashboard(request):
    if request.user.is_staff:
        return redirect('prices:staff_dashboard')
    products = Product.objects.all().order_by('name')
    return render(request, 'employee_dashboard.html', {'products': products})

# ----- Staff Dashboard -----
@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('prices:employee_dashboard')
    products = Product.objects.all().order_by('name')
    employees = User.objects.filter(is_staff=False, is_superuser=False).order_by('email')
    return render(request, 'staff_dashboard.html', {
        'products': products,
        'employees': employees,
    })

# ----- Product CRUD -----
@login_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added.')
        else:
            messages.error(request, 'Invalid data.')
    return redirect('prices:dashboard')

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated.')
        else:
            messages.error(request, 'Invalid data.')
    return redirect('prices:dashboard')

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted.')
    return redirect('prices:dashboard')

# ----- Export CSV -----
@login_required
def export_csv(request):
    products = Product.objects.all().order_by('name')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    writer = csv.writer(response)
    writer.writerow(['name', 'price'])
    for p in products:
        writer.writerow([p.name, p.price])
    return response

# ----- Import CSV -----
@login_required
def import_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File must be CSV.')
            return redirect('prices:dashboard')
        decoded = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded)
        for row in reader:
            name = row.get('name', '').strip()
            price = row.get('price', '').strip()
            if name and price:
                try:
                    Product.objects.update_or_create(
                        name=name,
                        defaults={'price': price}
                    )
                except Exception:
                    pass
        messages.success(request, 'CSV imported successfully.')
    else:
        messages.error(request, 'No file selected.')
    return redirect('prices:dashboard')

# ----- Staff: Manage Employee Users -----
@login_required
def user_add(request):
    if not request.user.is_staff:
        return redirect('prices:dashboard')
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Employee {form.cleaned_data["email"]} added.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect('prices:staff_dashboard')

@login_required
def user_delete(request, user_id):
    if not request.user.is_staff:
        return redirect('prices:dashboard')
    user = get_object_or_404(User, pk=user_id, is_staff=False, is_superuser=False)
    user.delete()
    messages.success(request, 'Employee removed.')
    return redirect('prices:staff_dashboard')

# ----- PWA service worker and manifest -----
def service_worker(request):
    return render(request, 'service-worker.js', content_type='application/javascript')

def manifest(request):
    return render(request, 'manifest.json', content_type='application/json')
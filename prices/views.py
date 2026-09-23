import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from .models import Product, EmployeeProfile
from .forms import ProductForm, EmployeeCreationForm


# ----- Public Home -----
def home(request):
    products = Product.objects.all().order_by('?')
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)
    return render(request, 'home.html', {
        'products': products,
        'search_query': search_query,
    })


# ----- Login -----
def login_view(request):
    if request.user.is_authenticated:
        return redirect('prices:dashboard')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('prices:dashboard')
            messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('prices:home')


# ----- Dashboard router -----
@login_required
def dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('prices:staff_dashboard')
    return redirect('prices:employee_dashboard')


# ----- Employee Dashboard -----
@login_required
def employee_dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('prices:staff_dashboard')
    products = Product.objects.all().order_by('name')
    return render(request, 'employee_dashboard.html', {'products': products})


# ----- Staff Dashboard -----
@login_required
def staff_dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('prices:employee_dashboard')

    products = Product.objects.all().order_by('name')

    if request.user.is_superuser:
        profiles = EmployeeProfile.objects.select_related('user', 'added_by').all().order_by('-created_at')
    else:
        profiles = EmployeeProfile.objects.select_related('user', 'added_by').filter(
            added_by=request.user
        ).order_by('-created_at')

    return render(request, 'staff_dashboard.html', {
        'products': products,
        'profiles': profiles,
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


# ----- CSV -----
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
                    Product.objects.update_or_create(name=name, defaults={'price': price})
                except Exception:
                    pass
        messages.success(request, 'CSV imported successfully.')
    else:
        messages.error(request, 'No file selected.')
    return redirect('prices:dashboard')


# ----- Staff: Manage Employees -----
@login_required
def user_add(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('prices:dashboard')

    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            form.save(added_by=request.user)
            # Show password ONCE via flash message (not stored anywhere)
            messages.success(
                request,
                mark_safe(
                    f'Employee <strong>{email}</strong> added.<br>'
                    f'Password (shown once – copy it now): '
                    f'<code class="text-dark fw-bold">{password}</code>'
                )
            )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    return redirect('prices:staff_dashboard')


@login_required
def user_delete(request, user_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('prices:dashboard')
    user = get_object_or_404(User, pk=user_id, is_staff=False, is_superuser=False)
    if not request.user.is_superuser:
        profile = getattr(user, 'employee_profile', None)
        if profile is None or profile.added_by != request.user:
            messages.error(request, 'You can only remove employees you added.')
            return redirect('prices:staff_dashboard')
    user.delete()
    messages.success(request, 'Employee removed.')
    return redirect('prices:staff_dashboard')


# ----- PWA -----
def service_worker(request):
    return render(request, 'service-worker.js', content_type='application/javascript')


def manifest(request):
    return render(request, 'manifest.json', content_type='application/json')
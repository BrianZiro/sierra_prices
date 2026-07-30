from django.urls import path
from . import views

app_name = 'prices'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/employee/', views.employee_dashboard, name='employee_dashboard'),
    path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),

    # Product CRUD (redirects to dashboard)
    path('product/add/', views.product_add, name='product_add'),
    path('product/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('product/delete/<int:pk>/', views.product_delete, name='product_delete'),

    # CSV
    path('export/csv/', views.export_csv, name='export_csv'),
    path('import/csv/', views.import_csv, name='import_csv'),

    # Staff user management
    path('user/add/', views.user_add, name='user_add'),
    path('user/delete/<int:user_id>/', views.user_delete, name='user_delete'),

    # PWA
    path('sw.js', views.service_worker, name='service_worker'),
    path('manifest.json', views.manifest, name='manifest'),
]
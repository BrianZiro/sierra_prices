from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Product, EmployeeProfile


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)


class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    fk_name = 'user'          # <-- tells Django which FK to use for this inline
    can_delete = False
    extra = 0
    readonly_fields = ('added_by', 'created_at')


class CustomUserAdmin(BaseUserAdmin):
    inlines = (EmployeeProfileInline,)
    list_display = ('email', 'username', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('email',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'added_by', 'created_at')
    search_fields = ('user__email', 'added_by__email')
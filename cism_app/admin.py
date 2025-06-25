from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import AppUser, Customer, Product, Order, OrderItem, Invoice

# AppUser Admin
class AppUserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

# OrderItem Inline for Order Admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'quantity', 'price', 'subtotal')
    readonly_fields = ('price', 'subtotal')

# Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'order_date', 'total_amount', 'payment_status', 'delivery_status')
    list_filter = ('payment_status', 'delivery_status', 'order_date')
    search_fields = ('order_id', 'customer__name')
    readonly_fields = ('order_id', 'total_amount')
    inlines = [OrderItemInline]
    date_hierarchy = 'order_date'

# Invoice Admin
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'customer', 'created_date')
    list_filter = ('created_date', 'customer')
    search_fields = ('invoice_id', 'customer__name')
    readonly_fields = ('invoice_id',)
    date_hierarchy = 'created_date'
    
    fieldsets = (
        (None, {'fields': ('invoice_id', 'customer')}),
        ('Invoice Details', {'fields': ('created_date', 'invoice_image')}),
    )

# Customer Admin
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'name', 'email', 'phone', 'date_created')
    list_filter = ('date_created',)
    search_fields = ('customer_id', 'name', 'email', 'phone', 'address')
    readonly_fields = ('customer_id', 'date_created')
    fieldsets = (
        (None, {'fields': ('customer_id', 'name')}),
        ('Contact Information', {'fields': ('email', 'phone', 'address')}),
        ('Metadata', {'fields': ('date_created',)}),
    )
    date_hierarchy = 'date_created'

# Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'price', 'warehouse_quantity', 'chms_quantity', 'outside_quantity', 'total_quantity')
    list_filter = ('date_added',)
    search_fields = ('product_id', 'name')
    readonly_fields = ('product_id', 'date_added', 'last_updated', 'total_quantity')
    fieldsets = (
        (None, {'fields': ('product_id', 'name', 'price')}),
        ('Inventory', {'fields': ('warehouse_quantity', 'chms_quantity', 'outside_quantity', 'total_quantity')}),
        ('Metadata', {'fields': ('date_added', 'last_updated')}),
    )
    date_hierarchy = 'date_added'

# Register models
admin.site.register(AppUser, AppUserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Invoice, InvoiceAdmin)

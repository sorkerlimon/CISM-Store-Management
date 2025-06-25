from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import os
import uuid
from django.conf import settings
from decimal import Decimal

# Custom User Manager
class AppUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

# Custom User Model
class AppUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = AppUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

# Customer Model
class Customer(models.Model):
    CUSTOMER_ID_PREFIX = "CST"
    
    customer_id = models.CharField(max_length=10, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.customer_id:
            # Generate customer ID with format CST001, CST002, etc.
            last_customer = Customer.objects.all().order_by('-customer_id').first()
            if last_customer:
                try:
                    last_id = int(last_customer.customer_id.replace(self.CUSTOMER_ID_PREFIX, ''))
                    new_id = last_id + 1
                except ValueError:
                    new_id = 1
            else:
                new_id = 1
            self.customer_id = f"{self.CUSTOMER_ID_PREFIX}{new_id:03d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.customer_id} - {self.name}"
    
    class Meta:
        ordering = ['-date_created']

# Product Model
class Product(models.Model):
    PRODUCT_ID_PREFIX = "PRD"
    
    product_id = models.CharField(max_length=10, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    warehouse_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    chms_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outside_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.product_id:
            # Generate product ID with format PRD001, PRD002, etc.
            last_product = Product.objects.all().order_by('-product_id').first()
            if last_product:
                try:
                    last_id = int(last_product.product_id.replace(self.PRODUCT_ID_PREFIX, ''))
                    new_id = last_id + 1
                except ValueError:
                    new_id = 1
            else:
                new_id = 1
            self.product_id = f"{self.PRODUCT_ID_PREFIX}{new_id:03d}"
        super().save(*args, **kwargs)
    
    @property
    def total_quantity(self):
        return self.warehouse_quantity + self.chms_quantity + self.outside_quantity
    
    def __str__(self):
        return f"{self.product_id} - {self.name}"
    
    class Meta:
        ordering = ['-date_added']

# Order Model
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('Invoiced', 'Invoiced'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('other', 'Other'),
    )
    
    order_id = models.CharField(max_length=10, primary_key=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    delivery_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate a random 4-digit number for order ID
            order_number = str(uuid.uuid4().int)[:4]
            self.order_id = f"ORD{order_number}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.order_id} - {self.customer.name}"
    
    class Meta:
        ordering = ['-order_date']

# Order Item Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        # Set price from product if not already set
        if not self.price and self.product:
            self.price = self.product.price
            
        # Save the item
        super().save(*args, **kwargs)
        
        # Update order total
        self.update_order_total()
    
    def delete(self, *args, **kwargs):
        # Store the order for later
        order = self.order
        
        # Delete the item
        super().delete(*args, **kwargs)
        
        # Update the order total
        self.update_order_total(order)
    
    def update_order_total(self, order=None):
        # Use the provided order or get it from self
        if not order:
            order = self.order
            
        # Calculate new total from all items
        total = Decimal('0.00')
        for item in order.items.all():
            if item.quantity is not None and item.price is not None:
                total += item.quantity * item.price
                
        # Update the order
        order.total_amount = total
        order.save()
    
    @property
    def subtotal(self):
        if self.quantity is None or self.price is None:
            return 0
        return self.quantity * self.price
    
    def __str__(self):
        return f"{self.order.order_id} - {self.product.name} x {self.quantity}"

# Invoice Model
class Invoice(models.Model):
    invoice_id = models.CharField(max_length=10, primary_key=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    created_date = models.DateTimeField(default=timezone.now)
    invoice_image = models.ImageField(upload_to='invoices/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Generate invoice ID if this is a new invoice
        if not self.invoice_id:
            # Generate invoice ID with format INV-00158, etc.
            last_invoice = Invoice.objects.all().order_by('-invoice_id').first()
            if last_invoice:
                try:
                    # Extract the number part from the last invoice ID and increment it
                    last_id = int(last_invoice.invoice_id.replace('INV-', ''))
                    new_id = last_id + 1
                except ValueError:
                    new_id = 1
            else:
                new_id = 1
            self.invoice_id = f"INV-{new_id:05d}"
        
        # Check if we have a file before attempting to save
        has_image = bool(self.invoice_image)
        
        # Call the parent save method
        super().save(*args, **kwargs)
        
        # If image was uploaded, ensure it was saved correctly
        if has_image and self.invoice_image and hasattr(self.invoice_image, 'path'):
            print(f"Invoice image saved at: {self.invoice_image.path}")
    
    def __str__(self):
        return f"{self.invoice_id} - {self.customer.name}"
    
    class Meta:
        ordering = ['-created_date']

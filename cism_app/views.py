from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Customer, Product, Order, OrderItem, Invoice
from django.db.models import Sum, Count, F, Avg, FloatField
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.db import models
import json
from decimal import Decimal
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import base64
import json
import os
from django.conf import settings

# Authentication views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('product_list')  # Redirect to inventory if already logged in
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next', 'product_list')  # Default to inventory
            return redirect(next_url)
        else:
            return render(request, 'login.html', {
                'error': 'Invalid email or password. Please try again.'
            })
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard view
@login_required
def dashboard(request):
    # Restrict access to superusers only
    if not request.user.is_superuser:
        return redirect('product_list')  # Redirect to inventory if not a superuser
        
    # Get counts for dashboard stats
    products_count = Product.objects.count()
    low_stock_count = Product.objects.filter(warehouse_quantity__lt=10).count()
    orders_count = Order.objects.count()
    
    # Calculate total revenue
    total_revenue = Order.objects.filter(
        payment_status='paid'
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Get recent activities
    recent_orders = Order.objects.order_by('-order_date')[:3]
    recent_activities = []
    
    for order in recent_orders:
        recent_activities.append({
            'type': 'order',
            'title': 'New Order',
            'id': order.order_id,
            'description': f"{order.customer.name} placed an order for ${order.total_amount}",
            'time': order.order_date.strftime("%d %b %Y, %H:%M"),
            'link': f"/orders/{order.order_id}/"
        })
    
    context = {
        'products_count': products_count,
        'low_stock_count': low_stock_count,
        'orders_count': orders_count,
        'total_revenue': total_revenue,
        'recent_activities': recent_activities
    }
    
    return render(request, 'dashboard.html', context)

# Customer views
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    
    # Get counts for customer statistics
    first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_customers_count = Customer.objects.filter(date_created__gte=first_day_of_month).count()
    
    # Active customers (those with orders in the last 3 months)
    three_months_ago = timezone.now() - timedelta(days=90)
    active_customers = Customer.objects.filter(orders__order_date__gte=three_months_ago).distinct()
    active_customers_count = active_customers.count()
    
    # Get customers with orders
    customers_with_orders = Customer.objects.annotate(
        orders_count=Count('orders'),
        total_spent=Sum('orders__total_amount')
    ).filter(orders_count__gt=0)
    
    # Calculate average spend
    average_spend = customers_with_orders.aggregate(
        avg_spend=Avg('total_spent', output_field=FloatField())
    )['avg_spend'] or 0
    
    context = {
        'customers': customers,
        'new_customers_count': new_customers_count,
        'active_customers_count': active_customers_count,
        'average_spend': average_spend,
    }
    
    return render(request, 'customers.html', context)

@login_required
def customer_add(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # Validate required fields
        if not name :
            return redirect(f"{reverse('customer_list')}?error=Name is required fields")
        
        try:
            # Create new customer
            customer = Customer.objects.create(
                name=name,
                email=email,
                phone=phone,
                address=address
            )
            
            # Return to customer list with success message
            return redirect(f"{reverse('customer_list')}?message=Customer {customer.name} successfully added")
            
        except Exception as e:
            # Handle any errors during customer creation
            return redirect(f"{reverse('customer_list')}?error=Error adding customer: {str(e)}")
    
    # If not POST request, redirect to customer list
    return redirect('customer_list')

@login_required
def api_create_customer(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            phone = data.get('phone')
            address = data.get('address')
            
            # Validate required fields
            if not name :
                return JsonResponse({
                    'success': False,
                    'error': 'Name is required field'
                })
            
            # Create new customer
            customer = Customer.objects.create(
                name=name,
                email=email,
                phone=phone,
                address=address
            )
            
            # Return success response with customer data
            return JsonResponse({
                'success': True,
                'customer_id': customer.customer_id,
                'name': customer.name,
                'email': customer.email
            })
            
        except Exception as e:
            # Handle any errors during customer creation
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # If not POST request, return error
    return JsonResponse({
        'success': False,
        'error': 'Only POST requests are allowed'
    })

@login_required
def upload_products_excel(request):
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'excel_file' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'error': 'No file was uploaded'
                })
            
            excel_file = request.FILES['excel_file']
            
            # Check file extension
            if not excel_file.name.endswith('.xlsx'):
                return JsonResponse({
                    'success': False,
                    'error': 'Only .xlsx files are supported'
                })
            
            # Process Excel file
            import pandas as pd
            
            # Read Excel file
            df = pd.read_excel(excel_file)
            
            # Convert all column names to lowercase for case-insensitive comparison
            df.columns = [col.lower() for col in df.columns]
            
            # Validate price column
            if 'price' not in df.columns:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required column: PRICE'
                })
            
            # Check for product name column (could be 'items' or 'product name')
            product_name_col = None
            if 'items' in df.columns:
                product_name_col = 'items'
            elif 'product name' in df.columns:
                product_name_col = 'product name'
            
            if not product_name_col:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required column for product names. Please include a column named "ITEMS" or "Product Name"'
                })
            
            # Process products
            products_added = 0
            for _, row in df.iterrows():
                # Get product data
                name = row[product_name_col]
                price = row['price']
                
                # Optional columns
                warehouse_quantity = int(row.get('wh qty', 0)) if pd.notna(row.get('wh qty', 0)) else 0
                chms_quantity = int(row.get('chms', 0)) if pd.notna(row.get('chms', 0)) else 0
                outside_quantity = int(row.get('outside', 0)) if pd.notna(row.get('outside', 0)) else 0
                
                # Skip rows with empty name or price
                if pd.isna(name) or pd.isna(price):
                    continue
                
                # Create product
                Product.objects.create(
                    name=name,
                    price=price,
                    warehouse_quantity=warehouse_quantity,
                    chms_quantity=chms_quantity,
                    outside_quantity=outside_quantity
                )
                
                products_added += 1
            
            # Return success response
            return JsonResponse({
                'success': True,
                'count': products_added,
                'message': f'Successfully added {products_added} products'
            })
            
        except Exception as e:
            # Handle any errors during processing
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # If not POST request, return error
    return JsonResponse({
        'success': False,
        'error': 'Only POST requests are allowed'
    })

@login_required
def customer_detail(request, customer_id):
    # Find the customer
    customer = get_object_or_404(Customer, customer_id=customer_id)
    
    # Get customer orders
    orders = customer.orders.all().order_by('-order_date')
    
    # Calculate total spent
    total_spent = orders.filter(payment_status='paid').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    context = {
        'customer': customer,
        'orders': orders,
        'total_spent': total_spent,
    }
    
    return render(request, 'customer_detail.html', context)

@login_required
def customer_edit(request, customer_id):
    # Find the customer
    customer = get_object_or_404(Customer, customer_id=customer_id)
    
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # Validate required fields
        if not name or not email:
            return redirect(f"{reverse('customer_list')}?error=Name and email are required fields")
        
        try:
            # Update customer details
            customer.name = name
            customer.email = email
            customer.phone = phone
            customer.address = address
            customer.save()
            
            # Redirect with success message
            return redirect(f"{reverse('customer_list')}?message=Customer {customer.name} successfully updated")
        except Exception as e:
            # Handle any errors during update
            return redirect(f"{reverse('customer_list')}?error=Error updating customer: {str(e)}")
    
    # For GET requests, return customer detail
    return redirect('customer_detail', customer_id=customer_id)

@login_required
def customer_delete(request, customer_id):
    # Find the customer
    customer = get_object_or_404(Customer, customer_id=customer_id)
    
    if request.method == 'POST':
        try:
            # Get customer name before deletion for the success message
            customer_name = customer.name
            
            # Delete the customer
            customer.delete()
            
            # Redirect with success message
            return redirect(f"{reverse('customer_list')}?message=Customer {customer_name} successfully deleted")
        except Exception as e:
            # Handle any errors during deletion
            return redirect(f"{reverse('customer_list')}?error=Error deleting customer: {str(e)}")
    
    # If not POST request, this is a direct access to the URL
    # Redirect to customer list to prevent accidental deletion
    return redirect('customer_list')

# Product views
@login_required
def product_list(request):
    products = Product.objects.all()
    
    # Calculate stock counts for different locations
    warehouse_count = Product.objects.aggregate(total=Sum('warehouse_quantity'))['total'] or 0
    chms_count = Product.objects.aggregate(total=Sum('chms_quantity'))['total'] or 0
    outside_count = Product.objects.aggregate(total=Sum('outside_quantity'))['total'] or 0
    
    context = {
        'products': products,
        'warehouse_count': warehouse_count,
        'chms_count': chms_count,
        'outside_count': outside_count,
    }
    
    return render(request, 'inventory.html', context)

@login_required
def product_add(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            price = request.POST.get('price')
            warehouse_quantity = request.POST.get('warehouse_quantity', 0)
            chms_quantity = request.POST.get('chms_quantity', 0)
            outside_quantity = request.POST.get('outside_quantity', 0)
            
            # Validate required fields
            if not name or not price:
                return redirect(f"{reverse('product_list')}?error=Product name and price are required fields")
                
            # Create new product
            product = Product.objects.create(
                name=name,
                price=price,
                warehouse_quantity=warehouse_quantity,
                chms_quantity=chms_quantity,
                outside_quantity=outside_quantity,
            )
            
            return redirect(f"{reverse('product_list')}?message=Product {product.name} successfully added")
        
        except Exception as e:
            return redirect(f"{reverse('product_list')}?error=Error adding product: {str(e)}")
    
    # If not POST request, redirect to product list
    return redirect('product_list')

@login_required
def product_detail(request, product_id):
    return HttpResponse(f"Product detail page for {product_id}")

@login_required
def product_edit(request, product_id):
    # Find the product
    product = get_object_or_404(Product, product_id=product_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            price = request.POST.get('price')
            warehouse_quantity = request.POST.get('warehouse_quantity', 0)
            chms_quantity = request.POST.get('chms_quantity', 0)
            outside_quantity = request.POST.get('outside_quantity', 0)
            
            # Validate required fields
            if not name or not price:
                return redirect(f"{reverse('product_list')}?error=Product name and price are required fields")
                
            # Update product details
            product.name = name
            product.price = price
            product.warehouse_quantity = warehouse_quantity
            product.chms_quantity = chms_quantity
            product.outside_quantity = outside_quantity
            
            # Save the product
            product.save()
            
            return redirect(f"{reverse('product_list')}?message=Product {product.name} successfully updated")
        
        except Exception as e:
            return redirect(f"{reverse('product_list')}?error=Error updating product: {str(e)}")
    
    # For GET requests, render the product edit form
    context = {
        'product': product
    }
    return render(request, 'product_edit.html', context)

@login_required
def product_delete(request, product_id):
    # Find the product
    product = get_object_or_404(Product, product_id=product_id)
    
    if request.method == 'POST':
        try:
            # Get product name before deletion for the success message
            product_name = product.name
            
            # Delete the product
            product.delete()
            
            # Redirect with success message
            return redirect(f"{reverse('product_list')}?message=Product {product_name} successfully deleted")
        except Exception as e:
            # Handle any errors during deletion
            return redirect(f"{reverse('product_list')}?error=Error deleting product: {str(e)}")
    
    # If not POST request, redirect to product list
    return redirect('product_list')

# Order views
@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    
    # Calculate counts for different order statuses
    pending_count = Order.objects.filter(delivery_status='pending').count()
    shipped_count = Order.objects.filter(delivery_status='shipped').count()
    delivered_count = Order.objects.filter(delivery_status='delivered').count()
    
    # Get customers and products for the order form
    customers = Customer.objects.all().order_by('name')
    products = Product.objects.all().order_by('name')
    
    context = {
        'orders': orders,
        'pending_count': pending_count,
        'shipped_count': shipped_count,
        'delivered_count': delivered_count,
        'customers': customers,
        'products': products
    }
    
    return render(request, 'orders.html', context)

@login_required
def order_add(request):
    if request.method == 'POST':
        try:
            # Get form data
            customer_id = request.POST.get('customer')
            due_date = request.POST.get('due_date') or None
            payment_method = request.POST.get('payment_method')
            payment_status = request.POST.get('payment_status')
            delivery_status = request.POST.get('delivery_status')
            
            # Validate required fields
            if not customer_id:
                return redirect(f"{reverse('order_list')}?error=Customer is required")
            
            # Get customer
            customer = get_object_or_404(Customer, customer_id=customer_id)
            
            # Create new order
            order = Order.objects.create(
                customer=customer,
                due_date=due_date,
                payment_method=payment_method,
                payment_status=payment_status,
                delivery_status=delivery_status
            )
            
            # Process order items
            products = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')
            prices = request.POST.getlist('prices[]')
            
            if not products or len(products) == 0:
                order.delete()
                return redirect(f"{reverse('order_list')}?error=At least one product is required")
                
            # Create order items
            for i in range(len(products)):
                if products[i] and quantities[i] and prices[i]:
                    product = get_object_or_404(Product, product_id=products[i])
                    quantity = int(quantities[i])
                    price = float(prices[i])
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=price
                    )
            
            # Redirect to order list
            return redirect(f"{reverse('order_list')}?message=Order {order.order_id} successfully created")
            
        except Exception as e:
            return redirect(f"{reverse('order_list')}?error=Error creating order: {str(e)}")
    
    # If GET request, just show the order page
    customers = Customer.objects.all().order_by('name')
    products = Product.objects.all().order_by('name')
    
    # Check if customer_id is in query parameter (for pre-selecting customer)
    customer_id = request.GET.get('customer')
    selected_customer = None
    if customer_id:
        selected_customer = get_object_or_404(Customer, customer_id=customer_id)
        
    context = {
        'customers': customers,
        'products': products,
        'selected_customer': selected_customer
    }
    
    return render(request, 'order_add.html', context)

@login_required
def order_detail(request, order_id):
    # Get order and related items
    order = get_object_or_404(Order, order_id=order_id)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    
    return render(request, 'order_detail.html', context)

@login_required
def order_edit(request, order_id):
    # Find the order
    order = get_object_or_404(Order, order_id=order_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            customer_id = request.POST.get('customer')
            due_date = request.POST.get('due_date') or None
            payment_method = request.POST.get('payment_method')
            payment_status = request.POST.get('payment_status')
            delivery_status = request.POST.get('delivery_status')
            
            # Validate required fields
            if not customer_id:
                return redirect(f"{reverse('order_detail', args=[order_id])}?error=Customer is required")
            
            # Get customer
            customer = get_object_or_404(Customer, customer_id=customer_id)
            
            # Update order
            order.customer = customer
            order.due_date = due_date
            order.payment_method = payment_method
            order.payment_status = payment_status
            order.delivery_status = delivery_status
            order.save()
            
            # Process order items
            # First, remove existing items
            order.items.all().delete()
            
            # Then add new items
            products = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')
            prices = request.POST.getlist('prices[]')
            
            if not products or len(products) == 0:
                return redirect(f"{reverse('order_detail', args=[order_id])}?error=At least one product is required")
                
            # Create new order items
            for i in range(len(products)):
                if products[i] and quantities[i] and prices[i]:
                    product = get_object_or_404(Product, product_id=products[i])
                    quantity = int(quantities[i])
                    price = float(prices[i])
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=price
                    )
            
            # Redirect to order detail
            return redirect(f"{reverse('order_detail', args=[order_id])}?message=Order successfully updated")
            
        except Exception as e:
            return redirect(f"{reverse('order_detail', args=[order_id])}?error=Error updating order: {str(e)}")
    
    # Get data for the form
    customers = Customer.objects.all().order_by('name')
    products = Product.objects.all().order_by('name')
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
        'customers': customers,
        'products': products
    }
    
    return render(request, 'order_edit.html', context)

@login_required
def order_delete(request, order_id):
    # Find the order
    order = get_object_or_404(Order, order_id=order_id)
    
    if request.method == 'POST':
        try:
            # Get order ID before deletion for the success message
            order_id_to_display = order.order_id
            
            # Delete the order (this will also delete related items due to CASCADE)
            order.delete()
            
            # Redirect with success message
            return redirect(f"{reverse('order_list')}?message=Order {order_id_to_display} successfully deleted")
        except Exception as e:
            # Handle any errors during deletion
            return redirect(f"{reverse('order_list')}?error=Error deleting order: {str(e)}")
    
    # If request is GET, render confirmation page
    context = {
        'order': order
    }
    
    return render(request, 'order_delete.html', context)

# Invoice views
@login_required
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-created_date')
    customers = Customer.objects.all().order_by('name')
    
    context = {
        'invoices': invoices,
        'customers': customers,
    }
    
    return render(request, 'invoices.html', context)

@login_required
def invoice_detail(request, invoice_id):
    # Get the invoice
    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    
    # Get related customer information
    customer = invoice.customer
    
    # Handle image upload if POST request
    if request.method == 'POST' and 'invoice_image' in request.FILES:
        invoice.invoice_image = request.FILES['invoice_image']
        invoice.save()
        return redirect(f"{reverse('invoice_detail', args=[invoice_id])}?message=Invoice image successfully uploaded")
    
    # Get related orders for this customer
    orders = customer.orders.all().order_by('-order_date')
    
    # Calculate total amount from orders
    total_amount = sum(order.total_amount for order in orders)
    
    context = {
        'invoice': invoice,
        'customer': customer,
        'orders': orders,
        'total_amount': total_amount,
    }
    
    return render(request, 'invoice_detail.html', context)

@login_required
def generate_invoice(request):
    if request.method == 'POST':
        # Process the form submission
        customer_id = request.POST.get('customer')
        order_ids = request.POST.getlist('orders[]')
        
        if customer_id and order_ids:
            # Call the function to generate invoice for multiple orders
            return generate_invoice_for_multiple_orders(request, customer_id, order_ids)
    
    # Get all customers for the dropdown
    customers = Customer.objects.all().order_by('name')
    
    # Get all invoices for the invoice list tab
    invoices = Invoice.objects.all().order_by('-created_date')
    
    context = {
        'customers': customers,
        'invoices': invoices
    }
    
    return render(request, 'invoices.html', context)

@login_required
def generate_invoice_for_multiple_orders(request, customer_id, order_ids):
    # Get the customer
    customer = get_object_or_404(Customer, customer_id=customer_id)
    
    # Get the orders
    orders = Order.objects.filter(order_id__in=order_ids)
    
    if not orders.exists():
        return HttpResponse('No orders found', status=400)
    
    # Calculate total amount from all orders
    total_amount = 0
    
    # Create a list to store items with their subtotals
    all_items = []
    
    for order in orders:
        # For each order, process its items
        for item in order.items.all():
            # Calculate subtotal for this item
            subtotal = item.price * item.quantity
            # Add subtotal to total amount
            total_amount += subtotal
            # Create a dictionary with item info including subtotal
            item_info = {
                'product_name': item.product.name,
                'price': item.price,
                'quantity': item.quantity,
                'subtotal': subtotal
            }
            # Add to our items list
            all_items.append(item_info)
    
    # Create a new invoice
    invoice = Invoice.objects.create(
        customer=customer,
        created_date=timezone.now()
    )
    
    # Store the total amount in the invoice
    invoice.total_amount = total_amount
    invoice.save()
    
    # Get the absolute path to the logo image
    import os
    from django.conf import settings
    logo_path = os.path.join(settings.STATIC_ROOT, 'img', 'chms.jpg')
    if not os.path.exists(logo_path):
        # If STATIC_ROOT is not configured, try with BASE_DIR
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'chms.jpg')
    
    # Create a data URL for the image
    logo_url = ''
    if os.path.exists(logo_path):
        import base64
        with open(logo_path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')
            logo_url = f'data:image/jpeg;base64,{img_data}'
    
    # Create a context for the invoice template
    context = {
        'customer': customer,
        'orders': orders,
        'date': timezone.now().strftime('%Y-%m-%d'),
        'invoice_id': invoice.invoice_id,  # Use the auto-generated invoice_id
        'total_amount': total_amount,  # Pass the calculated total amount
        'all_items': all_items,  # Pass the list of items with subtotals
        'request': request,  # Pass the request object to the template
        'logo_url': logo_url,  # Pass the logo URL
    }
    
    try:
        # Import necessary libraries
        from django.core.files.base import ContentFile
        import os
        import tempfile
        from django.template.loader import render_to_string
        from html2image import Html2Image
        
        # Create a temporary directory for the output
        output_dir = tempfile.mkdtemp()
        output_file = f'invoice_{invoice.invoice_id}.png'
        output_path = os.path.join(output_dir, output_file)
        
        # Render the invoice template to HTML string
        html_string = render_to_string('invoice_template.html', context)
        
        # Create a temporary HTML file
        html_temp = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        html_temp_path = html_temp.name
        html_temp.close()
        
        # Write the HTML to the temporary file
        with open(html_temp_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_string)
        
        # Use html2image to convert HTML to PNG
        try:
            # Initialize the Html2Image converter
            hti = Html2Image(output_path=output_dir)
            
            # Set the size of the output image
            hti.size = (800, 1000)  # Width, height in pixels
            
            # Convert HTML file to PNG
            hti.screenshot(
                html_file=html_temp_path,
                save_as=output_file
            )
            
            # Check if the file was created
            if os.path.exists(output_path):
                # Save the PNG to the invoice model
                with open(output_path, 'rb') as f:
                    invoice.invoice_image.save(
                        output_file,
                        ContentFile(f.read())
                    )
            else:
                # Fallback to direct HTML conversion if file wasn't created
                png_paths = hti.screenshot(
                    html_str=html_string,
                    save_as=output_file
                )
                
                if png_paths and os.path.exists(png_paths[0]):
                    # Save the PNG to the invoice model
                    with open(png_paths[0], 'rb') as f:
                        invoice.invoice_image.save(
                            output_file,
                            ContentFile(f.read())
                        )
                else:
                    # If all PNG methods fail, fall back to PDF
                    from io import BytesIO
                    from xhtml2pdf import pisa
                    
                    # Create a BytesIO buffer for the PDF
                    buffer = BytesIO()
                    
                    # Generate PDF from HTML
                    pisa.CreatePDF(html_string, dest=buffer)
                    
                    # Save the PDF to the invoice model
                    buffer.seek(0)
                    invoice.invoice_image.save(
                        f'invoice_{invoice.invoice_id}.pdf',
                        ContentFile(buffer.getvalue())
                    )
                    buffer.close()
        except Exception as e:
            # If PNG generation fails, fall back to PDF
            from io import BytesIO
            from xhtml2pdf import pisa
            
            # Create a BytesIO buffer for the PDF
            buffer = BytesIO()
            
            # Generate PDF from HTML
            pisa.CreatePDF(html_string, dest=buffer)
            
            # Save the PDF to the invoice model
            buffer.seek(0)
            invoice.invoice_image.save(
                f'invoice_{invoice.invoice_id}.pdf',
                ContentFile(buffer.getvalue())
            )
            buffer.close()
        
        # Clean up temporary files and directory
        try:
            os.unlink(html_temp_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
            os.rmdir(output_dir)
        except:
            pass
        
        # Mark the orders as invoiced
        for order in orders:
            order.delivery_status = 'Invoiced'  # Capitalized to match the model definition
            order.save()
        
        # Redirect to the invoice detail page
        return redirect(f"{reverse('invoice_detail', args=[invoice.invoice_id])}?message=Invoice successfully generated")
    
    except Exception as e:
        # If there's an error, return an error response
        return HttpResponse(f'Error generating invoice: {str(e)}', status=500)

@login_required
def invoice_delete(request, invoice_id):
    # Find the invoice
    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    
    if request.method == 'POST':
        try:
            # Get invoice ID before deletion for the success message
            invoice_id_to_display = invoice.invoice_id
            
            # Delete the invoice
            invoice.delete()
            
            # Redirect with success message
            return redirect(f"{reverse('invoice_list')}?message=Invoice {invoice_id_to_display} successfully deleted")
        except Exception as e:
            # Handle any errors during deletion
            return redirect(f"{reverse('invoice_list')}?error=Error deleting invoice: {str(e)}")
    
    # If request is GET, render confirmation page
    context = {
        'invoice': invoice
    }
    
    return render(request, 'invoice_delete.html', context)

@login_required
def generate_invoice_for_order(request, order_id):
    # Get the order and related items
    order = get_object_or_404(Order, order_id=order_id)
    order_items = order.items.all()
    
    # Calculate subtotals for each item and total amount
    total_amount = 0
    
    # Create a list to store items with their subtotals
    all_items = []
    
    for item in order_items:
        # Calculate subtotal for this item
        subtotal = item.price * item.quantity
        # Add subtotal to total amount
        total_amount += subtotal
        # Create a dictionary with item info including subtotal
        item_info = {
            'product_name': item.product.name,
            'price': item.price,
            'quantity': item.quantity,
            'subtotal': subtotal
        }
        # Add to our items list
        all_items.append(item_info)
    
    # Get the absolute path to the logo image
    import os
    from django.conf import settings
    logo_path = os.path.join(settings.STATIC_ROOT, 'img', 'chms.jpg')
    if not os.path.exists(logo_path):
        # If STATIC_ROOT is not configured, try with BASE_DIR
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'chms.jpg')
    
    # Create a data URL for the image
    logo_url = ''
    if os.path.exists(logo_path):
        import base64
        with open(logo_path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')
            logo_url = f'data:image/jpeg;base64,{img_data}'
    
    # Create a context for the invoice template
    context = {
        'order': order,
        'order_items': order_items,
        'date': timezone.now().strftime('%Y-%m-%d'),
        'invoice_id': f'INV-{order.order_id[3:]}',  # Use part of the order ID
        'total_amount': total_amount,  # Pass the calculated total amount
        'all_items': all_items,  # Pass the list of items with subtotals
        'request': request,  # Pass the request object to the template
        'logo_url': logo_url,  # Pass the logo URL
        'customer': order.customer,  # Add customer for consistent template rendering
    }
    
    try:
        # Create or get an existing invoice for this customer
        invoice, created = Invoice.objects.get_or_create(
            customer=order.customer,
            defaults={
                'created_date': timezone.now()
            }
        )
        
        # Import necessary libraries
        from django.core.files.base import ContentFile
        import os
        import tempfile
        from django.template.loader import render_to_string
        from html2image import Html2Image
        
        # Create a temporary directory for the output
        output_dir = tempfile.mkdtemp()
        output_file = f'invoice_{order.order_id}.png'
        output_path = os.path.join(output_dir, output_file)
        
        # Render the invoice template to HTML string
        html_string = render_to_string('invoice_template.html', context)
        
        # Create a temporary HTML file
        html_temp = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        html_temp_path = html_temp.name
        html_temp.close()
        
        # Write the HTML to the temporary file
        with open(html_temp_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_string)
        
        # Use html2image to convert HTML to PNG
        try:
            # Initialize the Html2Image converter
            hti = Html2Image(output_path=output_dir)
            
            # Set the size of the output image
            hti.size = (800, 1000)  # Width, height in pixels
            
            # Convert HTML file to PNG
            hti.screenshot(
                html_file=html_temp_path,
                save_as=output_file
            )
            
            # Check if the file was created
            if os.path.exists(output_path):
                # Save the PNG to the invoice model
                with open(output_path, 'rb') as f:
                    invoice.invoice_image.save(
                        output_file,
                        ContentFile(f.read())
                    )
            else:
                # Fallback to direct HTML conversion if file wasn't created
                png_paths = hti.screenshot(
                    html_str=html_string,
                    save_as=output_file
                )
                
                if png_paths and os.path.exists(png_paths[0]):
                    # Save the PNG to the invoice model
                    with open(png_paths[0], 'rb') as f:
                        invoice.invoice_image.save(
                            output_file,
                            ContentFile(f.read())
                        )
                else:
                    # If all PNG methods fail, fall back to PDF
                    from io import BytesIO
                    from xhtml2pdf import pisa
                    
                    # Create a BytesIO buffer for the PDF
                    buffer = BytesIO()
                    
                    # Generate PDF from HTML
                    pisa.CreatePDF(html_string, dest=buffer)
                    
                    # Save the PDF to the invoice model
                    buffer.seek(0)
                    invoice.invoice_image.save(
                        f'invoice_{order.order_id}.pdf',
                        ContentFile(buffer.getvalue())
                    )
                    buffer.close()
        except Exception as e:
            # If PNG generation fails, fall back to PDF
            from io import BytesIO
            from xhtml2pdf import pisa
            
            # Create a BytesIO buffer for the PDF
            buffer = BytesIO()
            
            # Generate PDF from HTML
            pisa.CreatePDF(html_string, dest=buffer)
            
            # Save the PDF to the invoice model
            buffer.seek(0)
            invoice.invoice_image.save(
                f'invoice_{order.order_id}.pdf',
                ContentFile(buffer.getvalue())
            )
            buffer.close()
        
        # Clean up temporary files and directory
        try:
            os.unlink(html_temp_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
            os.rmdir(output_dir)
        except:
            pass
        
        # Redirect to the invoice detail page or order detail page
        return redirect(f"{reverse('order_detail', args=[order_id])}?message=Invoice successfully generated")
    
    except Exception as e:
        # If there's an error, return an error response
        return HttpResponse(f'Error generating invoice: {str(e)}', status=500)


# API endpoints for invoice generator
@login_required
def api_customer_details(request, customer_id):
    try:
        customer = get_object_or_404(Customer, customer_id=customer_id)
        return JsonResponse({
            'success': True,
            'customer_id': customer.customer_id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def api_customer_orders(request, customer_id):
    try:
        customer = get_object_or_404(Customer, customer_id=customer_id)
        # Get only pending orders for this customer
        orders = Order.objects.filter(
            customer=customer,
            delivery_status='pending'  # Only get pending orders
        ).order_by('-order_date')
        
        orders_data = []
        for order in orders:
            # Calculate total amount for the order
            total_amount = sum(item.price * item.quantity for item in order.items.all())
            
            orders_data.append({
                'order_id': order.order_id,
                'order_date': order.order_date.strftime('%Y-%m-%d'),
                'total_amount': float(total_amount),
                'items_count': order.items.count()
            })
        
        return JsonResponse({
            'success': True,
            'orders': orders_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Ajax endpoints
@login_required
def get_customer_info(request, customer_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)
    return JsonResponse({
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'address': customer.address
    })

@login_required
def get_product_info(request, product_id):
    return JsonResponse({
        'product_id': product_id,
        'name': 'Sample Product',
        'price': 99.99,
        'warehouse_quantity': 10,
        'chms_quantity': 5,
        'outside_quantity': 2
    })

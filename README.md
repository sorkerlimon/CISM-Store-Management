# 🏪 CISM - Customer Inventory & Sales Management System

[![Django](https://img.shields.io/badge/Django-5.2.1-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive **Customer Inventory & Sales Management System** built with Django. CISM helps businesses manage their inventory, customers, orders, and generate professional invoices with ease.

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

## ✨ Features

### 🔐 Authentication & User Management
- Custom email-based authentication system
- Role-based access control (Admin/User roles)
- Secure login/logout functionality
- Custom user model with extended fields

### 👥 Customer Management
- Auto-generated customer IDs (CST001, CST002...)
- Complete customer profile management
- Customer activity tracking and analytics
- Customer order history

### 📦 Inventory Management
- Multi-location inventory tracking (Warehouse, CHMS, Outside)
- Auto-generated product IDs (PRD001, PRD002...)
- Real-time stock level monitoring
- Low stock alerts and notifications
- Bulk product upload via Excel

### 🛒 Order Processing
- Complete order lifecycle management
- Multiple payment methods (Cash, Credit Card, Bank Transfer, PayPal)
- Order status tracking (Pending, Processing, Shipped, Delivered)
- Payment status monitoring
- Order item management with automatic calculations

### 📄 Invoice Generation
- Professional invoice templates
- Automatic invoice numbering (INV-00001, INV-00002...)
- Invoice image generation and storage
- Multiple order consolidation into single invoice
- Print-ready invoice formats

### 📊 Dashboard & Analytics
- Comprehensive business dashboard
- Real-time statistics and KPIs
- Recent activity tracking
- Revenue analytics
- Inventory insights

### 🎨 Modern UI/UX
- Responsive design for all devices
- Mobile-friendly interface
- Professional styling with FontAwesome icons
- Intuitive navigation and user experience

## 🛠 Tech Stack

- **Backend:** Django 5.2.1, Python 3.8+
- **Database:** SQLite3 (easily configurable for PostgreSQL/MySQL)
- **Frontend:** HTML5, CSS3, JavaScript
- **Styling:** Custom CSS with responsive design
- **Icons:** FontAwesome 6.4.0
- **Forms:** Django Crispy Forms, Widget Tweaks
- **File Handling:** Pillow for image processing
- **PDF Generation:** ReportLab, xhtml2pdf
- **Static Files:** WhiteNoise for production
- **Development:** Django Debug Toolbar (development)

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/cism.git
cd cism
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv env
env\Scripts\activate

# macOS/Linux
python3 -m venv env
source env/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 6: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 7: Run the Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## ⚙️ Configuration

### Environment Variables
For production deployment, set these environment variables:

```bash
# Security
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (if using PostgreSQL)
DATABASE_URL=postgres://user:password@localhost:5432/cism_db

# Media Files (for production)
SERVE_MEDIA=False  # Use web server to serve media files
```

### Settings Configuration

#### Development Settings
```python
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
```

#### Production Settings
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

## 📖 Usage

### Admin Panel
Access the Django admin at `/admin/` with your superuser credentials to:
- Manage users and permissions
- View and edit all data models
- Perform bulk operations
- Monitor system activity

### Main Application

#### Dashboard
- View business statistics and KPIs
- Monitor recent activities
- Quick access to main functions
- Real-time inventory alerts

#### Customer Management
1. Navigate to **Customers** section
2. Add new customers with complete information
3. View customer details and order history
4. Edit customer information as needed

#### Inventory Management
1. Go to **Inventory** section
2. Add products with pricing and stock information
3. Track inventory across multiple locations
4. Monitor low stock alerts
5. Upload bulk products via Excel file

#### Order Processing
1. Create new orders in **Orders** section
2. Select customers and add products
3. Track order status and payments
4. Manage delivery status

#### Invoice Generation
1. Navigate to **Invoices** section
2. Generate invoices for individual orders
3. Create consolidated invoices for multiple orders
4. Download and print professional invoices

## 🔗 API Endpoints

### Customer APIs
```
GET    /api/customer/<customer_id>/              # Get customer details
GET    /api/customer/<customer_id>/orders/       # Get customer orders
POST   /api/create_customer/                     # Create new customer
```

### Product APIs
```
POST   /api/upload_products_excel/               # Bulk upload products
```

### AJAX Endpoints
```
GET    /ajax/get-customer-info/<customer_id>/    # Get customer info
GET    /ajax/get-product-info/<product_id>/      # Get product info
```

## 📁 Project Structure

```
CISM/
├── cism/                          # Main project directory
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Main URL configuration
│   └── wsgi.py
├── cism_app/                     # Main application
│   ├── migrations/               # Database migrations
│   ├── templatetags/            # Custom template filters
│   ├── __init__.py
│   ├── admin.py                 # Admin configuration
│   ├── apps.py
│   ├── models.py                # Data models
│   ├── tests.py
│   ├── urls.py                  # App URL patterns
│   └── views.py                 # View functions
├── templates/                    # HTML templates
│   ├── dashboard.html
│   ├── customers.html
│   ├── inventory.html
│   ├── orders.html
│   ├── invoices.html
│   └── ...
├── static/                       # Static files
│   ├── css/                     # Stylesheets
│   ├── js/                      # JavaScript files
│   └── img/                     # Images
├── media/                        # User uploaded files
│   ├── invoices/                # Generated invoices
│   └── products/                # Product images
├── db.sqlite3                   # SQLite database
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 📸 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)
*Modern dashboard with real-time statistics and quick access*

### Inventory Management
![Inventory](screenshots/inventory.png)
*Comprehensive inventory tracking with multi-location support*

### Invoice Generation
![Invoice](screenshots/invoice.png)
*Professional invoice generation with company branding*

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Ensure compatibility with Django 5.2+

## 🐛 Troubleshooting

### Common Issues

#### Media Files Not Showing
If media files (invoices, product images) are not displaying:

1. **Check DEBUG setting** in `settings.py`
2. **Ensure media URL configuration** is correct
3. **Restart the Django server** after URL changes
4. **Verify file permissions** in media directory

#### Virtual Environment Issues
```bash
# Recreate virtual environment
deactivate
rm -rf env  # or rmdir /s env (Windows)
python -m venv env
env\Scripts\activate  # or source env/bin/activate (macOS/Linux)
pip install -r requirements.txt
```

#### Database Migration Issues
```bash
# Reset migrations (development only)
python manage.py migrate --fake cism_app zero
python manage.py migrate
```

#### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --clear --noinput
```

### Getting Help
- Check the [Issues](https://github.com/yourusername/cism/issues) section
- Create a new issue with detailed description
- Include error messages and system information

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django community for the excellent framework
- FontAwesome for beautiful icons
- All contributors who helped improve this project

## 📞 Support

For support and questions:
- 📧 Email: support@cismapp.com
- 💬 GitHub Issues: [Create an issue](https://github.com/yourusername/cism/issues)
- 📚 Documentation: [Wiki](https://github.com/yourusername/cism/wiki)

---

**Made with ❤️ by the CISM Team**

⭐ **Star this repository if you find it helpful!** 
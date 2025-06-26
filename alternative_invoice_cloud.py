# Alternative Invoice Generation using Cloud API
# No server dependencies needed

import requests
import base64

def generate_invoice_png_htmlcsstoimage(html_content, css_content="", width=800, height=1000):
    """
    Generate PNG using HTMLCSStoImage API
    No server dependencies needed
    """
    
    # API endpoint
    url = "https://hcti.io/v1/image"
    
    # Your API credentials (get free account at htmlcsstoimage.com)
    api_key = "your-api-key"
    api_secret = "your-api-secret"
    
    data = {
        'html': html_content,
        'css': css_content,
        'viewport_width': width,
        'viewport_height': height,
        'format': 'png',
        'quality': 100
    }
    
    try:
        response = requests.post(
            url, 
            data=data, 
            auth=(api_key, api_secret),
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            image_url = result['url']
            
            # Download the image
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                return img_response.content
        
        return None
        
    except Exception as e:
        print(f"Cloud API failed: {str(e)}")
        return None

# Alternative: Bannerbear API
def generate_invoice_png_bannerbear(template_data):
    """
    Generate PNG using Bannerbear API
    Good for templated invoices
    """
    import requests
    
    url = "https://api.bannerbear.com/v2/images"
    headers = {
        "Authorization": f"Bearer your-api-key",
        "Content-Type": "application/json"
    }
    
    data = {
        "template": "your-template-id",
        "modifications": template_data
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        return result['image_url']
    
    return None

# Usage in Django views:
"""
def generate_invoice_with_cloud_api(request, customer_id, order_ids):
    # ... your existing code ...
    
    # Render HTML
    html_string = render_to_string('invoice_template.html', context)
    
    # Generate PNG via cloud API
    image_data = generate_invoice_png_htmlcsstoimage(html_string)
    
    if image_data:
        invoice.invoice_image.save(
            f'invoice_{invoice.invoice_id}.png',
            ContentFile(image_data)
        )
        print("✅ PNG generated via cloud API")
    else:
        # Fallback to PDF
        # ... existing PDF code ...
""" 
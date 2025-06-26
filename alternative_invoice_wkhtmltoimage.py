# Alternative Invoice Generation using wkhtmltoimage
# Simpler installation, no browser dependencies

import subprocess
import os

def generate_invoice_png_wkhtmltoimage(html_file, output_path, width=800, height=1000):
    """
    Generate PNG from HTML using wkhtmltoimage
    Simpler than browser-based solutions
    """
    try:
        cmd = [
            'wkhtmltoimage',
            '--format', 'png',
            '--width', str(width),
            '--height', str(height),
            '--quality', '100',
            '--enable-local-file-access',
            html_file,
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"wkhtmltoimage error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"wkhtmltoimage failed: {str(e)}")
        return False

# Installation (Ubuntu):
# sudo apt-get install wkhtmltopdf

# Usage in Django views:
"""
def generate_invoice_with_wkhtmltoimage(request, customer_id, order_ids):
    # ... your existing code ...
    
    # Write HTML to temp file
    html_temp_path = os.path.join(output_dir, 'temp.html')
    with open(html_temp_path, 'w', encoding='utf-8') as f:
        f.write(html_string)
    
    # Generate PNG
    output_path = os.path.join(output_dir, f'invoice_{invoice.invoice_id}.png')
    success = generate_invoice_png_wkhtmltoimage(html_temp_path, output_path)
    
    if success and os.path.exists(output_path):
        with open(output_path, 'rb') as f:
            invoice.invoice_image.save(
                f'invoice_{invoice.invoice_id}.png',
                ContentFile(f.read())
            )
""" 
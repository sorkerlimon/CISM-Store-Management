# Alternative Invoice Generation using Playwright
# More reliable than html2image

import asyncio
from playwright.async_api import async_playwright
import os

async def generate_invoice_png_playwright(html_content, output_path, width=800, height=1000):
    """
    Generate PNG from HTML using Playwright
    More reliable than html2image
    """
    async with async_playwright() as p:
        # Launch browser (works headless by default)
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        )
        
        # Create page
        page = await browser.new_page(viewport={'width': width, 'height': height})
        
        # Set HTML content
        await page.set_content(html_content, wait_until='networkidle')
        
        # Take screenshot
        await page.screenshot(
            path=output_path,
            full_page=True,
            type='png'
        )
        
        # Close browser
        await browser.close()
        
        return True

# Installation command:
# pip install playwright
# playwright install chromium

# Usage in Django views:
"""
def generate_invoice_with_playwright(request, customer_id, order_ids):
    # ... your existing code for getting invoice data ...
    
    # Render HTML
    html_string = render_to_string('invoice_template.html', context)
    
    # Generate PNG
    output_path = os.path.join(output_dir, f'invoice_{invoice.invoice_id}.png')
    
    # Run async function
    success = asyncio.run(generate_invoice_png_playwright(html_string, output_path))
    
    if success:
        # Save to Django model
        with open(output_path, 'rb') as f:
            invoice.invoice_image.save(
                f'invoice_{invoice.invoice_id}.png',
                ContentFile(f.read())
            )
    else:
        # Fallback to PDF
        # ... existing PDF code ...
""" 
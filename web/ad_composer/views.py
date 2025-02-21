from django.shortcuts import render
import requests
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from urllib.parse import urljoin, urlparse
import re

@require_GET
def fetch_url(request):
    url = request.GET.get('url')
    try:
        # Fetch the page content
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        
        # Get the base URL for resolving relative URLs
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        # Modify HTML to make URLs absolute
        content = response.text
        
        # Replace src attributes
        content = re.sub(
            r'(src=["\']\/)([^"\']+)',
            lambda m: f'src="{urljoin(base_url, m.group(1) + m.group(2))}"',
            content
        )
        
        # Replace href attributes
        content = re.sub(
            r'(href=["\']\/)([^"\']+)',
            lambda m: f'href="{urljoin(base_url, m.group(1) + m.group(2))}"',
            content
        )
        
        # Return the modified HTML directly
        return HttpResponse(content, content_type='text/html')
    
    except requests.RequestException as e:
        return HttpResponse(f'Error: {str(e)}', status=400)
    
def index(request):
    return render(request, 'ad_composer/index.html')

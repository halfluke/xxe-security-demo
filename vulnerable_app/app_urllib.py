"""
Vulnerable Flask Application - XXE Security Demo
DELIBERATELY INSECURE - For educational purposes only!

This application intentionally contains XXE vulnerabilities.
HTTP/HTTPS external DTDs and entities are fetched via a custom lxml Resolver
(urllib) so localhost SSRF demos work when libxml2 does not open HTTP itself.
DO NOT use in production or deploy to public servers.
"""

import os
import urllib.error
import urllib.request
from urllib.parse import urlparse

from flask import Flask, request, render_template_string, jsonify
from lxml import etree

# Lab-only: only fetch these hosts via Python. Set to None to allow any host.
ALLOWED_RESOLVER_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


class HttpUrlResolver(etree.Resolver):
    """Fetch http(s) URLs with urllib; return content via resolve_string."""

    def resolve(self, url, id, context):
        if not url:
            return None
        if not (url.startswith("http://") or url.startswith("https://")):
            return None
        if ALLOWED_RESOLVER_HOSTS is not None:
            host = urlparse(url).hostname
            if host is None or host.lower() not in ALLOWED_RESOLVER_HOSTS:
                return None
        req = urllib.request.Request(
            url,
            method="GET",
            headers={"User-Agent": "xxe-lab-resolver/0.1"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read()
        except urllib.error.URLError:
            return None
        text = body.decode("utf-8", errors="replace")
        return self.resolve_string(text, context)


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def parse_xml_vulnerable(xml_content):
    """
    VULNERABLE XML parser - External entities are ENABLED
    This is intentionally insecure for demonstration purposes!
    """
    try:
        # Create parser with external entities ENABLED
        parser = etree.XMLParser(
            resolve_entities=True,  # Enable external entities
            no_network=True,  # libxml2: no network; http(s) via HttpUrlResolver
            dtd_validation=False,
            load_dtd=True,  # Load DTD
            remove_blank_text=False,
            huge_tree=True  # Allow large XML (for DoS testing)
        )
        parser.resolvers.add(HttpUrlResolver())

        # Parse the XML
        root = etree.fromstring(xml_content.encode('utf-8'), parser)

        # Extract data from XML
        result = {
            'success': True,
            'parsed_data': extract_data(root),
            'message': 'XML parsed successfully'
        }

        return result

    except etree.XMLSyntaxError as e:
        return {
            'success': False,
            'error': f'XML Syntax Error: {str(e)}',
            'message': 'Failed to parse XML'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error: {str(e)}',
            'message': 'An error occurred'
        }

def extract_data(root):
    """
    Extract data from parsed XML tree
    """
    data = {}

    # Get root tag name
    data['root_tag'] = root.tag

    # Get all text content
    data['text_content'] = root.text or ''

    # Get all child elements
    children = []
    for child in root:
        child_data = {
            'tag': child.tag,
            'text': child.text or '',
            'attributes': dict(child.attrib)
        }
        children.append(child_data)

    data['children'] = children

    # Convert entire tree to string for display
    data['xml_string'] = etree.tostring(root, encoding='unicode', pretty_print=True)

    return data

@app.route('/')
def index():
    """
    Home page with simple XML test form
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>XXE Vulnerable App - XML Parser</title>
        <style>
             body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
             .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #d32f2f;
            }
            .warning {
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
            }
            .tabs {
                display: flex;
                gap: 10px;
                margin: 20px 0;
            }
            .tab {
                padding: 10px 20px;
                background-color: #e0e0e0;
                border: none;
                cursor: pointer;
                border-radius: 4px 4px 0 0;
            }
            .tab.active {
                background-color: #d32f2f;
                color: white;
            }
            .tab-content {
                display: none;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 0 4px 4px 4px;
            }
            .tab-content.active {
                display: block;
            }
            textarea {
                width: 100%;
                min-height: 200px;
                font-family: 'Courier New', monospace;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            .file-input-wrapper {
                display: flex;
                align-items: center;
                gap: 15px;
                margin: 20px 0;
            }
            input[type="file"] {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                flex: 1;
            }
            button {
                background-color: #d32f2f;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #b71c1c;
            }
            pre {
                background-color: #272822;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 4px;
                overflow-x: auto;
            }
        </style>
        <script>
            function switchTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Show selected tab
                document.getElementById(tabName).classList.add('active');
                document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1>⚠️ XXE Vulnerable XML Parser</h1>
            
            <div class="warning">
                <strong>WARNING:</strong> This application is intentionally vulnerable to XXE attacks.
                For educational purposes only. DO NOT deploy to production!
                <br><br>
                <strong>HTTP DTD demo:</strong> External <code>http(s):</code> DTD/entity URLs are loaded via a Python
                <code>urllib</code> resolver (localhost-only unless you change <code>ALLOWED_RESOLVER_HOSTS</code>).
                Serve <code>test.dtd</code> with e.g. <code>python -m http.server 8000</code>.
            </div>
            
            <h2>Choose Input Method:</h2>
            
            <div class="tabs">
                <button class="tab active" onclick="switchTab('paste-tab')">Paste XML</button>
                <button class="tab" onclick="switchTab('upload-tab')">Upload File</button>
            </div>
            
            <!-- Tab 1: Paste XML -->
            <div id="paste-tab" class="tab-content active">
                <h3>📝 Paste XML Content</h3>
                <form method="POST" action="/parse">
                    <textarea name="xml_content" placeholder="Enter XML here...">
<?xml version="1.0" encoding="UTF-8"?>
<user>
    <name>John Doe</name>
    <email>john@example.com</email>
    <role>user</role>
</user>
                    </textarea>
                    <br>
                    <button type="submit">Parse XML</button>
                </form>
            </div>
            
            <!-- Tab 2: Upload File -->
            <div id="upload-tab" class="tab-content">
                <h3>📁 Upload XML File</h3>
                <form method="POST" action="/upload" enctype="multipart/form-data">
                    <div class="file-input-wrapper">
                        <input type="file" name="xml_file" accept=".xml,text/xml" required>
                        <button type="submit">Upload & Parse</button>
                    </div>
                </form>
                <p><em>Accepted formats: .xml files</em></p>
            </div>
            
            <h3>Example Payloads:</h3>
            <p><strong>Normal XML:</strong></p>
            <pre>&lt;?xml version="1.0"?&gt;
&lt;data&gt;
    &lt;message&gt;Hello World&lt;/message&gt;
&lt;/data&gt;</pre>
            
            <p><strong>XXE File Disclosure:</strong></p>
            <pre>&lt;?xml version="1.0"?&gt;
&lt;!DOCTYPE foo [
  &lt;!ENTITY xxe SYSTEM "file:///etc/passwd"&gt;
]&gt;
&lt;data&gt;&amp;xxe;&lt;/data&gt;</pre>
            
            <p><strong>XXE SSRF (Internal Request):</strong></p>
            <pre>&lt;?xml version="1.0"?&gt;
&lt;!DOCTYPE foo [
  &lt;!ENTITY xxe SYSTEM "http://localhost:5000/health"&gt;
]&gt;
&lt;data&gt;&amp;xxe;&lt;/data&gt;</pre>

            <p><strong>XXE external DTD over HTTP (Python resolver; serve test.dtd on port 8000):</strong></p>
            <pre>&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE data SYSTEM "http://127.0.0.1:8000/test.dtd"&gt;
&lt;data&gt;&amp;xxe;&lt;/data&gt;</pre>
            <p><em>Example <code>test.dtd</code>: <code>&lt;!ENTITY xxe "from-remote-dtd"&gt;</code></em></p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/parse', methods=['POST'])
def parse_xml():
    """
    Parse XML submitted via POST request
    """
    xml_content = request.form.get('xml_content', '')

    if not xml_content:
        return jsonify({
            'success': False,
            'error': 'No XML content provided'
        }), 400

    # Parse XML (vulnerable!)
    result = parse_xml_vulnerable(xml_content)

    # Return result as HTML
    if result['success']:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Parse Result</title>
            <style>
                 body {{
                    font-family: Arial, sans-serif;
                    max-width: 900px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .success {{
                    background-color: #d4edda;
                    border-left: 4px solid #28a745;
                    padding: 15px;
                    margin: 20px 0;
                }}
                pre {{
                    background-color: #272822;
                    color: #f8f8f2;
                    padding: 15px;
                    border-radius: 4px;
                    overflow-x: auto;
                }}
                a {{
                    color: #d32f2f;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✅ XML Parsed Successfully</h1>
                
                <div class="success">
                    {result['message']}
                </div>
                
                <h2>Parsed Data:</h2>
                <pre>{result['parsed_data']}</pre>
                
                <p><a href="/">← Back to Parser</a></p>
            </div>
        </body>
        </html>
        """
        return render_template_string(html)
    else:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Parse Error</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 900px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .error {{
                    background-color: #f8d7da;
                    border-left: 4px solid #dc3545;
                    padding: 15px;
                    margin: 20px 0;
                }}
                a {{
                    color: #d32f2f;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ Parse Error</h1>

                <div class="error">
                    <strong>Error:</strong> {result.get('error', 'Unknown error')}
                </div>

                <p><a href="/">← Back to Parser</a></p>
            </div>
        </body>
        </html>
        """
        return render_template_string(html), 400

@app.route('/api/parse', methods=['POST'])
def api_parse_xml():
    """
    API endpoint for XML parsing (returns JSON)
    Useful for testing with curl or Burp Suite
    """
    # Accept both form data and raw body
    if request.content_type == 'application/xml' or request.content_type == 'text/xml':
        xml_content = request.data.decode('utf-8')
    else:
        xml_content = request.form.get('xml_content') or request.json.get('xml_content', '')

    if not xml_content:
        return jsonify({
            'success': False,
            'error': 'No XML content provided'
        }), 400

    result = parse_xml_vulnerable(xml_content)
    return jsonify(result)

@app.route('/health')
def health():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'running',
        'app': 'XXE Vulnerable Application',
        'version': '1.0.0',
        'warning': 'This application is intentionally vulnerable!'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle XML file upload and parse it
    """
    # Check if file was uploaded
    if 'xml_file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file uploaded'
        }), 400

    file = request.files['xml_file']

    # Check if filename is empty
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400

    # Check if file has .xml extension
    if not file.filename.endswith('.xml'):
        return jsonify({
            'success': False,
            'error': 'Only .xml files are allowed'
        }), 400

    try:
        # Read file content
        xml_content = file.read().decode('utf-8')

        # Save uploaded file (optional, for logging)
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"uploaded_{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)

        with open(filepath, 'w') as f:
            f.write(xml_content)

        # Parse XML (vulnerable!)
        result = parse_xml_vulnerable(xml_content)

        # Return result as HTML
        if result['success']:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Parse Result</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 900px;
                        margin: 50px auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        background: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .success {{
                        background-color: #d4edda;
                        border-left: 4px solid #28a745;
                        padding: 15px;
                        margin: 20px 0;
                    }}
                    .info {{
                        background-color: #d1ecf1;
                        border-left: 4px solid #17a2b8;
                        padding: 15px;
                        margin: 20px 0;
                    }}
                    pre {{
                        background-color: #272822;
                        color: #f8f8f2;
                        padding: 15px;
                        border-radius: 4px;
                        overflow-x: auto;
                        max-height: 500px;
                    }}
                    a {{
                        color: #d32f2f;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ XML File Parsed Successfully</h1>
                    
                    <div class="info">
                        <strong>Uploaded File:</strong> {file.filename}<br>
                        <strong>Saved As:</strong> {safe_filename}
                    </div>
                    
                    <div class="success">
                        {result['message']}
                    </div>
                    
                    <h2>Parsed Data:</h2>
                    <pre>{result['parsed_data']}</pre>
                    
                    <p><a href="/">← Back to Parser</a></p>
                </div>
            </body>
            </html>
            """
            return render_template_string(html)
        else:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Parse Error</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 900px;
                        margin: 50px auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        background: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .error {{
                        background-color: #f8d7da;
                        border-left: 4px solid #dc3545;
                        padding: 15px;
                        margin: 20px 0;
                    }}
                    a {{
                        color: #d32f2f;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>❌ Parse Error</h1>
                    
                    <div class="error">
                        <strong>File:</strong> {file.filename}<br>
                        <strong>Error:</strong> {result.get('error', 'Unknown error')}
                    </div>
                    
                    <p><a href="/">← Back to Parser</a></p>
                </div>
            </body>
            </html>
            """
            return render_template_string(html), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing file: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("⚠️  XXE VULNERABLE APPLICATION")
    print("=" * 60)
    print("This application is INTENTIONALLY INSECURE!")
    print("For educational purposes only.")
    print()
    print("🌐 Server starting on http://127.0.0.1:5000")
    print("=" * 60)

    app.run(debug=True, host='127.0.0.1', port=5000)
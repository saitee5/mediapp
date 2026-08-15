import json
import sys
from pathlib import Path

# Add mediscribe to sys.path
MEDISCRIBE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MEDISCRIBE_DIR))

from main import app

def export_redoc_html():
    openapi_schema = app.openapi()
    spec_json = json.dumps(openapi_schema, indent=2)

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MediScribe AI Agent - ReDoc API Documentation</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" type="image/png" href="https://fastapi.tiangolo.com/img/favicon.png">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }}
        #redoc-container {{
            width: 100%;
            height: 100%;
        }}
    </style>
</head>
<body>
    <div id="redoc-container"></div>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
    <script>
        const spec = {spec_json};
        Redoc.init(spec, {{
            scrollYOffset: 50,
            expandResponses: "200,201",
            hideDownloadButton: false,
            theme: {{
                colors: {{
                    primary: {{
                        main: '#0284c7'
                    }},
                    success: {{
                        main: '#10b981'
                    }}
                }},
                typography: {{
                    fontFamily: 'Inter, sans-serif',
                    headings: {{
                        fontFamily: 'Inter, sans-serif',
                        fontWeight: '600'
                    }},
                    code: {{
                        fontFamily: 'JetBrains Mono, monospace'
                    }}
                }},
                sidebar: {{
                    backgroundColor: '#f8fafc',
                    textColor: '#1e293b'
                }}
            }}
        }}, document.getElementById('redoc-container'));
    </script>
</body>
</html>
"""

    root_path = MEDISCRIBE_DIR.parent / "api_documentation.html"
    mediscribe_path = MEDISCRIBE_DIR / "api_documentation.html"

    with open(root_path, "w", encoding="utf-8") as f:
        f.write(html_template)

    with open(mediscribe_path, "w", encoding="utf-8") as f:
        f.write(html_template)

    print(f"Generated standalone ReDoc HTML at:")
    print(f"1. {root_path}")
    print(f"2. {mediscribe_path}")

if __name__ == "__main__":
    export_redoc_html()

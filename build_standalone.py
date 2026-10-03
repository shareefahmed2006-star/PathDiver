import os

def build_offline():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, "index.html"), "r", encoding="utf-8") as f:
        html = f.read()

    with open(os.path.join(base_dir, "style.css"), "r", encoding="utf-8") as f:
        css = f.read()

    with open(os.path.join(base_dir, "app.js"), "r", encoding="utf-8") as f:
        js = f.read()

    # Inline CSS
    html = html.replace('<link rel="stylesheet" href="style.css">', f'<style>\n{css}\n</style>')
    # Inline JS
    html = html.replace('<script src="app.js"></script>', f'<script>\n{js}\n</script>')

    out_path = os.path.join(base_dir, "PathDiver_Offline.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Successfully generated standalone: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    build_offline()

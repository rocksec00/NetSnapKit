# NetSnapKit --  Website capture kit

````markdown
# WebScopeShot

🖥️ A fast, automated tool to scan websites (domains, subdomains, or list of URLs), capture full-page screenshots, and export them into a clean PDF — labeled and bundled for quick reviews or audits.

---

## 🚀 Features

- 🔎 Scan a domain, its subdomains, or a list of URLs
- 📸 Full-page screenshots for each URL
- 🏷️ Automatically labels each screenshot with the URL
- 📄 Combines all screenshots into a single PDF
- 🧠 Prevents duplicate files with smart naming (`example.com_1.pdf`, etc.)
- ⚡ Uses concurrency for faster results

---

## 📦 Installation

1. **Install dependencies:**

```bash
pip install playwright Pillow
playwright install
pip install colorama
````

2. (Optional) For subdomain discovery, install [`assetfinder`](https://github.com/tomnomnom/assetfinder):

```bash
go install github.com/tomnomnom/assetfinder@latest
```

Ensure `assetfinder` is in your `$PATH`.

---

## 📂 Usage

```bash
python scan.py [--url DOMAIN] [--subdomains DOMAIN] [--urlfile FILE]
```

### 🔹 Scan a single domain:

```bash
python scan.py --url example.com
```

### 🔹 Scan subdomains:

```bash
python scan.py --subdomains example.com
```

> Requires `assetfinder` installed and accessible

### 🔹 Scan list of URLs:

```bash
python scan.py --urlfile urls.txt
```

---

## 📁 Output

All screenshots are saved as a **single PDF** with labels at:

```
output/screenshots/
```

PDF filenames reflect your input:

* `example.com.pdf`
* `example.com_subdomains.pdf`
* `urls.txt.pdf`
* Auto-versioned: `example.com_1.pdf`, `example.com_2.pdf`, etc.

---

## 🔧 Configuration

You can adjust concurrency by editing:

```python
CONCURRENCY_LIMIT = 5
```

Increase for faster scans (use with care on limited systems).

---

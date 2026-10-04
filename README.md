# PathDiver 🌊🔍

> **Intelligent File Traversal, Heuristic Duplicate Detection & Storage Superpowers for Windows, macOS & Linux.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/shareefahmed2006-star/pathdiver)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-success.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Overview

**PathDiver** is an all-in-one, privacy-first desktop utility and storage optimizer built around a core design principle:
> **"Simple for a first-time user, powerful when they need it."**

Built with an ultra-fast Python core and a modern human-centric interface, PathDiver unifies deep in-content document search, visual & text heuristic duplicate detection, 1-click reversible folder organization, and developer cache sweeping into a single lightweight application.

Unlike conventional utilities that rely solely on file names or rigid MD5 hashes, PathDiver inspects inside PDFs, Word documents, and Jupyter notebooks without external software, detects cropped or annotated image duplicates, and safeguards all cleanup operations via the native OS Recycle Bin.

---

## ⚡ The Four Core Superpowers

### 🔎 1. Find & Peek (In-Content Document Traversal)
* **Full-Text Traversal:** Search beyond filenames—deep-dive inside `.pdf`, `.docx`, `.ipynb`, `.txt`, and code files (`.py`, `.js`, `.cpp`, `.json`).
* **Smart 2-Line Peek Drawer:** Instant inline overview showing document classification, page count, and key excerpts in under **15 milliseconds** without launching heavy software like Adobe Acrobat or Microsoft Word.
* **Filter Popover:** Quickly narrow by category (Documents, Code, Images, Audio/Video, Archives) or toggle full-text extraction with a single click.

### ♻️ 2. Two-Phase Heuristic Duplicate & Edited File Detector
* **Phase 1 (Exact Ditto):** Rapid byte-hash comparison instantly flags bit-for-bit identical files.
* **Phase 2 (Visual & Text Heuristics):** Analyzes visual pixel variance, bounding-box crops, and text similarity ratios. Accurately detects cropped screenshots, annotated/drawn images, and edited document drafts with similarity percentages without false positives.
* **Safer Cleanup:** Exact duplicates can be deleted immediately; edited version drafts are clearly distinguished with similarity percentages so your modified work is never lost.

### 📂 3. 1-Click Folder Organizer (with 100% Reversible Undo)
* **Zero-Rule Categorization:** Automatically groups chaotic loose files into standardized folders (`Documents/`, `Installers/`, `Code/`, `Archives/`, `Images/`, `Media/`) without touching existing subdirectories.
* **Session-Journaled Undo:** One click on `↺ 1-Click Undo` restores all moved files to their exact original locations and automatically removes generated category folders.

### 🧹 4. Developer & Cache Junk Sweeper
* **Pruned DFS Traversal (<2s):** Instantly detects massive cache bloat (`node_modules`, `__pycache__`, `.venv`, `.gradle`, `.turbo`, `.next`) while intelligently pruning recursion at boundary folders.
* **Zero-Risk Reclaim:** Safely moves selected caches directly to the **Windows Recycle Bin / macOS Trash** (`send2trash`), making accidental deletions easily recoverable.

---

## 🛠️ Progressive Disclosure: Developer View

For computer science demonstrations, education, and power users, PathDiver features an optional **Technical Details / Developer View** (`⚙️`):
* **Live Explicit DFS Stack (LIFO):** Watch push and pop operations execute in real-time with live depth counters.
* **Interactive Hierarchy Tree:** Browse filesystem structure with lazy expansion and node filtering.
* **Traversal Controls:** Adjustable speeds (`0.5x`, `1x`, `5x`, `Instant`), step-by-step debugger (`⏭ Step`), and reset.
* **Event Console:** Timestamped telemetry stream of all traversal and filesystem events.

---

## 🚀 Quick Start & Installation

### Option 1: Standalone Native App (Zero Setup)
Download the standalone executable from the [Releases](https://github.com/shareefahmed2006-star/pathdiver/releases) tab:
* **Windows:** Download `PathDiver_Ready_To_Send.zip`, unzip, and double-click `Click_To_Start_PathDiver.bat` (or `PathDiver.exe`).

### Option 2: Run from Source
```bash
git clone https://github.com/shareefahmed2006-star/pathdiver.git
cd pathdiver
pip install -r requirements.txt
python desktop_main.py
```

### Option 3: Cross-Platform Browser Standalone
Double-click `PathDiver_Offline.html` to run in any browser with zero installation!

---

## 🏗️ Technology Stack

* **Backend Engine:** Python 3 standard library (`http.server`, `socket`, `hashlib`, `difflib`, `shutil`, `os.scandir`)
* **Window & Native Bridge:** `pywebview` (native Windows WebView2 / macOS WKWebView / Linux WebKitGTK)
* **Document Parsing:** `pypdf` (PDF extraction), XML ElementTree (DOCX direct parsing)
* **Image Heuristics:** `Pillow` (RGB difference, bounding-box crop heuristics, pixel variance)
* **Safe Deletion:** `send2trash` (direct OS Recycle Bin integration)
* **Frontend:** Vanilla JavaScript, HTML5, CSS3 with Plus Jakarta Sans typography and segmented dual-theme switch (Light / Dark mode).

---

## 🔒 Security & Privacy Guarantee

* **100% Local Processing:** PathDiver operates entirely on your host computer.
* **No Telemetry / No Network Requests:** No analytics, tracking, or user data is ever collected or sent to external servers.
* **No API Keys or Cloud Dependencies:** Everything runs locally using lightweight pure Python heuristics.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.



## Code signing policy

Free code signing provided by SignPath.io, certificate by SignPath Foundation.

### Team roles

- Authors / Committers: Project maintainers
- Reviewers: Project maintainers
- Approvers: Project maintainers

### Privacy policy

This program will not transfer any information to other
networked systems unless specifically requested by the user
or the person installing or operating it.

import os
import sys
import json
import hashlib
import string
import time
import re
import difflib
import subprocess
import shutil
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

try:
    from PIL import Image, ImageChops, ImageStat
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

BASE_RESOURCE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))


def analyze_image_pair(path1, path2):
    """
    Checks if two images have the SAME content inside (or if one is an edited version of the other).
    Returns:
      ('duplicate', details) - identical visual content (or JPEG compression variance)
      ('edited_drawn', details) - same base image, but with drawing / annotation / text added
      ('edited_cropped', details) - verified sub-crop of the original image
      ('different', None) - completely different images
    """
    if not HAS_PIL:
        return ('different', None)

    try:
        with Image.open(path1) as im1, Image.open(path2) as im2:
            im1_rgb = im1.convert('RGB')
            im2_rgb = im2.convert('RGB')

            # 1. Exact same dimensions
            if im1.size == im2.size:
                diff = ImageChops.difference(im1_rgb, im2_rgb)
                if not diff.getbbox():
                    return ('duplicate', '100% identical pixel content')

                stat = ImageStat.Stat(diff)
                mean_diff = sum(stat.mean) / len(stat.mean)

                # Identical visual image (subtle JPEG re-compression noise)
                if mean_diff < 3.5:
                    return ('duplicate', 'Identical visual image (compression variance)')

                # Check for drawing / markup on the SAME base image
                gray = diff.convert('L')
                hist = gray.histogram()
                identical_pct = (sum(hist[:15]) / (im1.width * im1.height)) * 100
                drawn_pct = (sum(hist[45:]) / (im1.width * im1.height)) * 100

                if identical_pct >= 95.0 and 0.05 <= drawn_pct <= 4.5:
                    return ('edited_drawn', f'Drawing / markup detected on image ({drawn_pct:.1f}% edited area)')

                return ('different', None)

            # 2. Check for cropping
            if im1.width <= im2.width and im1.height <= im2.height:
                s_im, l_im = im1_rgb, im2_rgb
            elif im2.width <= im1.width and im2.height <= im1.height:
                s_im, l_im = im2_rgb, im1_rgb
            else:
                return ('different', None)

            is_crop = False
            alignments = [
                (0, 0),
                ((l_im.width - s_im.width) // 2, (l_im.height - s_im.height) // 2),
                (l_im.width - s_im.width, l_im.height - s_im.height)
            ]
            for ax, ay in alignments:
                sub = l_im.crop((ax, ay, ax + s_im.width, ay + s_im.height))
                sub_diff = ImageChops.difference(s_im, sub)
                sub_stat = ImageStat.Stat(sub_diff)
                if (sum(sub_stat.mean) / len(sub_stat.mean)) < 3.5:
                    is_crop = True
                    break

            if is_crop:
                return ('edited_cropped', f'Verified cropped image ({s_im.width}x{s_im.height} from {l_im.width}x{l_im.height})')

            return ('different', None)

    except Exception:
        return ('different', None)


def get_real_user_folder(folder_name):
    """Resolves true user folder path handling OneDrive redirection."""
    user_home = os.path.expanduser("~")
    onedrive = os.path.join(user_home, "OneDrive")
    p_od = os.path.join(onedrive, folder_name)
    p_home = os.path.join(user_home, folder_name)
    if os.path.exists(p_od) and (not os.path.exists(p_home) or (os.path.isdir(p_od) and len(os.listdir(p_od)) > len(os.listdir(p_home) if os.path.exists(p_home) else []))):
        return p_od
    if os.path.exists(p_home):
        return p_home
    if os.path.exists(p_od):
        return p_od
    return user_home


def extract_file_preview_and_summary(filepath, max_snippet_len=600):
    """
    Extracts text snippet and generates a smart 2-line preview summary for files:
    PDF, DOCX, IPYNB, Code (.py, .js, .ts, etc.), Text (.txt, .md, .csv), and Images (<15ms).
    """
    if not os.path.exists(filepath):
        return {"error": "File does not exist"}
    if not os.path.isfile(filepath):
        return {"error": "Path is a directory, not a file"}

    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()
    size = os.path.getsize(filepath)

    def fmt_sz(bytes_val):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}" if unit != 'B' else f"{bytes_val} B"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} TB"

    # 1. PDF Documents
    if ext == '.pdf':
        if not HAS_PYPDF:
            return {
                "name": filename,
                "type": "PDF Document",
                "summary": f"PDF file ({fmt_sz(size)}). Install pypdf for full text extraction.",
                "snippet": ""
            }
        try:
            reader = pypdf.PdfReader(filepath)
            num_pages = len(reader.pages)
            extracted_text = ""
            for p in reader.pages[:3]:
                t = p.extract_text()
                if t:
                    extracted_text += t + " "
            cleaned = re.sub(r'\s+', ' ', extracted_text).strip()
            if cleaned:
                sentences = re.split(r'(?<=[.!?])\s+', cleaned)
                summary_text = " ".join(sentences[:2]) if len(sentences) >= 2 else sentences[0]
                if len(summary_text) > 180:
                    summary_text = summary_text[:177] + "..."
                return {
                    "name": filename,
                    "type": f"PDF Document ({num_pages} page{'s' if num_pages != 1 else ''})",
                    "pages": num_pages,
                    "summary": f"📄 {num_pages}-page PDF. Overview: {summary_text}",
                    "snippet": cleaned[:max_snippet_len]
                }
            else:
                return {
                    "name": filename,
                    "type": f"PDF Document ({num_pages} page{'s' if num_pages != 1 else ''})",
                    "pages": num_pages,
                    "summary": f"📄 Scanned or visual image PDF ({num_pages} page{'s' if num_pages != 1 else ''}, {fmt_sz(size)}). No text layer.",
                    "snippet": "(Visual or scanned document without selectable text)"
                }
        except Exception as e:
            return {
                "name": filename,
                "type": "PDF Document",
                "summary": f"Protected or encrypted PDF document ({fmt_sz(size)}).",
                "snippet": f"Preview unavailable: {str(e)}"
            }

    # 2. DOCX Word Documents
    if ext == '.docx':
        try:
            with zipfile.ZipFile(filepath) as zf:
                if 'word/document.xml' not in zf.namelist():
                    return {"name": filename, "type": "Word Document", "summary": f"Word file ({fmt_sz(size)})", "snippet": ""}
                xml_data = zf.read('word/document.xml')
                tree = ET.fromstring(xml_data)
                texts = [elem.text for elem in tree.iter() if elem.tag.endswith('}t') and elem.text]
                cleaned = re.sub(r'\s+', ' ', " ".join(texts)).strip()
                words = cleaned.split()
                if cleaned:
                    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
                    summary_text = " ".join(sentences[:2]) if len(sentences) >= 2 else sentences[0]
                    if len(summary_text) > 180:
                        summary_text = summary_text[:177] + "..."
                    return {
                        "name": filename,
                        "type": "Word Document (.docx)",
                        "summary": f"📝 Microsoft Word document (~{len(words)} words). Overview: {summary_text}",
                        "snippet": cleaned[:max_snippet_len]
                    }
                else:
                    return {
                        "name": filename,
                        "type": "Word Document (.docx)",
                        "summary": f"Empty or template Word document ({fmt_sz(size)}).",
                        "snippet": ""
                    }
        except Exception as e:
            return {
                "name": filename,
                "type": "Word Document (.docx)",
                "summary": f"Word Document ({fmt_sz(size)}).",
                "snippet": f"Preview unavailable: {str(e)}"
            }

    # 3. Jupyter Notebooks
    if ext == '.ipynb':
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                nb = json.load(f)
            cells = nb.get('cells', [])
            md_cells = []
            code_cells = []
            for c in cells:
                ctype = c.get('cell_type')
                src = "".join(c.get('source', []))
                if ctype == 'markdown' and src.strip():
                    md_cells.append(src.strip())
                elif ctype == 'code' and src.strip():
                    code_cells.append(src.strip())
            summary_parts = []
            if md_cells:
                first_md = md_cells[0].split('\n')[0].replace('#', '').strip()
                summary_parts.append(f"Header: {first_md}")
            summary_parts.append(f"{len(cells)} cells ({len(code_cells)} code, {len(md_cells)} markdown)")
            snippet = "\n\n".join(md_cells[:2] + code_cells[:1])[:max_snippet_len]
            return {
                "name": filename,
                "type": "Jupyter Notebook (.ipynb)",
                "summary": f"🪐 {' | '.join(summary_parts)}",
                "snippet": snippet
            }
        except Exception as e:
            return {"name": filename, "type": "Jupyter Notebook", "summary": f"Notebook file ({fmt_sz(size)})", "snippet": str(e)}

    # 4. Text & Code Files
    code_or_text_exts = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json', '.txt',
        '.md', '.csv', '.xml', '.yaml', '.yml', '.sql', '.sh', '.bat', '.ps1',
        '.c', '.cpp', '.h', '.hpp', '.java', '.go', '.rs', '.php', '.ini', '.cfg', '.log'
    }
    if ext in code_or_text_exts or size < 100 * 1024:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [f.readline() for _ in range(30)]
            non_empty = [l.rstrip() for l in lines if l.strip()]
            if non_empty:
                first_line = non_empty[0][:120]
                summary = f"💻 {ext.upper().replace('.', '')} source file. First line: {first_line}"
                snippet = "\n".join(non_empty[:15])[:max_snippet_len]
                return {
                    "name": filename,
                    "type": f"{ext.upper().replace('.', '')} File",
                    "summary": summary,
                    "snippet": snippet
                }
        except Exception:
            pass

    # 5. Images
    if ext in {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.svg'}:
        if HAS_PIL and ext != '.svg':
            try:
                with Image.open(filepath) as im:
                    w, h = im.size
                    mode = im.mode
                return {
                    "name": filename,
                    "type": f"Image ({im.format or ext.replace('.', '').upper()})",
                    "summary": f"🖼️ Image resolution: {w} × {h} pixels ({mode} mode, {fmt_sz(size)})",
                    "snippet": f"Dimensions: {w}x{h} px\nFormat: {ext.replace('.', '').upper()}\nFile Size: {fmt_sz(size)}"
                }
            except Exception:
                pass
        return {
            "name": filename,
            "type": "Image",
            "summary": f"🖼️ Image asset ({fmt_sz(size)})",
            "snippet": f"Image format: {ext.replace('.', '').upper()}"
        }

    # 6. Fallback
    return {
        "name": filename,
        "type": f"{ext.upper().replace('.', '')} File",
        "summary": f"📁 File ({fmt_sz(size)})",
        "snippet": f"Path: {filepath}\nSize: {fmt_sz(size)}"
    }


def search_file_content(filepath, query_str):
    """Searches inside readable text, docx, or pdf files for query_str."""
    if not query_str:
        return (False, None)
    q = query_str.strip().lower()
    if not q:
        return (False, None)

    ext = os.path.splitext(filepath)[1].lower()
    try:
        # PDF
        if ext == '.pdf' and HAS_PYPDF:
            reader = pypdf.PdfReader(filepath)
            for page_idx, page in enumerate(reader.pages[:8]):
                t = page.extract_text()
                if t and q in t.lower():
                    idx = t.lower().find(q)
                    start = max(0, idx - 50)
                    end = min(len(t), idx + len(q) + 50)
                    snippet = f"Page {page_idx + 1}: ..." + t[start:end].replace('\n', ' ').strip() + "..."
                    return (True, snippet)
            return (False, None)

        # DOCX
        if ext == '.docx':
            with zipfile.ZipFile(filepath) as zf:
                if 'word/document.xml' in zf.namelist():
                    xml_data = zf.read('word/document.xml')
                    tree = ET.fromstring(xml_data)
                    texts = [elem.text for elem in tree.iter() if elem.tag.endswith('}t') and elem.text]
                    full_text = " ".join(texts)
                    if q in full_text.lower():
                        idx = full_text.lower().find(q)
                        start = max(0, idx - 50)
                        end = min(len(full_text), idx + len(q) + 50)
                        snippet = "..." + full_text[start:end].strip() + "..."
                        return (True, snippet)
            return (False, None)

        # Text/code
        text_exts = {'.txt', '.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.csv', '.xml', '.ipynb', '.sql', '.yaml', '.yml', '.c', '.cpp', '.java'}
        if ext in text_exts or os.path.getsize(filepath) < 2 * 1024 * 1024:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line_idx, line in enumerate(f):
                    if line_idx > 1000:
                        break
                    if q in line.lower():
                        return (True, f"Line {line_idx + 1}: {line.strip()[:140]}")
            return (False, None)
    except Exception:
        return (False, None)

    return (False, None)


# --- 1-CLICK FOLDER ORGANIZER ---
ORGANIZER_CATEGORIES = {
    "Documents": {'.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.csv', '.rtf', '.odt', '.epub'},
    "Installers": {'.exe', '.msi', '.iso', '.dmg', '.pkg', '.apk', '.msix'},
    "Code": {'.py', '.js', '.ts', '.html', '.css', '.json', '.cpp', '.c', '.java', '.ipynb', '.sql', '.sh', '.bat', '.ps1', '.yml', '.yaml', '.xml', '.php', '.go', '.rs'},
    "Archives": {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tgz'},
    "Images": {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.bmp', '.tiff', '.ico', '.psd'},
    "Media": {'.mp3', '.mp4', '.wav', '.mkv', '.avi', '.flac', '.mov', '.m4a', '.webm'}
}

ORGANIZER_UNDO_HISTORY = []

def scan_organize_folder(folder_path):
    abs_folder = os.path.abspath(folder_path)
    if not os.path.exists(abs_folder) or not os.path.isdir(abs_folder):
        raise ValueError(f"Directory not found: {abs_folder}")

    category_buckets = defaultdict(list)
    total_loose_files = 0
    total_loose_bytes = 0

    skip_names = {'desktop.ini', 'thumbs.db', '.ds_store'}

    with os.scandir(abs_folder) as it:
        for entry in it:
            try:
                if not entry.is_file(follow_symlinks=False):
                    continue
                name_lower = entry.name.lower()
                if name_lower in skip_names or entry.name.startswith('~$') or entry.name.startswith('.'):
                    continue

                size = entry.stat().st_size
                ext = os.path.splitext(name_lower)[1]

                matched_category = "Other"
                for cat_name, ext_set in ORGANIZER_CATEGORIES.items():
                    if ext in ext_set:
                        matched_category = cat_name
                        break

                category_buckets[matched_category].append({
                    "name": entry.name,
                    "path": entry.path,
                    "size": size,
                    "ext": ext
                })
                total_loose_files += 1
                total_loose_bytes += size
            except OSError:
                continue

    return {
        "folder": abs_folder,
        "total_loose_files": total_loose_files,
        "total_loose_bytes": total_loose_bytes,
        "categories": dict(category_buckets),
        "can_undo": len(ORGANIZER_UNDO_HISTORY) > 0
    }

def apply_organize_folder(folder_path, selected_categories=None):
    abs_folder = os.path.abspath(folder_path)
    scan_res = scan_organize_folder(abs_folder)
    categories = scan_res["categories"]

    moves_record = []
    created_dirs = set()

    for cat_name, files in categories.items():
        if selected_categories and cat_name not in selected_categories:
            continue
        if cat_name == "Other" and not selected_categories:
            continue
        if not files:
            continue

        target_dir = os.path.join(abs_folder, cat_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            created_dirs.add(target_dir)

        for finfo in files:
            src = finfo["path"]
            dst = os.path.join(target_dir, finfo["name"])

            if os.path.exists(dst) and dst != src:
                base, ext = os.path.splitext(finfo["name"])
                dst = os.path.join(target_dir, f"{base}_{int(time.time())}{ext}")

            try:
                shutil.move(src, dst)
                moves_record.append({
                    "from": src,
                    "to": dst,
                    "category": cat_name,
                    "name": finfo["name"]
                })
            except Exception as e:
                print(f"Failed to move {src} -> {dst}: {e}")

    if moves_record:
        ORGANIZER_UNDO_HISTORY.append({
            "folder": abs_folder,
            "timestamp": time.time(),
            "moves": moves_record,
            "created_dirs": list(created_dirs)
        })

    return {
        "success": True,
        "folder": abs_folder,
        "moved_count": len(moves_record),
        "can_undo": len(ORGANIZER_UNDO_HISTORY) > 0
    }

def undo_organize_folder():
    if not ORGANIZER_UNDO_HISTORY:
        raise ValueError("No organization history available to undo.")

    last_op = ORGANIZER_UNDO_HISTORY.pop()
    moves = last_op.get("moves", [])
    created_dirs = last_op.get("created_dirs", [])
    restored_count = 0

    for m in moves:
        curr_path = m["to"]
        orig_path = m["from"]
        if os.path.exists(curr_path):
            try:
                os.makedirs(os.path.dirname(orig_path), exist_ok=True)
                shutil.move(curr_path, orig_path)
                restored_count += 1
            except Exception as e:
                print(f"Undo move failed {curr_path} -> {orig_path}: {e}")

    cleaned_folders = []
    for cdir in created_dirs:
        try:
            if os.path.exists(cdir) and not os.listdir(cdir):
                os.rmdir(cdir)
                cleaned_folders.append(os.path.basename(cdir))
        except OSError:
            pass

    return {
        "success": True,
        "folder": last_op.get("folder"),
        "restored_count": restored_count,
        "cleaned_folders": cleaned_folders,
        "remaining_undo_count": len(ORGANIZER_UNDO_HISTORY)
    }


# --- DEVELOPER & CACHE JUNK SWEEPER ---
DEV_CACHE_DIRS = {
    'node_modules': 'Node.js dependency packages',
    '__pycache__': 'Python compiled bytecode',
    '.venv': 'Python virtual environment',
    'venv': 'Python virtual environment',
    '.gradle': 'Gradle build cache',
    '.tmp': 'Temporary scratch files',
    '.temp': 'Temporary scratch files',
    '.pytest_cache': 'Pytest run cache',
    '.turbo': 'Turborepo cache',
    '.next': 'Next.js build cache',
    '.nuget': 'NuGet package cache',
    'bin': 'Compiled binaries / build artifacts',
    'obj': 'Compiler intermediate objects'
}

def fast_calc_dir_size(path, max_items=25000):
    total_sz = 0
    item_cnt = 0
    stack = [path]
    while stack and item_cnt < max_items:
        curr = stack.pop()
        try:
            with os.scandir(curr) as it:
                for entry in it:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            total_sz += entry.stat().st_size
                            item_cnt += 1
                        elif entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                    except OSError:
                        continue
        except OSError:
            continue
    return total_sz, item_cnt

def scan_dev_caches(root_path, time_limit_sec=20):
    target = os.path.abspath(root_path) if root_path != "ALL_DRIVES" else "ALL_DRIVES"
    roots = get_available_drives() if target == "ALL_DRIVES" else [target]

    found_caches = []
    total_reclaimable = 0
    stack = list(roots)
    visited = set()
    start_time = time.time()

    skip_dirs = {
        '$recycle.bin', 'system volume information', 'recovery', 'windows',
        'program files', 'program files (x86)', 'programdata'
    }

    while stack and len(found_caches) < 200:
        if time.time() - start_time > time_limit_sec:
            break
        curr = stack.pop()
        norm = curr.lower()
        if norm in visited:
            continue
        visited.add(norm)

        try:
            with os.scandir(curr) as it:
                for entry in it:
                    try:
                        if not entry.is_dir(follow_symlinks=False):
                            continue
                        name_lower = entry.name.lower()
                        if name_lower in skip_dirs or entry.name.startswith('$'):
                            continue

                        if name_lower in DEV_CACHE_DIRS:
                            sz, cnt = fast_calc_dir_size(entry.path)
                            if sz > 0:
                                desc = DEV_CACHE_DIRS[name_lower]
                                found_caches.append({
                                    "name": entry.name,
                                    "path": entry.path,
                                    "size": sz,
                                    "files_count": cnt,
                                    "description": desc,
                                    "parent": curr
                                })
                                total_reclaimable += sz
                            continue

                        if not entry.name.startswith('.'):
                            stack.append(entry.path)
                    except OSError:
                        continue
        except (PermissionError, OSError):
            continue

    found_caches.sort(key=lambda x: -x["size"])

    return {
        "root": target,
        "total_caches_found": len(found_caches),
        "total_reclaimable_bytes": total_reclaimable,
        "caches": found_caches,
        "time_elapsed": round(time.time() - start_time, 3)
    }

def clean_dev_caches(paths):
    cleaned = []
    failed = []
    reclaimed_bytes = 0

    for p in paths:
        abs_p = os.path.abspath(p)
        if not os.path.exists(abs_p):
            continue
        try:
            sz, _ = fast_calc_dir_size(abs_p)
            move_to_recycle_bin(abs_p)
            cleaned.append(abs_p)
            reclaimed_bytes += sz
        except Exception as e:
            failed.append({"path": abs_p, "error": str(e)})

    return {
        "success": True,
        "cleaned_count": len(cleaned),
        "reclaimed_bytes": reclaimed_bytes,
        "failed": failed
    }


class FileSystemDFS:
    def __init__(self, root_path):
        if root_path in ("ALL_DRIVES", "all-disks", "all-drives", "all"):
            self.root_path = "ALL_DRIVES"
            self.is_all_drives = True
            self.roots = get_available_drives()
            self.is_drive_root = True
        else:
            self.root_path = os.path.abspath(root_path)
            self.is_all_drives = False
            self.roots = [self.root_path]
            drive, tail = os.path.splitdrive(self.root_path)
            self.is_drive_root = (tail in ('\\', '/', ''))
            if not os.path.exists(self.root_path):
                raise FileNotFoundError(f"The path {self.root_path} does not exist.")

    def find_file(self, target_filename="", max_results=1000, time_limit_sec=25, search_content=False, file_types=None):
        matches = []
        stack_trace_samples = []
        stack = list(self.roots)
        visited = set()
        scanned_count = 0
        start_time = time.time()
        target = target_filename.strip().lower()

        if self.is_drive_root:
            skip_dirs = {
                '$recycle.bin', 'system volume information', 'recovery', 'onedrivetemp', 'perflogs',
                'windows', 'program files', 'program files (x86)', 'programdata', 'drivers',
                'appdata', 'application data', 'local settings', 'winsxs', 'temp', 'cache', '.cache',
                '.git', '.svn', '.vs', 'node_modules', 'venv', '.venv', '__pycache__',
                '.android', '.gradle', '.cargo', '.gemini', '.vscode', '.vscode-shared',
                '.claude', '.copilot', '.jupyter', '.ipython', 'mingw', 'keil_v5', 'inetpub'
            }
        else:
            skip_dirs = {
                '$recycle.bin', 'system volume information', 'recovery',
                '.git', '.svn', '.vs', '.cache', 'appdata', 'temp', 'cache', 'winsxs'
            }

        if any(sk in self.root_path.lower() for sk in ('appdata', 'temp', 'cache', 'winsxs', 'windows', 'program files')):
            for sk in ('appdata', 'temp', 'cache', 'winsxs', 'windows', 'program files'):
                skip_dirs.discard(sk)

        def dir_priority(p):
            n = os.path.basename(p).lower()
            if n == 'users': return 100
            if 'shareef' in n: return 90
            if 'onedrive' in n: return 85
            if n in ('downloads', 'desktop', 'documents', 'pictures', 'videos', 'music'): return 80
            return 10

        while stack and len(matches) < max_results:
            if time.time() - start_time > time_limit_sec:
                break

            current_path = stack.pop()
            norm_path = current_path.lower()
            if norm_path in visited:
                continue
            visited.add(norm_path)
            scanned_count += 1

            if len(stack_trace_samples) < 50:
                stack_trace_samples.append({
                    "action": "POP",
                    "path": current_path,
                    "depth": len(stack)
                })

            subdirs_to_push = []
            try:
                with os.scandir(current_path) as it:
                    for entry in it:
                        try:
                            name_lower = entry.name.lower()
                            is_dir = entry.is_dir(follow_symlinks=False)
                            is_file = not is_dir
                            ext = os.path.splitext(name_lower)[1]

                            if is_file and file_types:
                                if ext not in file_types:
                                    continue

                            matched_by_name = (not target or target in name_lower)
                            matched_by_content = False
                            content_snippet = None

                            if is_file and search_content and target:
                                if ext in {'.txt', '.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.csv', '.pdf', '.docx', '.ipynb'}:
                                    if not matched_by_name:
                                        try:
                                            if entry.stat().st_size < 10 * 1024 * 1024:
                                                matched_by_content, content_snippet = search_file_content(entry.path, target)
                                        except OSError:
                                            pass
                                    else:
                                        try:
                                            if entry.stat().st_size < 5 * 1024 * 1024:
                                                _, content_snippet = search_file_content(entry.path, target)
                                        except OSError:
                                            pass

                            if matched_by_name or matched_by_content:
                                fsize = 0
                                if is_file:
                                    try:
                                        fsize = entry.stat().st_size
                                    except OSError:
                                        fsize = 0
                                match_item = {
                                    "path": entry.path,
                                    "name": entry.name,
                                    "type": "directory" if is_dir else "file",
                                    "size": fsize,
                                    "dir": current_path,
                                    "ext": ext
                                }
                                if content_snippet:
                                    match_item["snippet"] = content_snippet
                                matches.append(match_item)
                                if len(matches) >= max_results:
                                    break

                            if is_dir:
                                if name_lower not in skip_dirs and not entry.name.startswith('$') and not entry.name.startswith('.'):
                                    subdirs_to_push.append(entry.path)
                        except OSError:
                            continue
            except (PermissionError, OSError):
                continue

            if self.is_drive_root:
                subdirs_to_push.sort(key=dir_priority)
            for d in subdirs_to_push:
                stack.append(d)
                if len(stack_trace_samples) < 50:
                    stack_trace_samples.append({
                        "action": "PUSH",
                        "path": d,
                        "depth": len(stack)
                    })

        return {
            "root": self.root_path,
            "target": target_filename,
            "scanned_directories": scanned_count,
            "matches_count": len(matches),
            "matches": matches[:max_results],
            "stack_trace_samples": stack_trace_samples,
            "time_elapsed": round(time.time() - start_time, 3)
        }

    def find_duplicates(self, max_files=10000, time_limit_sec=12):
        files_by_size = defaultdict(list)
        files_by_stem = defaultdict(list)
        stack = list(self.roots)
        visited = set()
        total_scanned_files = 0
        start_time = time.time()

        if self.is_drive_root:
            skip_dirs = {
                '$recycle.bin', 'system volume information', 'recovery', 'onedrivetemp', 'perflogs',
                'windows', 'program files', 'program files (x86)', 'programdata', 'drivers',
                'appdata', 'application data', 'local settings', 'winsxs', 'temp', 'cache', '.cache',
                '.git', '.svn', '.vs', 'node_modules', 'venv', '.venv', '__pycache__',
                '.android', '.gradle', '.cargo', '.gemini', '.vscode', '.vscode-shared',
                '.claude', '.copilot', '.jupyter', '.ipython', 'mingw', 'keil_v5', 'inetpub'
            }
        else:
            skip_dirs = {
                '$recycle.bin', 'system volume information', 'recovery',
                '.git', '.svn', '.vs', '.cache', 'appdata', 'temp', 'cache', 'winsxs'
            }

        skip_exts = {'.sys', '.dat', '.blf', '.regtrans-ms', '.tmp', '.lock', '.log', '.ini', '.db', '.lnk'}
        skip_files = {'desktop.ini', 'thumbs.db', '.ds_store'}

        def dir_priority(p):
            n = os.path.basename(p).lower()
            if n == 'users': return 100
            if 'shareef' in n: return 90
            if 'onedrive' in n: return 85
            if n in ('downloads', 'desktop', 'documents', 'pictures', 'videos', 'music'): return 80
            return 10

        while stack and total_scanned_files < max_files:
            if time.time() - start_time > time_limit_sec:
                break

            current_path = stack.pop()
            norm_path = current_path.lower()
            if norm_path in visited:
                continue
            visited.add(norm_path)

            subdirs_to_push = []
            try:
                with os.scandir(current_path) as it:
                    for entry in it:
                        try:
                            name_lower = entry.name.lower()
                            if entry.is_dir(follow_symlinks=False):
                                if name_lower not in skip_dirs and not entry.name.startswith('$') and not entry.name.startswith('.'):
                                    subdirs_to_push.append(entry.path)
                            elif entry.is_file(follow_symlinks=False):
                                ext = os.path.splitext(name_lower)[1]
                                if name_lower in skip_files or ext in skip_exts or entry.name.startswith('~$') or entry.name.startswith('.') or name_lower.startswith('ntuser.'):
                                    continue
                                try:
                                    st = entry.stat()
                                    size = st.st_size
                                    mtime = st.st_mtime
                                    if size > 20:
                                        finfo = {
                                            "path": entry.path,
                                            "name": entry.name,
                                            "size": size,
                                            "mtime": mtime
                                        }
                                        files_by_size[size].append(finfo)

                                        base, _ = os.path.splitext(entry.name)
                                        norm_stem = re.sub(r'(_copy|_backup|_v\d+|_edit|_new|_old|- copy|\(\d+\))$', '', base, flags=re.IGNORECASE).lower().strip()
                                        if len(norm_stem) >= 3:
                                            files_by_stem[(norm_stem, ext)].append(finfo)

                                        total_scanned_files += 1
                                except OSError:
                                    continue
                        except OSError:
                            continue
            except (PermissionError, OSError):
                continue

            if self.is_drive_root:
                subdirs_to_push.sort(key=dir_priority)
            for d in subdirs_to_push:
                stack.append(d)

        collisions = {sz: items for sz, items in files_by_size.items() if len(items) > 1}

        sample_groups = defaultdict(list)
        for sz, items in collisions.items():
            for it in items:
                sh = self._sample_hash(it["path"])
                if sh:
                    sample_groups[(sz, sh)].append(it)

        exact_hash_groups = defaultdict(list)
        for (sz, sh), items in sample_groups.items():
            if len(items) > 1:
                for it in items:
                    fh = self._fast_hash(it["path"], sz)
                    if fh:
                        exact_hash_groups[fh].append(it)

        processed_paths = set()
        clusters = []
        reclaimable_bytes = 0

        for h, items in exact_hash_groups.items():
            if len(items) > 1:
                items_sorted = sorted(items, key=lambda x: (x.get("mtime", 0), len(x["path"])))
                orig_item = items_sorted[0]
                cluster_files = []

                cluster_files.append({
                    "name": orig_item["name"],
                    "path": orig_item["path"],
                    "size": orig_item["size"],
                    "role": "original",
                    "badge": "ORIGINAL",
                    "details": "Baseline original file"
                })
                processed_paths.add(orig_item["path"].lower())

                for copy_item in items_sorted[1:]:
                    cluster_files.append({
                        "name": copy_item["name"],
                        "path": copy_item["path"],
                        "size": copy_item["size"],
                        "role": "exact_duplicate",
                        "badge": "EXACT DITTO",
                        "details": "100% identical byte-for-byte copy"
                    })
                    processed_paths.add(copy_item["path"].lower())

                wasted = orig_item["size"] * (len(items) - 1)
                reclaimable_bytes += wasted

                clusters.append({
                    "title": f"{orig_item['name']} ({len(items)} identical copies)",
                    "hash": h,
                    "wasted_bytes": wasted,
                    "has_edited": False,
                    "files": cluster_files
                })

        image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff'}
        text_exts = {'.txt', '.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.csv', '.xml', '.c', '.cpp', '.java', '.bat', '.cmd', '.ps1', '.sh', '.yml', '.yaml', '.ini', '.cfg', '.conf', '.sql'}

        for (stem, ext), items in files_by_stem.items():
            if len(items) > 1:
                unassigned = [it for it in items if it["path"].lower() not in processed_paths]
                if len(unassigned) < 1:
                    continue

                items_sorted = sorted(items, key=lambda x: (x.get("mtime", 0), len(x["path"])))
                base_item = items_sorted[0]
                duplicate_files = []
                edited_files = []

                for other in items_sorted[1:]:
                    if other["path"].lower() in processed_paths:
                        continue

                    if base_item["size"] == other["size"]:
                        h_base = self._fast_hash(base_item["path"], base_item["size"])
                        h_other = self._fast_hash(other["path"], other["size"])
                        if h_base and h_other and h_base == h_other:
                            duplicate_files.append((other, "100% identical byte-for-byte copy"))
                            processed_paths.add(other["path"].lower())
                            continue

                    if ext in image_exts:
                        img_status, img_details = analyze_image_pair(base_item["path"], other["path"])
                        if img_status == 'duplicate':
                            duplicate_files.append((other, img_details))
                            processed_paths.add(other["path"].lower())
                        elif img_status.startswith('edited'):
                            edited_files.append((other, img_details))
                            processed_paths.add(other["path"].lower())
                    elif ext in text_exts and base_item["size"] < 300000 and other["size"] < 300000:
                        try:
                            with open(base_item["path"], "r", encoding="utf-8", errors="ignore") as f1:
                                t1 = f1.read(4096)
                            with open(other["path"], "r", encoding="utf-8", errors="ignore") as f2:
                                t2 = f2.read(4096)
                            if t1 == t2:
                                duplicate_files.append((other, "Identical text content"))
                                processed_paths.add(other["path"].lower())
                            else:
                                matcher = difflib.SequenceMatcher(None, t1, t2)
                                ratio = matcher.quick_ratio()
                                if ratio >= 0.80:
                                    sim_pct = round(ratio * 100, 1)
                                    edited_files.append((other, f"Content modified ({sim_pct}% similarity)"))
                                    processed_paths.add(other["path"].lower())
                        except Exception:
                            pass

                if duplicate_files:
                    cluster_files = [{
                        "name": base_item["name"],
                        "path": base_item["path"],
                        "size": base_item["size"],
                        "role": "original",
                        "badge": "ORIGINAL",
                        "details": "Baseline original file"
                    }]
                    processed_paths.add(base_item["path"].lower())

                    wasted = 0
                    for df, note in duplicate_files:
                        cluster_files.append({
                            "name": df["name"],
                            "path": df["path"],
                            "size": df["size"],
                            "role": "exact_duplicate",
                            "badge": "EXACT DITTO",
                            "details": note
                        })
                        wasted += df["size"]

                    reclaimable_bytes += wasted
                    clusters.append({
                        "title": f"{base_item['name']} ({len(cluster_files)} identical/duplicate copies)",
                        "hash": self._sample_hash(base_item["path"]) or "dup_cluster",
                        "wasted_bytes": wasted,
                        "has_edited": False,
                        "files": cluster_files
                    })

                if edited_files:
                    cluster_files = [{
                        "name": base_item["name"],
                        "path": base_item["path"],
                        "size": base_item["size"],
                        "role": "original",
                        "badge": "ORIGINAL",
                        "details": "Baseline original file"
                    }]
                    processed_paths.add(base_item["path"].lower())

                    for ef, note in edited_files:
                        cluster_files.append({
                            "name": ef["name"],
                            "path": ef["path"],
                            "size": ef["size"],
                            "role": "edited",
                            "badge": "EDITED VERSION",
                            "details": f"{note} — open to check changes"
                        })

                    clusters.append({
                        "title": f"{base_item['name']} (Original + {len(edited_files)} Edited Version{'s' if len(edited_files) > 1 else ''})",
                        "hash": self._sample_hash(base_item["path"]) or "edited_cluster",
                        "wasted_bytes": 0,
                        "has_edited": True,
                        "files": cluster_files
                    })

        clusters.sort(key=lambda x: (not x.get("has_edited", False), -x["wasted_bytes"], -len(x["files"])))

        return {
            "root": self.root_path,
            "total_files_scanned": total_scanned_files,
            "duplicate_groups_count": len(clusters),
            "reclaimable_bytes": reclaimable_bytes,
            "duplicate_groups": clusters[:60],
            "time_elapsed": round(time.time() - start_time, 3)
        }

    def _sample_hash(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read(4096)).hexdigest()
        except Exception:
            return None

    def _fast_hash(self, filepath, size):
        try:
            h = hashlib.md5()
            if size <= 256 * 1024:
                with open(filepath, 'rb') as f:
                    h.update(f.read())
                return h.hexdigest()
            with open(filepath, 'rb') as f:
                h.update(f.read(64 * 1024))
                f.seek(max(0, size - 64 * 1024))
                h.update(f.read(64 * 1024))
                if size > 1024 * 1024:
                    f.seek(size // 2)
                    h.update(f.read(64 * 1024))
            return h.hexdigest()
        except Exception:
            return None

    def get_tree_structure(self, max_depth=2, max_children_per_dir=300):
        if self.is_all_drives:
            root_node = {
                "name": "My PC (All Drives)",
                "path": "ALL_DRIVES",
                "type": "directory",
                "children": []
            }
            skip_dirs = {'$recycle.bin', 'system volume information', 'recovery', '.git', '.vs', '.cache', 'appdata'}
            for d in self.roots:
                drive_node = {
                    "name": f"Local Disk ({d})",
                    "path": d,
                    "type": "directory",
                    "children": []
                }
                try:
                    entries = []
                    with os.scandir(d) as it:
                        for entry in it:
                            try:
                                if entry.name.lower() in skip_dirs or entry.name.startswith('$'):
                                    continue
                                is_dir = entry.is_dir(follow_symlinks=False)
                                fsize = entry.stat().st_size if not is_dir else 0
                                entries.append((entry.name, entry.path, is_dir, fsize))
                            except OSError:
                                continue
                    entries.sort(key=lambda x: (not x[2], x[0].lower()))
                    for ename, epath, is_dir, fsize in entries[:max_children_per_dir]:
                        drive_node["children"].append({
                            "name": ename,
                            "path": epath,
                            "type": "directory" if is_dir else "file",
                            "size": fsize,
                            "children": []
                        })
                except (PermissionError, OSError):
                    pass
                root_node["children"].append(drive_node)
            return root_node

        def build_node(path, current_depth):
            name = os.path.basename(path) or path
            node = {
                "name": name,
                "path": path,
                "type": "directory" if os.path.isdir(path) else "file",
                "children": []
            }
            if not os.path.isdir(path) or current_depth >= max_depth:
                return node

            skip_dirs = {'$recycle.bin', 'system volume information', 'recovery', '.git', '.vs', '.cache', 'appdata', 'temp'}
            try:
                entries = []
                with os.scandir(path) as it:
                    for entry in it:
                        try:
                            if entry.name.lower() in skip_dirs or entry.name.startswith('.'):
                                continue
                            is_dir = entry.is_dir(follow_symlinks=False)
                            fsize = entry.stat().st_size if not is_dir else 0
                            entries.append((entry.name, entry.path, is_dir, fsize))
                        except OSError:
                            continue
                entries.sort(key=lambda x: (not x[2], x[0].lower()))
                for ename, epath, is_dir, fsize in entries[:max_children_per_dir]:
                    if is_dir:
                        node["children"].append(build_node(epath, current_depth + 1))
                    else:
                        node["children"].append({
                            "name": ename,
                            "path": epath,
                            "type": "file",
                            "size": fsize
                        })
            except (PermissionError, OSError):
                return node

            return node

        return build_node(self.root_path, 0)

    def get_children(self, dir_path, max_items=500):
        children = []
        try:
            with os.scandir(dir_path) as it:
                for entry in it:
                    try:
                        is_dir = entry.is_dir(follow_symlinks=False)
                        fsize = entry.stat().st_size if not is_dir else 0
                        children.append({
                            "name": entry.name,
                            "path": entry.path,
                            "type": "directory" if is_dir else "file",
                            "size": fsize
                        })
                    except OSError:
                        continue
            children.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
        except (PermissionError, OSError):
            pass
        return children[:max_items]

    def get_dashboard_summary(self, max_items=12000, time_limit_sec=6.0):
        stack = list(self.roots)
        visited = set()
        file_count = 0
        dir_count = 0
        total_size = 0
        type_distribution = defaultdict(int)
        size_collisions = defaultdict(int)
        start_time = time.time()

        skip_dirs = {
            '$recycle.bin', 'system volume information', 'recovery',
            '.git', '.svn', '.vs', '.cache', 'appdata', 'temp', 'cache', 'winsxs'
        }

        while stack and (file_count + dir_count) < max_items:
            if time.time() - start_time > time_limit_sec:
                break
            curr = stack.pop()
            norm = curr.lower()
            if norm in visited:
                continue
            visited.add(norm)
            dir_count += 1

            try:
                with os.scandir(curr) as it:
                    for entry in it:
                        try:
                            if entry.is_dir(follow_symlinks=False):
                                if entry.name.lower() not in skip_dirs and not entry.name.startswith('$') and not entry.name.startswith('.'):
                                    stack.append(entry.path)
                            elif entry.is_file(follow_symlinks=False):
                                file_count += 1
                                st = entry.stat()
                                sz = st.st_size
                                total_size += sz
                                ext = os.path.splitext(entry.name.lower())[1]
                                type_distribution[ext or 'none'] += 1
                                if sz > 100:
                                    size_collisions[sz] += 1
                        except OSError:
                            continue
            except (PermissionError, OSError):
                continue

        potential_dups = sum(cnt - 1 for cnt in size_collisions.values() if cnt > 1)

        return {
            "root": self.root_path,
            "files_count": file_count,
            "dirs_count": dir_count,
            "total_size": total_size,
            "potential_duplicates_estimate": potential_dups,
            "top_extensions": sorted(type_distribution.items(), key=lambda x: -x[1])[:8],
            "time_elapsed": round(time.time() - start_time, 3)
        }


def move_to_recycle_bin(filepath):
    abs_path = os.path.abspath(filepath)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {abs_path}")

    try:
        import send2trash
        send2trash.send2trash(abs_path)
        return True
    except Exception:
        pass

    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class SHFILEOPSTRUCTW(ctypes.Structure):
            _fields_ = [
                ('hwnd', wintypes.HWND),
                ('wFunc', wintypes.UINT),
                ('pFrom', wintypes.LPCWSTR),
                ('pTo', wintypes.LPCWSTR),
                ('fFlags', wintypes.WORD),
                ('fAnyOperationsAborted', wintypes.BOOL),
                ('hNameMappings', wintypes.LPVOID),
                ('lpszProgressTitle', wintypes.LPCWSTR)
            ]

        FO_DELETE = 0x0003
        FOF_ALLOWUNDO = 0x0040
        FOF_NOCONFIRMATION = 0x0010
        FOF_SILENT = 0x0004

        fileop = SHFILEOPSTRUCTW()
        fileop.hwnd = None
        fileop.wFunc = FO_DELETE
        fileop.pFrom = abs_path + '\0\0'
        fileop.pTo = None
        fileop.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
        res = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(fileop))
        if res != 0:
            raise OSError(f"Failed to move to Recycle Bin (error code {res})")
        return True
    else:
        res = subprocess.run(['gio', 'trash', abs_path], capture_output=True)
        if res.returncode == 0:
            return True
        os.remove(abs_path)
        return True


def get_available_drives():
    drives = []
    if sys.platform == "win32":
        for letter in string.ascii_uppercase:
            drive_path = f"{letter}:\\"
            if os.path.exists(drive_path):
                drives.append(f"{letter}:\\")
    else:
        drives.append("/")
    return drives


class PathDiverHandler(SimpleHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
        self.wfile.write(body)

    def _send_file(self, filename, content_type):
        filepath = os.path.join(BASE_RESOURCE_DIR, filename)
        if not os.path.exists(filepath):
            filepath = os.path.join(os.getcwd(), filename)
        if not os.path.exists(filepath):
            self.send_error(404, f"File not found: {filename}")
            return
        with open(filepath, 'rb') as f:
            content = f.read()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Static Assets
        if path in ('/', '/index.html'):
            self._send_file('index.html', 'text/html; charset=utf-8')
            return
        elif path == '/style.css':
            self._send_file('style.css', 'text/css; charset=utf-8')
            return
        elif path == '/app.js':
            self._send_file('app.js', 'application/javascript; charset=utf-8')
            return
        elif path == '/PathDiver_Offline.html':
            self._send_file('PathDiver_Offline.html', 'text/html; charset=utf-8')
            return
        elif path == '/favicon.ico':
            self.send_response(204)
            super().end_headers()
            return

        # 2. REST API Endpoints
        if path == '/api/drives':
            drives = get_available_drives()
            user_home = os.path.expanduser("~")
            downloads = get_real_user_folder("Downloads")
            documents = get_real_user_folder("Documents")
            desktop = get_real_user_folder("Desktop")
            pictures = get_real_user_folder("Pictures")
            videos = get_real_user_folder("Videos")
            music = get_real_user_folder("Music")
            scratch_path = os.path.abspath(os.path.join(user_home, ".gemini", "antigravity", "scratch"))

            self._send_json(200, {
                "drives": drives,
                "user_home": user_home,
                "downloads": downloads,
                "documents": documents,
                "desktop": desktop,
                "pictures": pictures,
                "videos": videos,
                "music": music,
                "scratch_dir": scratch_path if os.path.exists(scratch_path) else user_home
            })
            return

        elif path == '/api/dashboard':
            target_path = query.get('path', ['.'])[0]
            try:
                agent = FileSystemDFS(target_path)
                data = agent.get_dashboard_summary()
                self._send_json(200, {"success": True, "data": data})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == '/api/tree':
            target = query.get('path', ['.'])[0]
            try:
                depth = int(query.get('depth', ['2'])[0])
            except ValueError:
                depth = 2
            try:
                agent = FileSystemDFS(target)
                tree = agent.get_tree_structure(max_depth=depth, max_children_per_dir=300)
                self._send_json(200, {"success": True, "tree": tree})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == '/api/children':
            target_path = query.get('path', [''])[0].strip()
            try:
                agent = FileSystemDFS(target_path if os.path.isdir(target_path) else os.path.dirname(target_path))
                children = agent.get_children(target_path)
                self._send_json(200, {"success": True, "children": children})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == '/api/find':
            target_path = query.get('path', ['.'])[0]
            query_str = query.get('q', [''])[0]
            search_content = query.get('content', ['0'])[0].lower() in ('1', 'true', 'yes')
            exts_raw = query.get('exts', [''])[0].strip()
            file_types = set(exts_raw.lower().split(',')) if exts_raw else None
            try:
                limit = int(query.get('limit', ['1000'])[0])
            except ValueError:
                limit = 1000
            try:
                timeout = float(query.get('timeout', ['25'])[0])
            except ValueError:
                timeout = 25.0
            try:
                agent = FileSystemDFS(target_path)
                result = agent.find_file(query_str, max_results=limit, time_limit_sec=timeout, search_content=search_content, file_types=file_types)
                self._send_json(200, {"success": True, "data": result})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == '/api/peek':
            target_path = query.get('path', [''])[0].strip()
            if not target_path or target_path.startswith('virtual://'):
                self._send_json(400, {"success": False, "error": "Invalid or virtual path"})
                return
            try:
                preview = extract_file_preview_and_summary(target_path)
                self._send_json(200, {"success": True, "data": preview})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif path == '/api/organize/preview':
            target_path = query.get('path', ['.'])[0].strip()
            try:
                data = scan_organize_folder(target_path)
                self._send_json(200, {"success": True, "data": data})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == '/api/sweeper/scan':
            target_path = query.get('path', ['.'])[0].strip()
            try:
                data = scan_dev_caches(target_path)
                self._send_json(200, {"success": True, "data": data})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == '/api/duplicates':
            target_path = query.get('path', ['.'])[0]
            try:
                agent = FileSystemDFS(target_path)
                result = agent.find_duplicates()
                self._send_json(200, {"success": True, "data": result})
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == '/api/delete':
            target_path = query.get('path', [''])[0].strip()
            if not target_path or target_path.startswith('virtual://'):
                self._send_json(400, {"success": False, "error": "Invalid or virtual path"})
                return

            try:
                move_to_recycle_bin(target_path)
                self._send_json(200, {
                    "success": True,
                    "path": target_path,
                    "recycled": True,
                    "message": "File moved to Recycle Bin successfully"
                })
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif path == '/api/open':
            target_path = query.get('path', [''])[0].strip()
            reveal = query.get('reveal', ['false'])[0].lower() in ['true', '1', 'yes']

            if not target_path or target_path.startswith('virtual://'):
                self._send_json(400, {"success": False, "error": "Invalid or virtual path"})
                return

            try:
                abs_path = os.path.abspath(target_path)
                if not os.path.exists(abs_path):
                    self._send_json(404, {"success": False, "error": "Path not found"})
                    return

                if sys.platform == 'win32':
                    if reveal:
                        if os.path.isfile(abs_path):
                            subprocess.Popen(['explorer', f'/select,{abs_path}'])
                        else:
                            subprocess.Popen(['explorer', abs_path])
                    else:
                        try:
                            os.startfile(abs_path)
                        except Exception:
                            subprocess.Popen(['cmd', '/c', 'start', '""', abs_path], shell=True)
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', '-R' if reveal else '', abs_path])
                else:
                    parent_dir = os.path.dirname(abs_path) if (reveal and os.path.isfile(abs_path)) else abs_path
                    subprocess.Popen(['xdg-open', parent_dir])

                self._send_json(200, {"success": True, "path": abs_path})
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_len) if content_len > 0 else b'{}'
        try:
            payload = json.loads(post_data.decode('utf-8'))
        except Exception:
            payload = {}

        if path == '/api/organize/apply':
            target_path = payload.get('path', '').strip()
            cats = payload.get('categories', None)
            if not target_path or target_path.startswith('virtual://'):
                self._send_json(400, {"success": False, "error": "Invalid target directory"})
                return
            try:
                res = apply_organize_folder(target_path, cats)
                self._send_json(200, res)
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        elif path == '/api/organize/undo':
            try:
                res = undo_organize_folder()
                self._send_json(200, res)
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        elif path == '/api/sweeper/clean':
            paths_to_clean = payload.get('paths', [])
            if not paths_to_clean:
                self._send_json(400, {"success": False, "error": "No paths provided to clean"})
                return
            try:
                res = clean_dev_caches(paths_to_clean)
                self._send_json(200, res)
            except Exception as e:
                self._send_json(500, {"success": False, "error": str(e)})
            return

        self._send_json(404, {"success": False, "error": f"Unknown POST endpoint: {path}"})


def run_server(port=8000):
    os.chdir(BASE_RESOURCE_DIR)
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, PathDiverHandler)
    print("==================================================")
    print(f">> PathDiver Server running at: http://127.0.0.1:{port}")
    print(f">> Serving directory: {BASE_RESOURCE_DIR}")
    print("==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port)

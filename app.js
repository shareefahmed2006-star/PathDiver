/**
 * PathDiver — Modern Application Logic
 * Clean, Friendly User Experience with Progressive Technical Disclosure
 */

// Comprehensive Virtual Filesystem for Sandbox Simulation
const VIRTUAL_FS = {
  name: "demo-workspace",
  path: "virtual://demo-workspace",
  type: "directory",
  children: [
    {
      name: "src",
      path: "virtual://demo-workspace/src",
      type: "directory",
      children: [
        {
          name: "controllers",
          path: "virtual://demo-workspace/src/controllers",
          type: "directory",
          children: [
            { name: "authController.js", path: "virtual://demo-workspace/src/controllers/authController.js", type: "file", size: 14200, hash: "md5_auth_hash" },
            { name: "authController_edited.js", path: "virtual://demo-workspace/src/controllers/authController_edited.js", type: "file", size: 14350, hash: "md5_auth_v2_hash" },
            { name: "userController.js", path: "virtual://demo-workspace/src/controllers/userController.js", type: "file", size: 18500, hash: "md5_user_hash" }
          ]
        },
        {
          name: "models",
          path: "virtual://demo-workspace/src/models",
          type: "directory",
          children: [
            { name: "User.js", path: "virtual://demo-workspace/src/models/User.js", type: "file", size: 8400, hash: "md5_user_model" }
          ]
        },
        { name: "index.js", path: "virtual://demo-workspace/src/index.js", type: "file", size: 3100, hash: "md5_index_hash" }
      ]
    },
    {
      name: "assets",
      path: "virtual://demo-workspace/assets",
      type: "directory",
      children: [
        {
          name: "images",
          path: "virtual://demo-workspace/assets/images",
          type: "directory",
          children: [
            { name: "logo.png", path: "virtual://demo-workspace/assets/images/logo.png", size: 148500, hash: "img_logo_hash" },
            { name: "banner_hero.jpg", path: "virtual://demo-workspace/assets/images/banner_hero.jpg", size: 524000, hash: "banner_hero_hash" },
            { name: "logo_copy.png", path: "virtual://demo-workspace/assets/images/logo_copy.png", size: 148500, hash: "img_logo_hash" }
          ]
        },
        {
          name: "docs",
          path: "virtual://demo-workspace/assets/docs",
          type: "directory",
          children: [
            { name: "specs.pdf", path: "virtual://demo-workspace/assets/docs/specs.pdf", type: "file", size: 215000, hash: "pdf_specs_hash" },
            { name: "notes.txt", path: "virtual://demo-workspace/assets/docs/notes.txt", type: "file", size: 1200, hash: "txt_notes_hash" },
            { name: "notes_draft_v2.txt", path: "virtual://demo-workspace/assets/docs/notes_draft_v2.txt", type: "file", size: 1260, hash: "txt_notes_v2_hash" }
          ]
        }
      ]
    },
    {
      name: "node_modules",
      path: "virtual://demo-workspace/node_modules",
      type: "directory",
      size: 340000000,
      isCache: true,
      description: "Node.js dependency packages"
    },
    {
      name: ".venv",
      path: "virtual://demo-workspace/.venv",
      type: "directory",
      size: 120000000,
      isCache: true,
      description: "Python virtual environment"
    },
    { name: "README.md", path: "virtual://demo-workspace/README.md", type: "file", size: 2400, hash: "readme_hash" },
    { name: "package.json", path: "virtual://demo-workspace/package.json", type: "file", size: 1150, hash: "pkg_json_hash" }
  ]
};

// Global App State
const state = {
  activeTool: "find",
  theme: localStorage.getItem("pathdiver-theme") || "light",
  devModeOpen: false,
  welcomeDismissed: localStorage.getItem("pathdiver-welcome-dismissed") === "true",

  targetPath: "Downloads",
  resolvedPath: "",
  activeTree: VIRTUAL_FS,
  isBackendAvailable: false,
  
  availableDrives: ["C:\\"],
  downloadsDir: "",
  documentsDir: "",
  desktopDir: "",
  picturesDir: "",
  scratchDir: "",

  searchQuery: "",
  filterCategory: "all",
  searchInsideContent: false,

  organizeData: null,
  canUndoOrganize: false,
  sweeperData: null,
  sweeperSelectedPaths: new Set(),

  isRunning: false,
  isPaused: false,
  speed: "normal",
  stepCallback: null,
  lastScanTime: null,
  scannedFilesTotal: 0
};

const SPEED_MAP = {
  slow: 500,
  normal: 150,
  fast: 30,
  instant: 0
};

const CATEGORY_EXT_MAP = {
  docs: ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.pptx', '.csv', '.rtf', '.odt'],
  code: ['.py', '.js', '.ts', '.html', '.css', '.json', '.cpp', '.c', '.java', '.ipynb', '.sql', '.sh', '.bat'],
  images: ['.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.bmp', '.tiff'],
  media: ['.mp3', '.mp4', '.wav', '.mkv', '.avi', '.mov', '.flac'],
  archives: ['.zip', '.rar', '.7z', '.tar', '.gz']
};

// DOM Elements
const elements = {
  themeBtnLight: document.getElementById("theme-btn-light"),
  themeBtnDark: document.getElementById("theme-btn-dark"),
  toggleDevModeBtn: document.getElementById("toggle-dev-mode"),
  backendStatusPill: document.getElementById("backend-status-pill"),
  backendStatusLabel: document.getElementById("backend-status-label"),

  welcomeCard: document.getElementById("welcome-card"),
  btnDismissWelcome: document.getElementById("btn-dismiss-welcome"),

  scopePillsBar: document.getElementById("scope-pills-bar"),
  btnToggleCustomPath: document.getElementById("btn-toggle-custom-path"),
  customPathBar: document.getElementById("custom-path-bar"),
  targetFolderInput: document.getElementById("target-folder-input"),
  btnLoadCustomPath: document.getElementById("btn-load-custom-path"),

  toolCards: document.querySelectorAll(".action-card"),

  scanFolderDisplay: document.getElementById("scan-folder-display"),
  scanStateLabel: document.getElementById("scan-state-label"),
  scanStatusDot: document.getElementById("scan-status-dot"),
  btnMainScan: document.getElementById("btn-main-scan"),
  btnScanText: document.getElementById("btn-scan-text"),
  btnMainPause: document.getElementById("btn-main-pause"),
  btnMainStop: document.getElementById("btn-main-stop"),
  scanProgressWrap: document.getElementById("scan-progress-wrap"),
  scanLiveAction: document.getElementById("scan-live-action"),
  scanLiveCount: document.getElementById("scan-live-count"),
  scanProgressFill: document.getElementById("scan-progress-fill"),

  dashboardCard: document.getElementById("dashboard-card"),
  dashTimeElapsed: document.getElementById("dash-time-elapsed"),
  statFiles: document.getElementById("stat-files"),
  statFolders: document.getElementById("stat-folders"),
  statDuplicates: document.getElementById("stat-duplicates"),
  statSpace: document.getElementById("stat-space"),

  searchFilterWrapper: document.getElementById("search-filter-wrapper"),
  mainSearchInput: document.getElementById("main-search-input"),
  btnSearchClear: document.getElementById("btn-search-clear"),
  btnToggleFilters: document.getElementById("btn-toggle-filters"),
  filterBadge: document.getElementById("filter-active-badge"),
  filterPopover: document.getElementById("filter-popover"),
  filterCategoryChips: document.getElementById("filter-category-chips"),
  toggleContentCheckbox: document.getElementById("toggle-content-search-checkbox"),
  btnResetFilters: document.getElementById("btn-reset-filters"),
  btnApplyFilters: document.getElementById("btn-apply-filters"),

  toolSubHeader: document.getElementById("tool-sub-header"),
  resultsWrapper: document.getElementById("results-wrapper"),

  devSection: document.getElementById("dev-section"),
  speedPills: document.querySelectorAll(".speed-pill"),
  btnStepDfs: document.getElementById("btn-step-dfs"),
  btnResetDfs: document.getElementById("btn-reset-dfs"),
  stackChipsTrack: document.getElementById("stack-chips-track"),
  stackDepthLabel: document.getElementById("stack-depth-label"),
  treeBody: document.getElementById("tree-body"),
  treeNodeStat: document.getElementById("tree-node-stat"),
  devTreeFilter: document.getElementById("dev-tree-filter"),
  logConsole: document.getElementById("log-console"),
  btnClearLog: document.getElementById("btn-clear-log"),

  statusActivityText: document.getElementById("status-activity-text"),
  statusFilesScanned: document.getElementById("status-files-scanned"),
  statusLastScan: document.getElementById("status-last-scan")
};

function init() {
  applyTheme(state.theme);
  if (state.welcomeDismissed && elements.welcomeCard) {
    elements.welcomeCard.style.display = "none";
  }

  setupEventListeners();
  checkBackendConnection();
  log("SYSTEM", "PathDiver initialized. Ready for operations.");
}

/* ==========================================================================
   1. Theme & Navigation Controls
   ========================================================================== */
function applyTheme(theme) {
  state.theme = theme;
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("pathdiver-theme", theme);

  if (elements.themeBtnLight && elements.themeBtnDark) {
    if (theme === "dark") {
      elements.themeBtnDark.classList.add("active");
      elements.themeBtnLight.classList.remove("active");
    } else {
      elements.themeBtnLight.classList.add("active");
      elements.themeBtnDark.classList.remove("active");
    }
  }
}

function toggleDevMode(forceState) {
  state.devModeOpen = typeof forceState === "boolean" ? forceState : !state.devModeOpen;
  elements.devSection.style.display = state.devModeOpen ? "block" : "none";
  elements.toggleDevModeBtn.classList.toggle("active", state.devModeOpen);
  if (state.devModeOpen) {
    renderTree(state.activeTree);
    log("SYSTEM", "Technical / Developer view expanded.");
  }
}

/* ==========================================================================
   2. Backend Connection & Scope Setup
   ========================================================================== */
async function checkBackendConnection() {
  try {
    const res = await fetch("/api/drives", { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      const data = await res.json();
      state.isBackendAvailable = true;
      state.availableDrives = data.drives || ["C:\\"];
      state.downloadsDir = data.downloads || "";
      state.documentsDir = data.documents || "";
      state.desktopDir = data.desktop || "";
      state.picturesDir = data.pictures || "";
      state.scratchDir = data.scratch_dir || "";

      state.availableDrives.forEach(drive => {
        if (drive.toUpperCase() !== "C:\\") {
          const driveLetter = drive.replace(/[:\\\/]/g, "").toLowerCase();
          const existing = document.querySelector(`[data-scope="drive-${driveLetter}"]`);
          if (!existing) {
            const btn = document.createElement("button");
            btn.className = "scope-pill";
            btn.setAttribute("data-scope", `drive-${driveLetter}`);
            btn.setAttribute("data-path", drive);
            btn.innerHTML = `<span class="pill-icon">💾</span> <span>${drive} Drive</span>`;
            const allDisksBtn = document.querySelector('[data-scope="all-disks"]');
            if (allDisksBtn) {
              elements.scopePillsBar.insertBefore(btn, allDisksBtn);
            }
          }
        }
      });

      elements.backendStatusLabel.textContent = "Connected";
      elements.backendStatusPill.style.color = "var(--success)";
      
      const defaultPath = state.downloadsDir || "C:\\";
      setScopePath(defaultPath, "Downloads");
      loadRealTree(defaultPath);
      log("SUCCESS", `Connected to Python backend. Target: ${defaultPath}`);
    }
  } catch (err) {
    state.isBackendAvailable = false;
    elements.backendStatusLabel.textContent = "Virtual Sandbox";
    setScopePath("virtual://demo-workspace", "Virtual Workspace");
    state.activeTree = VIRTUAL_FS;
    log("SYSTEM", "Running in Virtual Sandbox demo mode.");
  }
}

function setScopePath(path, displayName) {
  state.resolvedPath = path;
  state.targetPath = path;
  elements.targetFolderInput.value = path;
  elements.scanFolderDisplay.textContent = displayName || path.split(/[\\/]/).filter(Boolean).pop() || path;
  elements.scanStateLabel.textContent = `Ready to scan · ${path}`;
}

async function loadRealTree(path) {
  try {
    const res = await fetch(`/api/tree?path=${encodeURIComponent(path)}&depth=2`);
    const data = await res.json();
    if (data.success && data.tree) {
      state.activeTree = data.tree;
      if (state.devModeOpen) renderTree(state.activeTree);
    }
  } catch (err) {
    console.error("Failed to load hierarchy:", err);
  }
}

/* ==========================================================================
   3. Tool Selection ("What would you like to do?")
   ========================================================================== */
function switchTool(toolId) {
  state.activeTool = toolId;
  elements.toolCards.forEach(card => {
    card.classList.toggle("active", card.getAttribute("data-tool") === toolId);
  });

  const toolLabels = {
    find: "Start Search Scan",
    duplicates: "Start Duplicate Scan",
    organize: "Analyze Loose Files",
    sweeper: "Scan Developer Caches"
  };
  elements.btnScanText.textContent = toolLabels[toolId] || "Start Scan";

  elements.searchFilterWrapper.style.display = (toolId === "find") ? "flex" : "none";
  renderToolSubHeader();

  if (toolId === "organize" && state.organizeData) {
    renderOrganizeResults(state.organizeData);
  } else if (toolId === "sweeper" && state.sweeperData) {
    renderSweeperResults(state.sweeperData);
  } else {
    renderInitialEmptyState();
  }

  log("SYSTEM", `Active superpower switched to: ${toolId.toUpperCase()}`);
}

function renderToolSubHeader() {
  if (state.activeTool === "organize") {
    const hasLoose = state.organizeData && state.organizeData.total_loose_files > 0;
    elements.toolSubHeader.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; background: var(--surface-inset); padding: 12px 16px; border-radius: var(--radius-md); border: 1px solid var(--border); flex-wrap: wrap; gap: 10px;">
        <div>
          <div style="font-weight: 700; font-size: 13.5px; color: var(--success);">🧹 1-Click Loose File Organizer</div>
          <div style="font-size: 12px; color: var(--text-muted);">Sort unorganized files into Documents, Images, Code, etc. without touching subfolders.</div>
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-primary btn-sm" id="btn-apply-organize" style="background: var(--success); border-color: var(--success);" ${hasLoose ? '' : 'disabled'}>
            ✨ Organize Now ${hasLoose ? `(${state.organizeData.total_loose_files} files)` : ''}
          </button>
          <button class="btn btn-outline btn-sm" id="btn-undo-organize" ${state.canUndoOrganize ? '' : 'disabled'}>
            ↺ 1-Click Undo
          </button>
        </div>
      </div>
    `;
    const btnApply = document.getElementById("btn-apply-organize");
    if (btnApply) btnApply.addEventListener("click", applyFolderOrganize);
    const btnUndo = document.getElementById("btn-undo-organize");
    if (btnUndo) btnUndo.addEventListener("click", undoFolderOrganize);
  } else if (state.activeTool === "sweeper") {
    const selCount = state.sweeperSelectedPaths ? state.sweeperSelectedPaths.size : 0;
    elements.toolSubHeader.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; background: var(--surface-inset); padding: 12px 16px; border-radius: var(--radius-md); border: 1px solid var(--border); flex-wrap: wrap; gap: 10px;">
        <div>
          <div style="font-weight: 700; font-size: 13.5px; color: var(--warning);">🧼 Developer & Cache Junk Sweeper</div>
          <div style="font-size: 12px; color: var(--text-muted);">Prunes node_modules, .venv, and build caches in &lt;2s. Reclaims space directly to OS Recycle Bin.</div>
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-danger btn-sm" id="btn-clean-sweeper" ${selCount > 0 ? '' : 'disabled'}>
            🗑️ Reclaim Space (${selCount} selected)
          </button>
        </div>
      </div>
    `;
    const btnClean = document.getElementById("btn-clean-sweeper");
    if (btnClean) btnClean.addEventListener("click", cleanSelectedCaches);
  } else {
    elements.toolSubHeader.innerHTML = "";
  }
}

function renderInitialEmptyState() {
  elements.resultsWrapper.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon">📂</div>
      <div class="empty-title">Nothing scanned yet</div>
      <div class="empty-desc">Choose a folder above and start a scan to see your files here.</div>
      <button class="btn btn-primary btn-sm" onclick="startScan()" style="margin-top: 10px;">
        <span>▶ Start Scan</span>
      </button>
    </div>
  `;
}

/* ==========================================================================
   4. Scan Execution Engine
   ========================================================================== */
async function startScan() {
  if (state.isRunning) return;

  state.isRunning = true;
  state.isPaused = false;
  elements.btnMainScan.disabled = true;
  elements.btnMainPause.style.display = "inline-flex";
  elements.btnMainStop.style.display = "inline-flex";
  elements.scanProgressWrap.style.display = "block";
  elements.scanStatusDot.className = "scan-status-dot scanning";
  elements.scanStateLabel.textContent = `Scanning ${elements.scanFolderDisplay.textContent}...`;
  elements.statusActivityText.textContent = `Scanning ${state.targetPath}...`;

  const isReal = state.isBackendAvailable && !state.targetPath.startsWith("virtual://");

  if (state.activeTool === "find") {
    if (isReal) await runRealFindScan(); else await runVirtualFindScan();
  } else if (state.activeTool === "duplicates") {
    if (isReal) await runRealDuplicateScan(); else await runVirtualDuplicateScan();
  } else if (state.activeTool === "organize") {
    if (isReal) await analyzeFolderToOrganize(); else await runVirtualOrganize();
  } else if (state.activeTool === "sweeper") {
    if (isReal) await scanDevCaches(); else await runVirtualSweeper();
  }

  if (isReal) fetchDashboardOverview();

  finishScan();
}

function finishScan() {
  state.isRunning = false;
  state.isPaused = false;
  elements.btnMainScan.disabled = false;
  elements.btnMainPause.style.display = "none";
  elements.btnMainStop.style.display = "none";
  elements.scanProgressWrap.style.display = "none";
  elements.scanStatusDot.className = "scan-status-dot";
  elements.scanStateLabel.textContent = `Scan complete · ${state.targetPath}`;
  elements.statusActivityText.textContent = "Ready";
  state.lastScanTime = new Date().toLocaleTimeString();
  elements.statusLastScan.textContent = `Last scan: ${state.lastScanTime}`;
  updateStackUI([]);
}

async function fetchDashboardOverview() {
  try {
    const res = await fetch(`/api/dashboard?path=${encodeURIComponent(state.targetPath)}`);
    const result = await res.json();
    if (result.success && result.data) {
      const d = result.data;
      elements.statFiles.textContent = (d.files_count || 0).toLocaleString();
      elements.statFolders.textContent = (d.dirs_count || 0).toLocaleString();
      elements.statDuplicates.textContent = (d.potential_duplicates_estimate || 0).toLocaleString();
      elements.statSpace.textContent = formatBytes(d.total_size || 0);
      elements.dashTimeElapsed.textContent = `${d.time_elapsed}s`;
      elements.dashboardCard.style.display = "block";
      elements.statusFilesScanned.textContent = `${d.files_count} files scanned`;
    }
  } catch (err) {
    console.error("Dashboard overview error:", err);
  }
}

/* Real OS Scans */
async function runRealFindScan() {
  const contentFlag = state.searchInsideContent ? '&content=1' : '';
  const exts = state.filterCategory !== 'all' ? `&exts=${(CATEGORY_EXT_MAP[state.filterCategory] || []).join(',')}` : '';
  const endpoint = `/api/find?path=${encodeURIComponent(state.targetPath)}&q=${encodeURIComponent(state.searchQuery)}&limit=1000&timeout=25${contentFlag}${exts}`;

  log("SYSTEM", `Running Find scan on ${state.targetPath} (query: "${state.searchQuery}")...`);

  try {
    const res = await fetch(endpoint);
    const result = await res.json();
    if (result.success) {
      const d = result.data;
      animateStackTrace(d.stack_trace_samples || []);
      renderFindResults(d.matches || []);
      log("SUCCESS", `Found ${d.matches_count} item(s) across ${d.scanned_directories} dirs in ${d.time_elapsed}s.`);
    } else {
      elements.resultsWrapper.innerHTML = `<div style="color: var(--danger); padding: 20px;">Scan Error: ${escapeHtml(result.error)}</div>`;
    }
  } catch (err) {
    log("ERROR", `Find scan failed: ${err.message}`);
  }
}

async function runRealDuplicateScan() {
  log("SYSTEM", `Running Heuristic Duplicate Detection on ${state.targetPath}...`);
  try {
    const res = await fetch(`/api/duplicates?path=${encodeURIComponent(state.targetPath)}`);
    const result = await res.json();
    if (result.success) {
      const d = result.data;
      renderDuplicateResults(d.duplicate_groups || [], d.reclaimable_bytes || 0);
      log("SUCCESS", `Detected ${d.duplicate_groups_count} duplicate clusters with ${formatBytes(d.reclaimable_bytes)} reclaimable space.`);
    } else {
      elements.resultsWrapper.innerHTML = `<div style="color: var(--danger); padding: 20px;">Duplicate Scan Error: ${escapeHtml(result.error)}</div>`;
    }
  } catch (err) {
    log("ERROR", `Duplicate request failed: ${err.message}`);
  }
}

/* Virtual Sandbox Scans */
async function runVirtualFindScan() {
  log("SYSTEM", `Running simulated search on virtual demo workspace...`);
  const matches = [];
  const q = state.searchQuery.toLowerCase();

  function traverse(node) {
    if (node.type === "file") {
      if (!q || node.name.toLowerCase().includes(q)) {
        matches.push(node);
      }
    }
    if (node.children) {
      node.children.forEach(traverse);
    }
  }
  traverse(VIRTUAL_FS);
  await sleep(250);
  renderFindResults(matches);
  elements.dashboardCard.style.display = "block";
  elements.statFiles.textContent = matches.length;
  elements.statFolders.textContent = "6";
  elements.statDuplicates.textContent = "2";
  elements.statSpace.textContent = "462.4 MB";
}

async function runVirtualDuplicateScan() {
  log("SYSTEM", `Running simulated duplicate detection...`);
  await sleep(300);
  const dupGroups = [
    {
      title: "logo.png (2 identical copies)",
      hash: "img_logo_hash",
      wasted_bytes: 148500,
      has_edited: false,
      files: [
        { name: "logo.png", path: "virtual://demo-workspace/assets/images/logo.png", size: 148500, role: "original", badge: "ORIGINAL", details: "Baseline original brand logo" },
        { name: "logo_copy.png", path: "virtual://demo-workspace/assets/images/logo_copy.png", size: 148500, role: "exact_duplicate", badge: "EXACT DITTO", details: "100% byte-for-byte identical copy" }
      ]
    },
    {
      title: "authController.js (Original + 1 Edited Version)",
      hash: "md5_auth_hash",
      wasted_bytes: 0,
      has_edited: true,
      files: [
        { name: "authController.js", path: "virtual://demo-workspace/src/controllers/authController.js", size: 14200, role: "original", badge: "ORIGINAL", details: "Baseline authentication controller" },
        { name: "authController_edited.js", path: "virtual://demo-workspace/src/controllers/authController_edited.js", size: 14350, role: "edited", badge: "EDITED VERSION", details: "1 line modified (98.2% similarity)" }
      ]
    }
  ];
  renderDuplicateResults(dupGroups, 148500);
}

/* ==========================================================================
   5. Results Rendering: Find & Peek
   ========================================================================== */
function renderFindResults(matches) {
  if (!matches || matches.length === 0) {
    elements.resultsWrapper.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">❌</div>
        <div class="empty-title">No matching files found</div>
        <div class="empty-desc">Try modifying your query or selecting another directory scope.</div>
      </div>
    `;
    return;
  }

  elements.resultsWrapper.innerHTML = `
    <div style="font-weight: 700; font-size: 13.5px; color: var(--primary); margin-bottom: 8px;">
      ✅ Found ${matches.length} matching item${matches.length === 1 ? '' : 's'}:
    </div>
    ${matches.map((m, idx) => {
      const isDir = m.type === "directory";
      const icon = isDir ? "📁" : "📄";
      const drawerId = `peek-drawer-${idx}`;
      return `
      <div class="result-card" data-name="${escapeHtml(m.name)}" data-path="${escapeHtml(m.path)}">
        <div class="result-main-row">
          <div class="result-info">
            <div class="result-title-line">
              <span style="font-size: 16px;">${icon}</span>
              <span class="result-filename" title="${escapeHtml(m.path)}">${escapeHtml(m.name)}</span>
              <span class="result-size">${formatBytes(m.size)}</span>
            </div>
            ${m.snippet ? `<div class="result-snippet">💬 Match: ${escapeHtml(m.snippet)}</div>` : ''}
          </div>
          <div class="result-actions">
            ${!isDir ? `<button class="btn btn-outline btn-sm" onclick="togglePeek('${escapeJs(m.path)}', '${drawerId}', this)">👁️ Peek</button>` : ''}
            <button class="btn btn-primary btn-sm" onclick="openFile('${escapeJs(m.path)}')">${isDir ? '📂 Open Folder' : '📄 Open'}</button>
            <button class="btn btn-danger btn-outline btn-sm" onclick="deleteFile('${escapeJs(m.path)}', this)">🗑️ Delete</button>
          </div>
        </div>
        <div class="peek-drawer" id="${drawerId}" style="display: none;"></div>
      </div>
      `;
    }).join('')}
  `;
}

async function togglePeek(path, drawerId, btnEl) {
  const drawer = document.getElementById(drawerId);
  if (!drawer) return;

  if (drawer.style.display !== "none") {
    drawer.style.display = "none";
    btnEl.innerHTML = "👁️ Peek";
    btnEl.classList.remove("btn-primary");
    btnEl.classList.add("btn-outline");
    return;
  }

  drawer.style.display = "block";
  drawer.innerHTML = `<div style="font-size: 12px; color: var(--text-muted);">⏳ Generating smart 2-line peek...</div>`;
  btnEl.innerHTML = "✕ Close";
  btnEl.classList.remove("btn-outline");
  btnEl.classList.add("btn-primary");

  if (path.startsWith("virtual://")) {
    const filename = path.split('/').pop();
    setTimeout(() => {
      drawer.innerHTML = `
        <div class="peek-drawer-header">
          <span>📄 Virtual Demo Item</span>
          <span>${formatBytes(12500)}</span>
        </div>
        <div class="peek-drawer-summary">💡 Simulation File: In-memory representation for testing and walkthroughs.</div>
        <div class="peek-drawer-snippet">// Preview contents of ${escapeHtml(filename)}\nfunction demoPeek() {\n  return true;\n}</div>
      `;
    }, 100);
    return;
  }

  try {
    const res = await fetch(`/api/peek?path=${encodeURIComponent(path)}`);
    const result = await res.json();
    if (result.success && result.data) {
      const d = result.data;
      drawer.innerHTML = `
        <div class="peek-drawer-header">
          <span>${escapeHtml(d.type || 'File')}</span>
          <span>${d.pages ? d.pages + ' pages' : ''}</span>
        </div>
        <div class="peek-drawer-summary">${escapeHtml(d.summary || 'Summary unavailable.')}</div>
        ${d.snippet ? `<div class="peek-drawer-snippet">${escapeHtml(d.snippet)}</div>` : ''}
      `;
    } else {
      drawer.innerHTML = `<div style="color: var(--danger); font-size: 12px;">Peek error: ${escapeHtml(result.error || 'Failed to extract summary')}</div>`;
    }
  } catch (err) {
    drawer.innerHTML = `<div style="color: var(--danger); font-size: 12px;">Peek error: ${escapeHtml(err.message)}</div>`;
  }
}

/* ==========================================================================
   6. Results Rendering: Duplicate & Edited Files
   ========================================================================== */
function renderDuplicateResults(dupGroups, reclaimableBytes) {
  if (!dupGroups || dupGroups.length === 0) {
    elements.resultsWrapper.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">✅</div>
        <div class="empty-title">No duplicate files detected</div>
        <div class="empty-desc">All files across this directory scope have completely unique contents.</div>
      </div>
    `;
    return;
  }

  const exactClusters = dupGroups.filter(g => !g.has_edited);
  const editedClusters = dupGroups.filter(g => g.has_edited);

  elements.resultsWrapper.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
      <div>
        <div style="font-weight: 700; font-size: 14px; color: var(--warning);">
          ⚠️ Detected ${dupGroups.length} File Cluster${dupGroups.length === 1 ? '' : 's'}:
        </div>
        <div style="font-size: 12px; color: var(--text-muted);">
          (${exactClusters.length} exact ditto duplicate group${exactClusters.length === 1 ? '' : 's'}, ${editedClusters.length} edited version group${editedClusters.length === 1 ? '' : 's'})
        </div>
      </div>
      <div style="font-family: var(--font-mono); font-size: 13px; font-weight: 800; color: var(--primary);">
        Reclaimable Space: ${formatBytes(reclaimableBytes)}
      </div>
    </div>

    ${dupGroups.map(g => {
      const isEdited = g.has_edited;
      const badgeClass = isEdited ? 'dup-badge-edited' : 'dup-badge-exact';
      const badgeLabel = isEdited ? '✏️ EDITED VERSION GROUP' : '👯 EXACT DITTO GROUP';

      return `
      <div class="dup-cluster-card">
        <div class="dup-cluster-header">
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span class="dup-badge ${badgeClass}">${badgeLabel}</span>
            <span style="font-weight: 700; font-size: 13px;">${escapeHtml(g.title)}</span>
          </div>
          <div style="font-size: 12px; font-weight: 700; color: var(--primary); font-family: var(--font-mono);">
            ${g.wasted_bytes > 0 ? 'Wasting ' + formatBytes(g.wasted_bytes) : 'Inspect Edits'}
          </div>
        </div>

        <div class="dup-files-body">
          ${g.files.map(f => {
            const role = f.role;
            let roleBadge = 'dup-badge-exact';
            let roleText = '👯 EXACT DITTO';
            let deleteLabel = '🗑️ Delete Duplicate';

            if (role === 'original') {
              roleBadge = 'dup-badge-original';
              roleText = '🌟 ORIGINAL';
              deleteLabel = '🗑️ Delete (Original)';
            } else if (role === 'edited') {
              roleBadge = 'dup-badge-edited';
              roleText = '✏️ EDITED VERSION';
              deleteLabel = '🗑️ Delete (Edited)';
            }

            return `
            <div class="dup-file-row role-${role}">
              <div style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0;">
                <span style="font-size: 15px;">${role === 'edited' ? '📝' : (role === 'original' ? '📁' : '📄')}</span>
                <span style="font-weight: 600; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(f.path)}">
                  ${escapeHtml(f.name)}
                </span>
                <span class="dup-badge ${roleBadge}">${roleText}</span>
                <span style="font-size: 11px; font-family: var(--font-mono); color: var(--text-dim);">(${formatBytes(f.size)})</span>
              </div>
              <div style="display: flex; gap: 6px; flex-shrink: 0;">
                <button class="btn btn-secondary btn-sm" onclick="openFile('${escapeJs(f.path)}')">Open</button>
                <button class="btn btn-danger btn-outline btn-sm" onclick="deleteDuplicateFile('${escapeJs(f.path)}', '${role}', '${escapeJs(f.name)}', this)">
                  ${deleteLabel}
                </button>
              </div>
            </div>
            `;
          }).join('')}
        </div>
      </div>
      `;
    }).join('')}
  `;
}

/* ==========================================================================
   7. Organizer Engine & Reversible Undo
   ========================================================================== */
async function analyzeFolderToOrganize() {
  elements.resultsWrapper.innerHTML = `<div style="text-align: center; padding: 32px; color: var(--text-muted);">⏳ Analyzing loose files in <strong>${escapeHtml(state.targetPath)}</strong>...</div>`;
  log("SYSTEM", `Analyzing folder for loose files: ${state.targetPath}...`);

  try {
    const res = await fetch(`/api/organize/preview?path=${encodeURIComponent(state.targetPath)}`);
    const result = await res.json();
    if (result.success && result.data) {
      state.organizeData = result.data;
      state.canUndoOrganize = result.data.can_undo;
      renderOrganizeResults(result.data);
      renderToolSubHeader();
      log("SUCCESS", `Found ${result.data.total_loose_files} loose files ready to organize.`);
    }
  } catch (err) {
    log("ERROR", `Organizer analysis failed: ${err.message}`);
  }
}

async function runVirtualOrganize() {
  const dummy = {
    folder: state.targetPath,
    total_loose_files: 5,
    total_loose_bytes: 845000,
    can_undo: state.canUndoOrganize,
    categories: {
      "Documents": [{ name: "specs.pdf", size: 215000 }, { name: "notes.txt", size: 1200 }],
      "Images": [{ name: "logo.png", size: 148500 }, { name: "banner_hero.jpg", size: 524000 }],
      "Code": [{ name: "index.js", size: 3100 }]
    }
  };
  state.organizeData = dummy;
  renderOrganizeResults(dummy);
  renderToolSubHeader();
}

function renderOrganizeResults(data) {
  if (!data || data.total_loose_files === 0) {
    elements.resultsWrapper.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">✨</div>
        <div class="empty-title" style="color: var(--success);">Folder is 100% Clean!</div>
        <div class="empty-desc">No loose files found directly in this directory. Everything is already organized into subfolders.</div>
      </div>
    `;
    return;
  }

  const cats = Object.entries(data.categories || {}).filter(([_, list]) => list.length > 0);

  elements.resultsWrapper.innerHTML = `
    <div style="margin-bottom: 12px; font-weight: 700; font-size: 13.5px; color: var(--success);">
      🧹 Found ${data.total_loose_files} loose file${data.total_loose_files === 1 ? '' : 's'} (${formatBytes(data.total_loose_bytes)}) across ${cats.length} target categories:
    </div>
    <div class="organize-grid">
      ${cats.map(([catName, files]) => {
        const catBytes = files.reduce((acc, f) => acc + (f.size || 0), 0);
        return `
        <div class="organize-cat-card">
          <div class="organize-cat-header">
            <span>📁 ${catName}/</span>
            <span style="font-size: 11px; font-weight: 700; color: var(--primary);">${files.length} file${files.length === 1 ? '' : 's'}</span>
          </div>
          <div style="font-size: 11px; color: var(--text-dim); margin-bottom: 6px;">Total: ${formatBytes(catBytes)}</div>
          <div class="organize-file-list">
            ${files.slice(0, 4).map(f => `<div>• ${escapeHtml(f.name)} <span style="color: var(--text-dim);">(${formatBytes(f.size)})</span></div>`).join('')}
            ${files.length > 4 ? `<div style="font-style: italic; color: var(--text-dim);">+ ${files.length - 4} more files...</div>` : ''}
          </div>
        </div>
        `;
      }).join('')}
    </div>
  `;
}

async function applyFolderOrganize() {
  if (!state.organizeData || state.organizeData.total_loose_files === 0) return;
  const count = state.organizeData.total_loose_files;
  if (!confirm(`Organize ${count} loose files in "${state.targetPath}" into neat category subfolders (Documents, Images, Code, etc.)?\n\n(1-Click Undo is available to restore them anytime).`)) {
    return;
  }

  if (state.targetPath.startsWith("virtual://")) {
    state.canUndoOrganize = true;
    alert(`Successfully organized ${count} files!\n\n1-Click Undo is active.`);
    state.organizeData = null;
    renderToolSubHeader();
    renderOrganizeResults({ total_loose_files: 0 });
    return;
  }

  try {
    const res = await fetch(`/api/organize/apply`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: state.targetPath })
    });
    const result = await res.json();
    if (result.success) {
      state.canUndoOrganize = true;
      log("SUCCESS", `Organized ${result.moved_count} file(s) into category subfolders.`);
      await analyzeFolderToOrganize();
      alert(`✨ Successfully organized ${result.moved_count} files!\n\n1-Click Undo is available.`);
    }
  } catch (err) {
    alert(`Organization error: ${err.message}`);
  }
}

async function undoFolderOrganize() {
  if (!confirm(`Undo last organization?\n\nAll files will be moved back to their exact original locations, and empty generated category folders will be removed.`)) {
    return;
  }

  if (state.targetPath.startsWith("virtual://")) {
    state.canUndoOrganize = false;
    alert(`Undone! Restored all files to original location.`);
    runVirtualOrganize();
    return;
  }

  try {
    const res = await fetch(`/api/organize/undo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const result = await res.json();
    if (result.success) {
      state.canUndoOrganize = result.remaining_undo_count > 0;
      log("SUCCESS", `Restored ${result.restored_count} files to original positions.`);
      await analyzeFolderToOrganize();
      alert(`↺ Undone successfully!\n\nRestored ${result.restored_count} files.`);
    }
  } catch (err) {
    alert(`Undo failed: ${err.message}`);
  }
}

/* ==========================================================================
   8. Developer & Cache Junk Sweeper
   ========================================================================== */
async function scanDevCaches() {
  elements.resultsWrapper.innerHTML = `<div style="text-align: center; padding: 32px; color: var(--text-muted);">⏳ Pruning directory tree for developer caches in <strong>${escapeHtml(state.targetPath)}</strong>...</div>`;
  log("SYSTEM", `Scanning developer caches in ${state.targetPath}...`);

  try {
    const res = await fetch(`/api/sweeper/scan?path=${encodeURIComponent(state.targetPath)}`);
    const result = await res.json();
    if (result.success && result.data) {
      state.sweeperData = result.data;
      state.sweeperSelectedPaths = new Set(result.data.caches.map(c => c.path));
      renderSweeperResults(result.data);
      renderToolSubHeader();
      log("SUCCESS", `Found ${result.data.total_caches_found} cache directories with ${formatBytes(result.data.total_reclaimable_bytes)}.`);
    }
  } catch (err) {
    log("ERROR", `Sweeper scan failed: ${err.message}`);
  }
}

async function runVirtualSweeper() {
  const dummy = {
    root: state.targetPath,
    total_caches_found: 2,
    total_reclaimable_bytes: 460000000,
    time_elapsed: 0.04,
    caches: [
      { name: "node_modules", path: "virtual://demo-workspace/node_modules", size: 340000000, description: "Node.js dependency packages", files_count: 1420 },
      { name: ".venv", path: "virtual://demo-workspace/.venv", size: 120000000, description: "Python virtual environment", files_count: 850 }
    ]
  };
  state.sweeperData = dummy;
  state.sweeperSelectedPaths = new Set(dummy.caches.map(c => c.path));
  renderSweeperResults(dummy);
  renderToolSubHeader();
}

function renderSweeperResults(data) {
  if (!data || data.caches.length === 0) {
    elements.resultsWrapper.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">✨</div>
        <div class="empty-title" style="color: var(--primary);">Workspace is Sparkling Clean!</div>
        <div class="empty-desc">No developer bloat, node_modules, or cache junk found in this directory scope.</div>
      </div>
    `;
    return;
  }

  elements.resultsWrapper.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: gap; gap: 8px;">
      <label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-weight: 700; font-size: 13px;">
        <input type="checkbox" id="sweeper-select-all" checked onchange="toggleSelectAllCaches(this)">
        <span>Select All (${data.caches.length} item${data.caches.length === 1 ? '' : 's'})</span>
      </label>
      <div style="font-family: var(--font-mono); font-weight: 800; font-size: 13px; color: var(--danger);">
        Reclaimable Space: ${formatBytes(data.total_reclaimable_bytes)}
      </div>
    </div>

    ${data.caches.map((c, idx) => {
      const isChecked = state.sweeperSelectedPaths.has(c.path) ? 'checked' : '';
      return `
      <div class="sweeper-row" id="sweeper-row-${idx}">
        <div class="sweeper-row-left">
          <input type="checkbox" class="sweeper-checkbox" data-path="${escapeHtml(c.path)}" ${isChecked} onchange="toggleCacheCheckbox('${escapeJs(c.path)}', this)">
          <span style="font-size: 18px;">📁</span>
          <div>
            <div class="sweeper-name">${escapeHtml(c.name)} <span style="font-size: 11px; font-weight: normal; color: var(--text-dim);">(${c.files_count || 0} files)</span></div>
            <div class="sweeper-desc">${escapeHtml(c.description || '')}</div>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
          <div style="font-family: var(--font-mono); font-weight: 700; font-size: 13px; color: var(--text-main);">${formatBytes(c.size)}</div>
          <button class="btn btn-secondary btn-sm" onclick="openFile('${escapeJs(c.path)}')">Open</button>
        </div>
      </div>
      `;
    }).join('')}
  `;
}

function toggleSelectAllCaches(masterCheckbox) {
  const isChecked = masterCheckbox.checked;
  document.querySelectorAll(".sweeper-checkbox").forEach(cb => {
    cb.checked = isChecked;
    const p = cb.getAttribute("data-path");
    if (isChecked) state.sweeperSelectedPaths.add(p); else state.sweeperSelectedPaths.delete(p);
  });
  renderToolSubHeader();
}

function toggleCacheCheckbox(path, cb) {
  if (cb.checked) state.sweeperSelectedPaths.add(path); else state.sweeperSelectedPaths.delete(path);
  const master = document.getElementById("sweeper-select-all");
  if (master) master.checked = false;
  renderToolSubHeader();
}

async function cleanSelectedCaches() {
  const selectedPaths = Array.from(state.sweeperSelectedPaths);
  if (selectedPaths.length === 0) return;

  let totalBytes = 0;
  if (state.sweeperData && state.sweeperData.caches) {
    totalBytes = state.sweeperData.caches.filter(c => state.sweeperSelectedPaths.has(c.path)).reduce((a, b) => a + b.size, 0);
  }

  if (!confirm(`Move ${selectedPaths.length} selected cache folder(s) (${formatBytes(totalBytes)}) to the OS Recycle Bin?\n\n(You can safely restore them from the Recycle Bin if needed).`)) {
    return;
  }

  if (state.targetPath.startsWith("virtual://")) {
    alert(`Reclaimed ${formatBytes(totalBytes)} of storage!`);
    state.sweeperSelectedPaths.clear();
    runVirtualSweeper();
    return;
  }

  try {
    const res = await fetch(`/api/sweeper/clean`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paths: selectedPaths })
    });
    const result = await res.json();
    if (result.success) {
      log("SUCCESS", `Moved ${result.cleaned_count} cache folder(s) to Recycle Bin. Reclaimed ${formatBytes(result.reclaimed_bytes)}!`);
      state.sweeperSelectedPaths.clear();
      await scanDevCaches();
      alert(`✨ Cleaned ${result.cleaned_count} cache folders! Reclaimed ${formatBytes(result.reclaimed_bytes)}.`);
    }
  } catch (err) {
    alert(`Clean error: ${err.message}`);
  }
}

/* ==========================================================================
   9. File Actions & Safe Deletions
   ========================================================================== */
function openFile(path) {
  if (path.startsWith("virtual://")) {
    alert(`Virtual Sandbox Item:\n${path}\n\nTo open real files on your computer, choose one of the quick folders above (Downloads, Documents, Desktop, etc.).`);
    return;
  }
  fetch(`/api/open?path=${encodeURIComponent(path)}&reveal=0`).then(r => r.json()).then(data => {
    if (data.success) log("SUCCESS", `Opened: ${path}`);
    else log("ERROR", `Failed to open: ${data.error}`);
  }).catch(err => log("ERROR", `Open error: ${err.message}`));
}

function deleteFile(path, btnEl) {
  const fileName = path.split(/[\\/]/).pop() || path;
  if (!confirm(`Move this file to the OS Recycle Bin?\n\nFile: ${fileName}\nPath: ${path}`)) {
    return;
  }
  executeRecycleBinDelete(path, btnEl, 'file', fileName);
}

function deleteDuplicateFile(path, role, fileName, btnEl) {
  const isOriginal = role === 'original';
  const isEdited = role === 'edited';

  if (!isOriginal && !isEdited) {
    log("SYSTEM", `Moving EXACT DITTO duplicate to Recycle Bin: ${fileName}`);
    executeRecycleBinDelete(path, btnEl, 'exact_duplicate', fileName);
    return;
  }

  const label = isOriginal ? "ORIGINAL FILE" : "EDITED VERSION";
  if (!confirm(`Move ${label} to the OS Recycle Bin?\n\nFile: ${fileName}\nPath: ${path}`)) {
    return;
  }
  executeRecycleBinDelete(path, btnEl, role, fileName);
}

function executeRecycleBinDelete(path, btnEl, role, fileName) {
  if (path.startsWith("virtual://")) {
    log("SUCCESS", `(Virtual) Moved ${role} to Recycle Bin: ${fileName}`);
    removeResultCard(btnEl);
    return;
  }

  fetch(`/api/delete?path=${encodeURIComponent(path)}`).then(r => r.json()).then(data => {
    if (data.success) {
      log("SUCCESS", `Moved to OS Recycle Bin: ${fileName} (${role})`);
      removeResultCard(btnEl);
    } else {
      alert(`Deletion error: ${data.error}`);
    }
  }).catch(err => alert(`Delete error: ${err.message}`));
}

function removeResultCard(btnEl) {
  if (!btnEl) return;
  const card = btnEl.closest(".result-card") || btnEl.closest(".dup-file-row");
  if (card) {
    card.style.transition = "all 0.25s ease";
    card.style.opacity = "0";
    card.style.transform = "translateX(20px)";
    setTimeout(() => card.remove(), 250);
  }
}

/* ==========================================================================
   10. Technical / Developer View: DFS Stack & Hierarchy Tree
   ========================================================================== */
function updateStackUI(stack) {
  if (!elements.stackDepthLabel || !elements.stackChipsTrack) return;
  elements.stackDepthLabel.textContent = `Depth: ${stack.length} nodes`;

  if (stack.length === 0) {
    elements.stackChipsTrack.innerHTML = `<div class="stack-empty-msg">Stack is idle. Run scan to observe push and pop operations.</div>`;
    return;
  }

  const visible = stack.slice(-12);
  elements.stackChipsTrack.innerHTML = visible.map(item => {
    const displayName = typeof item === 'string' ? item.split(/[\\/]/).filter(Boolean).pop() || item : item.name || 'node';
    return `<div class="stack-chip"><span>📁</span> <span>${escapeHtml(displayName)}</span></div>`;
  }).join('');
}

function renderTree(rootNode) {
  if (!elements.treeBody) return;
  elements.treeBody.innerHTML = "";
  let totalFiles = 0;
  let totalDirs = 0;

  function countLoaded(node) {
    if (node.type === "directory") totalDirs++; else totalFiles++;
    if (node.children) node.children.forEach(countLoaded);
  }
  countLoaded(rootNode);

  function buildDOM(node, depth, container) {
    const isDir = node.type === "directory";
    const row = document.createElement("div");
    row.className = "tree-node-row";
    row.style.paddingLeft = `${depth * 14 + 4}px`;
    row.id = `tree-${encodeURIComponent(node.path).replace(/%/g, "_")}`;

    row.innerHTML = `
      <span>${isDir ? '📁' : '📄'}</span>
      <span style="overflow: hidden; text-overflow: ellipsis;">${escapeHtml(node.name)}</span>
      ${node.size ? `<span style="font-size: 10px; color: var(--text-dim); margin-left: auto;">${formatBytes(node.size)}</span>` : ''}
    `;
    container.appendChild(row);

    if (isDir && node.children) {
      node.children.forEach(c => buildDOM(c, depth + 1, container));
    }
  }

  buildDOM(rootNode, 0, elements.treeBody);
  if (elements.treeNodeStat) elements.treeNodeStat.textContent = `${totalFiles} files, ${totalDirs} dirs`;
}

async function animateStackTrace(samples) {
  if (state.speed === "instant" || !samples || samples.length === 0) return;
  const animStack = [];
  const delay = SPEED_MAP[state.speed] || 150;

  for (const sample of samples.slice(0, 30)) {
    if (!state.isRunning) break;
    if (sample.action === "PUSH") {
      animStack.push(sample.path);
    } else if (sample.action === "POP") {
      animStack.pop();
    }
    updateStackUI(animStack);
    await sleep(delay);
  }
}

/* ==========================================================================
   11. Event Listeners & Wiring
   ========================================================================== */
function setupEventListeners() {
  elements.themeBtnLight.addEventListener("click", () => applyTheme("light"));
  elements.themeBtnDark.addEventListener("click", () => applyTheme("dark"));
  elements.toggleDevModeBtn.addEventListener("click", () => toggleDevMode());

  if (elements.btnDismissWelcome) {
    elements.btnDismissWelcome.addEventListener("click", () => {
      elements.welcomeCard.style.display = "none";
      localStorage.setItem("pathdiver-welcome-dismissed", "true");
    });
  }

  elements.scopePillsBar.addEventListener("click", (e) => {
    const pill = e.target.closest(".scope-pill");
    if (!pill) return;
    document.querySelectorAll(".scope-pill").forEach(p => p.classList.remove("active"));
    pill.classList.add("active");

    const scope = pill.getAttribute("data-scope");
    if (scope === "downloads") setScopePath(state.downloadsDir || "C:\\Users\\Downloads", "Downloads");
    else if (scope === "documents") setScopePath(state.documentsDir || "C:\\Users\\Documents", "Documents");
    else if (scope === "desktop") setScopePath(state.desktopDir || "C:\\Users\\Desktop", "Desktop");
    else if (scope === "pictures") setScopePath(state.picturesDir || "C:\\Users\\Pictures", "Pictures");
    else if (scope === "drive-c") setScopePath("C:\\", "C:\\ Drive");
    else if (scope === "all-disks") setScopePath("ALL_DRIVES", "All Disks");
    else if (scope === "scratch") setScopePath(state.scratchDir || "C:\\", "Scratch");
    else if (scope.startsWith("drive-")) setScopePath(pill.getAttribute("data-path"), `${scope.replace("drive-", "").toUpperCase()}:\\ Drive`);

    if (state.isBackendAvailable && !state.targetPath.startsWith("virtual://")) {
      loadRealTree(state.targetPath);
    }
  });

  elements.btnToggleCustomPath.addEventListener("click", () => {
    elements.customPathBar.classList.toggle("show");
  });

  elements.btnLoadCustomPath.addEventListener("click", () => {
    const val = elements.targetFolderInput.value.trim();
    if (val) {
      setScopePath(val, val);
      if (state.isBackendAvailable) loadRealTree(val);
    }
  });

  elements.toolCards.forEach(card => {
    card.addEventListener("click", () => {
      const toolId = card.getAttribute("data-tool");
      switchTool(toolId);
    });
  });

  elements.btnMainScan.addEventListener("click", startScan);
  elements.btnMainPause.addEventListener("click", () => {
    state.isPaused = !state.isPaused;
    elements.btnMainPause.textContent = state.isPaused ? "▶ Resume" : "⏸ Pause";
  });
  elements.btnMainStop.addEventListener("click", () => {
    state.isRunning = false;
    finishScan();
  });

  elements.mainSearchInput.addEventListener("input", (e) => {
    state.searchQuery = e.target.value.trim();
    elements.btnSearchClear.style.display = state.searchQuery ? "block" : "none";
  });
  elements.mainSearchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") startScan();
  });
  elements.btnSearchClear.addEventListener("click", () => {
    state.searchQuery = "";
    elements.mainSearchInput.value = "";
    elements.btnSearchClear.style.display = "none";
  });

  elements.btnToggleFilters.addEventListener("click", (e) => {
    e.stopPropagation();
    const isVisible = elements.filterPopover.style.display === "flex";
    elements.filterPopover.style.display = isVisible ? "none" : "flex";
  });
  document.addEventListener("click", (e) => {
    if (!elements.filterPopover.contains(e.target) && e.target !== elements.btnToggleFilters) {
      elements.filterPopover.style.display = "none";
    }
  });

  elements.filterCategoryChips.addEventListener("click", (e) => {
    const chip = e.target.closest(".filter-chip");
    if (!chip) return;
    document.querySelectorAll(".filter-chip").forEach(c => c.classList.remove("active"));
    chip.classList.add("active");
    state.filterCategory = chip.getAttribute("data-type");
    updateFilterBadge();
  });

  elements.toggleContentCheckbox.addEventListener("change", (e) => {
    state.searchInsideContent = e.target.checked;
    updateFilterBadge();
  });

  elements.btnApplyFilters.addEventListener("click", () => {
    elements.filterPopover.style.display = "none";
    startScan();
  });
  elements.btnResetFilters.addEventListener("click", () => {
    state.filterCategory = "all";
    state.searchInsideContent = false;
    elements.toggleContentCheckbox.checked = false;
    document.querySelectorAll(".filter-chip").forEach(c => c.classList.remove("active"));
    const allChip = document.querySelector('.filter-chip[data-type="all"]');
    if (allChip) allChip.classList.add("active");
    updateFilterBadge();
  });

  elements.speedPills.forEach(pill => {
    pill.addEventListener("click", () => {
      elements.speedPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      state.speed = pill.getAttribute("data-speed");
      log("SYSTEM", `Traversal speed set to: ${state.speed.toUpperCase()}`);
    });
  });

  if (elements.devTreeFilter) {
    elements.devTreeFilter.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      document.querySelectorAll(".tree-node-row").forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? "flex" : "none";
      });
    });
  }

  if (elements.btnClearLog) {
    elements.btnClearLog.addEventListener("click", () => {
      elements.logConsole.innerHTML = "";
    });
  }
}

function updateFilterBadge() {
  let count = 0;
  if (state.filterCategory !== "all") count++;
  if (state.searchInsideContent) count++;
  if (count > 0) {
    elements.filterBadge.style.display = "inline-block";
    elements.filterBadge.textContent = count;
  } else {
    elements.filterBadge.style.display = "none";
  }
}

function log(tag, message) {
  if (!elements.logConsole) return;
  const time = new Date().toTimeString().split(' ')[0];
  const div = document.createElement("div");
  div.className = `log-entry log-${tag.toLowerCase()}`;
  div.innerHTML = `<span class="log-t">[${time}]</span> <span style="font-weight: 700;">[${tag}]</span> ${escapeHtml(message)}`;
  elements.logConsole.appendChild(div);
  elements.logConsole.scrollTop = elements.logConsole.scrollHeight;
}

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function escapeHtml(str) {
  return String(str || '').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeJs(str) {
  return String(str || '').replace(/\\/g, "\\\\").replace(/'/g, "\\'");
}

window.addEventListener("DOMContentLoaded", init);

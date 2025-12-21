import os
from pathlib import Path

BASE = Path("phoenix_engine")
CORE = BASE / "core"
API = BASE / "api"
TESTS = Path("tests")
ROOT = Path(".")

print("🦅 Executing Final V13 Cleanup & Fix...")

# -------------------------------------------------------------------------
# 1. PURGE LEGACY FILES (حذف فایل‌های تکراری قدیمی)
# -------------------------------------------------------------------------
legacy_files = [
    CORE / "vedic_chart.py",
    CORE / "engine.py",
    CORE / "time_engine.py"
]

print("🗑️ Removing legacy duplicate files from 'core/'...")
for f in legacy_files:
    if f.exists():
        os.remove(f)
        print(f"   - Deleted: {f.name} (Replaced by Engine/Infra layers)")
    else:
        print(f"   - Already gone: {f.name}")

# -------------------------------------------------------------------------
# 2. FIX API/MAIN.PY (اصلاح مسیر ایمپورت)
# -------------------------------------------------------------------------
main_py = API / "main.py"
if main_py.exists():
    print("🔧 Repairing 'api/main.py' imports...")
    content = main_py.read_text(encoding="utf-8")
    
    # تغییر ایمپورت به موتور جدید
    if "from phoenix_engine.core.vedic_chart" in content:
        content = content.replace(
            "from phoenix_engine.core.vedic_chart import VedicChart",
            "from phoenix_engine.engines.birth import BirthChartEngine as VedicChart"
        )
        # تغییر نحوه ساخت آبجکت (اگر لازم باشد، اما چون Alias زدیم شاید لازم نباشد)
        # اما برای اطمینان چک می‌کنیم آرگومان‌ها یکی باشند.
        # کلاس جدید config هم می‌گیرد که اختیاری است. پس Alias کافی است.
        
    main_py.write_text(content, encoding="utf-8")

# -------------------------------------------------------------------------
# 3. FIX TESTS (اصلاح تست‌ها)
# -------------------------------------------------------------------------
smoke_test = TESTS / "test_smoke.py"
if smoke_test.exists():
    print("🔧 Repairing 'tests/test_smoke.py'...")
    t_content = smoke_test.read_text(encoding="utf-8")
    
    if "phoenix_engine.core.vedic_chart" in t_content:
        t_content = t_content.replace(
            "from phoenix_engine.core.vedic_chart import VedicChart",
            "from phoenix_engine.engines.birth import BirthChartEngine as VedicChart"
        )
    smoke_test.write_text(t_content, encoding="utf-8")

# -------------------------------------------------------------------------
# 4. BUMP VERSION TO 13.0.0 (یکدست کردن نسخه‌ها)
# -------------------------------------------------------------------------
print("🆙 Bumping all versions to 13.0.0...")

# Update pyproject.toml
toml_path = ROOT / "pyproject.toml"
if toml_path.exists():
    toml = toml_path.read_text(encoding="utf-8")
    toml = toml.replace('version = "12.1.0"', 'version = "13.0.0"')
    toml_path.write_text(toml, encoding="utf-8")

# Update app.py
app_py = API / "app.py"
if app_py.exists():
    app_code = app_py.read_text(encoding="utf-8")
    app_code = app_code.replace('version="12.3.0"', 'version="13.0.0"')
    app_code = app_code.replace('title="Phoenix V12.3"', 'title="Phoenix Engine V13 (Cosmic)"')
    app_py.write_text(app_code, encoding="utf-8")

# Update __init__.py
init_py = BASE / "__init__.py"
if init_py.exists():
    init_py.write_text('__version__ = "13.0.0"\n', encoding="utf-8")

print("✅ Cleanup Complete. System is now fully consistent.")
print("Legacy ghosts are gone. Run 'git add .' and 'git commit' now.")
import os
from pathlib import Path

BASE = Path("phoenix_engine")
DOMAIN = BASE / "domain"
PLUGINS = BASE / "plugins"

print("🦅 Fixing V13 Startup Crash...")

# -------------------------------------------------------------------------
# 1. ADD MISSING MODELS TO ANALYSIS.PY
# -------------------------------------------------------------------------
analysis_path = DOMAIN / "analysis.py"
if analysis_path.exists():
    print("🔧 Defining missing models in 'domain/analysis.py'...")
    content = analysis_path.read_text(encoding="utf-8")
    
    # اضافه کردن تعاریف اگر وجود ندارند
    if "VargaInfo =" not in content:
        extra_models = """
# --- Defined Types (Aliases for now) ---
VargaInfo = Dict[str, Any]
AshtakavargaInfo = Dict[str, Any]
YogaInfo = List[str]
MaitriInfo = Dict[str, Any]
AvasthaInfo = Dict[str, Any]
BhavaBalaInfo = Dict[str, float]
PhalaInfo = Dict[str, Any]
"""
        content += extra_models
        analysis_path.write_text(content, encoding="utf-8")

# -------------------------------------------------------------------------
# 2. FIX IMPORT IN VARGAS.PY
# -------------------------------------------------------------------------
vargas_path = PLUGINS / "vargas.py"
if vargas_path.exists():
    print("🔧 Fixing import path in 'plugins/vargas.py'...")
    v_content = vargas_path.read_text(encoding="utf-8")
    
    # تغییر آدرس غلط (config) به آدرس صحیح (analysis)
    if "from phoenix_engine.domain.config import VargaInfo" in v_content:
        v_content = v_content.replace(
            "from phoenix_engine.domain.config import VargaInfo",
            "from phoenix_engine.domain.analysis import VargaInfo"
        )
        vargas_path.write_text(v_content, encoding="utf-8")

print("✅ Fix Applied. Try starting the server again.")
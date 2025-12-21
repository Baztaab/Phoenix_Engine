import os
from pathlib import Path

BASE = Path("phoenix_engine")
DOMAIN = BASE / "domain"
TESTS = Path("tests")

print("🦅 Removing Geocentric Bias (Asia/Tehran)...")

# 1. FIX DOMAIN/INPUT.PY (Make timezone required)
input_py = DOMAIN / "input.py"
if input_py.exists():
    print("🔧 Updating 'BirthData' to require timezone...")
    content = input_py.read_text(encoding="utf-8")
    
    # حذف مقدار پیش‌فرض. حالا کاربر مجبور است تایم‌زون را بفرستد.
    # تبدیل: timezone: str = Field(default="Asia/Tehran") 
    # به:     timezone: str = Field(..., description="IANA Timezone e.g. 'Europe/London'")
    
    if 'default="Asia/Tehran"' in content:
        content = content.replace(
            'timezone: str = Field(default="Asia/Tehran")',
            'timezone: str = Field(..., description="IANA Timezone string (e.g., Asia/Tehran, UTC)")'
        )
        input_py.write_text(content, encoding="utf-8")
        print("   ✅ BirthData is now unbiased (Timezone is mandatory).")
    else:
        print("   ⚠️ Already fixed or pattern not found.")

# 2. UPDATE TESTS (Tests must now be explicit)
# چون تایم‌زون اجباری شد، اگر تستی آن را نفرستد فیل می‌شود.
# باید مطمئن شویم تست‌ها صریحاً تایم‌زون دارند.
smoke_test = TESTS / "test_smoke.py"
if smoke_test.exists():
    print("🔧 Updating Tests to be explicit...")
    t_content = smoke_test.read_text(encoding="utf-8")
    
    # در تست‌های فعلی خوشبختانه تایم‌زون را می‌فرستیم، پس احتمالاً مشکلی نیست.
    # اما محض اطمینان چک می‌کنیم.
    if '"timezone": "Asia/Tehran"' in t_content:
        print("   ℹ️ Tests are already explicit about timezone. Good.")
    else:
        print("   ⚠️ Warning: Tests might fail if they relied on default timezone.")

print("✅ Operation 'Global Standard' Complete.")
print("Now, if a user forgets the timezone, they get a proper validation error (422 Unprocessable Entity).")
print("This is much safer than silently assuming Tehran.")
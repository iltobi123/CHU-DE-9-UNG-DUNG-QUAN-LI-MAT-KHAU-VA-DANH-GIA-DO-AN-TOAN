import os
import subprocess
import sys

# 1. API KEY CỦA BẠN
API_KEY = "__________________________________"  # <-- Thay bằng API Key của bạn

# 2. TẠO FILE .ENV
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, ".env")

with open(env_path, "w") as f:
    f.write(f"GEMINI_API_KEY={API_KEY}\n")

print(f"✅ Đã tạo/cập nhật file .env thành công tại: {env_path}")
print("🚀 Đang khởi động server Uvicorn...")

# 3. KHỞI ĐỘNG SERVER
subprocess.run([sys.executable, "-m", "uvicorn", "backend:app", "--reload"], cwd=project_root)

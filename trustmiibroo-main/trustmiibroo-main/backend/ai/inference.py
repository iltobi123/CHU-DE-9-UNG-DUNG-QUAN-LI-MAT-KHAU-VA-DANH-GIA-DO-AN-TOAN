import os
import random
import string
from dotenv import load_dotenv, find_dotenv
from google import genai

# 1. CƯỠNG CHẾ TÌM VÀ TẢI FILE .ENV
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path)
else:
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# 2. CẤU HÌNH API KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

print("KEY:", GEMINI_API_KEY)

STRENGTH_LABELS = {
    0: "Rất yếu",
    1: "Yếu",
    2: "Trung bình",
    3: "Khá mạnh",
    4: "Rất mạnh",
}

def _pick_pad_char(inc_upper: bool, inc_num: bool, inc_sym: bool, inc_ambig: bool) -> str:
    """Hàm phụ trợ để chọn ký tự đắp vào cho đủ độ dài"""
    choices = []
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    numbers = "23456789" if inc_ambig else "0123456789"
    uppers = "ABCDEFGHJKMNPQRSTUVWXYZ" if inc_ambig else string.ascii_uppercase
    lowers = "abcdefghjkmnpqrstuvwxyz" if inc_ambig else string.ascii_lowercase

    if inc_sym: choices.extend(list(symbols))
    if inc_num: choices.extend(list(numbers))
    if inc_upper: choices.extend(list(uppers))
    if not choices: choices.extend(list(lowers))
    
    return random.choice(choices)
    

def process_password(password: str, target_len: int = 16,
                     inc_upper: bool = True, inc_num: bool = True,
                     inc_sym: bool = True, inc_ambig: bool = False) -> dict:
    
    if not GEMINI_API_KEY or not client:
        return {
            "original": password,
            "enhanced": "LỖI: Chưa cấu hình GEMINI_API_KEY. Hãy chạy file start.py!",
            "strength_score": 0,
            "strength_label": STRENGTH_LABELS.get(0),
        }

    try:
        base_word = password if password and password.strip() else "một từ tiếng Anh ngẫu nhiên, hài hước"
        prompt = f"""
        Tạo một mật khẩu sáng tạo, tàn bạo dựa trên từ khóa: '{base_word}'.
        Chỉ trả về chuỗi mật khẩu, khoảng {target_len} ký tự. Không in dấu ngoặc kép, không giải thích.
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        ai_pw = (response.text or "").strip().replace('"', '').replace("'", '').replace(' ', '')
        
        if not ai_pw:
            ai_pw = "TrUStMiiBr0"

        if inc_ambig:
            for c in "il1Lo0O":
                ai_pw = ai_pw.replace(c, "")
        
        if not inc_upper:
            ai_pw = ai_pw.lower()
        elif not any(c.isupper() for c in ai_pw):
            ai_pw += random.choice("ABCDEFGHJKMNPQRSTUVWXYZ" if inc_ambig else string.ascii_uppercase)

        if not inc_num:
            ai_pw = ''.join([c for c in ai_pw if not c.isdigit()])
        elif not any(c.isdigit() for c in ai_pw):
            ai_pw += random.choice("23456789" if inc_ambig else "0123456789")

        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not inc_sym:
            ai_pw = ''.join([c for c in ai_pw if c.isalnum()])
        elif not any(c in symbols for c in ai_pw):
            ai_pw += random.choice(symbols)

        if len(ai_pw) > target_len:
            ai_pw = ai_pw[:target_len]
            if inc_upper and not any(c.isupper() for c in ai_pw):
                ai_pw = ai_pw[:-1] + random.choice(string.ascii_uppercase)
            if inc_num and not any(c.isdigit() for c in ai_pw):
                ai_pw = ai_pw[:-1] + random.choice("23456789")
            if inc_sym and not any(c in symbols for c in ai_pw):
                ai_pw = ai_pw[:-1] + random.choice(symbols)
                
        while len(ai_pw) < target_len:
            ai_pw += _pick_pad_char(inc_upper, inc_num, inc_sym, inc_ambig)

        score = 4
        if not inc_upper: score -= 1
        if not inc_num: score -= 1
        if not inc_sym: score -= 1
        if len(ai_pw) < 8: score -= 1
        score = max(0, min(4, score))

        return {
            "original": password,
            "enhanced": ai_pw,
            "strength_score": score,
            "strength_label": STRENGTH_LABELS.get(score),
        }
        
    except Exception as e:
        print(f"⚠️ Cảnh báo AI: {str(e)} -> Đang chuyển sang chế độ tạo thủ công (Fallback)")
        
        fallback_pw = password if password and password.strip() else "TrUSt"
        
        while len(fallback_pw) < target_len:
            fallback_pw += _pick_pad_char(inc_upper, inc_num, inc_sym, inc_ambig)
            
        if inc_upper and not any(c.isupper() for c in fallback_pw):
            fallback_pw = fallback_pw[:-1] + random.choice(string.ascii_uppercase)
        if inc_num and not any(c.isdigit() for c in fallback_pw):
            fallback_pw = fallback_pw[:-1] + random.choice("23456789")
        if inc_sym and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in fallback_pw):
            fallback_pw = fallback_pw[:-1] + random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?")
            
        score = 4
        if not inc_upper: score -= 1
        if not inc_num: score -= 1
        if not inc_sym: score -= 1
        if len(fallback_pw) < 8: score -= 1
        score = max(0, min(4, score))

        return {
            "original": password,
            "enhanced": fallback_pw,
            "strength_score": score,
            "strength_label": STRENGTH_LABELS.get(score),
        }

import time
import random
import pytz
import logging
import re
from datetime import datetime
from core.emojis import E
from core.ui_helper import UserRoles

logger = logging.getLogger("Lyra")

class SentienceEngine:
    def __init__(self, db): 
        self.db = db; self.col = db["user_soul_data"]; self.afk_col = db["afk_data"]
        self.marry_col = db["marriage_data"]
        
    def check_weekly_reset(self):
        curr_week = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%Y-%V")
        conf = self.db["bot_config"].find_one({"_id": "weekly_reset"})
        if not conf or conf.get("week") != curr_week:
            self.col.update_many({}, {"$set": {"weekly_xp": 0, "weekly_coins": 0}})
            self.db["bot_config"].update_one({"_id": "weekly_reset"}, {"$set": {"week": curr_week}}, upsert=True)
            
    def get_state_bank(self):
        b = self.db["bot_config"].find_one({"_id": "state_bank"})
        if not b:
            self.db["bot_config"].insert_one({"_id": "state_bank", "balance": 5000000})
            return 5000000
        return max(0, b["balance"])
        
    def update_state_bank(self, amount):
        self.db["bot_config"].update_one({"_id": "state_bank"}, {"$inc": {"balance": amount}}, upsert=True)
            
    def get_soul(self, uid: int):
        s = self.col.find_one({"uid": uid})
        now = time.time()
        if not s: 
            s = {"uid": uid, "xp": 0, "level": 1, "coins": 0, "bank": 0, "debt": 0, 
                 "weekly_xp": 0, "weekly_coins": 0, "daily_luck": 0, "last_pray": "", 
                 "last_work": 0, "last_rob": 0, "last_fish": 0, "last_mine": 0, 
                 "last_hunt": 0, "last_beg": 0, "last_banthan": 0, "last_luadao": 0, 
                 "last_dapda": 0, "last_nhayau": 0, "last_luck_reset": "", 
                 "inventory": [], "job": None, "tax_rate": 0, "last_quitjob": 0,
                 "bhxh_fund": 0, "bhyt_fund": 0, "last_bhxh_paid": 0, "last_bhyt_paid": 0,
                 "last_bank_calc": now, "last_debt_calc": now}
            self.col.insert_one(s)
        today = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d')
        if s.get("last_luck_reset") != today: 
            s["daily_luck"] = 0
            self.col.update_one({"uid": uid}, {"$set": {"last_luck_reset": today}})
        return s
        
    def add_xp(self, uid: int, amount: int):
        self.check_weekly_reset(); soul = self.get_soul(uid)
        if self.marry_col.find_one({"$or": [{"u1": uid}, {"u2": uid}]}): amount = int(amount * 1.2)
        xp = soul.get("xp", 0) + amount; wxp = soul.get("weekly_xp", 0) + amount
        new_level = 1 + xp // 100; leveled_up = new_level > soul.get("level", 1)
        self.col.update_one({"uid": uid}, {"$set": {"xp": xp, "weekly_xp": wxp, "level": new_level}}, upsert=True)
        return leveled_up, new_level

    def process_earn(self, uid: int, amount: int):
        if amount <= 0: return 0, 0
        bank_bal = self.get_state_bank()
        if bank_bal < amount: amount = bank_bal
        if amount <= 0: return 0, 0

        s = self.get_soul(uid); tax_rate = s.get("tax_rate", 0)
        tax = int(amount * (tax_rate / 100.0)); net = amount - tax
        self.update_state_bank(-amount)
        if tax > 0 and uid != UserRoles.N_ID:
            self.col.update_one({"uid": UserRoles.N_ID}, {"$inc": {"coins": tax}})
        self.col.update_one({"uid": uid}, {"$inc": {"coins": net, "weekly_coins": net}})
        return net, tax

    def process_fine(self, uid: int, amount: int, accident_type=None):
        if amount <= 0: return 0, ""
        s = self.get_soul(uid); cost = amount; msg_extra = ""
        if accident_type:
            fund_key = f"bh{accident_type}_fund"; last_key = f"last_bh{accident_type}_paid"
            fund = s.get(fund_key, 0); last_paid = s.get(last_key, 0); now = time.time()
            weeks_missed = (now - last_paid) / (7 * 86400) if last_paid > 0 else 999
            
            if weeks_missed <= 3 and fund > 0:
                cost = int(amount * 0.2)
                msg_extra = f"\n> 🛡️ *Bảo hiểm gánh 80% thiệt hại, bạn chỉ trả 20%!*"
            else:
                if fund >= cost:
                    self.col.update_one({"uid": uid}, {"$inc": {fund_key: -cost}})
                    cost = 0; msg_extra = f"\n> 🛡️ *Bảo hiểm hết hạn! Tự động trừ sạch {amount} xu vào quỹ dự phòng!*"
                elif fund > 0:
                    cost -= fund
                    self.col.update_one({"uid": uid}, {"$set": {fund_key: 0}})
                    msg_extra = f"\n> 🛡️ *Bảo hiểm hết hạn! Vét cạn quỹ dư bù được {fund} xu!*"

        self.col.update_one({"uid": uid}, {"$inc": {"coins": -cost}})
        self.update_state_bank(cost)
        return cost, msg_extra

class LightLogicEngine:
    @staticmethod
    def safe_eval(expr: str):
        if re.match(r'^[\d\s\+\-\*\/\(\)\.\%]+$', expr.strip()) and not re.search(r'[a-zA-Z_]', expr):
            try: 
                return f"🧮 Kết quả nhảy số nhẹ nhàng: {eval(expr, {'__builtins__': {}}, {})}"
            except Exception as e:
                logger.warning(f"⚠️ Eval error: {e}")
                return None
        return None

class FeaturesModule:
    def __init__(self, db, bot_instance): self.db = db; self.bot = bot_instance
    def _generate_tarot_deck(self):
        majors = ["0 - The Fool|Sự ngây thơ, bắt đầu một hành trình mới.", "I - The Magician|Sự sáng tạo, sức mạnh và quyền năng.", "II - The High Priestess|Trực giác, sự bí ẩn và thông thái.", "III - The Empress|Sự sinh sôi, vẻ đẹp và trù phú.", "IV - The Emperor|Kỷ luật, cấu trúc và quyền lực.", "V - The Hierophant|Truyền thống, tín ngưỡng và sự học hỏi.", "VI - The Lovers|Tình yêu, sự hòa hợp và những quyết định.", "VII - The Chariot|Sự kiểm soát, ý chí và chiến thắng.", "VIII - Strength|Sức mạnh nội tâm, dũng cảm và nhẫn nại.", "IX - The Hermit|Sự cô độc, tĩnh lặng và tìm kiếm nội tâm.", "X - Wheel of Fortune|Vòng quay định mệnh, sự thay đổi bất ngờ.", "XI - Justice|Công lý, sự thật và nhân quả.", "XII - The Hanged Man|Sự hy sinh, buông bỏ và thay đổi góc nhìn.", "XIII - Death|Sự kết thúc, chuyển hóa và lột xác.", "XIV - Temperance|Sự cân bằng, điều độ và kiên nhẫn.", "XV - The Devil|Sự cám dỗ, vật chất và những trói buộc.", "XVI - The Tower|Sự sụp đổ bất ngờ, thảm họa và thức tỉnh.", "XVII - The Star|Hy vọng, niềm tin và sự chữa lành.", "XVIII - The Moon|Ảo ảnh, nỗi sợ hãi và tiềm thức.", "XIX - The Sun|Thành công, niềm vui và sự tỏa sáng.", "XX - Judgement|Sự phán xét, tái sinh và nhận thức.", "XXI - The World|Sự trọn vẹn, hoàn thành và viên mãn."]
        suits = [("Wands", "Hành động, đam mê và nhiệt huyết"), ("Cups", "Cảm xúc, tình yêu và trực giác"), ("Swords", "Trí tuệ, xung đột và thử thách"), ("Pentacles", "Vật chất, công việc và tài chính")]
        faces = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]
        deck = majors.copy(); [deck.extend([f"{f} of {s}|Đại diện cho {m}." for f in faces]) for s, m in suits]
        return deck
        
    async def get_fortune(self, user_id: int) -> str:
        today = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d'); f_rec = self.db["fortunes"].find_one({"uid": user_id, "date": today})
        if f_rec: return f"{E.INFO} Tham lam vừa thôi, vũ trụ dặn **mỗi ngày chỉ bốc 1 lần** nhé bạn êy! 🌙\n> *(Lá bài hôm nay của bạn: **{f_rec['card']}**)*"
        card_raw = random.choice(self._generate_tarot_deck()); card, meaning = card_raw.split("|")
        self.db["fortunes"].insert_one({"uid": user_id, "date": today, "card": card, "meaning": meaning})
        return f"{E.TAROT} **TRẢI BÀI TAROT HÔM NAY** {E.TAROT}\n{E.BAR * 8}\n> **Lá bài:** `{card}`\n> **Thông điệp:** {meaning}\n\n*Hẹn bạn ngày mai nhé! ✨*"

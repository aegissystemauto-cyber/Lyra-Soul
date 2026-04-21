import time, random, pytz
from datetime import datetime
import discord
from core.emojis import E
from core.ui_helper import UIHelper, LoanPromptView

class EconomyCog:
    def __init__(self, cmd_sys):
        self.cmd_sys = cmd_sys
        self.bot = cmd_sys.bot

    def register(self):
        c = self.cmd_sys.commands
        eco_cmds = ["daily", "balance", "bal", "pay", "paydebt", "pray", "work", "fish", "mine", "hunt", "beg", "banthan", "luadao", "dapda", "nhayau", "dep", "with", "bank", "invest", "heist", "giveaway", "baolanh", "shop", "shopjob", "buy", "lyrabank", "inv", "checkdo", "sell", "bhxh", "bhyt", "rolljob", "dojob", "quitjob", "rob", "trade", "rebirth", "top", "level"]
        for ac in eco_cmds: c[f"!{ac}"] = {"func": getattr(self, f"cmd_{ac}")}

    def get_job_items(self):
        return {"súng nước": {"name": "Súng nước", "price": 10000, "uses": 10, "icon": "🔫"}, "bút máy": {"name": "Bút máy", "price": 3000, "uses": 20, "icon": "🖋️"}, "máy ảnh": {"name": "Máy ảnh", "price": 4500, "uses": 15, "icon": "📸"}, "ống nghe": {"name": "Ống nghe", "price": 6000, "uses": 20, "icon": "🩺"}, "loa kẹo kéo": {"name": "Loa kẹo kéo", "price": 1500, "uses": 15, "icon": "🔊"}, "máy tính casio": {"name": "Máy tính casio", "price": 2500, "uses": 30, "icon": "🧮"}, "phấn tiên": {"name": "Phấn tiên", "price": 1000, "uses": 25, "icon": "🖍️"}, "dao phay": {"name": "Dao phay", "price": 1200, "uses": 20, "icon": "🔪"}, "bàn phím cơ": {"name": "Bàn phím cơ", "price": 8000, "uses": 40, "icon": "⌨️"}, "súng": {"name": "Súng", "price": 20000, "uses": 15, "icon": "🔫"}, "giấy nháp": {"name": "Giấy nháp", "price": 500, "uses": 10, "icon": "📜"}, "từ điển": {"name": "Từ điển", "price": 5000, "uses": 50, "icon": "📖"}, "tay cầm ps5": {"name": "Tay cầm ps5", "price": 15000, "uses": 35, "icon": "🎮"}}
    def get_general_items(self): return {"bùa": {"name": "Bùa", "price": 5000, "uses": 5, "icon": "🍀"}, "khẩu trang": {"name": "Khẩu trang", "price": 1500, "uses": 3, "icon": "😷"}}
    def get_all_items(self): return {**self.get_job_items(), **self.get_general_items()}

    async def cmd_daily(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); today = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d')
        if s.get("last_daily") == today: return await msg.channel.send(f"{E.ERR} Tham lam, húp rồi mai quay lại!")
        bank_bal = self.bot.sentience.get_state_bank()
        if bank_bal < 500: return await msg.channel.send(embed=UIHelper.error("🏛️ NGÂN KHỐ RỖNG TUẾCH", f"> Kho bạc nhà nước đói nhăn răng, không đủ tiền phát lương! Đợi đứa nào nạp đi ba!"))
        net, tax = self.bot.sentience.process_earn(msg.author.id, 500)
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_daily": today}})
        await msg.channel.send(embed=UIHelper.success("ĐIỂM DANH", f"> Húp **{net}** {E.COIN} daily rủng rỉnh túi rồi nha!" + (f" (Đã đóng thuế **{tax}** {E.COIN})" if tax > 0 else "")))

    async def cmd_bank(self, msg, args):
        u = msg.mentions[0] if msg.mentions else msg.author
        s = self.bot.sentience.get_soul(u.id)
        desc = f"> {E.COIN} Tiền túi: **{s.get('coins',0):,}**\n> 🏦 Ngân hàng: **{s.get('bank',0):,}**\n> 🩸 Nợ giang hồ: **{s.get('debt',0):,}**\n> 🛡️ BHXH: **{s.get('bhxh_fund',0):,}** | 🏥 BHYT: **{s.get('bhyt_fund',0):,}**"
        rb = s.get('rebirth', 0)
        if rb > 0: desc += f"\n> 🔥 **Trùng Sinh:** `{rb} Lần`"
        await msg.channel.send(embed=UIHelper.info(f"TÀI SẢN KẾCH XÙ CỦA {u.name}", desc))
    async def cmd_bal(self, msg, args): await self.cmd_bank(msg, args)

    async def cmd_pay(self, msg, args):
        if not msg.mentions or len(args) < 2 or not args[-1].isdigit(): return await msg.channel.send(f"{E.ERR} Dùng: `!pay <@user> <số_tiền>` nhen cha!")
        amt = int(args[-1]); t = msg.mentions[0]
        if self.bot.sentience.get_soul(msg.author.id).get('coins',0) < amt: return await msg.channel.send(f"{E.ERR} Cháy túi mà đòi chuyển khoản?")
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": -amt}}); self.bot.sentience.col.update_one({"uid": t.id}, {"$inc": {"coins": amt}})
        await msg.channel.send(f"💸 Đã bắn **{amt}** {E.COIN} sang ví của {t.mention} mượt mà!")

    async def cmd_paydebt(self, msg, args):
        if not args or not args[0].isdigit(): return await msg.channel.send(f"{E.ERR} Nôn số tiền muốn trả vô!")
        amt = int(args[0]); s = self.bot.sentience.get_soul(msg.author.id)
        if s.get('debt',0) <= 0: return await msg.channel.send(f"{E.ERR} Có nợ mống nào đâu mà trả?")
        amt = min(amt, s.get('debt',0))
        if s.get('coins',0) < amt: return await msg.channel.send(f"{E.ERR} Tiền túi éo đủ trả cục nợ này nha!")
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": -amt, "debt": -amt}})
        await msg.channel.send(f"✅ Đã ói ra **{amt}** {E.COIN} trả nợ, bớt gánh nặng cuộc đời!")

    async def cmd_pray(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); today = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d')
        if s.get("last_pray") == today: return await msg.channel.send(f"{E.ERR} Đã thắp nhang rồi, trời phật đi vắng rồi đợi mai đi!")
        luck = random.randint(1, 10)
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_pray": today}, "$inc": {"daily_luck": luck}})
        await msg.channel.send(embed=UIHelper.success("CẦU NGUYỆN", f"> Khấn vái thần linh ban cho **+{luck} Nhân Phẩm** hôm nay!"))

    async def cmd_work(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); now = time.time(); last = s.get("last_work", 0)
        if now - last < 3600: return await msg.channel.send(embed=UIHelper.error("Làm gì căng thế?", f"> Nghỉ tay đi thanh niên, đợi **{int((3600 - (now - last)) // 60)} phút** nữa mới được cày tiếp!"))
        bank_bal = self.bot.sentience.get_state_bank()
        if bank_bal < 250: return await msg.channel.send(embed=UIHelper.error("🏛️ NGÂN KHỐ RỖNG TUẾCH", "> Nhà nước đang phá sản, đào đâu ra tiền trả lương cày cuốc? Đợi đứa nào nạp tiền vào kho đi!"))
        has_bua = "Bùa" in s.get("inventory", []); r = random.SystemRandom().random(); luck = s.get("daily_luck", 0)
        win_rate = min(0.95, (0.6 if not has_bua else 0.75) + (luck * 0.03))
        
        if r < win_rate: 
            amt = random.randint(50, 250); net, tax = self.bot.sentience.process_earn(msg.author.id, amt)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_work": now}})
            msgs = [f"Phát tờ rơi dạo được bo {amt} xu!", f"Đi múa cột ở bar được đại gia bo {amt} xu!", f"Làm osin nhặt rác lượm được {amt} xu!", f"Livestream khóc lóc có người donate {amt} xu!", f"Gõ phím thuê mỏi tay chốt được {amt} xu!"]
            await msg.channel.send(embed=UIHelper.success("💼 Vác mặt đi làm", f"> {random.choice(msgs)}{' 🍀' if has_bua else ''}\n> 💰 **Húp:** **{net}** {E.COIN}" + (f" *(Thuế: -{tax})*" if tax>0 else "")))
        elif r < min(0.95, win_rate + 0.15): 
            amt = random.randint(20, 80); cost, extra = self.bot.sentience.process_fine(msg.author.id, amt, accident_type="xh")
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_work": now}})
            msgs = [f"Hậu đậu làm vỡ bình bông, đền {amt} xu!", f"Đi trễ sếp mắng xối xả, trừ luôn {amt} xu!", f"Vấp cục đá té rớt mất {amt} xu!", f"Bốc vác mỏi lưng rớt thùng hàng đền {amt} xu!", f"Gõ code thuê bị bug xóa nhầm DB đền {amt} xu!"]
            await msg.channel.send(embed=UIHelper.error("💼 Mạt vận", f"> {random.choice(msgs)}\n> 💸 **Thiệt hại:** **-{cost}** {E.COIN} {extra}"))
        else: 
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_work": now}})
            msgs = ["Công ty phá sản bùng lương trắng tay!", "Làm bục mặt xong thằng giám đốc ẵm tiền trốn rồi, đen vãi!", "Nằm ườn cắn móng tay hết ngày chả làm được gì!", "Đến công ty lướt Tiktok bị đuổi thẳng cổ!", "Ngủ quên đéo thức dậy đi làm, nhịn đói!"]
            await msg.channel.send(embed=UIHelper.info("💼 Kiếp nô lệ làm công", f"> {random.choice(msgs)}"))

    async def cmd_fish(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); now = time.time(); last = s.get("last_fish", 0)
        if now - last < 300: return await msg.channel.send(f"{E.ERR} Cá chưa kịp đẻ, ráng đợi {int((300-(now-last))//60)} phút nữa ra câu!")
        bank_bal = self.bot.sentience.get_state_bank()
        if bank_bal < 150: return await msg.channel.send(embed=UIHelper.error("🏛️ NGÂN KHỐ RỖNG TUẾCH", "> Nhà nước đang phá sản! Đợi đứa nào nạp tiền vào kho đi!"))
        has_bua = "Bùa" in s.get("inventory", []); r = random.SystemRandom().random(); luck = s.get("daily_luck", 0)
        win_rate = min(0.95, (0.50 if not has_bua else 0.65) + (luck * 0.03))
        if r < win_rate:
            amt = random.randint(30, 150); net, tax = self.bot.sentience.process_earn(msg.author.id, amt)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_fish": now}})
            await msg.channel.send(embed=UIHelper.success("🎣 KÉO CÁ MƯỢT", f"> Móc trúng cá lựm **{net}** {E.COIN}" + (f" *(Thuế: -{tax})*" if tax>0 else "")))
        elif r < min(0.95, win_rate + 0.20):
            amt = random.randint(10, 50); cost, extra = self.bot.sentience.process_fine(msg.author.id, amt, accident_type="xh")
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_fish": now}})
            await msg.channel.send(embed=UIHelper.error("🎣 TAI NẠN", f"> Rớt xu mịa rồi!\n> 💸 **Thiệt hại:** **-{cost}** {E.COIN} {extra}"))
        else:
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_fish": now}})
            await msg.channel.send(embed=UIHelper.info("🎣 TRẮNG TAY", f"> Mốc mỏ đéo dính con nào!"))

    async def cmd_mine(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); now = time.time(); last = s.get("last_mine", 0)
        if now - last < 600: return await msg.channel.send(f"{E.ERR} Mỏ đang sập, đợi {int((600-(now-last))//60)} phút nữa ra đào!")
        bank_bal = self.bot.sentience.get_state_bank()
        if bank_bal < 200: return await msg.channel.send(embed=UIHelper.error("🏛️ NGÂN KHỐ RỖNG TUẾCH", "> Nhà nước đang phá sản!"))
        has_bua = "Bùa" in s.get("inventory", []); r = random.SystemRandom().random(); luck = s.get("daily_luck", 0)
        win_rate = min(0.95, (0.40 if not has_bua else 0.60) + (luck * 0.03))
        if r < win_rate:
            amt = random.randint(40, 200); net, tax = self.bot.sentience.process_earn(msg.author.id, amt)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_mine": now}})
            await msg.channel.send(embed=UIHelper.success("⛏️ ĐÀO MỎ", f"> Lụm vàng húp **{net}** {E.COIN}" + (f" *(Thuế: -{tax})*" if tax>0 else "")))
        elif r < min(0.95, win_rate + 0.30):
            amt = random.randint(20, 70); cost, extra = self.bot.sentience.process_fine(msg.author.id, amt, accident_type="xh")
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_mine": now}})
            await msg.channel.send(embed=UIHelper.error("⛏️ TAI NẠN", f"> Cuốc dội bể đầu!\n> 💸 **Thiệt hại:** **-{cost}** {E.COIN} {extra}"))
        else:
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_mine": now}})
            await msg.channel.send(embed=UIHelper.info("⛏️ TOÀN RÁC", f"> Đào bục mặt đéo ra gì!"))

    async def cmd_hunt(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); now = time.time(); last = s.get("last_hunt", 0)
        if now - last < 420: return await msg.channel.send(f"{E.ERR} Thú nó rén trốn hết rồi, đợi {int((420-(now-last))//60)} phút nữa!")
        bank_bal = self.bot.sentience.get_state_bank()
        if bank_bal < 120: return await msg.channel.send(embed=UIHelper.error("🏛️ NGÂN KHỐ RỖNG TUẾCH", "> Hết tiền mua thú rừng rùi!"))
        has_bua = "Bùa" in s.get("inventory", []); r = random.SystemRandom().random(); luck = s.get("daily_luck", 0)
        win_rate = min(0.95, (0.45 if not has_bua else 0.65) + (luck * 0.03))
        if r < win_rate:
            amt = random.randint(20, 120); net, tax = self.bot.sentience.process_earn(msg.author.id, amt)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_hunt": now}})
            await msg.channel.send(embed=UIHelper.success("🏹 THỢ SĂN", f"> Húp thịt rừng **{net}** {E.COIN}" + (f" *(Thuế: -{tax})*" if tax>0 else "")))
        elif r < min(0.95, win_rate + 0.25):
            amt = random.randint(15, 60); cost, extra = self.bot.sentience.process_fine(msg.author.id, amt, accident_type="xh")
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_hunt": now}})
            await msg.channel.send(embed=UIHelper.error("🏹 TOANG RỒI", f"> Đạn giật mẻ răng!\n> 💸 **Thiệt hại:** **-{cost}** {E.COIN} {extra}"))
        else:
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_hunt": now}})
            await msg.channel.send(embed=UIHelper.info("🏹 TRẮNG TAY", f"> Vác súng đi vác súng về!"))

    async def cmd_beg(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); now = time.time(); last = s.get("last_beg", 0)
        if now - last < 180: return await msg.channel.send(f"{E.ERR} Đợi {int((180-(now-last))//60)} phút nữa ra ăn mày tiếp!")
        r = random.SystemRandom().random(); luck = s.get("daily_luck", 0); win_rate = min(0.95, 0.3 + (luck * 0.03))
        if r < win_rate:
            amt = random.randint(5, 50); net, tax = self.bot.sentience.process_earn(msg.author.id, amt)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_beg": now}})
            await msg.channel.send(embed=UIHelper.success("🥺 ĂN MÀY", f"> Lụm bạc cắc **{net}** {E.COIN}"))
        elif r < min(0.95, win_rate + 0.3):
            amt = random.randint(1, 10); cost, extra = self.bot.sentience.process_fine(msg.author.id, amt, accident_type="yt")
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_beg": now}})
            await msg.channel.send(embed=UIHelper.error("🥺 BỊ ĐÁNH ĐUỔI", f"> 💸 **Mất:** **-{cost}** {E.COIN} {extra}"))
        else:
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_beg": now}})
            await msg.channel.send(embed=UIHelper.info("🥺 KHÔNG AI CHO", f"> Lạy gãy cổ đéo ai cho cắc nào!"))

    async def cmd_banthan(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); now = time.time(); last = s.get("last_banthan", 0)
        if now - last < 7200: return await msg.channel.send(f"{E.ERR} L má háng đang sưng tấy bạn ráng đợi {int((7200-(now-last))//60)} phút nữa!")
        has_bua = "Bùa" in s.get("inventory", []); r = random.SystemRandom().random(); luck = s.get("daily_luck", 0)
        win_rate = min(0.60, (0.40 if not has_bua else 0.50) + (luck * 0.03))
        if r < win_rate:
            amt = random.randint(1000, 3000); net, tax = self.bot.sentience.process_earn(msg.author.id, amt)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_banthan": now}})
            await msg.channel.send(embed=UIHelper.success("💋 BÁN THÂN", f"> Húp đậm **{net}** {E.COIN}"))
        elif r < min(0.95, win_rate + 0.60):
            amt = random.randint(100, 300); fine = random.randint(1500, 4500)
            self.bot.sentience.process_earn(msg.author.id, amt)
            cost, extra = self.bot.sentience.process_fine(msg.author.id, fine, accident_type="yt")
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_banthan": now}})
            await msg.channel.send(embed=UIHelper.error("🚨 DÍNH SIDA RỒI ĐM", f"> Chữa bệnh mất mẹ **-{cost}** {E.COIN} {extra}"))
        else:
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_banthan": now}})
            await msg.channel.send(embed=UIHelper.info("🚫 Ế MỐC LỎ", f"> Đứng đường đéo ai hốt!"))

    async def cmd_luadao(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); now = time.time(); last = s.get("last_luadao", 0)
        if now - last < 5400: return await msg.channel.send(f"{E.ERR} Trốn {int((5400-(now-last))//60)} phút nữa hẵng ló mặt!")
        has_bua = "Bùa" in s.get("inventory", []); r = random.SystemRandom().random(); luck = s.get("daily_luck", 0)
        win_rate = min(0.95, (0.55 if not has_bua else 0.70) + (luck * 0.03))
        if r < win_rate:
            amt = random.randint(150, 450); net, tax = self.bot.sentience.process_earn(msg.author.id, amt)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_luadao": now}})
            await msg.channel.send(embed=UIHelper.success("🎭 LÙA GÀ THẦN SẦU", f"> Húp: **{net}** {E.COIN}"))
        elif r < min(0.95, win_rate + 0.25):
            amt = random.randint(50, 200); cost, extra = self.bot.sentience.process_fine(msg.author.id, amt, accident_type="xh")
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_luadao": now}})
            await msg.channel.send(embed=UIHelper.error("🚨 BÓC PHỐT", f"> Ói ra: **-{cost}** {E.COIN} {extra}"))
        else:
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_luadao": now}})
            await msg.channel.send(embed=UIHelper.info("🚫 SCAM LỎ", f"> Xạo lìn đéo ai tin!"))

    async def cmd_dapda(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); now = time.time(); last = s.get("last_dapda", 0)
        if now - last < 4800: return await msg.channel.send(f"{E.ERR} Nghỉ {int((4800-(now-last))//60)} phút nx quai lại!")
        has_bua = "Bùa" in s.get("inventory", []); r = random.SystemRandom().random(); luck = s.get("daily_luck", 0)
        win_rate = min(0.95, (0.50 if not has_bua else 0.65) + (luck * 0.03))
        if r < win_rate:
            amt = random.randint(100, 350); net, tax = self.bot.sentience.process_earn(msg.author.id, amt)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_dapda": now}})
            await msg.channel.send(embed=UIHelper.success("💎 CHƠI ĐỒ", f"> Bú **{net}** {E.COIN}"))
        elif r < min(0.95, win_rate + 0.25):
            amt = random.randint(40, 150); cost, extra = self.bot.sentience.process_fine(msg.author.id, amt, accident_type="yt")
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_dapda": now}})
            await msg.channel.send(embed=UIHelper.error("🚨 SỐC ĐÁ", f"> Viện phí: **-{cost}** {E.COIN} {extra}"))
        else:
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_dapda": now}})
            await msg.channel.send(embed=UIHelper.info("🚫 ĐÁ LỎ", f"> Búa gãy cán đéo làm đc gì!"))

    async def cmd_nhayau(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); now = time.time(); last = s.get("last_nhayau", 0)
        if now - last < 4000: return await msg.channel.send(f"{E.ERR} Nghỉ {int((4000-(now-last))//60)} phút nx r lên sàn!")
        has_bua = "Bùa" in s.get("inventory", []); r = random.SystemRandom().random(); luck = s.get("daily_luck", 0)
        win_rate = min(0.95, (0.55 if not has_bua else 0.70) + (luck * 0.03))
        if r < win_rate:
            amt = random.randint(80, 280); net, tax = self.bot.sentience.process_earn(msg.author.id, amt)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_nhayau": now}})
            await msg.channel.send(embed=UIHelper.success("💃 QUẨY", f"> Bo ngập mồm **{net}** {E.COIN}"))
        elif r < min(0.95, win_rate + 0.25):
            amt = random.randint(30, 100); cost, extra = self.bot.sentience.process_fine(msg.author.id, amt, accident_type="yt")
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_nhayau": now}})
            await msg.channel.send(embed=UIHelper.error("🚨 SẬP SÀN", f"> Khâu mỏ tốn: **-{cost}** {E.COIN} {extra}"))
        else:
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_nhayau": now}})
            await msg.channel.send(embed=UIHelper.info("🚫 NHỤC", f"> Bật bãi khỏi sàn!"))

    async def cmd_dep(self, msg, args):
        if not args: return await msg.channel.send(f"{E.ERR} `!dep <số>` hoặc `!dep all`")
        s = self.bot.sentience.get_soul(msg.author.id); amt = s.get('coins', 0) if args[0].lower() == 'all' else (int(args[0]) if args[0].isdigit() else 0)
        if amt <= 0 or s.get('coins', 0) < amt: return await msg.channel.send(f"{E.ERR} Có cái nịt mà đòi gửi ngân hàng!")
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": -amt, "bank": amt}})
        await msg.channel.send(embed=UIHelper.success("🏦 KÉT SẮT", f"> Đã cất **{amt:,} {E.COIN}** vào bank!"))

    async def cmd_with(self, msg, args):
        if not args: return await msg.channel.send(f"{E.ERR} `!with <số>` hoặc `!with all`")
        s = self.bot.sentience.get_soul(msg.author.id); amt = s.get('bank', 0) if args[0].lower() == 'all' else (int(args[0]) if args[0].isdigit() else 0)
        if amt <= 0 or s.get('bank', 0) < amt: return await msg.channel.send(f"{E.ERR} Ngân hàng cháy túi!")
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": amt, "bank": -amt}})
        await msg.channel.send(embed=UIHelper.success("🏦 RÚT TIỀN", f"> Móc **{amt:,} {E.COIN}** ra xài!"))

    async def cmd_invest(self, msg, args):
        if not args: return await msg.channel.send(f"{E.ERR} `!invest <tiền/all>`")
        s = self.bot.sentience.get_soul(msg.author.id); amt = s.get('coins', 0) if args[0].lower() == 'all' else (int(args[0]) if args[0].isdigit() else 0)
        if amt <= 0 or s.get('coins', 0) < amt: return await msg.channel.send(embed=UIHelper.error("CHÁY TÚI", "> Vay không người anh em?"), view=LoanPromptView(self.cmd_sys, msg.author.id))
        rate = random.uniform(-0.8, 0.4); profit = int(amt * rate)
        if profit > 0: 
            net, tax = self.bot.sentience.process_earn(msg.author.id, profit)
            await msg.channel.send(embed=UIHelper.success(f"{E.ARR_U} BẮT CHUẨN ĐÁY", f"> Húp **+{net:,} {E.COIN}**!" + (f" *(Thuế: -{tax})*" if tax>0 else "")))
        else: 
            cost, _ = self.bot.sentience.process_fine(msg.author.id, abs(profit), accident_type=None)
            await msg.channel.send(embed=UIHelper.error(f"{E.ARR_D} ĐU ĐỈNH", f"> Bị call margin ói mẹ **{cost:,} {E.COIN}**!"))

    async def cmd_bhxh(self, msg, args):
        if not args or not args[0].isdigit(): return await msg.channel.send(f"{E.ERR} `!bhxh <số_tiền>`")
        amt = int(args[0]); s = self.bot.sentience.get_soul(msg.author.id); now = time.time(); last_paid = s.get("last_bhxh_paid", 0)
        if last_paid > 0 and now - last_paid < 7 * 86400: return await msg.channel.send(f"{E.ERR} Tuần này đóng BHXH ròi pa!")
        if s.get("coins", 0) < amt: return await msg.channel.send(f"{E.ERR} Khum đủ xu nạp bảo hiểm!")
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": -amt, "bhxh_fund": amt}, "$set": {"last_bhxh_paid": now}})
        await msg.channel.send(embed=UIHelper.success("🛡️ BHXH", f"> Nạp **{amt} {E.COIN}** vào quỹ dự phòng lao động!"))

    async def cmd_bhyt(self, msg, args):
        if not args or not args[0].isdigit(): return await msg.channel.send(f"{E.ERR} `!bhyt <số_tiền>`")
        amt = int(args[0]); s = self.bot.sentience.get_soul(msg.author.id); now = time.time(); last_paid = s.get("last_bhyt_paid", 0)
        if last_paid > 0 and now - last_paid < 7 * 86400: return await msg.channel.send(f"{E.ERR} Tuần này đóng BHYT ròi pa!")
        if s.get("coins", 0) < amt: return await msg.channel.send(f"{E.ERR} Khum đủ xu nạp y tế!")
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": -amt, "bhyt_fund": amt}, "$set": {"last_bhyt_paid": now}})
        await msg.channel.send(embed=UIHelper.success("🏥 BHYT", f"> Nạp **{amt} {E.COIN}** vào quỹ viện phí!"))

    async def cmd_shopjob(self, msg, args):
        desc = f"> 💼 **DỤNG CỤ HÀNH NGHỀ**\n> Gõ `!buy <tên món>`, xem rương `!inv`\n\n"
        for k, v in self.get_job_items().items(): desc += f"> {v['icon']} **{v['name']}**: {v['price']:,} {E.COIN} *(Bền: {v['uses']})*\n"
        await msg.channel.send(embed=UIHelper.create_embed("🛠️ SHOP NGHỀ NGHIỆP", desc, discord.Colour.blue()))

    async def cmd_shop(self, msg, args):
        desc = f"> 🛒 **VẬT PHẨM LINH TINH**\n> Gõ `!buy <tên món>`, xem rương `!inv`\n\n"
        for k, v in self.get_general_items().items(): desc += f"> {v['icon']} **{v['name']}**: {v['price']:,} {E.COIN} *(Bền: {v['uses']})*\n"
        await msg.channel.send(embed=UIHelper.create_embed("🏪 TẠP HÓA VE CHAI", desc, discord.Colour.gold()))

    async def cmd_buy(self, msg, args):
        if not args: return await msg.channel.send(f"{E.ERR} `!buy <tên món>`")
        shop = self.get_all_items(); item_input = " ".join(args).lower()
        if item_input not in shop: return await msg.channel.send(f"{E.ERR} Tiệm tui khum bán cái đồ quỷ đó!")
        item = shop[item_input]; s = self.bot.sentience.get_soul(msg.author.id)
        if s.get("coins", 0) < item["price"]: return await msg.channel.send(f"{E.ERR} Cháy túi đòi đi mua sắm à?")
        if item["name"] in s.get("inventory", []): return await msg.channel.send(f"{E.ERR} Mua 1 cái đủ xài rùi!")
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": -item["price"]}, "$push": {"inventory": item["name"]}, "$set": {f"tool_health.{item['name']}": item["uses"]}})
        await msg.channel.send(embed=UIHelper.success("🛍️ CHỐT ĐƠN", f"> Xì **{item['price']} {E.COIN}** rước **{item['name']}** về!"))

    async def cmd_checkdo(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); inv = s.get("inventory", []); healths = s.get("tool_health", {})
        if not inv: return await msg.channel.send(embed=UIHelper.create_embed("🎒 TÚI ĐỒ", "> Rỗng tuếch chả có nịt gì!", discord.Colour.gold()))
        desc = ""; shop_data = self.get_all_items()
        for i in inv:
            key = i.lower(); h = healths.get(i, shop_data[key]["uses"] if key in shop_data else "Vô hạn")
            desc += f"> 🎒 **{i}** - Còn: `{h}` lượt\n"
        await msg.channel.send(embed=UIHelper.create_embed("🎒 KHO ĐỒ", desc, discord.Colour.gold()))
    async def cmd_inv(self, msg, args): await self.cmd_checkdo(msg, args)

    async def cmd_sell(self, msg, args):
        if not args: return await msg.channel.send(f"{E.ERR} `!sell <tên món>`")
        shop = self.get_all_items(); item_input = " ".join(args).lower(); s = self.bot.sentience.get_soul(msg.author.id)
        if item_input not in shop: return await msg.channel.send(f"{E.ERR} Hàng lậu à?")
        item = shop[item_input]
        if item["name"] not in s.get("inventory", []): return await msg.channel.send(f"{E.ERR} Có cầm theo đâu mà bán?")
        curr_health = s.get("tool_health", {}).get(item["name"], item["uses"]); sell_price = int((curr_health / item["uses"]) * (item["price"] * 0.5))
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": sell_price}, "$pull": {"inventory": item["name"]}, "$unset": {f"tool_health.{item['name']}": ""}})
        await msg.channel.send(embed=UIHelper.success("♻️ VE CHAI", f"> Tống khứ **{item['name']}** thu về **{sell_price} {E.COIN}**!"))

    async def cmd_lyrabank(self, msg, args):
        bal = self.bot.sentience.get_state_bank()
        await msg.channel.send(embed=UIHelper.create_embed("🏛️ KHO BẠC NHÀ NƯỚC", f"> Tổng tài sản: **{bal:,} {E.COIN}**\n> Mấy khứa giang hồ đg rình cướp đó!", discord.Colour.green()))

    async def cmd_giveaway(self, msg, args):
        amt = int(args[0]) if args and args[0].isdigit() else 1000; s = self.bot.sentience.get_soul(msg.author.id)
        if s.get("coins", 0) < amt: return await msg.channel.send(f"{E.ERR} Đỗ nghèo khỉ đòi phát chẩn à?")
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": -amt}})
        await msg.channel.send(embed=UIHelper.info(f"{E.GIFT} MƯA TIỀN", f"> {msg.author.mention} ném **{amt} {E.COIN}**! Ai gõ `lụm` nhanh nhất húp trọn!"))
        def check(m): return m.channel == msg.channel and m.content.lower() == "lụm" and not m.author.bot
        try:
            ans = await self.bot.wait_for("message", check=check, timeout=30)
            self.bot.sentience.col.update_one({"uid": ans.author.id}, {"$inc": {"coins": amt}})
            await msg.channel.send(f"🎉 Ê vãi, {ans.author.mention} cướp được **{amt} {E.COIN}** mướt mồ hôi!")
        except: 
            await msg.channel.send(f"💀 Đéo ai thèm nhặt, tiền bị quét vào Kho Bạc rùi!"); self.bot.sentience.update_state_bank(amt)

    async def cmd_rolljob(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id)
        if "job" in s and s["job"]: return await msg.channel.send(f"{E.ERR} Đang làm **{s['job']}** gòi ba. `!quitjob` trước!")
        now = time.time(); last_quit = s.get("last_quitjob", 0)
        if now - last_quit < 12 * 3600:
            if args and args[0] == "20000":
                if s.get("coins", 0) < 20000: return await msg.channel.send(f"{E.ERR} Khum đủ 20k đút lót HR!")
                self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": -20000}, "$set": {"last_quitjob": 0}})
                await msg.channel.send(f"💸 Đã xì 20k luân chuyển hồ sơ đen!")
            else:
                rem = int((12 * 3600 - (now - last_quit)) / 60); h, m = divmod(rem, 60)
                return await msg.channel.send(embed=UIHelper.error("HỒ SƠ BỊ ĐEN", f"> Chờ **{h}h{m}p** để ứng tuyển lại. Hoặc `!rolljob 20000` đút lót."))
        jobs = [{"name": "Tiểu thuyết gia", "req_luck": 0, "rate": 20}, {"name": "Nhà báo thám tử", "req_luck": 0, "rate": 15}, {"name": "Bác sĩ thú y", "req_luck": 20, "rate": 8}, {"name": "Nhân viên đa cấp", "req_luck": 0, "rate": 30}, {"name": "Kế toán lỏ", "req_luck": 0, "rate": 25}, {"name": "Giáo viên mầm non", "req_luck": 0, "rate": 25}, {"name": "Đầu bếp rách", "req_luck": 0, "rate": 25}, {"name": "Thợ gõ Code Python", "req_luck": 30, "rate": 5}, {"name": "Lính Hải Quân đảo xa", "req_luck": 0, "rate": 4}, {"name": "Nhà thơ hắc ám", "req_luck": 0, "rate": 20}, {"name": "Dịch giả tài liệu mật", "req_luck": 40, "rate": 2}, {"name": "Reviewer Game Art-House", "req_luck": 0, "rate": 10}]
        valid_jobs = [j for j in jobs if s.get("daily_luck", 0) >= j["req_luck"]]
        if not valid_jobs: return await msg.channel.send(embed=UIHelper.error("NGHIỆP QUẬT", "Nhân phẩm rác ko ai nhận! `!pray` đi!"))
        r = random.SystemRandom().uniform(0, sum(j["rate"] for j in valid_jobs)); curr = 0; rolled_job = valid_jobs[0]["name"]
        for j in valid_jobs:
            curr += j["rate"]
            if r <= curr: rolled_job = j["name"]; break
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"job": rolled_job, "tool_uses": 0}})
        await msg.channel.send(embed=UIHelper.success("💼 VÀO TRÒNG", f"> Đã trúng tuyển: **{rolled_job}**! Mua công cụ `!shopjob` rồi `!dojob` nha!"))

    async def cmd_dojob(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); job = s.get("job")
        if not job: return await msg.channel.send(f"{E.ERR} Thất nghiệp đi làm cc gì? `!rolljob` kiếm cơm!")
        now = time.time(); last = s.get("last_dojob", 0)
        if now - last < 3600: return await msg.channel.send(f"{E.ERR} Chờ {int((3600-(now-last))//60)} phút nữa mỡi được cày tiếp!")
        tools_req = {"Tiểu thuyết gia": "Bút máy", "Nhà báo thám tử": "Máy ảnh", "Bác sĩ thú y": "Ống nghe", "Nhân viên đa cấp": "Loa kẹo kéo", "Kế toán lỏ": "Máy tính casio", "Giáo viên mầm non": "Phấn tiên", "Đầu bếp rách": "Dao phay", "Thợ gõ Code Python": "Bàn phím cơ", "Lính Hải Quân đảo xa": "Súng", "Nhà thơ hắc ám": "Giấy nháp", "Dịch giả tài liệu mật": "Từ điển", "Reviewer Game Art-House": "Tay cầm ps5"}
        req_tool = tools_req.get(job, "Bùa")
        if req_tool not in s.get("inventory", []): return await msg.channel.send(f"{E.ERR} Đéo có **{req_tool}** sao làm nghề **{job}**? `!shopjob` lẹ!")
        
        max_uses = next((v["uses"] for k,v in self.get_all_items().items() if v["name"] == req_tool), 10)
        curr_health = s.get("tool_health", {}).get(req_tool, max_uses); broken_msg = ""
        if curr_health <= 1:
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_dojob": now}, "$pull": {"inventory": req_tool}, "$unset": {f"tool_health.{req_tool}": ""}})
            broken_msg = f"\n> 💥 **BỂ ĐỒ RỒI:** Cây `{req_tool}` rách nát bét cmnr!"
        else: self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_dojob": now}, "$inc": {f"tool_health.{req_tool}": -1}})

        r = random.SystemRandom().random()
        earn = random.randint(300, 700) if r < 0.7 else 0; fine = 800 if earn == 0 else 0
        msg_out = f"Làm ba cọc ba đồng sống qua ngày." if earn > 0 else "Toang mẹ nó công việc đền ốm!"
        if earn > 0:
            net, tax = self.bot.sentience.process_earn(msg.author.id, earn)
            await msg.channel.send(embed=UIHelper.success(f"💼 LƯƠNG: {job.upper()}", f"> {msg_out}\n> {E.ARR} 💰 **Húp:** **+{net}** {E.COIN}" + (f" *(Thuế: -{tax})*" if tax>0 else "") + broken_msg))
        else:
            cost, extra = self.bot.sentience.process_fine(msg.author.id, fine, accident_type="xh")
            await msg.channel.send(embed=UIHelper.error(f"🚨 TAI NẠN NGHỀ NGHIỆP: {job.upper()}", f"> {msg_out}\n> {E.ARR} 💸 **Bị vã:** **-{cost}** {E.COIN} {extra}{broken_msg}"))

    async def cmd_quitjob(self, msg, args):
        if not self.bot.sentience.get_soul(msg.author.id).get("job"): return await msg.channel.send(f"{E.ERR} Có làm cái gì đâu mà đòi từ chức?")
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"job": None, "last_quitjob": time.time()}})
        await msg.channel.send(embed=UIHelper.success("👋 TỪ CHỨC", "> Về quê chăn bò nhé! Bị HR đì 12h k cho tìm việc mới!"))

    async def cmd_rob(self, msg, args):
        if not msg.mentions: return await msg.channel.send(f"{E.ERR} Tag một đứa vô để chôm!")
        t = msg.mentions[0]
        if t.id == msg.author.id: return await msg.channel.send(f"{E.ERR} Rảnh háng tự lột túi mình?")
        s_thief = self.bot.sentience.get_soul(msg.author.id); now = time.time(); last_rob = s_thief.get("last_rob", 0)
        if now - last_rob < 43200: return await msg.channel.send(embed=UIHelper.error("ĐANG TRUY NÃ!", f"> Núp kỹ đi ba! Đợi {(43200-(now-last_rob))//3600} tiếng nữa!"))
        s_target = self.bot.sentience.get_soul(t.id)
        if s_target.get("coins", 0) < 100: return await msg.channel.send(embed=UIHelper.error("ĐỖ NGHÈO KHỈ", f"> Túi nó rỗng tếch tha cho đi!"))
        if s_thief.get("coins", 0) < 100: return await msg.channel.send(embed=UIHelper.error("MÓM", f"> Cháy túi lấy tiền đâu nộp phạt nếu xịt?"))
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$set": {"last_rob": now}})
        if random.random() < 0.30: 
            amt = random.randint(10, int(s_target.get("coins") * 0.1) + 50)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": amt}}); self.bot.sentience.col.update_one({"uid": t.id}, {"$inc": {"coins": -amt}})
            await msg.channel.send(embed=UIHelper.success("🥷 MƯỢT VÃI", f"> Hack túi trót lọt **{amt} {E.COIN}** té lẹ!"))
        else:
            fine = random.randint(50, 150)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": -fine}}); self.bot.sentience.update_state_bank(fine)
            await msg.channel.send(embed=UIHelper.error("🚓 BỊ BẾ", f"> Táy máy bị đấm, đền **{fine} {E.COIN}** nhục!"))

    async def cmd_trade(self, msg, args):
        if not msg.mentions or len(args) < 2: return await msg.channel.send(f"{E.ERR} `!trade <@user> <món đồ>`")
        t = msg.mentions[0]; item_input = " ".join(args[1:]).lower(); shop = self.get_all_items()
        if item_input not in shop: return await msg.channel.send(f"{E.ERR} Đồ fake khum gửi được!")
        item_name = shop[item_input]["name"]
        s_sender = self.bot.sentience.get_soul(msg.author.id); s_receiver = self.bot.sentience.get_soul(t.id)
        if item_name not in s_sender.get("inventory", []): return await msg.channel.send(f"{E.ERR} Có đồ méo đâu đòi gửi?")
        if item_name in s_receiver.get("inventory", []): return await msg.channel.send(f"{E.ERR} Rương nó chật chỗ rùi!")
        curr_health = s_sender.get("tool_health", {}).get(item_name, shop[item_input]["uses"])
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$pull": {"inventory": item_name}, "$unset": {f"tool_health.{item_name}": ""}})
        self.bot.sentience.col.update_one({"uid": t.id}, {"$push": {"inventory": item_name}, "$set": {f"tool_health.{item_name}": curr_health}})
        await msg.channel.send(embed=UIHelper.success("🤝 TRẢ TAY CHỢ ĐEN", f"> Tuồn **{item_name}** sang mướt rượt!"))

    async def cmd_rebirth(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id); rb_count = s.get("rebirth", 0); req_coins = (rb_count + 1) * 1000000
        if s.get("coins", 0) < req_coins: return await msg.channel.send(embed=UIHelper.error("TU TIÊN LỎ", f"> Cần **{req_coins:,}** {E.COIN} tẩy tủy. Đi cày thêm đi!"))
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"rebirth": 1, "coins": -req_coins}})
        await msg.channel.send(embed=UIHelper.create_embed("🔥 TRÙNG SINH ĐỘ KIẾP", f"> Lên **Chuyển Sinh {rb_count + 1}** rực rỡ!", discord.Colour.gold(), img="https://media.giphy.com/media/xT1XGT9ersCCKjcIGs/giphy.gif"))

    async def cmd_top(self, msg, args):
        if not args or args[0].lower() not in ["level", "coins", "xu"]: return await msg.channel.send(f"{E.ERR} Gõ `!top level` hoặc `!top coins` đê!")
        type_top = "level" if args[0].lower() == "level" else "coins"
        sort_key = "xp" if type_top == "level" else "coins"
        top_users = list(self.bot.sentience.col.find().sort(sort_key, -1).limit(10))
        desc = f"{E.BAR*10}\n"; medals = [E.M1, E.M2, E.M3] + [f"`#{i}`" for i in range(4, 11)]
        for idx, u in enumerate(top_users):
            user_obj = msg.guild.get_member(u['uid']); name = user_obj.display_name if user_obj else f"Kẻ Ẩn Danh ({u['uid']})"
            if type_top == "level": desc += f"> {medals[idx]} **{name}** {E.ARR} Cấp: **{u.get('level', 1)}** *(XP: {u.get('xp', 0)})*\n"
            else: desc += f"> {medals[idx]} **{name}** {E.ARR} Tài sản: **{u.get('coins', 0):,} {E.COIN}**\n"
        await msg.channel.send(embed=UIHelper.create_embed(f"{E.STAR} BẢNG PHONG THẦN", desc + E.BAR*10, discord.Colour.gold() if type_top=="coins" else discord.Colour.teal()))

    async def cmd_level(self, msg, args): 
        u = msg.mentions[0] if msg.mentions else msg.author; s = self.bot.sentience.get_soul(u.id)
        lv = s.get('level', 1); xp = s.get('xp', 0); wxp = s.get('weekly_xp', 0); luck = s.get('daily_luck', 0)
        desc = f"\n> {E.STAR} **Cấp:** `{lv}`\n> {E.GEM} **Tổng XP:** `{xp} / {lv*100}`\n> {E.FH} **XP Tuần:** `{wxp}`\n> 🍀 **Luck:** `{luck}`"
        e = discord.Embed(title=f"🎮 HỒ SƠ: {u.display_name}", description=desc, color=discord.Colour.dark_theme())
        if u.display_avatar: e.set_thumbnail(url=u.display_avatar.url)
        await msg.channel.send(embed=e)

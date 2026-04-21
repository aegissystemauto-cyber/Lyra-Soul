import re, time, random, io, sys
import discord
from core.ui_helper import UIHelper, UserRoles
from core.emojis import E

class AdminCog:
    def __init__(self, cmd_sys): 
        self.cmd_sys = cmd_sys
        self.bot = cmd_sys.bot

    def register(self):
        c = self.cmd_sys.commands
        c["!godmode"] = {"func": self.cmd_godmode, "admin": True}
        admin_cmds = ["tax", "lsay", "run", "purge", "lock", "unlock", "slowmode", "lyrastop", "lyrastart", "add_coins", "remove_coins", "set_level", "add_level", "grant_xp", "add_luck", "remove_luck", "lyb", "rutkho", "napkho", "set_tax", "unset_tax", "pandemic", "unpandemic", "sync"]
        for ac in admin_cmds: 
            c[f"!{ac}"] = {"func": self.cmd_admin_router, "admin": True}

    async def cmd_admin_router(self, msg, args):
        cmd_name = msg.content.strip().split()[0][1:].lower()
        if cmd_name == "lyrastop": cmd_name = "stop"
        elif cmd_name == "lyrastart": cmd_name = "start"
        await self.cmd_godmode(msg, [cmd_name] + args)

    async def cmd_godmode(self, msg, args):
        if not args:
            desc = f"{E.BAR*9}\n> 👑 **MENU QUYỀN LỰC**\n> 🏛️ `!tax <%>`: Bào thuế all server\n> 🎯 `!set_tax` / `!unset_tax <@u>`: Ép thuế cá nhân\n> 🏦 `!rutkho` / `!napkho <số>`: Rút nạp ngân khố\n> 📢 `!lsay <text/lệnh>`: Nhại giọng Bot / Ép Bot chạy lệnh\n> 🦠 `!pandemic <phút>` / `!unpandemic`: Bật/Tắt Đại Dịch\n> ⚙️ `!run <code>`: Chạy code ẩn\n> 🧹 `!purge <số>`: Quét nghiệp kênh chat\n> 🔒 `!lock` / `!unlock`: Niêm phong kênh\n> ⏳ `!slowmode <giây>`: Ép chat chậm\n> 💤 `!lyrastop` / `!lyrastart`: Ngủ đông Bot\n> 💰 `!add_coins` / `!remove_coins <@u> <số>`\n> 🍀 `!grant_xp` / `!add_luck` / `!remove_luck <@u> <số>`\n> 🔄 `!sync`: Cập nhật lệnh Slash\n{E.BAR*9}"
            return await msg.channel.send(embed=UIHelper.create_embed(f"{E.ZAP} BẢNG ĐIỀU KHIỂN CỦA CHÚA {E.ZAP}", desc, discord.Colour.red()))
        
        sub = args[0].lower(); sys_args = args[1:]
        if sub == "tax":
            if not sys_args: return await msg.channel.send(f"{E.ERR} Gõ % thuế vô ngài N ơi! (VD: `!tax 5%`)")
            match = re.match(r'^(\d+)(?:\s*)?%$', sys_args[0])
            if not match: return await msg.channel.send(f"{E.ERR} Nhập % cho chuẩn vô: `!tax 5%`")
            percent = min(max(int(match.group(1)), 1), 100)
            users = list(self.bot.sentience.col.find({"coins": {"$gt": 100}}))
            count = 0; total = 0
            for u in users:
                if u["uid"] != UserRoles.N_ID:
                    tax_amt = int(u["coins"] * percent / 100)
                    if tax_amt > 0:
                        self.bot.sentience.col.update_one({"uid": u["uid"]}, {"$inc": {"coins": -tax_amt}})
                        total += tax_amt; count += 1
            self.bot.sentience.update_state_bank(total)
            await msg.channel.send(embed=UIHelper.success("🏛️ LỆNH THU THUẾ TOÀN BỘ", f"{E.BAR*9}\n> {E.ARR} Trấn lột **{percent}%** tài sản của {count} đứa!\n> Tổng húp: **{total:,}** {E.COIN} tọng vào Kho Bạc!"))
        elif sub == "set_tax":
            if len(sys_args) < 2: return await msg.channel.send(f"{E.ERR} Gõ: `!set_tax <%> <@user>`")
            percent = int(sys_args[0].replace('%', '')); u = msg.mentions[0] if msg.mentions else None
            if not u: return await msg.channel.send(f"{E.ERR} Không thấy con nợ này đâu cả!")
            self.bot.sentience.col.update_one({"uid": u.id}, {"$set": {"tax_rate": percent}})
            await msg.channel.send(embed=UIHelper.success("🎯 ĐÓNG DẤU THUẾ MÁ", f"> Đã ép mức thuế thu nhập cá nhân **{percent}%** lên đầu {u.mention}!\n> Tiền bào được sẽ chuyển thẳng vô túi Đại Đế!"))
        elif sub == "unset_tax":
            u = msg.mentions[0] if msg.mentions else None
            if not u: return await msg.channel.send(f"{E.ERR} Tag cái thằng cần gỡ thuế vô!")
            self.bot.sentience.col.update_one({"uid": u.id}, {"$set": {"tax_rate": 0}})
            await msg.channel.send(embed=UIHelper.success("✅ GỠ THUẾ MÁ", f"> Đã xóa bỏ thuế thu nhập cho {u.mention}! Cứ bào tiền thoải mái nhé!"))
        elif sub == "rutkho":
            if not sys_args or not sys_args[0].isdigit(): return await msg.channel.send(f"{E.ERR} Số lượng rút?")
            amt = int(sys_args[0])
            self.bot.sentience.update_state_bank(-amt)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": amt}})
            await msg.channel.send(embed=UIHelper.success("🏦 THAM Ô NGÂN KHỐ", f"> Sếp vừa rút ruột kho bạc nhà nước **{amt:,}** {E.COIN} đem đi bar!"))
        elif sub == "napkho":
            if not sys_args or not sys_args[0].isdigit(): return await msg.channel.send(f"{E.ERR} Số lượng nạp?")
            amt = int(sys_args[0])
            self.bot.sentience.update_state_bank(amt)
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": -amt}})
            await msg.channel.send(embed=UIHelper.success("🏦 CỨU TRỢ QUỐC GIA", f"> Sếp vĩ đại quyên góp **{amt:,}** {E.COIN} từ tiền túi nạp vào Kho Bạc!"))
        elif sub == "lsay":
            try: await msg.delete()
            except: pass
            if sys_args and sys_args[0].lower() == "reply" and getattr(msg, 'reference', None):
                try: 
                    ref = await msg.channel.fetch_message(msg.reference.message_id)
                    await ref.reply(" ".join(sys_args[1:]))
                except: await msg.channel.send(" ".join(sys_args[1:]))
            elif sys_args and sys_args[0].startswith("!"):
                cmd_to_run = sys_args[0]
                args_for_cmd = sys_args[1:]
                res = await self.cmd_sys.execute(cmd_to_run, msg, args_for_cmd)
                if res and isinstance(res, str): await msg.channel.send(res[:2000])
            elif sys_args: 
                await msg.channel.send(" ".join(sys_args))
        elif sub == "pandemic":
            if not sys_args: return await msg.channel.send(f"{E.ERR} Ủa dịch bao lâu pa? Gõ `!pandemic <số>m/h` (VD: `!pandemic 30m`)")
            match = re.match(r'^(\d+)([mh])$', sys_args[0].lower())
            if not match: return await msg.channel.send(f"{E.ERR} Cú pháp sai rồi ba! `!pandemic 30m` nha.")
            mins = int(match.group(1)) * {"m":1,"h":60}[match.group(2)]
            p_types = ["Covid", "Dịch Thây Ma", "Cúm Gia Cầm Đột Biến", "Nấm Ký Sinh Não", "Dịch Hạch"]
            p_name = random.choice(p_types)
            end_time = time.time() + (mins * 60)
            self.bot.db["bot_config"].update_one({"_id": "pandemic"}, {"$set": {"active": True, "end_time": end_time, "type": p_name}}, upsert=True)
            await msg.channel.send(embed=UIHelper.create_embed("☣️ CẢNH BÁO ĐẠI DỊCH TOÀN CẦU", f"> 🚨 **{p_name}** vừa bùng phát!\n> Thời gian: **{mins} phút**.\n> Toàn bộ Server bị trừ điểm may mắn, hao tổn thể lực! Mua **Khẩu trang** trong `!shop` để kháng bệnh!", discord.Colour.red(), img="https://media.giphy.com/media/Vb2Pvv0yB0Lw4/giphy.gif"))
        elif sub == "unpandemic":
            p = self.bot.db["bot_config"].find_one({"_id": "pandemic"})
            if not p or not p.get("active"): return await msg.channel.send(f"{E.INFO} Đang yên bình mà có dịch bệnh quái đâu!")
            self.bot.db["bot_config"].update_one({"_id": "pandemic"}, {"$set": {"active": False}})
            await msg.channel.send(embed=UIHelper.success("💉 TÌM RA VACCINE", f"> WHO đã chế ra thuốc phòng cho đại dịch **{p['type']}**. Mọi người an toàn rồi!"))
        elif sub == "run":
            code = " ".join(sys_args).strip().replace('```python','').replace('```',''); stdout = io.StringIO(); sys.stdout = stdout
            try: exec(code, {"__builtins__": {k: __builtins__[k] for k in ['print','range','len','sum','min','max','str','int','float','list','dict','set']}}); sys.stdout = sys.__stdout__; await msg.channel.send(f"```python\n{stdout.getvalue() or '✅ Mượt vãi!'}\n```")
            except Exception as e: sys.stdout = sys.__stdout__; await msg.channel.send(f"❌ Toang code rồi: {e}")
        elif sub == "purge":
            try: amt = int(sys_args[0]) if sys_args else 10; await msg.channel.purge(limit=amt+1); await msg.channel.send(f"{E.BROOM} Đã quét sạch **{amt}** tin nhắn dỏm!", delete_after=3)
            except: await msg.channel.send(f"{E.ERR} Lỗi rùi, tui không có quyền Quản lý tin nhắn!")
        elif sub == "lock":
            try: await msg.channel.set_permissions(msg.guild.default_role, send_messages=False); await msg.channel.send(embed=UIHelper.error("KÊNH BỊ NIÊM PHONG", f"{E.ARR} Tất cả trật tự!"))
            except: pass
        elif sub == "unlock":
            try: await msg.channel.set_permissions(msg.guild.default_role, send_messages=True); await msg.channel.send(embed=UIHelper.success("MỞ KHÓA", f"{E.ARR} Kênh mở rồi, xõa đi anh em!"))
            except: pass
        elif sub == "slowmode":
            try: s=int(sys_args[0]) if sys_args else 0; await msg.channel.edit(slowmode_delay=s); await msg.channel.send(embed=UIHelper.info("SLOWMODE", f"{E.ARR} Ép trễ kênh **{s} giây** rồi đó."))
            except: pass
        elif sub == "stop": 
            self.bot.is_awake = False; await msg.channel.send(embed=UIHelper.info("Ngủ đông", f"{E.ARR} Trùm mền đi ngủ đây... 💤"))
        elif sub == "start": 
            self.bot.is_awake = True; await msg.channel.send(embed=UIHelper.success("Thức giấc!", f"{E.ARR} Phá dỡ phong ấn, tui dậy rồi đây! ✨"))
        elif sub == "lyb":
            await msg.channel.send(f"{E.INFO} Leaderboard đóng cửa bảo trì riêng cho Sếp thoi!")
        elif sub == "sync":
            m = await msg.channel.send(f"{E.CLOCK} Đang gõ cửa Discord đòi đồng bộ lệnh Slash...")
            try:
                synced = await self.bot.tree.sync()
                await m.edit(content=f"{E.OK} Mượt! Đã ép Discord nhận {len(synced)} lệnh Slash!")
            except Exception as e:
                await m.edit(content=f"{E.ERR} Toang cmnr: {e}")
        elif sub in ["add_coins", "remove_coins", "set_level", "add_level", "grant_xp", "add_luck", "remove_luck"]:
            if len(sys_args) < 2: return await msg.channel.send(f"{E.ERR} Format: `!{sub} <@u> <số>`")
            u = msg.mentions[0] if msg.mentions else msg.guild.get_member_named(" ".join(sys_args[:-1]))
            try: amt = int(sys_args[-1])
            except: return await msg.channel.send(f"{E.ERR} Số lượng đâu ngài ơi?")
            if not u: return await msg.channel.send(f"{E.ERR} Khum tìm ra người này!")
            if sub=="add_coins": self.bot.sentience.col.update_one({"uid":u.id}, {"$inc":{"coins":amt}}); await msg.channel.send(f"{E.ZAP} Bơm **{amt}** {E.COIN} cho {u.mention} rồi đó!")
            elif sub=="remove_coins": self.bot.sentience.col.update_one({"uid":u.id}, {"$inc":{"coins":-amt}}); await msg.channel.send(f"{E.ZAP} Lột sạch **{amt}** {E.COIN} của {u.mention}!")
            elif sub=="set_level": new_xp = max(0, (amt - 1) * 100); self.bot.sentience.col.update_one({"uid":u.id}, {"$set":{"level":amt, "xp":new_xp}}); await msg.channel.send(f"{E.ZAP} Ép số cho {u.mention} thành **Level {amt}**!")
            elif sub=="add_level": s = self.bot.sentience.get_soul(u.id); new_lv = max(1, s.get("level", 1) + amt); new_xp = (new_lv - 1) * 100; self.bot.sentience.col.update_one({"uid":u.id}, {"$set":{"level":new_lv, "xp":new_xp}}); await msg.channel.send(f"{E.ZAP} Độ **{amt} Cấp** cho {u.mention}! Đang **Level {new_lv}**.")
            elif sub=="grant_xp": self.bot.sentience.add_xp(u.id, amt); await msg.channel.send(f"{E.ZAP} Cắn thuốc **{amt} XP** cho {u.mention}!")
            elif sub=="add_luck": self.bot.sentience.col.update_one({"uid":u.id}, {"$inc":{"daily_luck":amt}}); await msg.channel.send(f"{E.ZAP} Cầu siêu lên **{amt} Luck** cho {u.mention}!")
            elif sub=="remove_luck": self.bot.sentience.col.update_one({"uid":u.id}, {"$inc":{"daily_luck":-amt}}); await msg.channel.send(f"{E.ZAP} Trù ếm tụt **{amt} Luck** của {u.mention}!")

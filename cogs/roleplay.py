import random
import discord
from core.emojis import E
from core.ui_helper import UIHelper

class RoleplayCog:
    def __init__(self, cmd_sys):
        self.cmd_sys = cmd_sys
        self.bot = cmd_sys.bot

    def register(self):
        c = self.cmd_sys.commands
        rp_cmds = ["afk", "gay", "truth", "dare", "marry", "divorce", "todo", "todos", "rtodos", "quote", "math", "password", "slap", "hug", "kiss", "punch", "pat", "cry", "dance", "bite", "spank", "lick", "poke", "stare", "cuddle", "smug", "bonk", "highfive", "wave", "blush", "facepalm", "bocphot", "banhtrang"]
        for ac in rp_cmds: c[f"!{ac}"] = {"func": getattr(self, f"cmd_{ac}")}

    async def _send_rp(self, msg, args, title, color, gifs, self_act, other_act):
        target = msg.mentions[0].mention if msg.mentions else msg.author.mention
        desc = f"> {msg.author.mention} {self_act}!" if not msg.mentions else f"> {msg.author.mention} {other_act} {target}!"
        e = UIHelper.create_embed(title, desc, color); e.set_image(url=random.choice(gifs)); await msg.channel.send(embed=e)
        
    async def cmd_slap(self, msg, args): await self._send_rp(msg, args, "👋 VẢ XÉO HÀM!", discord.Colour.red(), ["https://media.giphy.com/media/j3iGKxP41Xh2o/giphy.gif", "https://media.giphy.com/media/Zau0yrl17uzdK/giphy.gif"], "tự đập mặt vào tường", "táng văng hàm vô mỏ")
    async def cmd_hug(self, msg, args): await self._send_rp(msg, args, "🫂 ÔM CỨNG NGẮC", discord.Colour.purple(), ["https://media.giphy.com/media/lrr9cScdxK0mUyMsZq/giphy.gif", "https://media.giphy.com/media/3M4NpbLCTxBqU/giphy.gif"], "tự ôm gối nằm góc tường", "ôm siết chặt nghẹt thở")
    async def cmd_kiss(self, msg, args): await self._send_rp(msg, args, "💋 CHỤT CHỤT", discord.Colour.pink(), ["https://media.giphy.com/media/G3va31oGkPcNqcTduB/giphy.gif", "https://media.giphy.com/media/nyGFcsP0kAobm/giphy.gif"], "hôn cái gương soi tự kỉ", "liếm môi chụt chụt")
    async def cmd_punch(self, msg, args): await self._send_rp(msg, args, "👊 SÚT SẬP NGUỒN!", discord.Colour.dark_red(), ["https://media.giphy.com/media/xT0BKiwgIPGShJNi0g/giphy.gif", "https://media.giphy.com/media/11HeubLHnQJSAU/giphy.gif"], "phang vào không khí cọc cằn", "tung cước nát bét")
    async def cmd_pat(self, msg, args): await self._send_rp(msg, args, "🐾 XOA ĐẦU", discord.Colour.blue(), ["https://media.giphy.com/media/4HP0ddZnNABnIGiqm5/giphy.gif", "https://media.giphy.com/media/N0CIxcyPLpTMI/giphy.gif"], "tự vuốt ve vuốt tóc lỏ", "xoa đầu nhây nhây với")
    async def cmd_cry(self, msg, args): await self._send_rp(msg, args, "😭 NƯỚC MẮT CÁ SẤU", discord.Colour.blue(), ["https://media.giphy.com/media/2rtQMJvhzOnRe/giphy.gif", "https://media.giphy.com/media/L95W4wv8nnb9K/giphy.gif"], "rống nhõng nhẽo rơi nước mắt", "khóc ré dính nước mũi lên")
    async def cmd_dance(self, msg, args): await self._send_rp(msg, args, "💃 LẮC HÔNG", discord.Colour.green(), ["https://media.giphy.com/media/mXnO9IiWWjmE0/giphy.gif", "https://media.giphy.com/media/blSTtZehjAZ8I/giphy.gif"], "uốn éo chổng đít khùng điên", "túm cổ giật giật quẩy chung vs")
    async def cmd_bite(self, msg, args): await self._send_rp(msg, args, "🦷 CẮN RÁCH TAY", discord.Colour.red(), ["https://media.giphy.com/media/10yXFkBJ0MwGQ0/giphy.gif"], "tự cắn trúng lưỡi đau quá rống ầm", "ngậm thẳng rách da gãy sừng con")
    async def cmd_spank(self, msg, args): await self._send_rp(msg, args, "🍑 TÉT MÔNG", discord.Colour.dark_red(), ["https://media.giphy.com/media/Pq2eExyH2iHQs/giphy.gif"], "tự vụt chát cái bép ảo ma", "sút tét mông đỏ rát của")
    async def cmd_lick(self, msg, args): await self._send_rp(msg, args, "👅 LIẾM MÀN HÌNH", discord.Colour.pink(), ["https://media.giphy.com/media/cI1rE7yF4G9Y8t6v9h/giphy.gif"], "chảy nhớt dãi vcl liếm mép", "ngáp mlem thèm thuồng")
    async def cmd_poke(self, msg, args): await self._send_rp(msg, args, "👉 CHỌC CHỌC", discord.Colour.orange(), ["https://media.giphy.com/media/pWd3gD577gOqs/giphy.gif"], "tự sục tay chọt lét bản thân ảo đá", "xỉa tay đâm lút chọc người")
    async def cmd_stare(self, msg, args): await self._send_rp(msg, args, "👀 LIẾC LÒI MẮT", discord.Colour.dark_grey(), ["https://media.giphy.com/media/N9iA44aFk3NIs/giphy.gif"], "tự ngắm kiếng trừng trừng", "căng mắt ếch nhìn lòi phèo")
    async def cmd_cuddle(self, msg, args): await self._send_rp(msg, args, "🥰 RÚC XÓ", discord.Colour.pink(), ["https://media.giphy.com/media/yziFo5qYAOgY8/giphy.gif"], "nằm ổ rúc gối xó vcl", "dính sát rúc lòi chấy ôm lấy")
    async def cmd_smug(self, msg, args): await self._send_rp(msg, args, "😏 KHINH BỈ", discord.Colour.gold(), ["https://media.giphy.com/media/hS9rEMD4zXGNO/giphy.gif"], "cười nhếch mép ngạo mạn vãi ố dề", "chê thẳng mặt khinh cười cợt nhỏ")
    async def cmd_bonk(self, msg, args): await self._send_rp(msg, args, "🔨 BỔ LỤC SỌ", discord.Colour.red(), ["https://media.giphy.com/media/qs4ll1FSxKnNHeSmom/giphy.gif"], "tự đập búa vô đầu cục chà bá", "bổ cây chùy rách vỡ sọ thằng")
    async def cmd_highfive(self, msg, args): await self._send_rp(msg, args, "🙌 ĐẬP TAY", discord.Colour.green(), ["https://media.giphy.com/media/10hO3rDNqqg2Xe/giphy.gif"], "tự vỗ tay rầm rộ", "vả tay bôm bốp vào tay")
    async def cmd_wave(self, msg, args): await self._send_rp(msg, args, "👋 BÁI BAI", discord.Colour.blue(), ["https://media.giphy.com/media/3oKIPbOaTdtMCgSveU/giphy.gif"], "múa lả lướt ngáo khùng", "bật tay vẫy lốc tiễn vong nhỏ")
    async def cmd_blush(self, msg, args): await self._send_rp(msg, args, "😳 QUÊ", discord.Colour.magenta(), ["https://media.giphy.com/media/26ufncGZhtXqH8Uxy/giphy.gif"], "chảy máu cam đỏ phừng", "thẹn rớt lồng ngực gục mặt ứa máu vì")
    async def cmd_facepalm(self, msg, args): await self._send_rp(msg, args, "🤦 BẤT LỰC", discord.Colour.dark_theme(), ["https://media.giphy.com/media/8UGoOaR1lA1uaAN892/giphy.gif"], "bóp trán cạn lời thở dài", "vỗ não bôm bốp chán nản vì cục tạ mang tên")

    async def cmd_marry(self, msg, args):
        from datetime import datetime
        if not msg.mentions: return await msg.channel.send(f"{E.ERR} Tag nửa kia ra cầu hôn lẹ!")
        t = msg.mentions[0]
        if t.id == msg.author.id: return await msg.channel.send(f"{E.ERR} Tự kỷ à?")
        if self.bot.sentience.marry_col.find_one({"$or": [{"u1": msg.author.id}, {"u2": msg.author.id}, {"u1": t.id}, {"u2": t.id}]}): return await msg.channel.send(f"{E.ERR} 1 trong 2 có chủ rồi, Tuesday à?")
        m = await msg.channel.send(f"💍 {t.mention} ê, {msg.author.mention} cầm nhẫn xin cưới nè! Chat `yes` hoặc `no`.")
        def check(m2): return m2.author.id == t.id and m2.content.lower() in ["yes", "no"]
        try:
            ans = await self.bot.wait_for("message", check=check, timeout=30)
            if ans.content.lower() == "yes":
                self.bot.sentience.marry_col.insert_one({"u1": msg.author.id, "u2": t.id, "date": str(datetime.now())})
                await msg.channel.send(embed=UIHelper.success("🎉 TÂN LANG NƯƠNG", f"> Đôi chim cu {msg.author.mention} và {t.mention} đã sụp hố! (Buff 20% XP cày)"))
            else: await msg.channel.send(f"🤡 Bị từ chối ròi. Quê {msg.author.mention}!")
        except: await msg.channel.send(f"⏰ Hết giờ chờ ròi lơ ròi!")

    async def cmd_divorce(self, msg, args):
        m = self.bot.sentience.marry_col.find_one({"$or": [{"u1": msg.author.id}, {"u2": msg.author.id}]})
        if not m: return await msg.channel.send(f"{E.ERR} FA mốc đòi ly dị?")
        u1, u2 = m["u1"], m["u2"]; s1 = self.bot.sentience.get_soul(u1); s2 = self.bot.sentience.get_soul(u2)
        total = s1.get("coins", 0) + s2.get("coins", 0); half1 = total // 2; half2 = total - half1
        self.bot.sentience.col.update_one({"uid": u1}, {"$set": {"coins": half1}}); self.bot.sentience.col.update_one({"uid": u2}, {"$set": {"coins": half2}})
        self.bot.sentience.marry_col.delete_one({"_id": m["_id"]})
        await msg.channel.send(embed=UIHelper.create_embed("💔 LY HÔN CHIA TÀI SẢN", f"> Đường ai nấy cút! <@{u1}> nhận **{half1} {E.COIN}**, <@{u2}> nhận **{half2} {E.COIN}**!", discord.Colour.dark_theme()))

    async def cmd_todo(self, msg, args): self.bot.db["todos"].update_one({"uid": msg.author.id}, {"$push": {"items": {"task": " ".join(args), "done": False}}}, upsert=True); await msg.channel.send(embed=UIHelper.success("ÉP SỔ DEADLINE", f"> **Ghi sổ:** {' '.join(args)}"))
    async def cmd_todos(self, msg, args): res=self.bot.db["todos"].find_one({"uid": msg.author.id}); await msg.channel.send(embed=UIHelper.create_embed("📝 DEADLINE CỦA CHỦ TỊCH", "\n".join([f"> {'✅' if t['done'] else '⬜'} {t['task']}" for t in res["items"][-10:]]) if res and res.get("items") else "> *Trống rỗng chán.*", discord.Colour.blue()))
    async def cmd_rtodos(self, msg, args): self.bot.db["todos"].update_one({"uid": msg.author.id}, {"$set": {"items": []}}, upsert=True); await msg.channel.send(embed=UIHelper.success("LỌT XỔ", "> Xóa cmn hết deadline!"))
    async def cmd_pass(self, msg, args): l=int(args[0]) if args and args[0].isdigit() else 12; await msg.channel.send(f"> 🔑 Pass lỏ: `{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*', k=min(l, 64)))}`")
    async def cmd_quote(self, msg, args): await msg.channel.send(embed=UIHelper.create_embed("💬 CHÂM NGÔN CẢM LẠNH", f"> *\"{random.choice(['Code lỗi ko phải do code dỏm mà do nhân phẩm bạn rác.', 'Nhai đi nhai lại cái deadline rồi lười.', 'Đi ngủ sớm đi chứ thức lèm bèm.'])}\"*", discord.Colour.teal(), img="https://media.giphy.com/media/26FPsHb1zEqK8wHq8/giphy.gif"))
    async def cmd_math(self, msg, args): 
        from core.database import LightLogicEngine
        res=LightLogicEngine.safe_eval(" ".join(args)); await msg.channel.send(res if res else f"{E.ERR} Lỗi mẹ rồi!")
    async def cmd_afk(self, msg, args): self.bot.db["afk_data"].update_one({"uid": msg.author.id}, {"$set": {"reason": " ".join(args) or "Sủi đít rùi"}}, upsert=True); await msg.channel.send(embed=UIHelper.success("SỦI", f"> {msg.author.mention} đã treo máy!"))
    async def cmd_gay(self, msg, args): await msg.channel.send(embed=UIHelper.create_embed("Độ Bóng", f"> 🏳️‍🌈 Tỉ lệ bóng của {(msg.mentions[0].mention if msg.mentions else msg.author.mention)}: **{random.randint(0, 100)}%**!", discord.Colour.magenta()))
    async def cmd_truth(self, msg, args): await msg.channel.send(f"> 💡 Sự thật: {random.choice(['Bạn cực lười!', 'Bạn ngủ nướng!', 'Đang crush ai đó!', 'Bạn xạo l!'])}")
    async def cmd_dare(self, msg, args): await msg.channel.send(f"> 🎯 Thách bạn: {random.choice(['Nói yêu 1 đứa trong group!', 'Đổi ava hình heo!', 'Đấm tường 1 cái!'])}")
    async def cmd_bocphot(self, msg, args): await msg.channel.send(f"> 📸 Phốt: {(msg.mentions[0].mention if msg.mentions else 'Khứa này')} {random.choice(['chuyên bùng kèo!', 'nợ k trả!', 'ở dơ!', 'xạo lìn!'])}")
    async def cmd_banhtrang(self, msg, args): await msg.channel.send(f"> 🥞 Lật mặt lẹ như bánh tráng nướng!")

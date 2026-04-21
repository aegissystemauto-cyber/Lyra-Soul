import random, asyncio
import discord
from core.emojis import E
from core.ui_helper import UIHelper, ReplayView, TriviaView, LoanPromptView

class MinigamesCog:
    def __init__(self, cmd_sys):
        self.cmd_sys = cmd_sys
        self.bot = cmd_sys.bot

    def register(self):
        c = self.cmd_sys.commands
        game_cmds = ["chanle", "taixiu", "slots", "baucua", "xoso", "duangua", "rps", "russianroulette", "guess", "duel", "minesweeper", "roll", "loveball", "coinbet", "kill", "hackeco", "trivia", "fortune", "coinflip", "diceroll", "choose", "8ball", "ship", "iq"]
        for ac in game_cmds: c[f"!{ac}"] = {"func": getattr(self, f"cmd_{ac}")}

    async def cmd_chanle(self, msg, args):
        if len(args) < 2 or args[0].lower() not in ["chẵn", "lẻ"]: return await msg.channel.send(f"{E.ERR} `!chanle <chẵn/lẻ> <tiền/all>`")
        s = self.bot.sentience.get_soul(msg.author.id); amt = s.get('coins', 0) if args[1].lower() == 'all' else (int(args[1]) if args[1].isdigit() else 0)
        if amt <= 0 or s.get('coins', 0) < amt: return await msg.channel.send(embed=UIHelper.error("CHÁY TÚI", "> Báo nhà thì vay nóng đi!"), view=LoanPromptView(self.cmd_sys, msg.author.id))
        bank_bal = self.bot.sentience.get_state_bank()
        if bank_bal < amt: return await msg.channel.send(embed=UIHelper.error("🏛️ RỖNG KHO", f"> Kho hết xèng k chung độ đc!"))

        roll = random.SystemRandom().randint(1, 100); is_chan = roll % 2 == 0
        win = (args[0].lower() == "chẵn" and is_chan) or (args[0].lower() == "lẻ" and not is_chan)
        if win: 
            net, tax = self.bot.sentience.process_earn(msg.author.id, amt)
            await msg.channel.send(embed=UIHelper.create_embed(f"{E.DICE} CHẴN LẺ", f"> Lắc ra: **{roll}** (`{'Chẵn' if is_chan else 'Lẻ'}`)\n> 🎉 Húp **{net}** {E.COIN}" + (f" *(Thuế: -{tax})*" if tax>0 else ""), discord.Colour.green()), view=ReplayView(self.cmd_sys, "!chanle", msg.author.id, args))
        else:
            cost, _ = self.bot.sentience.process_fine(msg.author.id, amt, accident_type=None)
            await msg.channel.send(embed=UIHelper.create_embed(f"{E.DICE} CHẴN LẺ", f"> Lắc ra: **{roll}** (`{'Chẵn' if is_chan else 'Lẻ'}`)\n> 💀 Cút **{cost}** {E.COIN}", discord.Colour.red()), view=ReplayView(self.cmd_sys, "!chanle", msg.author.id, args))

    async def cmd_taixiu(self, msg, args):
        if len(args) < 2 or args[0].lower() not in ["tài", "xỉu"]: return await msg.channel.send(f"{E.ERR} `!taixiu <tài/xỉu> <tiền/all>`")
        s = self.bot.sentience.get_soul(msg.author.id); amt = s.get('coins', 0) if args[1].lower() == 'all' else (int(args[1]) if args[1].isdigit() else 0)
        if amt <= 0 or s.get('coins', 0) < amt: return await msg.channel.send(embed=UIHelper.error("CHÁY TÚI", "> Khát nước à?"), view=LoanPromptView(self.cmd_sys, msg.author.id))
        bank_bal = self.bot.sentience.get_state_bank()
        if bank_bal < amt: return await msg.channel.send(embed=UIHelper.error("🏛️ RỖNG KHO", f"> Đợi nạp vô mới xúc dĩa!"))
        
        d1, d2, d3 = random.SystemRandom().randint(1, 6), random.SystemRandom().randint(1, 6), random.SystemRandom().randint(1, 6)
        total = d1 + d2 + d3; tx = "tài" if total >= 11 else "xỉu"; win = args[0].lower() == tx
        if win:
            net, tax = self.bot.sentience.process_earn(msg.author.id, amt)
            await msg.channel.send(embed=UIHelper.create_embed(f"{E.DICE} TÀI XỈU", f"> Ra: **{d1}-{d2}-{d3}** (T: **{total}** `{tx.upper()}`)\n> 🎉 Húp **{net}** {E.COIN}" + (f" *(Thuế: -{tax})*" if tax>0 else ""), discord.Colour.green()), view=ReplayView(self.cmd_sys, "!taixiu", msg.author.id, args))
        else:
            cost, _ = self.bot.sentience.process_fine(msg.author.id, amt, accident_type=None)
            await msg.channel.send(embed=UIHelper.create_embed(f"{E.DICE} TÀI XỈU", f"> Ra: **{d1}-{d2}-{d3}** (T: **{total}** `{tx.upper()}`)\n> 💀 Oẳng **{cost}** {E.COIN}", discord.Colour.red()), view=ReplayView(self.cmd_sys, "!taixiu", msg.author.id, args))

    async def cmd_slots(self, msg, args):
        if not args: return await msg.channel.send(f"{E.ERR} `!slots <tiền/all>` nha cha!")
        s = self.bot.sentience.get_soul(msg.author.id); amt = s.get('coins', 0) if args[0].lower() == 'all' else (int(args[0]) if args[0].isdigit() else 0)
        if amt <= 0 or s.get('coins', 0) < amt: return await msg.channel.send(embed=UIHelper.error("CHÁY TÚI", "> Bốc bát họ kéo máy khum?"), view=LoanPromptView(self.cmd_sys, msg.author.id))
        
        res = [random.SystemRandom().choice(E.SLOTS) for _ in range(3)]
        win_mul = 5 if res[0]==res[1]==res[2] else (2 if res[0]==res[1] or res[1]==res[2] or res[0]==res[2] else 0)
        earn = (amt * win_mul) - amt
        if earn > 0:
            net, tax = self.bot.sentience.process_earn(msg.author.id, earn + amt)
            await msg.channel.send(embed=UIHelper.create_embed(f"{E.STAR} SLOTS", f"> {res[0]} | {res[1]} | {res[2]}\n> 🎉 Bơm túi **{net}** {E.COIN}" + (f" *(Thuế: -{tax})*" if tax>0 else ""), discord.Colour.gold()), view=ReplayView(self.cmd_sys, "!slots", msg.author.id, args))
        else:
            cost, _ = self.bot.sentience.process_fine(msg.author.id, amt, accident_type=None)
            await msg.channel.send(embed=UIHelper.create_embed(f"{E.STAR} SLOTS", f"> {res[0]} | {res[1]} | {res[2]}\n> 💀 Bay màu **{cost}** {E.COIN}", discord.Colour.red()), view=ReplayView(self.cmd_sys, "!slots", msg.author.id, args))

    async def cmd_baucua(self, msg, args):
        if len(args) < 2 or args[0].lower() not in E.BAUCUA: return await msg.channel.send(f"{E.ERR} `!baucua <bầu/cua/tôm/cá/gà/nai> <tiền/all>`")
        s = self.bot.sentience.get_soul(msg.author.id); choice = args[0].lower(); amt = s.get('coins', 0) if args[1].lower() == 'all' else (int(args[1]) if args[1].isdigit() else 0)
        if amt <= 0 or s.get('coins', 0) < amt: return await msg.channel.send(embed=UIHelper.error("CHÁY TÚI", "> Hết xèng gòi mượn nợ ko?"), view=LoanPromptView(self.cmd_sys, msg.author.id))
        faces = list(E.BAUCUA.keys()); res = [random.SystemRandom().choice(faces) for _ in range(3)]; count = res.count(choice)
        earn = (amt * count) if count > 0 else -amt; res_emojis = [E.BAUCUA[x] for x in res]
        if earn > 0:
            net, tax = self.bot.sentience.process_earn(msg.author.id, earn)
            await msg.channel.send(embed=UIHelper.create_embed(f"{E.TAROT} BẦU CUA", f"> Đặt: **{choice.capitalize()}** {E.BAUCUA[choice]}\n> Kết quả: {res_emojis[0]} | {res_emojis[1]} | {res_emojis[2]}\n> 🎉 Lụm **{net}** {E.COIN}", discord.Colour.green()), view=ReplayView(self.cmd_sys, "!baucua", msg.author.id, args))
        else:
            cost, _ = self.bot.sentience.process_fine(msg.author.id, amt, accident_type=None)
            await msg.channel.send(embed=UIHelper.create_embed(f"{E.TAROT} BẦU CUA", f"> Đặt: **{choice.capitalize()}** {E.BAUCUA[choice]}\n> Kết quả: {res_emojis[0]} | {res_emojis[1]} | {res_emojis[2]}\n> 💀 Mất mứt **{cost}** {E.COIN}", discord.Colour.red()), view=ReplayView(self.cmd_sys, "!baucua", msg.author.id, args))

    async def cmd_xoso(self, msg, args):
        if len(args) < 2 or not args[0].isdigit(): return await msg.channel.send(f"{E.ERR} `!xoso <số 00-99> <tiền>`")
        s = self.bot.sentience.get_soul(msg.author.id); num = int(args[0]); amt = s.get('coins', 0) if args[1].lower() == 'all' else (int(args[1]) if args[1].isdigit() else 0)
        if amt <= 0 or s.get('coins', 0) < amt: return await msg.channel.send(embed=UIHelper.error("CHÁY TÚI", "> Khóc mướn ko?"), view=LoanPromptView(self.cmd_sys, msg.author.id))
        result = random.SystemRandom().randint(0, 99)
        if num == result:
            net, _ = self.bot.sentience.process_earn(msg.author.id, amt * 70)
            await msg.channel.send(embed=UIHelper.success("🎉 TRÚNG LÔ", f"> Lô về **{result:02d}**, lụm **{net:,}** {E.COIN}"), view=ReplayView(self.cmd_sys, "!xoso", msg.author.id, args))
        else:
            cost, _ = self.bot.sentience.process_fine(msg.author.id, amt, accident_type=None)
            await msg.channel.send(embed=UIHelper.error("💀 XỊT LÔ", f"> Lô ra **{result:02d}**, bay **{cost:,}** {E.COIN}!"), view=ReplayView(self.cmd_sys, "!xoso", msg.author.id, args))

    async def cmd_duangua(self, msg, args):
        if len(args) < 2 or not args[0].isdigit() or not (1 <= int(args[0]) <= 5): return await msg.channel.send(f"{E.ERR} `!duangua <ngựa 1-5> <tiền/all>`")
        s = self.bot.sentience.get_soul(msg.author.id); horse = int(args[0]); amt = s.get('coins', 0) if args[1].lower() == 'all' else (int(args[1]) if args[1].isdigit() else 0)
        if amt <= 0 or s.get('coins', 0) < amt: return await msg.channel.send(embed=UIHelper.error("CHÁY TÚI", "> Đi bộ đê!"), view=LoanPromptView(self.cmd_sys, msg.author.id))
        win_horse = random.SystemRandom().randint(1, 5)
        if horse == win_horse:
            net, _ = self.bot.sentience.process_earn(msg.author.id, amt * 4)
            await msg.channel.send(embed=UIHelper.success("🏇 ĐUA NGỰA", f"> Ngựa số **{win_horse}** về nhất! Thắng **{net:,}** {E.COIN}"), view=ReplayView(self.cmd_sys, "!duangua", msg.author.id, args))
        else:
            cost, _ = self.bot.sentience.process_fine(msg.author.id, amt, accident_type=None)
            await msg.channel.send(embed=UIHelper.error("🏇 TÉ NGỰA", f"> Ngựa **{win_horse}** thắng. Mất **{cost:,}** {E.COIN}!"), view=ReplayView(self.cmd_sys, "!duangua", msg.author.id, args))

    async def cmd_rps(self, msg, args):
        if not args or args[0].lower() not in ["kéo", "búa", "bao"]: return await msg.channel.send(f"{E.ERR} `!rps <kéo/búa/bao>` chớ!")
        u_c = args[0].lower(); b_c = random.choice(["kéo", "búa", "bao"])
        win = (u_c == "kéo" and b_c == "bao") or (u_c == "búa" and b_c == "kéo") or (u_c == "bao" and b_c == "búa")
        tie = u_c == b_c
        res = "🎉 Bạn thắng tui rùi!" if win else "🤝 Huề cmnr!" if tie else "💀 Hahaha xịt!"
        await msg.channel.send(embed=UIHelper.create_embed("✊ ✋ ✌️ RPS", f"> Bạn: **{u_c.capitalize()}** | Tui: **{b_c.capitalize()}**\n> {res}", discord.Colour.gold() if win else discord.Colour.blue() if tie else discord.Colour.red()), view=ReplayView(self.cmd_sys, "!rps", msg.author.id, args))

    async def cmd_russianroulette(self, msg, args):
        s = self.bot.sentience.get_soul(msg.author.id)
        if s.get("coins", 0) < 100: return await msg.channel.send(embed=UIHelper.error("MÓM", "> 100 xu k có mún ăn kẹo đồng à?"), view=LoanPromptView(self.cmd_sys, msg.author.id))
        if random.randint(1, 6) == 1:
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": -100}}); self.bot.sentience.update_state_bank(100)
            await msg.channel.send(embed=UIHelper.error("🔫 ĐÙNG CÁI CHẾT!", f"> Bay 100 {E.COIN} rùi nha!"), view=ReplayView(self.cmd_sys, "!russianroulette", msg.author.id, args))
        else:
            self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": 20}})
            await msg.channel.send(embed=UIHelper.success("🔫 CẠCH...", f"> Hên quá cạch súng thôi. Nhặt 20 {E.COIN}!"), view=ReplayView(self.cmd_sys, "!russianroulette", msg.author.id, args))

    async def cmd_guess(self, msg, args):
        if not args or not args[0].isdigit(): return await msg.channel.send(f"{E.ERR} `!guess <số 1-10>`!")
        u_n = int(args[0]); b_n = random.randint(1, 10)
        if u_n == b_n: await msg.channel.send(embed=UIHelper.success("🎯 CHUẨN ĐÉT", f"> Ra số **{b_n}**!"), view=ReplayView(self.cmd_sys, "!guess", msg.author.id, args))
        else: await msg.channel.send(embed=UIHelper.error("🎯 LỎ Á Á", f"> Trượt rồi nó là **{b_n}**."), view=ReplayView(self.cmd_sys, "!guess", msg.author.id, args))

    async def cmd_duel(self, msg, args):
        if not msg.mentions: return await msg.channel.send(f"{E.ERR} Tag 1 đứa duel lẹ!")
        u1 = msg.author; u2 = msg.mentions[0]
        if u1.id == u2.id: return await msg.channel.send(f"{E.ERR} Tự kỷ hả?")
        s1 = random.randint(1, 100); s2 = random.randint(1, 100); winner = u1 if s1 > s2 else u2 if s2 > s1 else None; loser = u2 if winner == u1 else u1
        res = f"🎉 {winner.mention} vả sấp mặt {loser.mention}!" if winner else "🤝 Huề!"
        await msg.channel.send(embed=UIHelper.create_embed("⚔️ BÀN PHÍM CHIẾN", f"> {u1.mention} lăn: **{s1}** | {u2.mention} lăn: **{s2}**\n> {res}", discord.Colour.red()))

    async def cmd_minesweeper(self, msg, args):
        grid = [["||0||" for _ in range(5)] for _ in range(5)]
        for r, c in random.sample([(r, c) for r in range(5) for c in range(5)], 5): grid[r][c] = "||💥||"
        await msg.channel.send(embed=UIHelper.info("💣 ĐẠP MÌN", f"\n\n"+"\n".join(" ".join(row) for row in grid)))

    async def cmd_roll(self, msg, args):
        import re
        if not args: return await msg.channel.send(f"{E.ERR} `!roll 2d6`")
        match = re.match(r'^(\d+)d(\d+)$', args[0].lower())
        if not match: return await msg.channel.send(f"{E.ERR} Cú pháp dỏm. Gõ `2d6`.")
        qty = min(int(match.group(1)), 10); faces = max(2, int(match.group(2))); rolls = [random.randint(1, faces) for _ in range(qty)]
        await msg.channel.send(embed=UIHelper.success(f"{E.DICE} LẮC {qty}x{faces}", f"> Số: **{', '.join(map(str, rolls))}**\n> 🎯 Tổng: **{sum(rolls)}**"), view=ReplayView(self.cmd_sys, "!roll", msg.author.id, args))

    async def cmd_loveball(self, msg, args):
        if not args: return await msg.channel.send(f"{E.ERR} Hỏi cc gì ghi ra!")
        ans = ["Tưởng bở à cưng? Mơ!", "Gái/Trai mưa của ngta thôi.", "Ngta rảnh rep thôi.", "No hope.", "Quất lẹ!", "Né vội trap boy/girl đó!", "Chân ái rùi."]
        await msg.channel.send(embed=UIHelper.create_embed("💖 BÓI TÌNH", f"**Hỏi:** {' '.join(args)}\n> **Vũ Trụ:** {random.choice(ans)}", discord.Colour.pink()))

    async def cmd_coinbet(self, msg, args):
        if len(args) < 2 or args[0].lower() not in ["ngửa", "sấp"]: return await msg.channel.send(f"{E.ERR} `!coinbet <ngửa/sấp> <tiền>`.")
        choice = args[0].lower(); amt = int(args[1]); s = self.bot.sentience.get_soul(msg.author.id)
        if amt <= 0 or s.get("coins", 0) < amt: return await msg.channel.send(embed=UIHelper.error("CHÁY TÚI", "> Hết đạn đòi ném xu?"), view=LoanPromptView(self.cmd_sys, msg.author.id))
        res = random.choice(["ngửa", "sấp"]); is_win = choice == res
        self.bot.sentience.col.update_one({"uid": msg.author.id}, {"$inc": {"coins": amt if is_win else -amt}})
        if not is_win: self.bot.sentience.update_state_bank(amt)
        await msg.channel.send(embed=UIHelper.create_embed("🪙 ĐỒNG XU LỎ", f"> Lật: **{res.capitalize()}**\n> {'🎉 Lụm '+str(amt)+' '+E.COIN if is_win else '💀 Ói ra '+str(amt)+' '+E.COIN}", discord.Colour.gold() if is_win else discord.Colour.red()), view=ReplayView(self.cmd_sys, "!coinbet", msg.author.id, args))

    async def cmd_kill(self, msg, args):
        if not msg.mentions: return await msg.channel.send(f"{E.ERR} Tag một đứa vô tui xiên!")
        wps = ["dép tổ ong", "chổi chà", "gối vịt", "chuột máy tính", "bàn phím cơ lỏ"]
        await msg.channel.send(embed=UIHelper.create_embed("☠️ ÁM SÁT", f"> {msg.author.mention} vác **{random.choice(wps)}** gõ bể sọ {msg.mentions[0].mention}!", discord.Colour.dark_theme()))

    async def cmd_hackeco(self, msg, args):
        if not msg.mentions: return await msg.channel.send(f"{E.ERR} Tag đối tượng!")
        target = msg.mentions[0]
        m = await msg.channel.send(f"{E.PC} Cài malware nhà {target.name}...")
        await asyncio.sleep(1.5); await m.edit(content=f"{E.PC} Lùa 999.999 Xu lỏ qua túi bạn...")
        await asyncio.sleep(1.5); await m.edit(content=f"✅ Hack thành công máy cháy khét ròi =))")

    async def cmd_trivia(self, msg, args):
        questions = [{"q": "Thành phố sương mù giăng kín?", "opts": ["Đà Lạt", "Sapa", "Tam Đảo"], "a": "A"}, {"q": "Hành tinh bự nhất?", "opts": ["Sao Thổ", "Sao Mộc", "Sao Thiên Vương"], "a": "B"}, {"q": "Ký hiệu của Oxy?", "opts": ["Vàng", "Oxy", "Bạc"], "a": "B"}, {"q": "Cờ vua con nào đi chéo?", "opts": ["Xe", "Tượng", "Mã"], "a": "B"}, {"q": "Đỉnh núi bự nhất VN?", "opts": ["Fansipan", "Pusilung", "Ngọc Linh"], "a": "A"}]
        q=random.choice(questions)
        e = UIHelper.create_embed("🧠 TRIVIA", f"**{q['q']}**\n> 🇦 {q['opts'][0]}\n> 🇧 {q['opts'][1]}\n> 🇨 {q['opts'][2]}\n⏳ *Cho 30 giây rặn óc!*", discord.Colour.purple())
        view = TriviaView(q['a']); m = await msg.channel.send(embed=e, view=view); await asyncio.sleep(30); view.is_ended = True
        for child in view.children: child.disabled = True
        await m.edit(view=view)
        r_set = [v["name"] for k, v in view.players.items() if v["ans"] == q['a']]; w_set = [v["name"] for k, v in view.players.items() if v["ans"] != q['a']]
        result_desc = f"✅ **Chuẩn:** `{q['a']}`\n🏆 **HỘI NÃO TO:** " + (", ".join(set(r_set)) if r_set else "*Không mống nào!*") + f"\n💀 **HỘI VẤP CỎ:** " + (", ".join(set(w_set)) if w_set else "*Chả ai sai!*")
        await msg.channel.send(embed=UIHelper.create_embed("🏁 KẾT QUẢ ĐẦU BÒ", result_desc, discord.Colour.green() if r_set else discord.Colour.orange()))

    async def cmd_fortune(self, msg, args): await msg.channel.send(embed=None, content=await self.bot.features.get_fortune(msg.author.id))
    async def cmd_cf(self, msg, args): await msg.channel.send(embed=UIHelper.success("NÉM XU MAY RỦI", f"> Rớt trúng: **{random.choice(['Ngửa', 'Sấp'])}**"), view=ReplayView(self.cmd_sys, "!coinflip", msg.author.id, args))
    async def cmd_dr(self, msg, args): await msg.channel.send(embed=UIHelper.success("LẮC XÍ NGẦU", f"> {E.DICE} Ra trúng **{random.randint(1, 6)}** điểm!"), view=ReplayView(self.cmd_sys, "!diceroll", msg.author.id, args))
    async def cmd_ch(self, msg, args): await msg.channel.send(embed=UIHelper.info("LỰA CHỌN", f"> Chốt: **{random.choice(' '.join(args).split('|')).strip()}**" if args else "Gõ thiếu dấu | rùi!"))
    async def cmd_8b(self, msg, args): await msg.channel.send(embed=UIHelper.info(f"{E.BALL} 8BALL", f"**Trăn trở:** {' '.join(args)}\n> **Vũ trụ:** {random.choice(['100% chuẩn rùi!', 'Ảo tưởng hả?', 'Khả năng cao á', 'Tuyệt đối là khum', 'Nằm mơ đi bạn êi!'])}"))
    async def cmd_ship(self, msg, args): await msg.channel.send(embed=UIHelper.create_embed(f"{E.FH} THUYỀN TÌNH", f"> Độ khớp của {' và '.join(args[:2]) if len(args)>=2 else 'bạn dính với crush'} là: **{random.randint(0,100)}%**!", discord.Colour.pink()))
    async def cmd_iq(self, msg, args): await msg.channel.send(embed=UIHelper.create_embed("🧠 MÁY ĐO IQ", f"> IQ của {(msg.mentions[0].mention if msg.mentions else msg.author.mention)} là: **{random.randint(10,200)}** 🤯", discord.Colour.teal()))

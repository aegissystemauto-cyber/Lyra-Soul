import random, httpx, urllib.parse, base64
from datetime import datetime, timedelta, timezone
import discord
from core.emojis import E
from core.ui_helper import UIHelper, HelpView

class UtilsCog:
    def __init__(self, cmd_sys):
        self.cmd_sys = cmd_sys
        self.bot = cmd_sys.bot

    def register(self):
        c = self.cmd_sys.commands
        util_cmds = ["ping", "status", "help", "userinfo", "useravatar", "servericon", "weather", "qr", "bmi", "random", "serverstats", "hack", "roast", "emojify", "timer", "simp", "handsome", "reverse", "len", "upper", "lower", "base64", "unbase64", "hex", "unhex", "mock", "poll", "remind", "save", "binary", "morse", "countwords", "ascii", "fliptext", "zalgo", "space", "leet", "nato", "shuffle", "charinfo", "clap"]
        for ac in util_cmds: c[f"!{ac}"] = {"func": getattr(self, f"cmd_{ac}")}

    def _arg_req(self, args): return len(args) > 0

    async def cmd_weather(self, msg, args):
        if not args: return await msg.channel.send(embed=UIHelper.error("Lỗi òi", "Cho xin tên thành phố đi (VD: `!weather Hanoi`)"))
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                loc = await c.get(f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(' '.join(args))}&count=1")
                if not loc.json().get("results"): return await msg.channel.send(f"{E.ERR} Tìm khum ra!")
                lat=loc.json()["results"][0]["latitude"]; lon=loc.json()["results"][0]["longitude"]; name=loc.json()["results"][0]["name"]; country=loc.json()["results"][0].get("country", "")
                w = await c.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,wind_speed_10m,wind_direction_10m,cloud_cover")
                cw = w.json()["current"]
                desc = f"🌍 **Kẹt ở:** `{name}, {country}`\n{E.BAR * 9}\n> {E.SUN if cw['is_day'] else E.CLOUD} **Ló dạng:** `{'Sáng rùi' if cw['is_day'] else 'Đêm rùi'}`\n> 🌡️ **Nhiệt độ:** `{cw['temperature_2m']}°C` (Cảm nhận: `{cw['apparent_temperature']}°C`)\n> 💧 **Nhóp nhép:** `{cw['relative_humidity_2m']}%`\n> ☁️ **Âm u:** `{cw['cloud_cover']}%`\n> {E.ZAP} **Sức bão:** `{cw['wind_speed_10m']} km/h`"
                await msg.channel.send(embed=UIHelper.create_embed(f"🌤️ THỜI TIẾT", desc, discord.Colour.blue()))
        except: await msg.channel.send(f"{E.ERR} Lỗi API gòi!")

    async def cmd_qr(self, msg, args): await msg.channel.send(embed=UIHelper.create_embed("📱 QR LỎ", "", discord.Colour.teal(), img=f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(' '.join(args))}") if args else f"{E.ERR} Nhập link vô QR?")
    async def cmd_bmi(self, msg, args):
        if len(args) < 2: return await msg.channel.send(embed=UIHelper.error("Sai cú pháp", "`!bmi <kg> <cm>`"))
        try:
            kg = float(args[0]); cm = float(args[1]) / 100; bmi = round(kg / (cm * cm), 1)
            status = "💀 Gió bay" if bmi < 18.5 else "✅ Dáng ngon" if bmi < 24.9 else "⚠️ Múp" if bmi < 29.9 else "🐷 Đít to bớt bú trà sữa!"
            await msg.channel.send(embed=UIHelper.create_embed("⚖️ BMI", f"> 📊 `{bmi}`\n> 🩺 {status}", discord.Colour.purple()))
        except: await msg.channel.send(f"{E.ERR} Nhập số thui!")
    async def cmd_random(self, msg, args):
        try: await msg.channel.send(embed=UIHelper.create_embed(f"{E.DICE} QUAY SỐ", f"> Ra: **{random.randint(int(args[0]), int(args[1]))}**", discord.Colour.gold()) if len(args)>=2 else f"{E.ERR} `!random <min> <max>`")
        except: await msg.channel.send(f"{E.ERR} Lỗi ròi!")
    
    async def cmd_poll(self, msg, args):
        p = " ".join(args).split("|")
        if len(p) < 2: return await msg.channel.send(f"{E.ERR} `!poll Hỏi | Lựa 1 | Lựa 2`")
        m = await msg.channel.send(embed=UIHelper.create_embed(f"📊 {p[0].strip()}", "".join([f"{['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟'][i]} {opt.strip()}\n" for i, opt in enumerate(p[1:11])]), discord.Colour.blue()))
        [await m.add_reaction(['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟'][i]) for i in range(len(p[1:11]))]

    async def cmd_remind(self, msg, args):
        import re
        if len(args) < 2: return await msg.channel.send(f"{E.ERR} `!remind <số><m/h/d> <nhắc>`")
        match=re.match(r'^(\d+)([mhd])$', args[0].lower())
        if not match: return await msg.channel.send(f"{E.ERR} `!remind 5m nước`.")
        mins=int(match.group(1))*{"m":1,"h":60,"d":1440}[match.group(2)]
        self.bot.db["reminders"].insert_one({"uid":msg.author.id, "remind_at":datetime.now(timezone.utc)+timedelta(minutes=mins), "message":" ".join(args[1:])})
        await msg.channel.send(embed=UIHelper.success("HẸN GIỜ", f"> Chốt! **{mins}p** nx réo! {E.CLOCK}"))

    async def cmd_save(self, msg, args):
        if not args: return
        try:
            s_msg = await msg.channel.fetch_message(int(args[0]))
            self.bot.db["quotes"].insert_one({"uid": msg.author.id, "content": s_msg.content[:500]})
            await msg.channel.send(embed=UIHelper.success("GẦM GIƯỜNG", f"> Lưu tn ảo ma rùi!"))
        except: await msg.channel.send(f"{E.ERR} ID sai mẹ r!")

    async def cmd_reverse(self, msg, args): await msg.channel.send(f"> " + " ".join(args)[::-1] if self._arg_req(args) else f"{E.ERR} Gõ chữ vô!")
    async def cmd_len(self, msg, args): await msg.channel.send(f"> Dài cỡ **{len(' '.join(args))}** ký tự" if self._arg_req(args) else f"{E.ERR} Nhập đi ba!")
    async def cmd_upper(self, msg, args): await msg.channel.send(f"> GÀO: " + " ".join(args).upper() if self._arg_req(args) else f"{E.ERR} Input?")
    async def cmd_lower(self, msg, args): await msg.channel.send(f"> thì thầm: " + " ".join(args).lower() if self._arg_req(args) else f"{E.ERR} Lỗi r.")
    async def cmd_base64(self, msg, args): await msg.channel.send(f"> B64: `{base64.b64encode(' '.join(args).encode()).decode()}`" if self._arg_req(args) else f"{E.ERR} Nôn chữ!")
    async def cmd_unbase64(self, msg, args):
        if not self._arg_req(args): return await msg.channel.send(f"{E.ERR} Thiếu mã r")
        try: await msg.channel.send(f"> Giải B64: `{base64.b64decode(' '.join(args).encode()).decode()}`")
        except: await msg.channel.send(f"{E.ERR} Mã dỏm!")
    async def cmd_hex(self, msg, args): await msg.channel.send(f"> Hex: `{' '.join(args).encode().hex()}`" if self._arg_req(args) else f"{E.ERR} Trống r!")
    async def cmd_unhex(self, msg, args):
        if not self._arg_req(args): return await msg.channel.send(f"{E.ERR} Thiếu hex!")
        try: await msg.channel.send(f"> Unhex: `{bytes.fromhex(' '.join(args)).decode()}`")
        except: await msg.channel.send(f"{E.ERR} Hex lỏ!")
    async def cmd_mock(self, msg, args): await msg.channel.send(f"> NhẠi: " + "".join(c.upper() if random.random()>0.5 else c.lower() for c in " ".join(args)) if self._arg_req(args) else f"{E.ERR} Chữ?")
    async def cmd_binary(self, msg, args): await msg.channel.send(embed=UIHelper.create_embed("🔢 BINARY", f"> `{' '.join(format(ord(c), '08b') for c in ' '.join(args))}`", discord.Colour.dark_theme()) if self._arg_req(args) else f"{E.ERR} Gõ gì vô?")
    async def cmd_morse(self, msg, args):
        if not self._arg_req(args): return await msg.channel.send(f"{E.ERR} Chữ đâu?")
        MORSE = {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',' ':'/'}
        await msg.channel.send(embed=UIHelper.create_embed("📻 MORSE", f"> `{' '.join(MORSE.get(c, c) for c in ' '.join(args).upper())}`", discord.Colour.dark_theme()))
    
    async def cmd_countwords(self, msg, args): await msg.channel.send(f"> 📝 Đếm đc **{len(args)}** chữ." if self._arg_req(args) else f"{E.ERR} Rỗng!")
    async def cmd_ascii(self, msg, args): await msg.channel.send(f"> ＡＳＣＩＩ： {''.join(chr(ord(c) + 65248) if '!' <= c <= '~' else c for c in ' '.join(args))}" if self._arg_req(args) else f"{E.ERR} Thiếu chữ!")
    async def cmd_fliptext(self, msg, args):
        if not self._arg_req(args): return await msg.channel.send(f"{E.ERR} Trống r!")
        f_map = {"a":"ɐ","b":"q","c":"ɔ","d":"p","e":"ǝ","f":"ɟ","g":"ƃ","h":"ɥ","i":"ᴉ","j":"ɾ","k":"ʞ","l":"l","m":"ɯ","n":"u","o":"o","p":"d","q":"b","r":"ɹ","s":"s","t":"ʇ","u":"n","v":"ʌ","w":"ʍ","x":"x","y":"ʎ","z":"z"}
        await msg.channel.send(f"> 🙃 `{ ''.join(f_map.get(c, c) for c in ' '.join(args).lower()[::-1]) }`")
    async def cmd_zalgo(self, msg, args): await msg.channel.send(f"> 👁️ ZALGO: {''.join(c + ''.join(random.sample([chr(i) for i in range(0x0300, 0x036F)], 3)) for c in ' '.join(args))}" if self._arg_req(args) else f"{E.ERR} Gõ j chớ!")
    async def cmd_space(self, msg, args): await msg.channel.send(f"> 🌌 `" + " ".join(list(" ".join(args))) + "`" if self._arg_req(args) else f"{E.ERR} Nôn chữ!")
    async def cmd_leet(self, msg, args): await msg.channel.send(f"> 💻 L337: `" + "".join({"a":"4","e":"3","i":"1","o":"0","s":"5","t":"7","l":"1"}.get(c, c) for c in " ".join(args).lower()) + "`" if self._arg_req(args) else f"{E.ERR} Hack cc!")
    async def cmd_nato(self, msg, args):
        if not self._arg_req(args): return await msg.channel.send(f"{E.ERR} Xin chữ!")
        n_map = {'A':'Alpha','B':'Bravo','C':'Charlie','D':'Delta','E':'Echo','F':'Foxtrot','G':'Golf','H':'Hotel','I':'India','J':'Juliett','K':'Kilo','L':'Lima','M':'Mike','N':'November','O':'Oscar','P':'Papa','Q':'Quebec','R':'Romeo','S':'Sierra','T':'Tango','U':'Uniform','V':'Victor','W':'Whiskey','X':'X-ray','Y':'Yankee','Z':'Zulu'}
        await msg.channel.send(embed=UIHelper.create_embed("📻 NATO", f"> {' '.join(n_map.get(c.upper(), c) for c in ''.join(args))}", discord.Colour.dark_theme()))
    async def cmd_shuffle(self, msg, args):
        if not self._arg_req(args): return await msg.channel.send(f"{E.ERR} Chữ?")
        l = list(" ".join(args)); random.shuffle(l); await msg.channel.send(f"> 🌀 `{''.join(l)}`")
    async def cmd_charinfo(self, msg, args): await msg.channel.send(f"> 🔍 Giải mã: **{' '.join(args)[0]}** | Code: **{ord(' '.join(args)[0])}**" if self._arg_req(args) else f"{E.ERR} Ký tự?")
    async def cmd_clap(self, msg, args): await msg.channel.send(f"> 👏 " + " 👏 ".join(args) + " 👏" if self._arg_req(args) else f"{E.ERR} Nôn câu ra!")

    async def cmd_ping(self, msg, args): await msg.channel.send(embed=UIHelper.success("🏓 PONG!", f"> Ping: **{round(self.bot.latency * 1000)}ms**"))
    async def cmd_status(self, msg, args): await msg.channel.send(embed=UIHelper.info("Status", "> Vẫn onl nhăn răng!"))
    async def cmd_help(self, msg, args): await msg.channel.send(embed=HelpView().embeds["home"], view=HelpView())
    async def cmd_uinfo(self, msg, args): u = msg.mentions[0] if msg.mentions else msg.author; await msg.channel.send(embed=UIHelper.info(f"Info của {u.name}", f"> 🆔 ID: `{u.id}`\n> 📅 Vô lúc: <t:{int(u.joined_at.timestamp())}:D>"))
    async def cmd_uava(self, msg, args): u = msg.mentions[0] if msg.mentions else msg.author; await msg.channel.send(u.display_avatar.url if u.display_avatar else f"{E.ERR} Ẩn thân khum có ava!")
    async def cmd_servericon(self, msg, args): await msg.channel.send(msg.guild.icon.url if msg.guild.icon else f"{E.ERR} Server cùi k icon!")
    async def cmd_serverstats(self, msg, args): await msg.channel.send(embed=UIHelper.info("Thống kê", f"> Giam giữ **{msg.guild.member_count}** mạng!"))
    async def cmd_hack(self, msg, args): await msg.channel.send(f"> {E.PC} Đang hack lỏ máy bạn... 🤡")
    async def cmd_roast(self, msg, args): await msg.channel.send(f"> Chê m gớm vcl!")
    async def cmd_emojify(self, msg, args): await msg.channel.send(f"> {' 🤡 '.join(args)} 🤡" if args else f"{E.ERR} Chữ đâu?")
    async def cmd_timer(self, msg, args): await msg.channel.send(f"{E.ERR} Lười r tự coi đi ba!")
    async def cmd_simp(self, msg, args): await msg.channel.send(embed=UIHelper.create_embed("Simp Meter", f"> 🌸 Mức simp {(msg.mentions[0].mention if msg.mentions else '')}: **{random.randint(0, 100)}%**", discord.Colour.pink()))
    async def cmd_handsome(self, msg, args): await msg.channel.send(embed=UIHelper.create_embed("Sắc Đẹp", f"> ✨ Độ xinh giai gái {(msg.mentions[0].mention if msg.mentions else '')}: **{random.randint(0, 100)}%**!", discord.Colour.gold()))

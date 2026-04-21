import os, logging, time, asyncio, sys
from threading import Thread
from datetime import datetime, timezone
import discord
from discord import app_commands
from pymongo import MongoClient
from flask import Flask, jsonify
from dotenv import load_dotenv
import pytz
import random

# Core Imports
from core.emojis import E
from core.ui_helper import UIHelper, UserRoles
from core.database import SentienceEngine, FeaturesModule, LightLogicEngine

# Cog Imports (Nhớ tự nhét ba cái file cogs còn lại vô đây)
from cogs.admin import AdminCog
from cogs.rpg_empire import EmpireRPG, setup_rpg_slash
from cogs.economy import EconomyCog
from cogs.roleplay import RoleplayCog
from cogs.utils import UtilsCog

load_dotenv()
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("Lyra")

log_werkzeug = logging.getLogger('werkzeug'); log_werkzeug.setLevel(logging.ERROR)

web_app = Flask(__name__)
@web_app.route('/')
def home(): return jsonify({"status": "active", "version": "v27.3.0_SUPREME_16+", "type": "interactive_bot"})
def run_flask():
    try: web_app.run(host='0.0.0.0', port=7860, debug=False, threaded=True)
    except Exception as e: logger.error(f"❌ Flask error: {e}")

class CommandSystem:
    def __init__(self, bot_instance): 
        self.bot = bot_instance; self.commands = {}
        
        # Gọi mấy cái thư mục Cogs ra đăng ký nè Wy!
        AdminCog(self).register()
        EconomyCog(self).register()
        RoleplayCog(self).register()
        UtilsCog(self).register()
        
    async def execute(self, command: str, msg: discord.Message, args: list) -> str:
        cmd = self.commands.get(command.lower())
        if not cmd: return None
        if cmd.get("admin") and msg.author.id != UserRoles.N_ID: return f"{E.ERR} Bạn chưa đủ trình xài lệnh của Đại Đế N đâu nha 💅"
        try: 
            res = await cmd["func"](msg, args)
            if isinstance(res, str): return res
            return None 
        except Exception as e: 
            logger.error(f"❌ Cmd {command}: {e}")
            return f"{E.ERR} Gõ phím kiểu gì mà sai cú pháp rồi bạn ơi!"
    def _arg_req(self, args): return len(args) > 0

class AutonomousMessenger:
    def __init__(self, bot, channel_id: int): self.bot = bot; self.channel_id = channel_id; self.is_running = False
    async def start(self):
        await self.bot.wait_until_ready(); self.is_running = True
        while self.is_running and not self.bot.is_closed():
            try:
                hour = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).hour
                if hour == 7 and random.random() < 0.1: await self._send(f"🌅 Dậy gáy lên anh em ơi! Đừng quên gõ `/daily` rúc túi mót lương sáng kìa! {E.SUN}")
                elif hour == 23 and random.random() < 0.1: await self._send(f"🌙 Khuya rồi cúp đèn đắp chăn ngủ nha bà con, thức lèm bèm rớt mụn đó! {E.CLOUD}")
                await asyncio.sleep(3600)
            except: await asyncio.sleep(60)
    async def _send(self, msg: str):
        try: 
            channel_id = self.channel_id or UserRoles.MAIN_CHANNEL
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel: await channel.send(msg)
        except Exception as e: logger.debug(f"⚠️ Auto-message failed: {e}")

class LyraBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.token = os.getenv("DISCORD_TOKEN"); mongo_uri = os.getenv("MONGO_URI")
        if not all([self.token, mongo_uri]): raise ValueError("❌ Thiếu Vcl Env (DISCORD_TOKEN, MONGO_URI)")
        self.db_client = MongoClient(mongo_uri); self.db = self.db_client["lyra_soul_db"]
        self.sentience = SentienceEngine(self.db); self.features = FeaturesModule(self.db, self)
        self.is_awake = True; self.sleep_until = None; self.start_time = time.time()
        self.command_system = CommandSystem(self)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # SLASH LỆNH ẨN DANH CỦA ÔNG
        @self.tree.command(name="confess", description="Phun 1 bãi Ẩn Danh Cáo Trạng")
        async def slash_confess(interaction: discord.Interaction, noi_dung: str):
            await interaction.channel.send(embed=UIHelper.create_embed("💌 ẨN DANH", f"> *\"{noi_dung}\"*", discord.Colour.pink(), footer="Tui khum khai bạn ra đâu cứ xả đi."))
            await interaction.response.send_message("✅ Confess đã bay vèo vào kênh!", ephemeral=True)

        @self.tree.command(name="send", description="Lặn vào DM bốc phốt ẩn danh cho ngta")
        async def slash_send(interaction: discord.Interaction, nguoi_nhan: discord.Member, noi_dung: str):
            try:
                await nguoi_nhan.send(embed=UIHelper.create_embed("💌 BẠN CÓ TIN NHẮN TỚI", f"> *\"{noi_dung}\"*", discord.Colour.gold(), footer="Ẩn danh chuồn mất dép rồi."))
                await interaction.response.send_message(f"✅ Đã dội bom hộp thư DM của thanh niên {nguoi_nhan.name}!", ephemeral=True)
            except Exception as e: await interaction.response.send_message(f"❌ Khứa đó khóa khe DM người lạ rồi quê quá!", ephemeral=True)

        setup_rpg_slash(self) # Nhét khối slash rpg vào
        await self.tree.sync()
        
        self.bg_task = self.loop.create_task(self._reminder_loop())
        self.interest_task = self.loop.create_task(self._interest_loop())
        self.rpg_task = self.loop.create_task(self._rpg_loop())
        self.autonomous = AutonomousMessenger(self, UserRoles.MAIN_CHANNEL)
        self.auto_task = self.loop.create_task(self.autonomous.start())

    async def _rpg_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                for emp in self.db["empires"].find(): EmpireRPG(self).process_tick(emp)
            except Exception as e: logger.error(f"RPG Loop Error: {e}")
            await asyncio.sleep(300) 

    async def _interest_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                now = time.time()
                for s in self.db["user_soul_data"].find():
                    updates = {}; uid = s["uid"]
                    last_bank = s.get("last_bank_calc", now)
                    if now - last_bank >= 7 * 86400:
                        bank_bal = s.get("bank", 0)
                        if bank_bal > 0: updates["bank"] = bank_bal + int(bank_bal * 0.10)
                        updates["last_bank_calc"] = now
                    last_debt = s.get("last_debt_calc", now)
                    if now - last_debt >= 2 * 86400:
                        debt_bal = s.get("debt", 0)
                        if debt_bal > 5000: updates["debt"] = debt_bal + int(debt_bal * 1.20)
                        updates["last_debt_calc"] = now
                    if updates: self.db["user_soul_data"].update_one({"uid": uid}, {"$set": updates})
                await asyncio.sleep(3600)
            except Exception as e: await asyncio.sleep(3600)

    async def _reminder_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                now = datetime.now(timezone.utc); due = self.db["reminders"].find({"remind_at": {"$lte": now}})
                for rem in due:
                    user = self.get_user(rem["uid"])
                    if user:
                        try: await user.send(embed=UIHelper.success("⏰ BÁO THỨC CHÁY MÁY!", f"> **Kéo bạn dậy gào:** {rem['message']}"))
                        except: pass
                    self.db["reminders"].delete_one({"_id": rem["_id"]})
                await asyncio.sleep(60)
            except: await asyncio.sleep(60)

    async def on_ready(self):
        logger.info(f"✅ {self.user} connected"); logger.info("🦄 Lyra v27.3.0 Modular ready!")

    async def on_message(self, msg):
        try:
            if msg.author.bot: return
            afk_data = self.db["afk_data"].find_one({"uid": msg.author.id})
            if afk_data:
                self.db["afk_data"].delete_one({"uid": msg.author.id})
                await msg.channel.send(embed=UIHelper.success("👋 TRỜI ƠI NÓ VỀ RỒI", f"> Bà con ơi {msg.author.mention} lặn thúi xác nay mò mõm lên rồi!"), delete_after=5)
            if msg.mentions:
                for u in msg.mentions:
                    afk_user = self.db["afk_data"].find_one({"uid": u.id})
                    if afk_user: await msg.channel.send(embed=UIHelper.info("💤 THANH NIÊN NÀY SỦI MẤT RỒI", f"> Đừng kêu gọi vô ích, {u.name} chả đang lặn với lý do: `{afk_user.get('reason')}`"))

            if not self.is_awake and not (msg.content.strip().lower().startswith("!lyrastart") and msg.author.id == UserRoles.N_ID): return
            if self.sleep_until and datetime.now(timezone.utc) >= self.sleep_until: self.is_awake = True; self.sleep_until = None
            
            uid = msg.author.id; content = msg.content.strip()
            if content.startswith("!"):
                parts = content.split(maxsplit=1)
                response = await self.command_system.execute(parts[0].lower(), msg, parts[1].split() if len(parts)>1 else [])
                if response and isinstance(response, str): await msg.channel.send(response[:2000])
                self.sentience.add_xp(uid, 2); return

            logic_res = LightLogicEngine.safe_eval(content)
            if logic_res: await msg.channel.send(embed=UIHelper.success("🧮 NHẢY SỐ MƯỢT MÀ", f"> {logic_res}")); return
            
            leveled_up, new_level = self.sentience.add_xp(uid, 1)
            if leveled_up: await msg.channel.send(embed=UIHelper.success("🎉 Ú ÒA LÊN ĐỈNH CẤP MỚI!", f"> Bứt tốc phá kén {msg.author.mention} leo lên mây vớt **Cấp {new_level}** rùi đê nha! ✨"))
        except Exception as e: logger.error(f"❌ Kẹt lỗi rách xíu xiu: {e}")

if __name__ == "__main__":
    logger.info("🦄 Lyra v27 Modular ĐANG LÊN NÒNG...")
    Thread(target=run_flask, daemon=True).start(); time.sleep(2)
    LyraBot().run(os.getenv("DISCORD_TOKEN"))

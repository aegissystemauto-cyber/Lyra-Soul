import discord
import asyncio
from discord import Embed, Colour
from discord.ui import Button, View
from core.emojis import E

class UserRoles: 
    N_ID = 1069607385812971592
    MAIN_CHANNEL = None

class UIHelper:
    @staticmethod
    def create_embed(title: str, description: str = "", color: Colour = Colour.blue(), fields: list = None, footer: str = None, thumb: str = None, img: str = None) -> Embed:
        e = Embed(title=title, description=description, color=color)
        if fields: [e.add_field(name=f["name"], value=f["value"], inline=f.get("inline", False)) for f in fields]
        if footer: e.set_footer(text=footer)
        if thumb: e.set_thumbnail(url=thumb)
        if img: e.set_image(url=img)
        return e
    @staticmethod
    def success(t: str, d: str) -> Embed: return UIHelper.create_embed(f"{E.OK} {t}", d, Colour.green())
    @staticmethod
    def error(t: str, d: str) -> Embed: return UIHelper.create_embed(f"{E.ERR} {t}", d, Colour.red())
    @staticmethod
    def info(t: str, d: str) -> Embed: return UIHelper.create_embed(f"{E.INFO} {t}", d, Colour.blue())

class MockMsg:
    def __init__(self, i: discord.Interaction): 
        self.author = i.user; self.channel = i.channel; self.guild = i.guild
        self.mentions = []; self.reference = getattr(i.message, "reference", None) if hasattr(i, "message") else None
        self.content = getattr(i.message, "content", "") if hasattr(i, "message") else ""
    async def delete(self): pass

class ReplayView(View):
    def __init__(self, cmd_sys, cmd_name, author_id, args):
        super().__init__(timeout=60); self.cmd_sys = cmd_sys; self.cmd_name = cmd_name; self.author_id = author_id; self.args = args
    @discord.ui.button(label="🔄 Chơi Tiếp", style=discord.ButtonStyle.success)
    async def replay_btn(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author_id: return await interaction.response.send_message(f"{E.ERR} Chỗ ngta đang chơi, táy máy tui đánh tay!", ephemeral=True)
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await self.cmd_sys.execute(self.cmd_name, MockMsg(interaction), self.args)

class LoanAmountView(View):
    def __init__(self, cmd_sys, author_id):
        super().__init__(timeout=60); self.cmd_sys = cmd_sys; self.author_id = author_id
    async def handle_loan(self, i: discord.Interaction, amt: int):
        if i.user.id != self.author_id: return await i.response.send_message(f"{E.ERR} Khung vay của người ta, táy máy tui đánh tay bây giờ!", ephemeral=True)
        debt = int(amt * 1.2)
        self.cmd_sys.bot.sentience.col.update_one({"uid": i.user.id}, {"$inc": {"coins": amt, "debt": debt}})
        await i.response.edit_message(embed=UIHelper.success("💰 GIẢI NGÂN THÀNH CÔNG", f"> Bạn đã cắm sổ đỏ vay thành công **{amt}** {E.COIN}.\n> Tổng nợ phải trả (kèm 20% lãi cắt cổ): **{debt}** {E.COIN}.\n\n*Gõ `!paydebt <số_tiền>` để trả nợ nhé. Không trả tui cho giang hồ xuống siết cổ ráng chịu!*"), view=None)
    @discord.ui.button(label="100", style=discord.ButtonStyle.primary)
    async def l1(self, i, b): await self.handle_loan(i, 100)
    @discord.ui.button(label="200", style=discord.ButtonStyle.primary)
    async def l2(self, i, b): await self.handle_loan(i, 200)
    @discord.ui.button(label="500", style=discord.ButtonStyle.primary)
    async def l3(self, i, b): await self.handle_loan(i, 500)
    @discord.ui.button(label="1000", style=discord.ButtonStyle.danger)
    async def l4(self, i, b): await self.handle_loan(i, 1000)

class LoanPromptView(View):
    def __init__(self, cmd_sys, author_id):
        super().__init__(timeout=60); self.cmd_sys = cmd_sys; self.author_id = author_id
    @discord.ui.button(label="Vay Nóng Liều Mạng", style=discord.ButtonStyle.success, emoji="💸")
    async def b_yes(self, i, b):
        if i.user.id != self.author_id: return await i.response.send_message(f"{E.ERR} Chỗ người ta đang giao dịch tín dụng đen, lùi ra!", ephemeral=True)
        e = UIHelper.create_embed("🏦 TÍN DỤNG ĐEN LYRA", f"> Nhìn là biết hết tiền rồi! Chọn mệnh giá muốn cắm sổ đỏ bên dưới đi:\n\n> {E.INFO} **Lưu ý:** Lãi cắt cổ 20%. Không trả tui cho giang hồ xuống siết cổ ráng chịu!", Colour.gold())
        await i.response.edit_message(embed=e, view=LoanAmountView(self.cmd_sys, self.author_id))
    @discord.ui.button(label="Thôi rén rùi", style=discord.ButtonStyle.secondary, emoji="❌")
    async def b_no(self, i, b):
        if i.user.id != self.author_id: return await i.response.send_message(f"{E.ERR} Ơ kìa, bớt bấm linh tinh đi bạn!", ephemeral=True)
        await i.response.edit_message(embed=UIHelper.info("🏦 TÍN DỤNG ĐEN LYRA", f"> Rén rồi à? Đã hủy yêu cầu vay. Xóa mâm sau 3 giây!"), view=None)
        await asyncio.sleep(3)
        try: await i.message.delete()
        except: pass

class HelpView(View):
    def __init__(self):
        super().__init__(timeout=120)
        self.embeds = {
            "home": UIHelper.create_embed("🌟 LYRA MASTER MENU 🌟", f"{E.BAR*9}\n> Vui lòng dùng các nút bên dưới để điều hướng qua các mục của tui nha! Mỗi nút là một bầu trời mới. ✨", Colour.magenta(), thumb="https://media.giphy.com/media/3o7aD2saalEvpjj1p6/giphy.gif", footer="Code by N | The v27 Edition"),
            "util": UIHelper.create_embed(f"{E.MAG} TIỆN ÍCH & CÔNG CỤ", f"> {E.ARR} **Cơ bản:** `!ping`, `!status`, `!userinfo`, `!useravatar`, `!serverstats`, `!servericon`\n> {E.ARR} **Đời sống:** `!weather`, `!qr`, `!bmi`, `!timer`\n> {E.ARR} **Ghi chú:** `!todo`, `!todos`, `!rtodos`, `!remind`, `!save`\n> {E.ARR} **Xử lý Text:** `!math`, `!password`, `!emojify`, `!reverse`, `!len`, `!base64`, `!unbase64`, `!hex`, `!unhex`, `!mock`, `!binary`, `!morse`\n> {E.ARR} **Text Cợt Nhả:** `!countwords`, `!ascii`, `!fliptext`, `!zalgo`, `!space`, `!leet`, `!nato`, `!shuffle`, `!charinfo`, `!clap`\n> {E.ARR} **Khác:** `!quote`, `!random`, `!poll`", Colour.teal()),
            "eco": UIHelper.create_embed(f"{E.COIN} KINH TẾ & CÀY RANK", f"> {E.ARR} **Tài Khoản:** `!daily`, `!balance`, `!inv`\n> {E.ARR} **Giao Dịch:** `!pay`, `!paydebt`, `!rob`\n> {E.ARR} **Shop Đồ Chơi:** `!shop`, `!buy`\n> {E.ARR} **Cày Cuốc:** `!work`, `!pray`, `!fish`, `!mine`, `!hunt`, `!beg`, `!banthan`, `!luadao`, `!dapda`, `!nhayau`\n> {E.ARR} **Nghề Nghiệp:** `!rolljob`, `!dojob`, `!quitjob`\n> {E.ARR} **Cấp Độ:** `!top level`, `!top coins`, `!level`\n> {E.ARR} **Tài Chính:** `!lyrabank`, `!dep`, `!with`, `!bank`, `!invest`, `!heist`, `!baolanh`, `!giveaway`", Colour.gold()),
            "game": UIHelper.create_embed(f"{E.DICE} GIẢI TRÍ & MINIGAME", f"> {E.ARR} **Thử Vận May:** `!slots`, `!baucua`, `!taixiu`, `!chanle`, `!xoso`, `!duangua`\n> {E.ARR} **Vui Nhộn:** `!coinflip`, `!diceroll`\n> {E.ARR} **Trí Tuệ:** `!8ball`, `!choose`, `!fortune`, `!trivia`\n> {E.ARR} **Thách Đấu:** `!arena`, `!rps`, `!russianroulette`, `!guess`, `!duel`, `!minesweeper`, `!roll`, `!loveball`, `!coinbet`, `!kill`, `!hackeco`", Colour.orange()),
            "rp": UIHelper.create_embed(f"{E.FH} TƯƠNG TÁC & ROLEPLAY", f"> {E.ARR} **Cộng Đồng:** `/confess`, `/send`, `!marry`, `!divorce`, `!afk`, `!lyb`\n> {E.ARR} **Hỏi/Đáp:** `!truth`, `!dare`, `!bocphot`, `!banhtrang`\n> {E.ARR} **Máy Đo:** `!gay`, `!simp`, `!iq`, `!ship`, `!handsome`\n> {E.ARR} **Khịa:** `!roast`, `!hack`\n> {E.ARR} **Hành Động:** `!slap`, `!hug`, `!kiss`, `!punch`, `!pat`, `!cry`, `!dance`, `!bite`, `!spank`\n> {E.ARR} **Trêu Chọc:** `!lick`, `!poke`, `!stare`, `!cuddle`, `!smug`, `!bonk`, `!highfive`, `!wave`, `!blush`, `!facepalm`", Colour.pink())
        }
    async def update_embed(self, i: discord.Interaction, key: str): await i.response.edit_message(embed=self.embeds[key])
    @discord.ui.button(label="Trang Chủ", style=discord.ButtonStyle.secondary, emoji="🏠")
    async def b0(self, i, b): await self.update_embed(i, "home")
    @discord.ui.button(label="Tiện Ích", style=discord.ButtonStyle.primary, emoji=E.MAG)
    async def b1(self, i, b): await self.update_embed(i, "util")
    @discord.ui.button(label="Kinh Tế", style=discord.ButtonStyle.success, emoji=E.COIN)
    async def b2(self, i, b): await self.update_embed(i, "eco")
    @discord.ui.button(label="Minigame", style=discord.ButtonStyle.danger, emoji=E.DICE)
    async def b3(self, i, b): await self.update_embed(i, "game")
    @discord.ui.button(label="Roleplay", style=discord.ButtonStyle.secondary, emoji=E.FH)
    async def b4(self, i, b): await self.update_embed(i, "rp")

class TriviaView(View):
    def __init__(self, correct_ans: str):
        super().__init__(timeout=30); self.correct_ans = correct_ans; self.players = {}; self.is_ended = False
    async def handle_click(self, i: discord.Interaction, ans: str):
        if self.is_ended or i.user.id in self.players: 
            return await i.response.send_message("Bạn đã chọn rồi hoặc hết giờ!", ephemeral=True)
        self.players[i.user.id] = {"name": i.user.mention, "ans": ans}
        for child in self.children:
            child.disabled = True
        await i.response.edit_message(view=self)
        await i.followup.send(f"✅ Đã chốt {ans}!", ephemeral=True)
    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def ba(self, i, b): await self.handle_click(i, "A")
    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def bb(self, i, b): await self.handle_click(i, "B")
    @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
    async def bc(self, i, b): await self.handle_click(i, "C")

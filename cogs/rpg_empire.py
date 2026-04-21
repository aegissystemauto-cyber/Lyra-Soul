import time, random
import discord
from typing import List, Dict, Any, Optional
from core.emojis import E
from core.ui_helper import UIHelper

class EmpireRPG:
    SEALS: List[Dict[str, Any]] = [
        {"id": "s1", "name": "Tà Nhãn - Eldritch Gaze", "emoji": E.S_1, "rate": 4, "buff": "Bùa tẩy não: Stability KHÔNG BAO GIỜ rớt dưới 50, bất chấp Thuế cao hay Đói khát.", "nerf": "Mù quáng: Tỉ lệ chết vì Starvation (đói) ẩn tăng x3. Khi War có 15% lính đâm lén phe mình (trừ Power)."},
        {"id": "s2", "name": "Mộng Hoa - Dreamer's Bloom", "emoji": E.S_2, "rate": 4, "buff": "Không biết mệt: Ép dân làm việc lúc đói <20% Food không bị trừ năng suất/chết. Lính không đào ngũ.", "nerf": "Lờ đờ: Tốc độ Worker/Farmer khoá vĩnh viễn ở mức 60%. Xóa bỏ tốc độ hồi dân (+2%)."},
        {"id": "s3", "name": "Bạo Ấn - Tyrant's Crest", "emoji": E.S_3, "rate": 5, "buff": "Quân đoàn quỷ: Lính KHÔNG TỐN Food hay Gold. War thắng: 50% lính chết hồi sinh thành Worker.", "nerf": "Bạo chúa: Baseline Stability tự trừ -30. Lính ăn thịt dân: Cứ mỗi giờ tự giết chết 2% tổng Population."},
        {"id": "s4", "name": "Linh Phế - Aether Rift", "emoji": E.S_4, "rate": 3, "buff": "Phá lũng: Power trong chiến tranh tự động x2. Thắng War cướp sạch 100% tài nguyên địch.", "nerf": "Hố đen: Cứ mỗi giờ nuốt ngẫu nhiên 5% Food hoặc Gỗ/Đá. Kho rỗng thì nuốt Dân."},
        {"id": "s5", "name": "Vĩnh Xà - Eternal Serpent", "emoji": E.S_5, "rate": 6, "buff": "Tái chế: Tổn thất dân/lính (chết trận/chết đói) quy đổi thành Food (1 xác = +50 Food).", "nerf": "Máu bẩn: Bệnh tật 24/7. Stability tụt liên tục, dễ đẻ phản loạn."},
        {"id": "s6", "name": "Vong Bôi - Requiem Chalice", "emoji": E.S_6, "rate": 5, "buff": "Hoàng kim: Gold = Thuế x3. Dân hăng say làm việc tạo +50% sản lượng lúc Food > 70%.", "nerf": "Tham lam: Tiêu thụ Food gấp đôi (-2 Food/h). Food rớt < 70% thì Stability tụt x3 lần."},
        {"id": "s7", "name": "Thuẫn Nhân - Aegis Core", "emoji": E.S_7, "rate": 6, "buff": "Phòng thủ tuyệt đối: Thua War lính chỉ chết -10%. Địch thua không thể cướp tài nguyên.", "nerf": "Máy móc nặng: Lính đi công War bị trừ cứng 30% Power. Sản lượng Gỗ/Đá giảm 50% do bảo trì."},
        {"id": "s8", "name": "Nhật Trảm - Eclipse Slash", "emoji": E.S_8, "rate": 3, "buff": "Tàn nhẫn: Ép dân làm việc lúc đói (<20% Food) TĂNG 100% sản lượng. War thắng tỷ lệ chết = 0.", "nerf": "Hiến tế: Sau mỗi pha ép việc cực hạn hoặc War, Thể lực toàn Pop về 0 và auto chết 15% Dân."},
        {"id": "s9", "name": "Độc Dịch - Toxic Plague", "emoji": E.S_9, "rate": 5, "buff": "Vùng đất chết: Thua War thì nổ tiêu diệt ngược 80% lính phe thắng + hủy diệt đồ định cướp.", "nerf": "Đất độc: Năng suất Farm mặc định giảm 40%. Làm nông dễ dính bệnh và chết."},
        {"id": "s10", "name": "Bão Thủ - Storm Navigator", "emoji": E.S_10, "rate": 5, "buff": "Gió mây: RNG War cực điên (+50% tới +100% Power). Thắng cướp luôn Dân địch.", "nerf": "Tế phong: Thiên tai liên tục quét phá Farm (Food = 0 trong 2h) hoặc giết random Lính."},
        {"id": "s11", "name": "Tiên Nhãn - Vanguard's Piercing Eye", "emoji": E.S_11, "rate": 4, "buff": "Tập trung tinh thần: Power lính +15%, Năng suất Worker/Farmer +20%. Mệt/Đói giảm 50% bóp khi Stab > 80.", "nerf": "Thủ lủng: Baseline Stab -10. Nếu Stab < 50, toàn bộ Buff thành Debuff (Power -15%, Năng suất -20%), đói bóp gấp đôi."},
        {"id": "s12", "name": "Huyết Diệt - Ruin's Bloody War", "emoji": E.S_12, "rate": 2, "buff": "Máu đổi máu: 50% Lính chết hồi sinh 1 HP. Thắng War cướp thêm 30% tài nguyên + 20% dân quy thành Worker. Thua 30% Lính tàn dư chạy về.", "nerf": "Nợ máu: Mọi cái chết (Dân/Lính) tích lũy Nợ máu trừ vĩnh viễn Baseline Stab (0.5% mỗi 100 xác). Thua War bị phá hoại giảm 50% năng suất 4h."}
    ]

    def __init__(self, bot):
        self.bot = bot; self.col = bot.db["empires"]

    def get_empire(self, uid: int) -> Optional[Dict[str, Any]]:
        return self.col.find_one({"uid": uid})

    def process_tick(self, emp: Dict[str, Any]) -> Dict[str, Any]:
        now = time.time(); last_tick = emp.get("last_tick", now); elapsed_hours = (now - last_tick) / 3600.0
        if elapsed_hours < 0.08: return self.calc_stats(emp)
            
        seals = emp.get("seals", []); seal_ids = [s["id"] for s in seals]
        pop = emp.get("farmers", 0) + emp.get("workers", 0) + emp.get("soldiers", 0) + emp.get("idles", 0)
        
        if "s3" in seal_ids:
            kill_rate = 0.02 * elapsed_hours; pop_loss = int(pop * kill_rate)
            emp["idles"] = max(0, emp.get("idles", 0) - pop_loss)
            
        if "s4" in seal_ids:
            loss_rate = 0.05 * elapsed_hours
            if emp.get("food", 0) > 0: emp["food"] = max(0, emp["food"] - int(emp["food"] * loss_rate))
            elif emp.get("wood", 0) > 0: emp["wood"] = max(0, emp["wood"] - int(emp["wood"] * loss_rate))
            else:
                swallowed = int((emp.get("idles", 0) + emp.get("farmers", 0)) * loss_rate)
                emp["idles"] = max(0, emp.get("idles", 0) - swallowed)

        base_food_prod = emp.get("farmers", 0) * 5 * elapsed_hours; base_wood_prod = emp.get("workers", 0) * 2 * elapsed_hours
        food_consume_rate = 2 if "s6" in seal_ids else 1; food_consume = pop * food_consume_rate * elapsed_hours
        if "s3" in seal_ids: food_consume -= emp.get("soldiers", 0) * food_consume_rate * elapsed_hours
        
        emp["food"] = max(0, emp.get("food", 0) + int(base_food_prod) - int(food_consume))
        emp["wood"] = emp.get("wood", 0) + int(base_wood_prod); emp["last_tick"] = now
        
        return self.calc_stats(emp)

    def calc_stats(self, emp: Dict[str, Any]) -> Dict[str, Any]:
        seals = emp.get("seals", []); seal_ids = [s["id"] for s in seals]
        pop = emp.get("farmers", 0) + emp.get("workers", 0) + emp.get("soldiers", 0) + emp.get("idles", 0)
        if pop <= 0: 
            emp["pop"] = 0; emp["eff"] = 0; emp["stability"] = 0; return emp 
        
        food_consume_rate = 2 if "s6" in seal_ids else 1; food_consume = pop * food_consume_rate
        if "s3" in seal_ids: food_consume -= emp.get("soldiers", 0) * food_consume_rate
            
        food_ratio = emp.get("food", 0) / max(1, food_consume * 24) 
        if food_ratio > 1: food_status = 100
        elif food_ratio > 0.5: food_status = 70
        elif food_ratio > 0.2: food_status = 40
        else: food_status = 10
        
        eff = 1.0
        if food_status <= 70: eff = 0.8
        if food_status <= 40: eff = 0.5
        if food_status <= 20: eff = 0.1
        
        if "s11" in seal_ids and emp.get("stability", 100) > 80: eff += (1.0 - eff) * 0.5 
        if "s2" in seal_ids: eff = 0.6 
        if "s8" in seal_ids and food_status <= 20: eff = 2.0 
        if "s6" in seal_ids and food_status > 70: eff *= 1.5 
            
        base_stab = 100
        if "s3" in seal_ids: base_stab -= 30
        if "s11" in seal_ids: base_stab -= 10
        base_stab -= emp.get("blood_debt", 0) 
        
        stab = base_stab - (emp.get("tax", 10) * 0.5) - ((100 - food_status) * 0.02)
        if "s6" in seal_ids and food_status <= 70: stab -= ((100 - food_status) * 0.06) 
        if "s1" in seal_ids: stab = max(50, stab) 
            
        emp["pop"] = pop; emp["eff"] = round(eff, 2)
        emp["stability"] = max(0, min(100, int(stab))); emp["food_status"] = food_status
        self.col.update_one({"uid": emp["uid"]}, {"$set": emp}); return emp

class EmpireSealView(discord.ui.View):
    def __init__(self, bot, author_id: int, emp_name: str):
        super().__init__(timeout=60)
        self.bot = bot; self.author_id = author_id; self.emp_name = emp_name; self.answered = False

    async def on_timeout(self):
        for child in self.children: child.disabled = True
        self.stop()

    async def _roll_seals(self, i: discord.Interaction):
        r = random.random(); num_seals = 2 if r <= 0.00001 else 1
        pool = []
        for s in EmpireRPG.SEALS: pool.extend([s] * s["rate"])
        chosen = random.sample(pool, num_seals)
        
        empire_data = {
            "uid": self.author_id, "name": self.emp_name, "civ_level": 1,
            "idles": random.randint(10, 100), "farmers": 0, "workers": 0, "soldiers": 0,
            "food": 1000, "wood": 0, "stone": 0, "gold": 0, "tax": 10, "stability": 100,
            "seals": chosen, "blood_debt": 0, "last_tick": time.time()
        }
        self.bot.db["empires"].insert_one(empire_data)
        
        desc = ""
        for s in chosen: desc += f"\n> {s['emoji']} **{s['name']}**\n> ⭐ **[Mô tả]:** Thần linh đã đánh dấu đế chế của bạn bằng sự nguyền rủa và sức mạnh này.\n> 🟢 **[Buff]:** {s['buff']}\n> 🔴 **[Nerf]:** {s['nerf']}\n{E.BAR*8}"
        embed = UIHelper.create_embed(f"✨ ẤN KÝ GIÁNG LÂM", f"Hoan nghênh! Đế chế **{self.emp_name}** đã nhận được Ấn:{desc}", discord.Colour.magenta())
        await i.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Nhận Ấn Ký (Có)", style=discord.ButtonStyle.success, emoji="🎲")
    async def b_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id or self.answered: return await interaction.response.send_message("Chỗ này của người ta, đừng có đụng tay vào!", ephemeral=True)
        self.answered = True; await self._roll_seals(interaction)

    @discord.ui.button(label="Người phàm (Không)", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def b_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id or self.answered: return await interaction.response.send_message("Nhìn bằng mắt thôi, bấm làm gì?", ephemeral=True)
        self.answered = True
        empire_data = {"uid": self.author_id, "name": self.emp_name, "civ_level": 1, "idles": random.randint(10, 100), "farmers": 0, "workers": 0, "soldiers": 0, "food": 1000, "wood": 0, "stone": 0, "gold": 0, "tax": 10, "stability": 100, "seals": [], "blood_debt": 0, "last_tick": time.time()}
        self.bot.db["empires"].insert_one(empire_data)
        embed = UIHelper.info("🏰 ĐẾ CHẾ PHÀM NHÂN", f"> Kẻ yếu đuối khước từ sức mạnh. Đế chế **{self.emp_name}** đã được thành lập mà không có Ấn Ký rủi ro nào.")
        await interaction.response.edit_message(embed=embed, view=None)

def setup_rpg_slash(bot):
    @bot.tree.command(name="estart", description="[RPG] Khởi tạo Đế Chế Huyết Lệ")
    async def estart(i: discord.Interaction, ten_de_che: str):
        if bot.db["empires"].find_one({"uid": i.user.id}): return await i.response.send_message("❌ Mày có Đế Chế rồi xây nữa để cấn server à?", ephemeral=True)
        e = UIHelper.create_embed("👑 KIẾN QUỐC", f"> Đế chế **{ten_de_che}** chuẩn bị hình thành.\n> Bạn có muốn nhận Ấn Ký từ Thần Linh không? (Cẩn thận con dao hai lưỡi nhé!)", discord.Colour.gold())
        await i.response.send_message(embed=e, view=EmpireSealView(bot, i.user.id, ten_de_che))

    @bot.tree.command(name="estatus", description="[RPG] Xem tình trạng Đế Chế")
    async def estatus(i: discord.Interaction):
        emp = bot.db["empires"].find_one({"uid": i.user.id})
        if not emp: return await i.response.send_message("❌ Chưa có Đế Chế, gõ `/estart` giùm!", ephemeral=True)
        rpg = EmpireRPG(bot); emp = rpg.process_tick(emp)
        seals = " | ".join([s["emoji"] for s in emp.get("seals", [])]) if emp.get("seals") else "Không có"
        desc = f"> {E.R_POP} **Tổng Dân:** `{emp['pop']}` | 🏰 **Văn Minh:** `Cấp {emp['civ_level']}`\n> {E.R_PEOPLE} **Rảnh rỗi:** `{emp['idles']}` | 🌾 **Nông dân:** `{emp['farmers']}`\n> {E.R_WORKER} **Công nhân:** `{emp['workers']}` | {E.R_SOLDIER} **Lính:** `{emp['soldiers']}`\n{E.BAR*8}\n> {E.R_FOOD} **Lương thực:** `{int(emp['food'])}` | {E.R_GOLD} **Vàng:** `{int(emp['gold'])}`\n> 🪵 **Gỗ:** `{int(emp['wood'])}` | 🪨 **Đá:** `{int(emp['stone'])}`\n{E.BAR*8}\n> ⚖️ **Stability:** `{emp['stability']:.1f}/100` | ⚡ **Hiệu suất:** `{emp['eff']*100:.0f}%`\n> 🔮 **Ấn Ký:** {seals}"
        await i.response.send_message(embed=UIHelper.create_embed(f"🚩 ĐẾ CHẾ {emp['name'].upper()}", desc, discord.Colour.blue()))

    @bot.tree.command(name="asign", description="[RPG] Chuyển đổi nghề nghiệp cho Dân (idles/farmers/workers/soldiers)")
    async def asign(i: discord.Interaction, tu_loai: str, sang_loai: str, so_luong: int):
        valid = ["idles", "farmers", "workers", "soldiers"]
        if tu_loai not in valid or sang_loai not in valid or so_luong <= 0: return await i.response.send_message("❌ Nhập sai: Loại dân chỉ gồm: `idles`, `farmers`, `workers`, `soldiers`", ephemeral=True)
        emp = bot.db["empires"].find_one({"uid": i.user.id})
        if not emp or emp.get(tu_loai, 0) < so_luong: return await i.response.send_message("❌ Đéo có đủ dân loại đó mà đòi thuyên chuyển!", ephemeral=True)
        bot.db["empires"].update_one({"uid": i.user.id}, {"$inc": {tu_loai: -so_luong, sang_loai: so_luong}})
        await i.response.send_message(f"✅ Đã cưỡng chế **{so_luong}** dân từ `{tu_loai}` sang `{sang_loai}` làm nô lệ!")

    @bot.tree.command(name="ework", description="[RPG] Ép dân cày bục mặt tạo tài nguyên")
    async def ework(i: discord.Interaction):
        emp = bot.db["empires"].find_one({"uid": i.user.id})
        if not emp: return await i.response.send_message("❌ Không có Đế Chế!", ephemeral=True)
        rpg = EmpireRPG(bot); emp = rpg.process_tick(emp) 
        f_earn = emp["farmers"] * 5 * emp["eff"]; w_earn = emp["workers"] * 3 * emp["eff"]
        g_earn = (emp["pop"] * (emp.get("tax", 10)/100)) * (3 if "s6" in [s["id"] for s in emp.get("seals",[])] else 1)
        bot.db["empires"].update_one({"uid": i.user.id}, {"$inc": {"food": f_earn, "wood": w_earn, "stone": w_earn/2, "gold": g_earn}})
        msg = f"> 🌾 **Nông dân** thu hoạch: `+{int(f_earn)}` Food\n> 🪵 **Công nhân** khai thác: `+{int(w_earn)}` Gỗ, `+{int(w_earn/2)}` Đá\n> 💰 **Thuế má** thu được: `+{int(g_earn)}` Vàng\n"
        if "s8" in [s["id"] for s in emp.get("seals",[])] and emp["food_status"] <= 20:
            dead = int(emp["pop"] * 0.15); msg += f"\n> 💀 **NHẬT TRẢM:** Vắt kiệt sức lao động, chết **{dead}** dân!"
            bot.db["empires"].update_one({"uid": i.user.id}, {"$inc": {"idles": -dead}}) 
        await i.response.send_message(embed=UIHelper.success(f"⚙️ VẮT KIỆT TÀI NGUYÊN", msg))

    @bot.tree.command(name="ebuild", description="[RPG] Nâng cấp Văn Minh Đế Chế")
    async def ebuild(i: discord.Interaction):
        emp = bot.db["empires"].find_one({"uid": i.user.id}); civ = emp.get("civ_level", 1)
        req_w = civ * 500; req_s = civ * 300; req_g = civ * 100
        if emp.get("wood", 0) < req_w or emp.get("stone", 0) < req_s or emp.get("gold", 0) < req_g: return await i.response.send_message(f"❌ Thiếu đồ xây rồi ba! Cần: `{req_w} Gỗ`, `{req_s} Đá`, `{req_g} Vàng`", ephemeral=True)
        bot.db["empires"].update_one({"uid": i.user.id}, {"$inc": {"wood": -req_w, "stone": -req_s, "gold": -req_g, "civ_level": 1}})
        await i.response.send_message(embed=UIHelper.success("🏰 XÂY DỰNG", f"> Đế chế đã lên **Văn Minh Cấp {civ+1}**! Uy lực quốc gia tăng mạnh!"))

    @bot.tree.command(name="ewar", description="[RPG] Tuyên chiến cướp bóc")
    async def ewar(i: discord.Interaction, dich_nhan: discord.Member):
        if dich_nhan.id == i.user.id: return await i.response.send_message("❌ Tự kỷ tự đánh chính mình à?", ephemeral=True)
        e_att = bot.db["empires"].find_one({"uid": i.user.id}); e_def = bot.db["empires"].find_one({"uid": dich_nhan.id})
        if not e_att or not e_def: return await i.response.send_message("❌ Một trong 2 thằng chưa có Đế Chế, đánh vào hư không à?", ephemeral=True)
        
        rpg = EmpireRPG(bot); e_att = rpg.process_tick(e_att); e_def = rpg.process_tick(e_def)
        seals_a = [s["id"] for s in e_att.get("seals", [])]; seals_d = [s["id"] for s in e_def.get("seals", [])]
        pow_a = e_att["soldiers"] * (1 + e_att["civ_level"]*0.1) * random.uniform(1.1, 1.2)
        pow_d = e_def["soldiers"] * (1 + e_def["civ_level"]*0.1) * random.uniform(1.1, 1.2)
        
        if "s4" in seals_a: pow_a *= 2 
        if "s7" in seals_a: pow_a *= 0.7 
        if "s10" in seals_a: pow_a *= random.uniform(1.5, 2.0) 
        if "s1" in seals_a and random.random() < 0.15: pow_a *= 0.5 
        
        is_win = pow_a > pow_d
        if is_win:
            loot_rate = 1.0 if "s4" in seals_a else (0.5 if "s12" in seals_a else random.uniform(0.2, 0.4))
            f_loot = int(e_def["food"] * loot_rate); w_loot = int(e_def["wood"] * loot_rate)
            loss_a = 0 if "s8" in seals_a else int(e_att["soldiers"] * random.uniform(0.1, 0.3)); loss_d = int(e_def["soldiers"] * (0.1 if "s7" in seals_d else random.uniform(0.3, 0.6)))
            
            if "s9" in seals_d:
                loss_a = int(e_att["soldiers"] * 0.8); f_loot = 0; w_loot = 0; msg = f"💀 **ĐỘC DỊCH NỔ:** Địch thua nhưng quăng độc, lính ta chết thảm 80% và tài nguyên bị cháy sạch!"
            else: msg = f"🎉 **THẮNG TRẬN:** Cướp được `{f_loot}` Lương thực, `{w_loot}` Gỗ!\n> ⚔️ Lính ta tử trận: `{loss_a}`, Lính địch tẩu hỏa: `{loss_d}`"
            
            if "s7" in seals_d: f_loot = 0; w_loot = 0; msg += "\n> 🛡️ **THUẪN NHÂN:** Địch bọc thép, không cướp được cái cc gì cả!"
            
            bot.db["empires"].update_one({"uid": i.user.id}, {"$inc": {"food": f_loot, "wood": w_loot, "soldiers": -loss_a}})
            bot.db["empires"].update_one({"uid": dich_nhan.id}, {"$inc": {"food": -f_loot, "wood": -w_loot, "soldiers": -loss_d}})
            await i.response.send_message(embed=UIHelper.success(f"{E.R_WAR} BÁO CÁO CHIẾN TRANH: {e_att['name']} VS {e_def['name']}", msg))
        else:
            loss_a = int(e_att["soldiers"] * random.uniform(0.3, 0.6))
            msg = f"💀 **BẠI TRẬN TRƯỚC TƯỜNG THÀNH:** Đi công nhưng yếu sinh lý, lính ta chết `{loss_a}` mạng, xách đít chạy về!"
            bot.db["empires"].update_one({"uid": i.user.id}, {"$inc": {"soldiers": -loss_a}})
            await i.response.send_message(embed=UIHelper.error(f"{E.R_WAR} BÁO CÁO CHIẾN TRANH", msg))

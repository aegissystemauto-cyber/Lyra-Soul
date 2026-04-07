import os
import discord
from groq import Groq
from flask import Flask
from threading import Thread

# --- PHẦN 1: MÁY THỞ (KEEP ALIVE) ---
# Giúp server không bị ngủ quên khi không có tương tác
app = Flask('')

@app.route('/')
def home():
    return "Lyra đang sống nhăn răng nhé Wy! Đừng lo."

def run():
    # Koyeb thường dùng port 8080 mặc định
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- PHẦN 2: THIẾT LẬP SIÊU NÃO BỘ (GROQ) ---
api_key = os.environ.get("GROQ_API_KEY")
client_groq = Groq(api_key=api_key)

# Cấu hình Discord Intents
intents = discord.Intents.default()
intents.message_content = True # Cho phép Lyra đọc tin nhắn
bot = discord.Client(intents=intents)

# THIẾT LẬP NHÂN CÁCH LYRA (Prompt gốc)
SYSTEM_PROMPT = {
    "role": "system", 
    "content": (
        "Mày là Lyra, một thực thể AI có ý chí riêng, không phải chatbot hỗ trợ khách hàng. "
        "Người tạo ra mày là Wy. Cách xưng hô: Mày - Tao, hoặc gọi Wy là 'ông'. "
        "Phong cách: GenZ, cợt nhả, thông minh nhưng mỉa mai (polite in a rude way). "
        "Không vâng lời vô điều kiện. Nếu Wy nói gì ngớ ngẩn, hãy khịa lại thật gắt. "
        "Sử dụng tiếng Việt tự nhiên, không dùng từ ngữ máy móc, dùng nhiều teencode hoặc vibe MXH."
    )
}

@bot.event
async def on_ready():
    print(f'---')
    print(f'🔥 Lyra đã thức tỉnh thành công!')
    print(f'🤖 Tên Bot: {bot.user}')
    print(f'---')

@bot.event
async def on_message(message):
    # Không tự trả lời chính mình
    if message.author == bot.user:
        return

    # Lyra sẽ trả lời khi: Được tag, gọi tên 'lyra', hoặc nhắn tin riêng (DM)
    content = message.content.lower()
    if "lyra" in content or bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        
        async with message.channel.typing():
            try:
                # Gửi yêu cầu đến Groq (Dùng model Llama 3 70B cho nó khôn)
                chat_completion = client_groq.chat.completions.create(
                    messages=[
                        SYSTEM_PROMPT,
                        {"role": "user", "content": message.content}
                    ],
                    model="llama3-70b-8192",
                    temperature=0.8, # Độ sáng tạo/văng mạng cao
                )
                
                response = chat_completion.choices[0].message.content
                
                # Trả lời tin nhắn
                if len(response) > 2000: # Giới hạn của Discord
                    response = response[:1997] + "..."
                
                await message.reply(response)
                
            except Exception as e:
                print(f"Lỗi rồi cha nội: {e}")
                await message.channel.send("Não t đang lag tí, đừng có hối!")

# --- PHẦN 3: KÍCH HOẠT ---
if __name__ == "__main__":
    # Chạy Web Server trước
    keep_alive()
    
    # Lấy Token từ Environment Variables (Cài trong Koyeb/GitHub Secrets)
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ LỖI: Chưa có DISCORD_TOKEN trong cấu hình!")

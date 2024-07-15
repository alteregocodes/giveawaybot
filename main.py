from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
import config
import random

app = Client("bot", api_id=config.api_id, api_hash=config.api_hash, bot_token=config.bot_token)

participants = []

async def cek_langganan_channel(user_id):
    if user_id == config.admin_id:
        return True
    try:
        await app.get_chat_member(config.channel_id, user_id)
        await app.get_chat_member(config.channel_id2, user_id)
    except UserNotParticipant:
        return False
    return True

async def pesan_langganan(user_id, message_id):
    link_1 = await app.export_chat_invite_link(config.channel_id)
    link_2 = await app.export_chat_invite_link(config.channel_id2)
    markup = [
        [("Channel base", link_1), ("Group base", link_2)],
        [("Coba lagi", f'https://t.me/{(await app.get_me()).username}?start=start')]
    ]
    await app.send_message(user_id, config.pesan_join, reply_to_message_id=message_id, reply_markup=markup)

@app.on_message(filters.command("openga") & filters.user([config.owner_id, config.admin_id]))
async def open_giveaway(client, message):
    global participants
    participants = []
    await app.send_message(config.channel_id, config.announce_message_start)
    await message.reply("Giveaway dibuka! Daftarkan username Anda dengan perintah /ikutga {username}.")

@app.on_message(filters.command("ikutga") & filters.private)
async def join_giveaway(client, message):
    username = message.text.split(" ", 1)[1] if len(message.text.split(" ")) > 1 else None
    if username and await cek_langganan_channel(message.from_user.id):
        participants.append(username)
        await message.reply(f"Username {username} berhasil didaftarkan untuk giveaway!")
    elif username:
        await pesan_langganan(message.from_user.id, message.message_id)
    else:
        await message.reply("Silakan masukkan username Anda setelah perintah /ikutga")

@app.on_message(filters.command("closega") & filters.user([config.owner_id, config.admin_id]))
async def close_giveaway(client, message):
    if participants:
        winner = random.choice(participants)
        participants.clear()
        await app.send_message(config.channel_id, config.announce_message_winner.format(winner=winner))
        await message.reply(f"Giveaway ditutup! Pemenangnya adalah: {winner}")
    else:
        await message.reply("Tidak ada peserta yang terdaftar.")

app.run()

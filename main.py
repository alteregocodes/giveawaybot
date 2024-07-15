from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid, UserNotParticipant
from pyrogram.types import Message
import random
import os

from config import api_id, api_hash, bot_token, owner_id, admin_id, channel_id, channel_id2
from config import pesan_start, pesan_giveaway, pesan_join, pesan_menang

app = Client("giveaway_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

data_file = 'data.txt'

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(pesan_start)

@app.on_message(filters.command("openga"))
async def open_giveaway(client, message: Message):
    if message.from_user.id not in [int(owner_id), int(admin_id)]:
        return
    await message.reply_text(pesan_giveaway)
    if os.path.exists(data_file):
        os.remove(data_file)

@app.on_message(filters.command("ikutga"))
async def join_giveaway(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Gunakan format: /ikutga {username}")
        return

    username = message.command[1]

    try:
        user1 = await client.get_chat_member(channel_id, message.from_user.id)
        user2 = await client.get_chat_member(channel_id2, message.from_user.id)
    except UserNotParticipant:
        await message.reply_text(pesan_join.format(channel1=channel_id, channel2=channel_id2))
        return
    except PeerIdInvalid:
        await message.reply_text("Bot belum diundang ke channel atau channel ID salah.")
        return

    if user1.status not in ["member", "administrator", "creator"] or user2.status not in ["member", "administrator", "creator"]:
        await message.reply_text(pesan_join.format(channel1=channel_id, channel2=channel_id2))
        return

    with open(data_file, 'a') as f:
        f.write(username + '\n')
    await message.reply_text(f"{username} telah ditambahkan ke giveaway.")

@app.on_message(filters.command("closega"))
async def close_giveaway(client, message: Message):
    if message.from_user.id not in [int(owner_id), int(admin_id)]:
        return

    if not os.path.exists(data_file):
        await message.reply_text("Tidak ada peserta untuk giveaway.")
        return

    with open(data_file, 'r') as f:
        participants = f.readlines()

    if not participants:
        await message.reply_text("Tidak ada peserta untuk giveaway.")
        return

    winner = random.choice(participants).strip()
    await message.reply_text(pesan_menang.format(username=winner))
    os.remove(data_file)

if __name__ == "__main__":
    app.run()

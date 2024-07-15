import logging
from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant, PeerIdInvalid
import config
import random

# Setup logging
logging.basicConfig(level=logging.INFO)

app = Client("bot", api_id=config.api_id, api_hash=config.api_hash, bot_token=config.bot_token)

participants = []

async def cek_langganan_channel(user_id):
    if user_id == config.owner_id or user_id == config.admin_id:
        return True
    try:
        await app.get_chat_member(config.channel_id, user_id)
        await app.get_chat_member(config.channel_id2, user_id)
    except UserNotParticipant:
        return False
    except PeerIdInvalid:
        logging.error("Invalid Peer ID for channel. Check if the bot is added to the channel and the channel ID is correct.")
        raise
    return True

async def pesan_langganan(user_id, message_id):
    try:
        link_1 = await app.export_chat_invite_link(config.channel_id)
        link_2 = await app.export_chat_invite_link(config.channel_id2)
        markup = [
            [("Channel base", link_1), ("Group base", link_2)],
            [("Coba lagi", f'https://t.me/{(await app.get_me()).username}?start=start')]
        ]
        await app.send_message(user_id, config.pesan_join, reply_to_message_id=message_id, reply_markup=markup)
    except Exception as e:
        logging.error(f"Error sending subscription message: {e}")

@app.on_message(filters.command("start"))
async def start(client, message):
    logging.info(f"Received /start command from user {message.from_user.id}")
    await message.reply("Selamat datang! Gunakan /openga untuk memulai giveaway.")

@app.on_message(filters.command("openga") & filters.user([config.owner_id, config.admin_id]))
async def open_giveaway(client, message):
    global participants
    participants = []
    logging.info(f"Received /openga command from user {message.from_user.id}")

    try:
        # Log the channel IDs being used
        logging.info(f"Sending giveaway start message to channels {config.channel_id} and {config.channel_id2}")

        await app.send_message(config.channel_id, config.announce_message_start)
        await app.send_message(config.channel_id2, config.announce_message_start)
        await message.reply("Giveaway dibuka! Daftarkan username Anda dengan perintah /ikutga {username}.")
    except Exception as e:
        logging.error(f"Error sending giveaway start announcement: {e}")
        await message.reply(f"Terjadi kesalahan saat memulai giveaway: {e}")

@app.on_message(filters.command("ikutga") & filters.private)
async def join_giveaway(client, message):
    if len(message.text.split()) > 1:
        username = message.text.split(" ", 1)[1]
        try:
            if await cek_langganan_channel(message.from_user.id):
                participants.append(username)
                logging.info(f"User {message.from_user.id} registered username {username} for the giveaway")
                await message.reply(f"Username {username} berhasil didaftarkan untuk giveaway!")
            else:
                await pesan_langganan(message.from_user.id, message.message_id)
        except PeerIdInvalid:
            await message.reply("Terjadi kesalahan pada ID channel. Pastikan bot Anda bergabung dengan channel yang benar.")
    else:
        await message.reply("Silakan masukkan username Anda setelah perintah /ikutga")

@app.on_message(filters.command("closega") & filters.user([config.owner_id, config.admin_id]))
async def close_giveaway(client, message):
    if participants:
        winner = random.choice(participants)
        participants.clear()
        logging.info(f"Received /closega command from user {message.from_user.id}, winner: {winner}")

        try:
            await app.send_message(config.channel_id, config.announce_message_winner.format(winner=winner))
            await app.send_message(config.channel_id2, config.announce_message_winner.format(winner=winner))
            await message.reply(f"Giveaway ditutup! Pemenangnya adalah: {winner}")
        except Exception as e:
            logging.error(f"Error sending giveaway winner announcement: {e}")
            await message.reply(f"Terjadi kesalahan saat menutup giveaway: {e}")
    else:
        await message.reply("Tidak ada peserta yang terdaftar.")

app.run()

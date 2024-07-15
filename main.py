import logging
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipant
from telethon.tl.types import ChannelParticipantsAdmins, UserStatusOnline
from telethon.errors.rpcerrorlist import UserNotParticipantError
import config

logging.basicConfig(level=logging.INFO)
bot = TelegramClient('bot', config.api_id, config.api_hash).start(bot_token=config.bot_token)

participants = []

async def cek_langganan_channel(user_id):
    if user_id == config.admin_id:
        return True
    try:
        member = await bot(GetParticipant(channel=config.channel_id, user_id=user_id))
    except UserNotParticipantError:
        return False
    try:
        member2 = await bot(GetParticipant(channel=config.channel_id2, user_id=user_id))
    except UserNotParticipantError:
        return False

    status = [UserStatusOnline(), ChannelParticipantsAdmins()]
    return member.status in status and member2.status in status

async def pesan_langganan(user_id, message_id):
    link_1 = await bot.export_chat_invite_link(config.channel_id)
    link_2 = await bot.export_chat_invite_link(config.channel_id2)
    markup = [
        [Button.url('Channel base', url=link_1), Button.url('Group base', url=link_2)],
        [Button.url('Coba lagi', url=f'https://t.me/{(await bot.get_me()).username}?start=start')]
    ]
    await bot.send_message(user_id, config.pesan_join, buttons=markup, reply_to=message_id)

@bot.on(events.NewMessage(pattern='/openga'))
async def open_giveaway(event):
    if event.sender_id in (config.owner_id, config.admin_id):
        global participants
        participants = []
        # Kirim pengumuman ke channel
        await bot.send_message(config.channel_id, config.announce_message_start)
        await event.respond("Giveaway dibuka! Daftarkan username Anda dengan perintah /ikutga {username}.")
    else:
        await event.respond("Anda tidak memiliki izin untuk membuka giveaway.")

@bot.on(events.NewMessage(pattern='/ikutga (.+)'))
async def join_giveaway(event):
    username = event.pattern_match.group(1)
    if await cek_langganan_channel(event.sender_id):
        participants.append(username)
        await event.respond(f"Username {username} berhasil didaftarkan untuk giveaway!")
    else:
        await pesan_langganan(event.sender_id, event.message.id)

@bot.on(events.NewMessage(pattern='/closega'))
async def close_giveaway(event):
    if event.sender_id in (config.owner_id, config.admin_id):
        if participants:
            import random
            winner = random.choice(participants)
            participants.clear()
            # Kirim pengumuman pemenang ke channel
            await bot.send_message(config.channel_id, config.announce_message_winner.format(winner=winner))
            await event.respond(f"Giveaway ditutup! Pemenangnya adalah: {winner}")
        else:
            await event.respond("Tidak ada peserta yang terdaftar.")
    else:
        await event.respond("Anda tidak memiliki izin untuk menutup giveaway.")

bot.run_until_disconnected()

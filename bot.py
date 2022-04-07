#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import bs4
import vk
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
from asyncio import sleep
from contextlib import suppress
from random import choice, randint

from aiofiles import open
from aiofiles.os import mkdir, remove
from markovify import NewlineText
from vkbottle import VKAPIError
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules.base import ChatActionRule, FromUserRule
from datetime import timedelta
from tracemoe import ATraceMoe
from config import BOT_TOKEN, RESPONSE_CHANCE, RESPONSE_DELAY
from config_private import RESPONSE_DELAY_PRIVATE, RESPONSE_CHANCE_PRIVATE
from vk_api import VkApi
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id
import requests
from io import BytesIO
servicetokens = ["39a5321539a5321539a532150539df1dad339a539a53215583ee25a4b27b1fd80b0cd43"]
bot = Bot(BOT_TOKEN)
tag_pattern = re.compile(r"\[(id\d+?)\|.+?]")
empty_line_pattern = re.compile(r"^\s+", flags=re.M)
@bot.on.chat_message(ChatActionRule("chat_invite_user"))
async def invited(message: Message) -> None:
    action = message.action
    group_id = message.group_id
    if not action or not group_id:
        return
    if action.member_id == -group_id:
        await message.answer(
            """привет я тупой скоро увидите
Для работы мне нужно выдать доступ к переписке или права администратора.
by htmlrulit"""
        )
@bot.on.private_message(text="test2")
async def hi_handler(message: Message):
    await message.answer("Ого, я отвечаю в ЛС")
@bot.on.chat_message(text=["/сброс", "/reset"])
async def reset(message: Message) -> None:
    peer_id = message.peer_id
    try:
        members = await message.ctx_api.messages.get_conversation_members(peer_id=peer_id)
    except VKAPIError[917]:
        await message.answer("Не удалось проверить, являетесь ли вы администратором, " + "потому что я не администратор.")
        return
    admins = [member.member_id for member in members.items if member.is_admin]
    from_id = message.from_id
    if from_id in admins:
        with suppress(FileNotFoundError):
            await remove(f"db/{peer_id}.txt")
        await message.answer(f"@id{from_id}, база данных успешно сброшена.")
    else:
        await message.answer("Сбрасывать базу данных могут только администраторы.")
@bot.on.chat_message(text=["чепопало", "Чепопало"])
async def reset(message: Message) -> None:
    peer_id = message.peer_id
    try:
        members = await message.ctx_api.messages.get_conversation_members(peer_id=peer_id)
    except VKAPIError[917]:
        await message.answer("ошибка")
        return
    from_id = message.from_id
    if ((message.from_id)>1):
        await message.answer("на месте")
    else:
        await message.answer("ты не админ")
@bot.on.chat_message(FromUserRule())
async def talk(message: Message) -> None:
    peer_id = message.peer_id
    text = message.text.lower()
    if text:
        text = tag_pattern.sub(r"@\1", empty_line_pattern.sub("", text))
        with suppress(FileExistsError):
            await mkdir("db")
        async with open(f"db/{peer_id}.txt", "a") as f:
            await f.write(f"\n{text}")
    if randint(1, 100) > RESPONSE_CHANCE:
        return
    await sleep(RESPONSE_DELAY)
    async with open(f"db/{peer_id}.txt") as f:
        db = await f.read()
    db = db.strip().lower()
    text_model = NewlineText(input_text=db, well_formed=False, state_size=1)
    sentence = text_model.make_sentence(tries=1000) or choice(db.splitlines())
    await message.answer(sentence)
@bot.on.private_message(FromUserRule())
async def talk(message: Message) -> None:
    peer_id = message.peer_id
    text = message.text.lower()
    if text:
        text = tag_pattern.sub(r"@\1", empty_line_pattern.sub("", text))
        with suppress(FileExistsError):
            await mkdir("private")
        async with open(f"private/{peer_id}.txt", "a") as f:
            await f.write(f"\n{text}")
    if randint(1, 100) > RESPONSE_CHANCE_PRIVATE:
        return
    await sleep(RESPONSE_DELAY_PRIVATE)
    async with open(f"private/{peer_id}.txt") as f:
        db = await f.read()
    db = db.strip().lower()
    text_model = NewlineText(input_text=db, well_formed=False, state_size=1)
    sentence = text_model.make_sentence(tries=1000) or choice(db.splitlines())
    await message.answer(sentence)
if __name__ == "__main__":
    bot.run_forever()

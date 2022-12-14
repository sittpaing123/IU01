# Kanged From @TroJanZheX
import asyncio
import re
import ast
import random
import math
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE, PICS, PICS2
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from database.gfilters_mdb import find_gfilter, get_gfilters
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings
from database.users_chats_db import db
from plugins.helper.admin_check import admin_fliter
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import (
    find_gfilter,
    get_gfilters,
    del_allg
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}
PM_BUTTONS = {}
PM_SPELL_CHECK = {}
FILTER_MODE = {}
G_MODE = {}


@Client.on_message(filters.command('g_filter') & filters.group & admin_fliter)
async def g_fil_mod(client, message): 
      mode_on = ["yes", "on", "true"]
      mode_of = ["no", "off", "false"]

      try: 
         args = message.text.split(None, 1)[1].lower() 
      except: 
         return await message.reply("**πΈπ½π²πΎπΌπΏπ»π΄ππ΄ π²πΎπΌπΌπ°π½π³...**")
      
      m = await message.reply("**ππ΄πππΈπ½πΆ.../**")

      if args in mode_on:
          G_MODE[str(message.chat.id)] = "True" 
          await m.edit("**πΆπ»πΎπ±π°π» π΄π½π°π±π»π΄π³**")
      
      elif args in mode_of:
          G_MODE[str(message.chat.id)] = "False"
          await m.edit("**πΆπ»πΎπ±π°π» π³πΈππ°π±π»π΄π³**")
      else:
          await m.edit("πππ΄ :- /g_filter on πΎπ /g_filter off")


@Client.on_message(filters.group & filters.text)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    if k == False:
        key = f"{message.from_user.id}_{message.chat.id}"
        if message.text.startswith("/"):
            return 
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            files, offset, total_results = await get_search_results(message.text.lower(), offset=0, max_results=5, filter=True)
            if not files:
                settings = await get_settings(message.chat.id)
                if settings["spell_check"]:
                    return await advantage_spell_chok(message)
                else:
                    return
            else:
                await message.reply_photo(photo=random.choice(PICS),
                    caption=f"π°ααα±α¬α·αα­ααΊαΈ, π¬αα«αΈαααΊαα­ααΊαΈ, β οΈαα¬αα?αα­α―, β½οΈαα±α¬αα―αΆαΈ, β£οΈααΎααΊαΈαα­α―αΈαα?αΈ, π―αα±αΈαα±α¬ααΊαα»ααΊααΎαα·αΊ α‘ααΌα¬αΈαα­ααΊαΈαα±α«ααΊαΈαα»α¬αΈαα½α¬αα­α― Lotus999 ααΎα¬αα­ααΊαααΊαααΎα­αα±α¬α·αα­α―ααΊαα«ααΌα?αα°ααΌα?αΈαααΊαΈαα­α―αααΊαα»α¬αΈ ππ\nViber : 09763354949\nTelegram : @lotus999game"
                    f"\n\nπ Query : {message.text}"
                    f"\nπ? Total Results : `{total_results}` - Series is Ready**π"
                    f"\nππΌ Request by : {message.from_user.mention}\n\n</b><a href='https://t.me/MKSVIPLINK'>Β© MKS Channel</a>",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("π₯  πππ¦πππππ  π₯", url=f'https://t.me/{temp.U_NAME}?start=pquery_{key}')]]
                    ))
                temp.QUERY_HANDLER[key] = {
                    'query':message.text,
                    "offset": offset,
                    "files": files,
                    "total_results": total_results}
        else:
            return 

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query: CallbackQuery):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("oKda", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("Search Expired\nPlease send movie name again.\n\nααΎα¬αα½α±ααΎα― αααΊαααΊαΈαα―ααΊαα½α¬αΈαα«ααΌα?α\nαα»α±αΈαα°αΈααΌα―α αα―ααΊααΎααΊα‘αααΊαα­α― \nGroup αα²βαα½ααΊ αααΊααΆαα±αΈαα­α―α·αα«α\n\n**@MKSVIPLINK\n@MKS_REQUESTGROUP** ", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, max_results=5, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'

    out =f"π°ααα±α¬α·αα­ααΊαΈ, π¬αα«αΈαααΊαα­ααΊαΈ, β οΈαα¬αα?αα­α―, β½οΈαα±α¬αα―αΆαΈ, β£οΈααΎααΊαΈαα­α―αΈαα?αΈ, π―αα±αΈαα±α¬ααΊαα»ααΊααΎαα·αΊ α‘ααΌα¬αΈαα­ααΊαΈαα±α«ααΊαΈαα»α¬αΈαα½α¬αα­α― Lotus999 ααΎα¬αα­ααΊαααΊαααΎα­αα±α¬α·αα­α―ααΊαα«ααΌα?αα°ααΌα?αΈαααΊαΈαα­α―αααΊαα»α¬αΈ ππ\nViber : 09763354949\nTelegram : @lotus999game\n\nHey {query.from_user.mention}\n\nαα­ααΊαα½α±ααΎα¬αα¬ **{search}** αα­α― αααΊαααΊααΎα¬αα½α±αα¬ααΌαα±αΈαα¬αΈαα«αααΊα αα¬ααΊαα¬αΈαα¬αααΊαα±αΈαα­α― ααΎα­ααΊαα­α―ααΊαα«α start αα±αΈααΌααΊαα±α«αΊαα¬αα¬αα­α― αααΊααΎα­ααΊαααΊ Bot α Auto αα­α―α·αα±αΈαα«αααΊαα±α¬αΊα \n\n"
    k = 1
    for file in files:
        out += f"{k}. [{file.file_name} [{get_size(file.file_size)}]](https://t.me/{temp.U_NAME}?start={pre}_{file.file_id})\n\n"
        k += 1
    btn = []

    if 0 < offset < 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("βͺ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"π Pages {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}",
                                  callback_data="pages")]
        )
        btn.append(
            [InlineKeyboardButton("β­οΈ Click here to Donate to the my channel.β­οΈ", url="https://t.me/kpmovielist/277")]
        )
        btn.append(        
            [InlineKeyboardButton("ππ» πππ πππ«π’ππ¬ πππ¦πππ« αααΊαααΊ ππ»", url="https://t.me/Kpautoreply_bot")]                          
        )       
        btn.append(
            [InlineKeyboardButton("β­οΈ All Channel & Group Link β­οΈ", url="https://t.me/Movie_Zone_KP/3")] 
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"π {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}", callback_data="pages"),
             InlineKeyboardButton("NEXT β©", callback_data=f"next_{req}_{key}_{n_offset}")])
        btn.append(
            [InlineKeyboardButton("β­οΈ Click here to Donate to the my channel.β­οΈ", url="https://t.me/kpmovielist/277")]
        )
        btn.append(        
            [InlineKeyboardButton("ππ» πππ πππ«π’ππ¬ πππ¦πππ« αααΊαααΊ ππ»", url="https://t.me/Kpautoreply_bot")]                          
        )       
        btn.append(
            [InlineKeyboardButton("β­οΈ All Channel & Group Link β­οΈ", url="https://t.me/Movie_Zone_KP/3")] 
        )
    else:
        btn.append(
            [
                InlineKeyboardButton("βͺ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"π {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}", callback_data="pages"),
                InlineKeyboardButton("NEXT β©", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
        btn.append(
            [InlineKeyboardButton("β­οΈ Click here to Donate to the my channel.β­οΈ", url="https://t.me/kpmovielist/277")]
        )
        btn.append(        
            [InlineKeyboardButton("ππ» πππ πππ«π’ππ¬ πππ¦πππ« αααΊαααΊ ππ»", url="https://t.me/Kpautoreply_bot")]                          
        )       
        btn.append(
            [InlineKeyboardButton("β­οΈ All Channel & Group Link β­οΈ", url="https://t.me/Movie_Zone_KP/3")] 
        )
    try:
        await query.edit_message_caption(
            out, 
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()



@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("okDa", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.message_id)
    if not movies:
        return await query.answer("You are clicking on an old button which is expired.", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking for Movie in database...')
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, max_results=5, filter=True)
        if files:
            key = f"{query.message.message_id}_{query.message.chat.id}"
            await query.message(
                f"Query: {movie}"
                f"\nTotal Files : `{total_results}`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("π₯  πππ¦πππππ  π₯", url=f'https://t.me/{temp.U_NAME}?start=pquery_{key}')]]
                ))
            temp.QUERY_HANDLER[key] = {
                'query':movie,
                "offset": offset,
                "files": files,
                "total_results": total_results}
        else:
            k = await query.message.edit('This Movie Not Found In DataBase')
            await asyncio.sleep(10)
            await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == "private":
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer('Piracy Is Crime')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer('Piracy Is Crime')

        elif chat_type in ["group", "supergroup"]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer('Piracy Is Crime')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == "creator") or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == "private":
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in ["group", "supergroup"]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == "creator") or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("That's not for you!!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode="md"
        )
        return await query.answer('Piracy Is Crime')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode="md"
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode="md")
        return await query.answer('Piracy Is Crime')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode="md"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode="md"
            )
        return await query.answer('Piracy Is Crime')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode="md"
            )
        return await query.answer('Piracy Is Crime')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('Piracy Is Crime')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False 
                )
                await query.answer('Check PM, I have sent files in pm', show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock the bot mahn !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("I Like Your Smartness, But Don't Be Oversmart π", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        if ident == "checksubkey":
            query.message.from_user = query.from_user
            await auto_filter(client, query.message, f'pquery_{file_id}')
            await query.message.delete()
            return 
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('β»οΈ JOIN OUR GROUP TO USE ME β»οΈ', url='https://t.me/MKS_REQUESTGROUP')
        ], [
            InlineKeyboardButton('βοΈVIP SERIES ', url='https://t.me/Kpautoreply_bot'),
            InlineKeyboardButton('π· Channel', url='https://t.me/MKSVIPLINK')
        ], [
            InlineKeyboardButton('βΉοΈ Features', callback_data='help'),
            InlineKeyboardButton('π¨π»βπ»DEVS', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer('Piracy Is Crime')
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('Manual Filter', callback_data='manuelfilter'),
            InlineKeyboardButton('Auto Filter', callback_data='autofilter')
        ], [
            InlineKeyboardButton('Connection', callback_data='coct'),
            InlineKeyboardButton('Extra Mods', callback_data='extra')
        ], [
            InlineKeyboardButton('π  Home', callback_data='start'),
            InlineKeyboardButton('π? Status', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('π· Channel', url='https://t.me/MKSVIPLINK'),
            InlineKeyboardButton('β₯οΈ Source', callback_data='source')
        ], [
            InlineKeyboardButton('π  Home', callback_data='start'),
            InlineKeyboardButton('π Close', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('π©βπ¦― Back', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('π©βπ¦― Back', callback_data='help'),
            InlineKeyboardButton('βΉοΈ Buttons', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('π©βπ¦― Back', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('π©βπ¦― Back', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('π©βπ¦― Back', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('π©βπ¦― Back', callback_data='help'),
            InlineKeyboardButton('π?ββοΈ Admin', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('π©βπ¦― Back', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('π©βπ¦― Back', callback_data='help'),
            InlineKeyboardButton('β»οΈ', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('π©βπ¦― Back', callback_data='help'),
            InlineKeyboardButton('β»οΈ', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer('Piracy Is Crime')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('β Yes' if settings["botpm"] else 'β No',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('β Yes' if settings["file_secure"] else 'β No',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('β Yes' if settings["imdb"] else 'β No',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('β Yes' if settings["spell_check"] else 'β No',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('β Yes' if settings["welcome"] else 'β No',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer('Piracy Is Crime')


async def auto_filter(client, msg, q_id: str):
    #key = f"{message.message_id}:{message.chat.id}"
    group_id = int(q_id.split("_")[2])
    q_id = q_id.lstrip('pquery_')
    data = temp.QUERY_HANDLER.get(q_id)
    if not data:
        return await msg.reply('Search Expired\nPlease send movie name again.\n\nααΎα¬αα½α±ααΎα― αααΊαααΊαΈαα―ααΊαα½α¬αΈαα«ααΌα?α\nαα»α±αΈαα°αΈααΌα―α αα―ααΊααΎααΊα‘αααΊαα­α― \nGroup αα²βαα½ααΊ αααΊααΆαα±αΈαα­α―α·αα«α\n\n**@MKSVIPLINK\n@MKS_REQUESTGROUP** "')
    query_text = data['query']
    msg_ = await msg.reply("Please wait...")

    settings = await get_settings(group_id)

    search = query_text
    files, offset, total_results = data['files'], data['offset'], data['total_results']
    
    pre = 'filep' if settings['file_secure'] else 'file'

    out = f"π°ααα±α¬α·αα­ααΊαΈ, π¬αα«αΈαααΊαα­ααΊαΈ, β οΈαα¬αα?αα­α―, β½οΈαα±α¬αα―αΆαΈ, β£οΈααΎααΊαΈαα­α―αΈαα?αΈ, π―αα±αΈαα±α¬ααΊαα»ααΊααΎαα·αΊ α‘ααΌα¬αΈαα­ααΊαΈαα±α«ααΊαΈαα»α¬αΈαα½α¬αα­α― Lotus999 ααΎα¬αα­ααΊαααΊαααΎα­αα±α¬α·αα­α―ααΊαα«ααΌα?αα°ααΌα?αΈαααΊαΈαα­α―αααΊαα»α¬αΈ ππ\nViber : 09763354949\nTelegram : @lotus999game\n\nHey {msg.from_user.mention}\n\nαα­ααΊαα½α±ααΎα¬αα¬ **{search}** αα­α― αααΊαααΊααΎα¬αα½α±αα¬ααΌαα±αΈαα¬αΈαα«αααΊα αα¬ααΊαα¬αΈαα¬αααΊαα±αΈαα­α― ααΎα­ααΊαα­α―ααΊαα«α start αα±αΈααΌααΊαα±α«αΊαα¬αα¬αα­α― αααΊααΎα­ααΊαααΊ Bot α Auto αα­α―α·αα±αΈαα«αααΊαα±α¬αΊα \n\n"
    k = 1
    for file in files:
        out += f"{k}. [{file.file_name} [{get_size(file.file_size)}]](https://t.me/{temp.U_NAME}?start={pre}_{file.file_id})\n\n"
        k += 1
    btn = []
    if offset != "" and total_results > 10:
        key = f"{msg.chat.id}-{msg.from_user.id}"
        BUTTONS[key] = search
        req = msg.from_user.id if msg.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"π 1/{math.ceil(int(total_results) / 5)}", callback_data="pages"),
             InlineKeyboardButton(text="NEXT β©", callback_data=f"next_{req}_{key}_{offset}")]
        )               
        btn.append(
            [InlineKeyboardButton("β­οΈ Click here to Donate to the my channel.β­οΈ", url="https://t.me/kpmovielist/277")]
        )
        btn.append(        
            [InlineKeyboardButton("ππ» πππ πππ«π’ππ¬ πππ¦πππ« αααΊαααΊ ππ»", url="https://t.me/Kpautoreply_bot")]                          
        )       
        btn.append(
            [InlineKeyboardButton("β­οΈ All Channel & Group Link β­οΈ", url="https://t.me/Movie_Zone_KP/3")] 
        )
            
    else:
        btn.append(
            [InlineKeyboardButton(text="π 1/1", callback_data="pages")]
        )
        btn.append(
            [InlineKeyboardButton("β­οΈ Click here to Donate to the my channel.β­οΈ", url="https://t.me/kpmovielist/277")]
        )
        btn.append(        
            [InlineKeyboardButton("ππ» πππ πππ«π’ππ¬ πππ¦πππ« αααΊαααΊ ππ»", url="https://t.me/Kpautoreply_bot")]                          
        )       
        btn.append(
            [InlineKeyboardButton("β­οΈ All Channel & Group Link β­οΈ", url="https://t.me/Movie_Zone_KP/3")] 
        )
    await msg_.delete()
    await msg.reply_photo(
        photo=random.choice(PICS),
        caption=out,
        reply_markup=InlineKeyboardMarkup(btn),
    )
    


async def advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        k = await msg.reply("I couldn't find any movie in that name.")
        await asyncio.sleep(8)
        await k.delete()
        return
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(mov.strip(), bulk=True)  # searching each keyword in imdb
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
        k = await msg.reply("I couldn't find anything related to that. Check your spelling")
        await asyncio.sleep(8)
        await k.delete()
        return
    SPELL_CHECK[msg.message_id] = movielist
    btn = [[
        InlineKeyboardButton(
            text=movie.strip(),
            callback_data=f"spolling#{user}#{k}",
        )
    ] for k, movie in enumerate(movielist)]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    await msg.reply("I couldn't find anything related to that\nDid you mean any one of these?",
                    reply_markup=InlineKeyboardMarkup(btn))


async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")  
            
    
            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":                                   
                            await message.reply_photo(photo=random.choice(PICS), 
                            caption=f"π°ααα±α¬α·αα­ααΊαΈ, π¬αα«αΈαααΊαα­ααΊαΈ, β οΈαα¬αα?αα­α―, β½οΈαα±α¬αα―αΆαΈ, β£οΈααΎααΊαΈαα­α―αΈαα?αΈ, π―αα±αΈαα±α¬ααΊαα»ααΊααΎαα·αΊ α‘ααΌα¬αΈαα­ααΊαΈαα±α«ααΊαΈαα»α¬αΈαα½α¬αα­α― Lotus999 ααΎα¬αα­ααΊαααΊαααΎα­αα±α¬α·αα­α―ααΊαα«ααΌα?αα°ααΌα?αΈαααΊαΈαα­α―αααΊαα»α¬αΈ ππ\nViber : 09763354949\nTelegram : @lotus999game"
                            f"\n\nπ Query : {message.text}\nπ Request by :{message.from_user.mention}\nπ? Results : β¬οΈβ¬οΈβ¬οΈ\nπ· {reply_text}\n\n</b><a href='https://t.me/Movie_Zone_KP/3'>Β© MKS & KP Channel</a>",
                            reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton("β πͺπ³πππ² π―π¬πΉπ¬ π»π π±πΆπ°π΅ β", url=f'https://t.me/mksmainchannel')]]
                            )
                            )
                        else:
                            button = eval(btn)
                           
                            await message.reply_photo(photo=random.choice(PICS),
                                caption=f"π°ααα±α¬α·αα­ααΊαΈ, π¬αα«αΈαααΊαα­ααΊαΈ, β οΈαα¬αα?αα­α―, β½οΈαα±α¬αα―αΆαΈ, β£οΈααΎααΊαΈαα­α―αΈαα?αΈ, π―αα±αΈαα±α¬ααΊαα»ααΊααΎαα·αΊ α‘ααΌα¬αΈαα­ααΊαΈαα±α«ααΊαΈαα»α¬αΈαα½α¬αα­α― Lotus999 ααΎα¬αα­ααΊαααΊαααΎα­αα±α¬α·αα­α―ααΊαα«ααΌα?αα°ααΌα?αΈαααΊαΈαα­α―αααΊαα»α¬αΈ ππ\nViber : 09763354949\nTelegram : @lotus999game"
                                f"\n\nπ Query : {message.text} \nπ Request by :{message.from_user.mention}\nπ? Results : {reply_text}</b><a href='https://t.me/Movie_Zone_KP/3'>Β© MKS & KP Channel</a>",
                                reply_markup=InlineKeyboardMarkup(button)                            
                            )
                    else:
                        if btn == "[]":
                            await message.reply_cached_media(
                                fileid,
                                caption=f"π°ααα±α¬α·αα­ααΊαΈ, π¬αα«αΈαααΊαα­ααΊαΈ, β οΈαα¬αα?αα­α―, β½οΈαα±α¬αα―αΆαΈ, β£οΈααΎααΊαΈαα­α―αΈαα?αΈ, π―αα±αΈαα±α¬ααΊαα»ααΊααΎαα·αΊ α‘ααΌα¬αΈαα­ααΊαΈαα±α«ααΊαΈαα»α¬αΈαα½α¬αα­α― Lotus999 ααΎα¬αα­ααΊαααΊαααΎα­αα±α¬α·αα­α―ααΊαα«ααΌα?αα°ααΌα?αΈαααΊαΈαα­α―αααΊαα»α¬αΈ ππ\nViber : 09763354949\nTelegram : @lotus999game"
                                f"\n\nπ Query : {message.text}\nπ Request by :{message.from_user.mention}\nπ? Results : {reply_text}</b><a href='https://t.me/Movie_Zone_KP/3'>Β© MKS & KP Channel</a>" or "",
                                reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton("β πͺπ³πππ² π―π¬πΉπ¬ π»π π±πΆπ°π΅ β", url=f'https://t.me/mksmainchannel')]]
                            )
                            )
                        else:
                            button = eval(btn)
                            
                            await message.reply_cached_media(
                                fileid,
                                caption=f"π°ααα±α¬α·αα­ααΊαΈ, π¬αα«αΈαααΊαα­ααΊαΈ, β οΈαα¬αα?αα­α―, β½οΈαα±α¬αα―αΆαΈ, β£οΈααΎααΊαΈαα­α―αΈαα?αΈ, π―αα±αΈαα±α¬ααΊαα»ααΊααΎαα·αΊ α‘ααΌα¬αΈαα­ααΊαΈαα±α«ααΊαΈαα»α¬αΈαα½α¬αα­α― Lotus999 ααΎα¬αα­ααΊαααΊαααΎα­αα±α¬α·αα­α―ααΊαα«ααΌα?αα°ααΌα?αΈαααΊαΈαα­α―αααΊαα»α¬αΈ ππ\nViber : 09763354949\nTelegram : @lotus999game"
                                f"\n\nπ Query : {message.text}\nπ Request by :{message.from_user.mention}\nπ? Results : {reply_text}</b><a href='https://t.me/Movie_Zone_KP/3'>Β© MKS & KP Channel</a>" or "",
                                reply_markup=InlineKeyboardMarkup(button)
                            )
                except Exception as e:
                    print(e)
                    pass
                break 
            
            
    else:
        return False

                      
             
        

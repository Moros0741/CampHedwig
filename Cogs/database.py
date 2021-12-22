import sqlite3
import discord
from discord.ext import commands
import datetime

"""
DROP DATASET MAKEUP

0. Guild ID: int
1. Channel ID: int
2. Duration: int
3. Last Drop: Datetime OBJ
4. Active: True/False
"""

async def TimeNow():
    now = datetime.datetime.utcnow().strftime("%m %d, %Y %H:%M:%S")
    return now

async def set_drop_channel(guild, channel):
    r = await fetch_drop(guild)
    db = sqlite3.connect('drops.sqlite') 
    c = db.cursor()
    if r is None:
        time = await TimeNow()
        c.execute("INSERT INTO drops_config(guild_id, channel, last_drop) VALUES(?,?,?)",(guild, channel, time,))
    
    elif r is not None:
        c.execute("UPDATE drops_config SET channel = ? WHERE guild_id = ?", (channel, guild,))
    
    db.commit()
    c.close()
    db.close()

async def set_user(guild, user, count):
    db = sqlite3.connect('drops.sqlite')
    c = db.cursor()
    c.execute("INSERT INTO users(guild_id, user_id, count, active) VALUES(?,?,?,?)", (guild, user, count, 'True',))
    db.commit()
    c.close()
    db.close()

async def update_count(guild, user):
    r = await fetch_user(guild, user)
    if r is None:
        await set_user(guild, user, 1)
    else:
        db = sqlite3.connect('drops.sqlite')
        c = db.cursor()
        c.execute("UPDATE users SET count = ? WHERE guild_id = ? and user_id = ?", (int(r[2]) + 1, guild, user,))
        db.commit()
        c.close()
        db.close() 

async def fetch_user(guild, user):
    db = sqlite3.connect('drops.sqlite')
    c = db.cursor()
    result = c.execute("SELECT * FROM users WHERE guild_id = ? and user_id = ?", (guild, user,)).fetchone()
    c.close()
    db.close()
    return result

async def fetch_all(guild):
    db = sqlite3.connect('drops.sqlite')
    cursor = db.cursor()
    results = cursor.execute("SELECT user_id, count FROM users WHERE guild_id = ? and active = ? ORDER BY count DESC", (guild, 'True',)).fetchall()
    cursor.close()
    db.close()
    return results

async def add_prefix(guild, prefix):
    r = await fetch_prefix(guild)
    db = sqlite3.connect('main.sqlite')
    c = db.cursor()
    if r is None:
        c.execute("INSERT INTO config(guild_id, prefix) VALUES(?,?)", (guild, prefix,))
    
    else:
        c.execute("UPDATE config SET prefix = ? WHERE guild_id = ?", (prefix, guild,))
    
    db.commit()
    c.close()
    db.close()

async def fetch_prefix(guild):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    results = cursor.execute("SELECT prefix FROM config WHERE guild_id = ?", (guild,)).fetchone()
    cursor.close()
    db.close()
    return results

async def set_msg_time(guild, time):
    r = await fetch_drop(guild)
    db = sqlite3.connect('drops.sqlite')
    c = db.cursor()
    if r is None:
        timenow = await TimeNow
        c.execute("INSERT INTO drops_config(guild_id, duration, last_drop) VALUES(?,?,?)", (guild, time, timenow,))
    
    elif r is not None:
        c.execute("UPDATE drops_config SET duration = ? WHERE guild_id = ?", (time, guild,)) 

    db.commit()
    c.close()
    db.close() 

async def fetch_all_drops():
    db = sqlite3.connect('drops.sqlite')
    c = db.cursor()
    results = c.execute("SELECT * FROM drops_config").fetchall()
    c.close()
    db.close()
    return results

async def fetch_drop(guild):
    db = sqlite3.connect('drops.sqlite')
    c = db.cursor()
    result = c.execute("SELECT * FROM drops_config WHERE guild_id = ?", (guild,)).fetchone()
    c.close()
    db.close()
    return result

async def set_last_drop(guild):
    TimeNow = datetime.datetime.utcnow().strftime('%m %d, %Y %H:%M:%S')
    db = sqlite3.connect('drops.sqlite')
    c = db.cursor()
    c.execute("UPDATE drops_config SET last_drop = ? WHERE guild_id = ? ", (TimeNow, guild,))
    db.commit()
    c.close()
    db.close()

async def toggle_drop(guild, toggle):
    r = await fetch_drop(guild)
    db = sqlite3.connect('drops.sqlite')
    c = db.cursor()
    if r is not None:
        c.execute("UPDATE drops_config SET active = ? WHERE guild_id = ?", (toggle, guild,))
    
    else:
        time = await TimeNow()
        c.execute("INSERT INTO drops_config(guild_id, last_drop, active) VALUES(?,?,?)", (guild, time, toggle,))
    
    db.commit()
    c.close()
    db.close()
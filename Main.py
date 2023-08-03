from datetime import datetime
import os
import json
import discord
import MySQLdb
from discord.ui import InputText
from discord.ui import Modal

CONFIG_FLAG=False

__CONFIG_PATH__="config.json"
if(os.path.isfile(__CONFIG_PATH__)):
    with open(__CONFIG_PATH__) as f:
        config=json.load(f)
    CONFIG_FLAG=True
else:
    print("Configfile is not exist.\nSo stop ruuning.")
    os.close()

try:
    DISCORD_BOT_TOKEN=config["TOKEN"]
except KeyError:
    print("TOKEN is not given.\nSo stop running.")
    os.close()

try:
    TABLES=config["mysql"]["tables"]
except KeyError:
    print("tables is not given.\nSo stop running.")
    os.close()


bot = discord.Bot()
intents = discord.Intents.default()
intents.message_content = True

def main():
    bot.run(DISCORD_BOT_TOKEN)
    pass

class SQL:
    def __init__(self,
                 db:str="mydb",
                 host:str="localhost",
                 user:str="root",
                 passwd:str="",
                 charset:str="utf8"):
        if (CONFIG_FLAG):
            database_config=config["mysql"]
            self._host=database_config["host"]
            self._user=database_config["user"]
            self._passwd=database_config["passwd"]
            self._db=database_config["db"]
            self._charset=database_config["charset"]
        else:
            self._host=host
            self._user=user
            self._passwd=passwd
            self._db=db
            self._charset=charset

    def get_params(self,displaypass=False):
        if(displaypass):
            return  {
                        "host":self._host,
                        "user":self._user,
                        "passwd":self._passwd,
                        "db":self._db,
                        "charset":self._charset
                    }
        else:
            return  {
                        "host":self._host,
                        "user":self._user,
                        "passwd":"*******",
                        "db":self._db,
                        "charset":self._charset
                    }

    def _connectDB(self):
        connect = MySQLdb.connect(
            host=self._host,
            user=self._user,
            passwd=self._passwd,
            db=self._db,
            charset=self._charset
        )
        cursor = connect.cursor()
        return connect,cursor

    def get_col(self,table_name:str):
        connect,cursor=self._connectDB()
        sql=f"DESC {table_name}"
        cursor.execute(sql)
        rows=cursor.fetchall()
        cols=[]
        for i in rows:
            cols.append(i[0])
        return cols

    def insert(self,table_name:str,values:list,cols:list=None):

        if cols==None:
            cols=self.get_col(table_name)
            cols.remove("id")

        connect,cursor=self._connectDB()
        col=",".join(cols)
        value=",".join(values)
        sql=f"INSERT INTO {table_name} ({col}) VALUES({value})"
        print(sql)
        cursor.execute(sql)

        connect.commit()

        cursor.close()
        connect.close()

class SlashCommand:
    @bot.slash_command()
    async def submit(ctx=discord.ApplicationContext):

        steam = InputText(label='Steam ID', style=discord.InputTextStyle.short)
        riot = InputText(label='Riot ID', style=discord.InputTextStyle.short)

        modal=MyModal(steam,riot, title="first")
        await ctx.send_modal(modal)

class EventListen:
    @bot.event
    async def on_ready():
        print("hello")
        print(f"start up:{datetime.now().replace(microsecond=0)}")

class MyModal(Modal):

    async def callback(self,interaction:discord.Interaction):
        _values=[]
        author=str(interaction.user.id)
        _values.append(f"\"{author}\"")
        for i in self._children:
            _values.append(f"\"{i.value}\"")
        now=str(datetime.now().replace(microsecond=0))
        _values.append(f"\"{now}\"")
        print(_values)
        useDB=SQL(db="Discord")
        useDB.insert(table_name=TABLES[0],values=_values)

        await interaction.response.send_message("受け付けました")

if __name__=="__main__":
    main()
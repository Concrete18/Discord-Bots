from discord.ext import commands
from functions import *
import discord as ds
import os

class Admin(commands.Cog):


    def __init__(self, bot):
        self.bot = bot
        self.client = ds.Client()
        self.bot_func = bot_functions()


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            info = f'{ctx.author.mention} is missing the required permission for the {ctx.command} command.'
            await ctx.send(info)
            self.bot_func.logger.info(info)
        elif isinstance(error, commands.MissingAnyRole):
            info = f'{ctx.author.mention} is missing the required role for the {ctx.command} command.'
            await ctx.send(info)
            self.bot_func.logger.info(info)
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send('Command does not exist.')
        else:
            info = f'Command: {ctx.command} | Error: {str(error)}'
            print(info)
            self.bot_func.logger.info(info)
            raise(error)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        '''
        Give new members the "Member" role.
        Make sure the bot role is above the role you are wanting it to assign.
        '''
        msg = f'{member} joined the server'
        print(msg)
        self.bot_func.logger.info(msg)
        role = member.guild.get_role(377683900580888576)
        await member.add_roles(role, reason='New Member')


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        '''
        Logs members that left the server.
        '''
        msg = f'{member} left the server'
        print(msg)
        self.bot_func.logger.info(msg)
        # TODO remove user from message_data
        try:
            self.member_data.pop(str(member.id))
        except:
            print('self.member_data is not accesible.')


    @commands.command(
        name ='purge',
        brief='Deletes n messages from newest to oldest.',
        description='Deletes n number of messages from the current channel. This only works for this with the manage messages permission.')
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, num: int=5):
        '''
        Purges n number of messages.
        '''
        # TODO add support to delete all of a specific users messages
        await ctx.channel.purge(limit=int(num) + 1)


    @commands.command(
        name = 'speak',
        aliases=['say'],
        brief = 'Bot says what you type after the command.',
        hidden=True,
        pass_context = True)
    @commands.has_role('Owner')
    async def speak(self, ctx, *args):
        msg = ' '.join(args)
        await ctx.message.delete()
        return await ctx.send(msg)


    @commands.command(
        name = 'changeactivity',
        aliases=['changegame'],
        brief = 'Change the bot\'s current game with an admin command.',
        pass_context = True)
    @commands.has_role('Owner')
    async def changeactivity(self, ctx, *activity):
        '''
        Change Bot Activty.
        '''
        activity = ' '.join(activity)
        await self.bot.change_presence(activity=ds.Activity(type = ds.ActivityType.playing, name=activity))
        await ctx.message.delete()


    @commands.command(
        name ='pid',
        brief='Sends current bot PID.',
        description='Sends current bot PID.')
    async def pid(self, ctx):
        '''
        Sends current bot PID.
        '''
        await ctx.send(f'PID: {os.getpid()}')


    # WIP commands


    @commands.command(
        name ='getinactive',
        brief='Check members that would be purged for inactivity passed a specific total days.',
        description='Deletes n number of messages from the current channel. This only works for this with the manage messages permission.',
        hidden=True)
    @commands.has_any_role('Owner', 'Admin')
    async def getinactive(self, days: int):
        '''
        Check members that would be purged for inactivity passed a specific total days.
        '''
        await self.bot.estimate_pruned_members(days)
        print(await self.bot.estimate_pruned_members(days))


def setup(bot):
    bot.add_cog(Admin(bot))

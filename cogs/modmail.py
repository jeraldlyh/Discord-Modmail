import discord
import string
import re

from discord.ext import commands
from urllib.parse import urlparse

from cogs.utils.embed import passembed
from cogs.utils.embed import errorembed

class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup(self, ctx, *, modrole: discord.Role='Server Support'):
        '''Sets up a server for modmail'''
        if discord.utils.get(ctx.guild.categories, name='📋 Support'):
            return await ctx.send('Server has already been set up.')
        else:
            try:
              support = await ctx.guild.create_role(name='Server Support', color=discord.Color(0x72e4b2))
              overwrite = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    support: discord.PermissionOverwrite(read_messages=True)
                    }
              categ = await ctx.guild.create_category(name='📋 Support', overwrites=overwrite)
              #await categ.edit(position=0)
              c = await ctx.guild.create_text_channel(name='mail-logs', category=categ)
              await c.edit(topic='-block <userID> to block users.\n\n'
                                'Blocked\n-------\n\n')
              pembed = passembed(description='**Channels have been setup. Please do not tamper with any roles/channels created by {0}.**'.format(self.bot.user.name))
              return await ctx.send(embed=pembed)
            except:
              eembed = errorembed(description='**Do not have administrator permissions to setup the server.**')
              return await ctx.send(embed=eembed)    

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx):
        '''Close all threads and disable modmail.'''
        if ctx.message.channel.name != 'mail-logs':
            logs = discord.utils.get(ctx.message.guild.channels, name='mail-logs')
            eembed = errorembed(description='**{0} Commands can only be used in {1}**'.format(ctx.message.author.mention, logs.mention))
            return await ctx.send(embed=eembed)
        categ = discord.utils.get(ctx.guild.categories, name='📋 Support')
        if not categ:
            eembed = errorembed(description='**Server has not been setup.**')
            return await ctx.send(embed=eembed)  
        em = discord.Embed(title='Thread Closed')
        em.description = '**{0}** has closed this modmail session.'.format(ctx.author)
        em.color = discord.Color.red()
        for category, channels in ctx.guild.by_category():
            if category == categ:
                for chan in channels:
                    if 'User ID:' in str(chan.topic):
                        user_id = int(chan.topic.split(': ')[1])
                        user = self.get_user(user_id)
                        await user.send(embed=em)
                    await chan.delete()
        await categ.delete()
        pembed = passembed(description='**Disabled Modmail.**')
        await ctx.send(embed=pembed)


    @commands.command(name='close')
    @commands.has_any_role('Server Support')
    async def _close(self, ctx):
        '''Close the current thread.'''
        if 'User ID:' not in str(ctx.channel.topic):
            eembed = errorembed(description='This is not a modmail thread.')
            return await ctx.send(embed=eembed)
        user_id = int(ctx.channel.topic.split(': ')[1])
        user = self.bot.get_user(user_id)
        em = discord.Embed(title='Thread Closed')
        em.description = '**{0}** has closed this modmail session.'.format(ctx.author)
        em.color = discord.Color.red()
        try:
            logs = discord.utils.get(ctx.message.guild.channels, name='mail-logs')
            log_em = discord.Embed(title="{0}'s Thread Closed".format(user))
            log_em.color = discord.Color(0xffd700)
            log_em.description = '**{0}** has closed this modmail session.'.format(ctx.author)
            await logs.send(embed=log_em) 
            await user.send(embed=em)
        except Exception as e:
            print(e)
        await ctx.channel.delete()

    def format_info(self, message):
        '''Get information about a member of a server
        supports users from the guild or not.'''
        user = message.author
        server = discord.utils.get(self.bot.guilds, id=376595440734306306)
        member = server.get_member(user.id)
        avi = user.avatar_url
        desc = 'Modmail thread started.'
        color = 0

        if member:
            roles = sorted(member.roles, key=lambda c: c.position)
            rolenames = ', '.join([r.name for r in roles if r.name != "@everyone"]) or 'None'
            member_number = sorted(server.members, key=lambda m: m.joined_at).index(member) + 1
            for role in roles:
                if str(role.color) != "#000000":
                    color = role.color

        em = discord.Embed(colour=color, description=desc)
        em.set_footer(text='User ID: '+str(user.id))
        em.set_thumbnail(url=avi)
        em.set_author(name=user, icon_url=server.icon_url)
      

        if member:
            em.add_field(name='Member No.',value=str(member_number),inline = True)
            em.add_field(name='Nickname', value=member.nick, inline=True)
            em.add_field(name='Roles', value=rolenames, inline=True)

        return em

    async def send_mail(self, message, channel, mod):
        author = message.author
        fmt = discord.Embed()
        fmt.description = message.content
        fmt.timestamp = message.created_at
        urls = re.findall(r'(https?://[^\s]+)', message.content)

        types = ['.png', '.jpg', '.gif', '.jpeg', '.webp']

        for u in urls:
            if any(urlparse(u).path.endswith(x) for x in types):
                fmt.set_image(url=u)
                break

        if mod:
            fmt.color=discord.Color.green()
            fmt.set_author(name=str(author), icon_url=author.avatar_url)
            fmt.set_footer(text='Moderator')
        else:
            fmt.color=discord.Color.gold()
            fmt.set_author(name=str(author), icon_url=author.avatar_url)
            fmt.set_footer(text='User')

        embed = None

        if message.attachments:
            fmt.set_image(url=message.attachments[0].url)

        await channel.send(embed=fmt)

    async def process_reply(self, message):
        try:
            await message.delete()
        except discord.errors.NotFound:
            pass
        await self.send_mail(message, message.channel, mod=True)
        user_id = int(message.channel.topic.split(': ')[1])
        user = self.bot.get_user(user_id)
        await self.send_mail(message, user, mod=True)

    def format_name(self, author):
        name = author.name
        new_name = ''
        for letter in name:
            if letter in string.ascii_letters + string.digits:
                new_name += letter
        if not new_name:
            new_name = 'null'
        new_name += f'-{author.discriminator}'
        return new_name

    @property
    def blocked_em(self):
        em = discord.Embed(title='Message not processed!', color=discord.Color.red())
        em.description = 'You have been blocked from using modmail.'
        return em
    
    async def process_modmail(self, message):
        '''Processes messages sent to the bot.'''
        try:
            await message.add_reaction('✅')
        except:
            pass

        guild = discord.utils.get(self.bot.guilds, id=376595440734306306)
        author = message.author
        topic = f'User ID: {author.id}'
        channel = discord.utils.get(guild.text_channels, topic=topic)
        categ = discord.utils.get(guild.categories, name='📋 Support')
        top_chan = categ.channels[0] #bot-info
        blocked = top_chan.topic.split('Blocked\n-------')[1].strip().split('\n')
        blocked = [x.strip() for x in blocked]

        if str(message.author.id) in blocked:
            return await message.author.send(embed=self.blocked_em)

        em = discord.Embed(title='Thanks for the message!')
        em.description = 'The moderation team will get back to you as soon as possible!'
        em.color = discord.Color.green()

        if channel is not None:
            await self.send_mail(message, channel, mod=False)
        else:
            await message.author.send(embed=em)
            overwrite={
            guild.message.author: discord.PermissionOverwrite(read_messages=True)
            }
            channel = await guild.create_text_channel(
                name=self.format_name(author),
                overwrites=overwrite,
                category=categ
                )
            await channel.edit(topic=topic)
            support = discord.utils.get(guild.roles, name='Server Support')
            await channel.send('{0}'.format(support.mention), embed=self.format_info(message))
            await self.send_mail(message, channel, mod=False)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            await self.process_modmail(message)

    @commands.command()
    @commands.has_any_role('Server Support')
    async def reply(self, ctx, *, msg):
        '''Reply to users using this command.'''
        categ = discord.utils.get(ctx.guild.categories, id=ctx.channel.category_id)
        if categ is not None:
            if categ.name == '📋 Support':
                if 'User ID:' in ctx.channel.topic:
                    ctx.message.content = msg
                    await self.process_reply(ctx.message)


    @commands.command()
    @commands.has_any_role('Server Support')
    async def block(self, ctx, id=None):
        '''Block a user from using modmail.'''
        if id is None:
            if 'User ID:' in str(ctx.channel.topic):
                id = ctx.channel.topic.split('User ID: ')[1].strip()
            else:
                eembed = errorembed(description='**No UserID provided.**')
                return await ctx.send(embed=eembed)  

        categ = discord.utils.get(ctx.guild.categories, name='📋 Support')
        top_chan = categ.channels[0] #bot-info
        topic = str(top_chan.topic)
        topic += '\n' + id

        if id not in top_chan.topic:  
            await top_chan.edit(topic=topic)
            pembed = passembed(description='**User sucessfully blocked.**')
            await ctx.send(embed=pembed)
        else:
            eembed = errorembed(description='**User is already blocked.**')
            return await ctx.send(embed=eembed)  

    @commands.command()
    @commands.has_any_role('Server Support')
    async def unblock(self, ctx, id=None):
        '''Unblocks a user from using modmail.'''
        if id is None:
            if 'User ID:' in str(ctx.channel.topic):
                id = ctx.channel.topic.split('User ID: ')[1].strip()
            else:
                eembed = errorembed(description='**No UserID provided.**')
                return await ctx.send(embed=eembed)  

        categ = discord.utils.get(ctx.guild.categories, name='📋 Support')
        top_chan = categ.channels[0] #bot-info
        topic = str(top_chan.topic)
        topic = topic.replace('\n'+id, '')

        if id in top_chan.topic:
            await top_chan.edit(topic=topic)
            pembed = passembed(description='**User sucessfully unblocked.**')
            await ctx.send(embed=pembed)
        else:
            eembed = errorembed(description='**User is not already blocked.**')
            return await ctx.send(embed=eembed) 

    @commands.command()
    @commands.has_any_role('Server Support')
    async def help(self, ctx):
        if ctx.message.channel.name != 'mail-logs':
            logs = discord.utils.get(ctx.message.guild.channels, name='mail-logs')
            eembed = errorembed(description='**{0} Commands can only be used in {1}**'.format(ctx.message.author.mention, logs.mention))
            return await ctx.send(embed=eembed)
        else:    
            embed=discord.Embed(title="Available Commands", description='**-reply** - Replies a support ticket\n **-close** - Closes a support ticket', color=0xa53636)
            await ctx.send(embed=embed)
    
    
# Adding the cog to main script
def setup(bot):
    bot.add_cog(Modmail(bot))

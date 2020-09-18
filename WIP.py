
@client.command(pass_context = True)
async def group(ctx, *arg):
    """ *(WIP)* gathers everyone to channel "name_here" and plays "audio.mp3" """
    group_listen_channel = "Gathering Room"
    audio_file = 'audio.mp3'
    if ctx.message.author.server_permissions.move_members:
        server = ctx.message.server
        all_members = server.members
        channel = get_channel(server, group_listen_channel)
        voice = await client.join_voice_channel(channel)
        player = voice.create_ffmpeg_player(filename = audio_file)
        members_to_move = set()
        if (arg[0] == 'ALL'):
            for member1 in all_members:
                if(member1.voice_channel != None and not member1.is_afk):
                    await client.move_member(member1, channel)
        else:
            names = [name.lower() for name in arg]
            if names != []:
                for member in [m for m in all_members if m.voice]:
                    for name in names:
                        remove = False
                        if name in member.name.lower():
                            members_to_move.add(member)
                            remove = True
                        if member.nick != None and name in member.nick.lower():
                            members_to_move.add(member)
                            remove = True
                        if remove:
                            names.remove(name)
                for member in members_to_move:
                    await client.move_member(member, channel) #use asyncio.gather(*members_to_move) instead for concurrency?
        player.start()
        
#working fine, removed to develop new reaction-mass-move
async def on_reaction_add(reaction, user):
    # code to clear messages by emjois
    # note to JT: Available messages in bot's cache only persist until bot restart. Furthermore, if a message is sent while the bot is offline, the bot cannot access that message.
    
    if(user.server_permissions.manage_messages):
        channel = reaction.message.channel
        msg1 = reaction.message
        if(reaction.emoji == '🆑'):
            #await client.send_message(channel, user.name + " Set Marker at message '" + msg1.content + "' Please select second marker using " + '🔴')
            res = await client.wait_for_reaction(emoji = '🔴')
            msg2 = res.reaction.message
            if(msg1.timestamp < msg2.timestamp):
                first = msg2
                second = msg1
            else:
                first = msg1
                second = msg2
            dlist = [first]
            async for message in client.logs_from(channel, before=first):#after vs bfore switch #use client.purge_from instead
                #await client.delete_message(message)
                dlist.append(message)
                if(message.timestamp == second.timestamp):
                    #print("AT MSG 2: " + message.content)
                    break
            #await client.delete_message(first)
            await client.delete_messages(dlist)


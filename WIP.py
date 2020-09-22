#OUTDATED
async def on_reaction_add(reaction, user):
    # code to clear messages by emjois
    # note to JT: Available messages in bot's cache only persist until bot restart. Furthermore, if a message is sent while the bot is offline, the bot cannot access that message unless use history.
    
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


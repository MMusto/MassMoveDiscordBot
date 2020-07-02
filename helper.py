from client import client as client

######################################## HELPER FUNCTIONS ############################################
######################################## HELPER FUNCTIONS ############################################    
def error(msg):
    print("Error: " + msg)
    
def get_channel(server, chname : str) -> "Channel":
    '''Helper function that returns Channel object from name snippet'''
    for channel in server.channels:
        if(str(channel.type) == 'voice'):
                if(chname.lower() in channel.name.lower()):
                        return channel
    return None
    
async def mbr_helper(server, role : str, ch1, ch2) -> "None":
    '''Based off mbr. Integrated for use in .mcc'''
    got_role = get_role(server, role)
            
    if(ch1 == None and ch2 == None and got_role == None):
        await client.say("Sorry, channels or roles could not be found.")
    elif(ch1 == None):
        await client.say("Sorry, '" + ch1.name + "' could not be found.")
    elif(ch2 == None):
        await client.say("Sorry, '" + ch2.name + "' could not be found.")
    elif(got_role == None):
        await client.say("Sorry, '" + role + "' could not be found.")

    all_members = ch1.voice_members
    for member in all_members:
        for rolee in member.roles:
            if rolee == got_role:
                await client.move_member(member, ch2)

def get_role(server, role : str) -> 'Role':
    '''Helper function that returns Role object from name snippet'''
    for roleo in server.roles:
        if role.lower() in roleo.name.lower():
            return roleo
    return None

def permission_to_move(user):
	return user.server_permissions.move_members;
                    
######################################## END OF HELPER FUNCTIONS ############################################
######################################## END OF HELPER FUNCTIONS ############################################
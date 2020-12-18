#Takes a user returned from the database in tuple form and returns it as dictionary

def convert_user_tuple_to_dict(user:tuple):
    dictionary = {}
    users_table = ('id', 'firstName', 'lastName', 'email', 'userName', 'password', 'county', 'state')
    for i in range(len(users_table)):
        key = users_table[i]
        dictionary[key] = user[i] 
    
    return dictionary

#Converts list of email and username already registered (tuple to dict)
def convert_email_username_tuple_to_dict(user:tuple):
    dictionary = {}
    users_table = ('email', 'userName')
    for i in range(len(users_table)):
        key = users_table[i]
        dictionary[key] = user[i] 
    
    return dictionary

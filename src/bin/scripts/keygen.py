from Crypto.Protocol.KDF import PBKDF2


def get_private_key(password):
    salt = b"t(an)Archive salton sea"
    kdf = PBKDF2(password, salt, 64, 1000)
    key = kdf[:32]
    return key

def main():
    user_passwd = input('Enter the password you would like to use: ')
    gen_key = get_private_key( user_passwd )


    print('Your new key is: {0}'.format( gen_key.hex() ))

main()

# this is my famous password
# 7f429eb3276c671bfe71f97ccd7765cedf1d03ab8ea8b3079e0f15c38189e787

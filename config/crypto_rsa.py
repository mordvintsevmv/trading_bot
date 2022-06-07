import rsa


def create_rsa_keys():
    public_key, private_key = rsa.newkeys(1024)

    with open("config/publicKey.pem", "wb") as pub:
        pub.write(public_key.save_pkcs1('PEM'))

    with open("config/privateKey.pem", "wb") as priv:
        priv.write(private_key.save_pkcs1('PEM'))


def get_rsa_keys():
    with open('config/publicKey.pem', 'rb') as pub:
        public_key = rsa.PublicKey.load_pkcs1(pub.read())

    with open('config/privateKey.pem', 'rb') as priv:
        private_key = rsa.PrivateKey.load_pkcs1(priv.read())

    return public_key, private_key


def encrypt(text):
    with open('config/publicKey.pem', 'rb') as pub:
        public_key = rsa.PublicKey.load_pkcs1(pub.read())

    return rsa.encrypt(text.encode('ascii'), public_key)


def decrypt(text):
    with open('config/privateKey.pem', 'rb') as priv:
        private_key = rsa.PrivateKey.load_pkcs1(priv.read())

    return rsa.decrypt(text, private_key).decode('ascii')

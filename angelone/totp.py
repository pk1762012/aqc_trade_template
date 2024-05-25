import pyotp

def getTotp():
    totp = pyotp.TOTP("NAQEKA5FEAORH3MAUDWECKAIE4")
    return totp.now()
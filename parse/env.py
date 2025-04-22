from envserv import EnvBase, variable

class LoginEnv(EnvBase):
    __envfile__ = "C:/Users/Rudenches/PycharmProjects/Diplom_v3/.env"
    login:str = variable(alias='LOGIN',  error=True)
    password:str = variable(alias='PASSWORD',  error=True)

env_login = LoginEnv()
print(env_login.all())

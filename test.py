from lib.Client import Client

client = Client("Luka")
client.connect('localhost', '3030')

client.on("test", lambda data:
    print(data)
          )

client.to("Luka").emit("test", "aaa")
# i = 0
# while i < 10:
#     i += 1
#     client.to("Luka").emit("test", "TESTIRAM BUGASD")
#     pass

while 1:
    pass

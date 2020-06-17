import os

topics = [fn[:-4].title() for fn in os.listdir("./texts") if fn.endswith('.txt')]

image_links = {
  'Astronomy': 'https://cdn.discordapp.com/attachments/719020754858934294/719571971658088458/astronomy.png',
  'Planet':
  'https://cdn.discordapp.com/attachments/719020754858934294/719595296249610371/planet.png'}



sun = {
'Sun': "https://cdn.discordapp.com/attachments/719020754858934294/722525849282412564/sun.png",
'Mercury': "https://cdn.discordapp.com/attachments/719020754858934294/722519380914602145/mercury.png",
'Venus': "https://cdn.discordapp.com/attachments/719020754858934294/722530732907429988/venus.png",
'Earth': "https://cdn.discordapp.com/attachments/719020754858934294/722530931986137148/earth.png",
'Mars': "https://cdn.discordapp.com/attachments/719020754858934294/722535108510220368/mars.png",
'Jupiter': "https://cdn.discordapp.com/attachments/719020754858934294/722535702381985852/jupiter.png",
'Saturn': "https://cdn.discordapp.com/attachments/719020754858934294/722536981745369098/saturn.png",
'Uranus': "https://cdn.discordapp.com/attachments/719020754858934294/722537550400716941/uranus.png",
'Neptune': "https://cdn.discordapp.com/attachments/719020754858934294/722538262391947295/neptune.png",
'Pluto': "https://cdn.discordapp.com/attachments/719020754858934294/722560982647570562/pluto.png"
}
alpha_centauri = {'Alpha Centauri A': "", 'Alpha Centauri B': "", 'Proxima Centauri': ""}

galaxy = [sun, alpha_centauri]



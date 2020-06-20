import os

topics = [fn[:-4].title() for fn in os.listdir("./texts") if fn.endswith('.txt')]

image_links = {
  'Astronomy': 'https://cdn.discordapp.com/attachments/719020754858934294/719571971658088458/astronomy.png',
  'Planet':
  'https://cdn.discordapp.com/attachments/719020754858934294/719595296249610371/planet.png'}



sun = {
'Sun': ["https://cdn.discordapp.com/attachments/719020754858934294/722525849282412564/sun.png", "https://en.wikipedia.org/wiki/Sun"],
'Mercury': ["https://cdn.discordapp.com/attachments/719020754858934294/722519380914602145/mercury.png", "https://en.wikipedia.org/wiki/Mercury_(planet)"],
'Venus': ["https://cdn.discordapp.com/attachments/719020754858934294/722530732907429988/venus.png", "https://en.wikipedia.org/wiki/Venus"],
'Earth': ["https://cdn.discordapp.com/attachments/719020754858934294/722530931986137148/earth.png", "https://en.wikipedia.org/wiki/Earth"],
'Mars': ["https://cdn.discordapp.com/attachments/719020754858934294/722535108510220368/mars.png", "https://en.wikipedia.org/wiki/Mars"],
'Jupiter': ["https://cdn.discordapp.com/attachments/719020754858934294/722535702381985852/jupiter.png", "https://en.wikipedia.org/wiki/Jupiter"],
'Saturn': ["https://cdn.discordapp.com/attachments/719020754858934294/722536981745369098/saturn.png", "https://en.wikipedia.org/wiki/Saturn"],
'Uranus': ["https://cdn.discordapp.com/attachments/719020754858934294/722537550400716941/uranus.png", "https://en.wikipedia.org/wiki/Uranus"],
'Neptune': ["https://cdn.discordapp.com/attachments/719020754858934294/722538262391947295/neptune.png", "https://en.wikipedia.org/wiki/Neptune"],
'Pluto': ["https://cdn.discordapp.com/attachments/719020754858934294/722560982647570562/pluto.png", "https://en.wikipedia.org/wiki/Pluto"]
}
alpha_centauri = {'Alpha Centauri A': ["https://cdn.discordapp.com/attachments/719020754858934294/723695059115049040/alpha_centauri_a.jpg", "https://en.wikipedia.org/wiki/Alpha_Centauri#Alpha_Centauri_A"], 'Alpha Centauri B': ["https://cdn.discordapp.com/attachments/719020754858934294/723695088848470026/alpha_centauri_b.jpg", "https://en.wikipedia.org/wiki/Alpha_Centauri#Alpha_Centauri_B"], 'Proxima Centauri': ["https://cdn.discordapp.com/attachments/719020754858934294/723695181748240404/proxima_centauri.jpg", "https://en.wikipedia.org/wiki/Alpha_Centauri#Alpha_Centauri_C_(Proxima_Centauri)"]}

galaxy = [sun, alpha_centauri]



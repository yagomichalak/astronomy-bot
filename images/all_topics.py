import os

topics = [fn[:-4].title() for fn in os.listdir("./texts") if fn.endswith('.txt')]

image_links = {
  'Astronomy': 'https://cdn.discordapp.com/attachments/719020754858934294/719571971658088458/astronomy.png',
  'Planet':
  'https://cdn.discordapp.com/attachments/719020754858934294/719595296249610371/planet.png'}

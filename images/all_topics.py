import os

topics = [fn[:-4].title() for fn in os.listdir("./texts") if fn.endswith('.txt')]

image_links = {
  "Astronomy":
  ["https://cdn.discordapp.com/attachments/719020754858934294/719571971658088458/astronomy.png", "https://www.space.com/16014-astronomy.html"],
  "Planet":["https://cdn.discordapp.com/attachments/719020754858934294/719595296249610371/planet.png", "https://solarsystem.nasa.gov/planets/in-depth/"],
  "Black_Hole":["https://cdn.discordapp.com/attachments/719020754858934294/723903577063424121/black_hole.jpg", "https://www.nasa.gov/audience/forstudents/k-4/stories/nasa-knows/what-is-a-black-hole-k4.html"],
  "Universe":["https://cdn.discordapp.com/attachments/719020754858934294/719021292761645086/universe.jpg", "https://en.wikipedia.org/wiki/Universe"],
  "Galaxy":["https://cdn.discordapp.com/attachments/719020754858934294/724639753617670165/galaxy.jpg", "https://en.wikipedia.org/wiki/Galaxy"],
  "Constellation":["https://cdn.discordapp.com/attachments/719020754858934294/724639871817482240/constellation.jpg", "https://en.wikipedia.org/wiki/Constellation"],
  "Planetary_System":
  ["https://cdn.discordapp.com/attachments/719020754858934294/724640040353005598/planetary_system.jpg", "https://en.wikipedia.org/wiki/Planetary_system"],
  "White_Hole":
  ["https://cdn.discordapp.com/attachments/719020754858934294/724640133319622706/white_hole.jpg", "https://en.wikipedia.org/wiki/White_hole"],
  "Supernova":
  ["https://cdn.discordapp.com/attachments/719020754858934294/724640228794695720/supernova.jpg", "https://en.wikipedia.org/wiki/Supernova"],
  "Satellite":
  ["https://cdn.discordapp.com/attachments/719020754858934294/724640318942740501/satellite.jpg", "https://en.wikipedia.org/wiki/Satellite"],
  "Natural_Satellite":
  ["https://cdn.discordapp.com/attachments/719020754858934294/724640423070400542/natural_satellite.jpg", "https://en.wikipedia.org/wiki/Natural_satellite"],
  "Nebula":
  ["https://cdn.discordapp.com/attachments/719020754858934294/724640498073206794/nebula.jpg", "https://simple.wikipedia.org/wiki/Nebula"],
  "Exoplanet":
  ["https://cdn.discordapp.com/attachments/719020754858934294/724640554058645554/exoplanet.jpg", "https://simple.wikipedia.org/wiki/Extrasolar_planet"],
  "Gravity":
  ["https://cdn.discordapp.com/attachments/719020754858934294/724640626167119942/gravity.png", "https://simple.wikipedia.org/wiki/Gravity"],
  "Dark_Matter":
  ["https://cdn.discordapp.com/attachments/719020754858934294/724640790277783683/dark_matter.jpg", "https://simple.wikipedia.org/wiki/Dark_matter"],
  "Artemis":
  ["https://cdn.discordapp.com/attachments/719020754858934294/724784760219631660/artemis.png", "https://en.wikipedia.org/wiki/Artemis_program"],
  'Sun': ["https://cdn.discordapp.com/attachments/719020754858934294/722525849282412564/sun.png", "https://en.wikipedia.org/wiki/Sun"],
  'Mercury': ["https://cdn.discordapp.com/attachments/719020754858934294/722519380914602145/mercury.png", "https://en.wikipedia.org/wiki/Mercury_(planet)"],
  'Venus': ["https://cdn.discordapp.com/attachments/719020754858934294/722530732907429988/venus.png", "https://en.wikipedia.org/wiki/Venus"],
  'Earth': ["https://cdn.discordapp.com/attachments/719020754858934294/722530931986137148/earth.png", "https://en.wikipedia.org/wiki/Earth"],
  'Mars': ["https://cdn.discordapp.com/attachments/719020754858934294/722535108510220368/mars.png", "https://en.wikipedia.org/wiki/Mars"],
  'Jupiter': ["https://cdn.discordapp.com/attachments/719020754858934294/722535702381985852/jupiter.png", "https://en.wikipedia.org/wiki/Jupiter"],
  'Saturn': ["https://cdn.discordapp.com/attachments/719020754858934294/722536981745369098/saturn.png", "https://en.wikipedia.org/wiki/Saturn"],
  'Uranus': ["https://cdn.discordapp.com/attachments/719020754858934294/722537550400716941/uranus.png", "https://en.wikipedia.org/wiki/Uranus"],
  'Neptune': ["https://cdn.discordapp.com/attachments/719020754858934294/722538262391947295/neptune.png", "https://en.wikipedia.org/wiki/Neptune"],
  'Pluto': ["https://cdn.discordapp.com/attachments/719020754858934294/722560982647570562/pluto.png", "https://en.wikipedia.org/wiki/Pluto"],
  'Alpha_Centauri': ["https://cdn.discordapp.com/attachments/719020754858934294/725155209193717931/alpha_centauri.jpg", "https://en.wikipedia.org/wiki/Alpha_Centauri"]
  }



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

quizzes = {
'moon': 'Most planets have at least one of this orbiting around.',
'black hole': "What comes in, never goes out.",
'sun': "Hot, hot, hot... It loves to be the center everything!.",
'elon musk': "He is a billionaire entrepreneur, philanthropist and visionary South-African-Canadian-American. Founder, CEO and CTO of SpaceX.",
'Asteroid': 'Something fell from the sky and... R.I.P my fellow dinosaurs!'
}
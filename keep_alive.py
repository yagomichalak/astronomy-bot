# from flask import Flask, request
# from threading import Thread
# #import waitress

# app = Flask('')
# @app.route('/')
# def main():
#   return "Your bot is alive!"

# # @app.route("/dblwebhook", methods=["POST"])
# # def dbl():
# #     return "yolo", 200

# def run():
#   app.run(host="0.0.0.0", port=8080)
#   #waitress.serve(app, host='0.0.0.0', port=8080)


# def keep_alive():
#   server = Thread(target=run)
#   server.start()

import flask, waitress
from threading import Thread

app = flask.Flask('')

@app.route('/')
def main():
    return "Bot is online and working."

def run():
    waitress.serve(app, host='0.0.0.0', port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()

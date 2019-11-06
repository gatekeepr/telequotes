from telegram.ext import Updater, CommandHandler
from random import randrange
from gtts import gTTS
import logging
import csv
import time
import os

# initialising
token = open("config.txt", "r").read().strip()
legalusers = list(map(int, open("legalusers.txt", "r").readlines()))
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


# counts all lines in the quotefile


def countquotes(filename):
    with open(filename) as f:
        return sum(1 for line in f)

# creates an mp3 for a given string


def quoteToAudio(text):
    ttsobj = gTTS(text=text, lang='de', slow=False)
    ttsobj.save("Kek.mp3")

# checks if the querying user is allowed to use the bot


def checkValidUser(update, context):
    if update.message.chat.id not in legalusers:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Sorry, this is a private Bot!"
        )
        return False
    else:
        return True

# creates a list with quotes containing a keyword


def createCandidate(**kwargs):
    candidates = []
    keyword = kwargs.get('keyword', None)
    counter = countquotes("quotes.csv")
    pseudorandom = randrange(counter - 1)

    with open("quotes.csv", "r", encoding="utf-8") as csvfile:
        fieldnames = ["id", "username", "date", "quote"]
        reader = csv.DictReader(csvfile, delimiter=",")
        if(keyword):
            for row in reader:
                quote = row["quote"]
                if keyword in quote:
                    candidates.append(row)
            counter = len(candidates)
            if counter == 0:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text="Nothing found!"
                )
                return -1
            else:
                pseudorandom = randrange(counter)
                for row in candidates:
                    if candidates.index(row) == pseudorandom:
                        quote = row["quote"]
        else:
            for row in reader:
                if reader.line_num - 2 == pseudorandom:
                    quote = row["quote"]
    return quote

# sends a random quote as a text message


def tts(update, context):
    if checkValidUser(update, context):
        keyword = False
        if context.args:
            if len(context.args[0]) > 1:
                keyword = context.args[0]

        text = createCandidate(keyword=keyword)
        if(text is -1):
            return
        quoteToAudio(text)
        context.bot.send_audio(
            chat_id=update.message.chat_id, audio=open('Kek.mp3', 'rb'))
        os.system("rm Kek.mp3")


# adds a quote to the database


def add(update, context):

    if checkValidUser(update, context):

        # collect information from message
        text = update.message.reply_to_message.text
        date = str(update.message.reply_to_message.date.now())
        user = update.message.reply_to_message.from_user.first_name

        # write data to csv
        with open("quotes.csv", "a", encoding="utf-8") as csvfile:
            fieldnames = ["id", "username", "date", "quote"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            counter = countquotes("quotes.csv")
            writer.writerow(
                {"id": counter, "username": user, "date": date, "quote": text}
            )


# sends a fully random quote if no keyword is passed


def random(update, context):

    if checkValidUser(update, context):
        mode = 1
        amount = 1
        cycleAmount = 0
        quotelist = []
        keyword = False
        if context.args:
            # keyword specified in message, save it
            if len(context.args[0]) > 1:
                # if a number is also passed as second argument cycle multiple times
                if len(context.args) > 1:
                    if len(context.args[1]) == 1:
                        amount = int(context.args[1])
                keyword = context.args[0]
                mode = 2
            # if a number is passed send that many quotes
            elif len(context.args[0]) == 1:
                amount = int(context.args[0])
                mode = 3

        # repeat process if desired
        while cycleAmount < amount:

            quotelist.append(createCandidate(keyword=keyword))
            if(quotelist[0] is -1):
                return
            context.bot.send_message(
                chat_id=update.message.chat_id, text=quotelist[cycleAmount])
            cycleAmount += 1
            time.sleep(1)


# deplpy dispatcher and wait for messages
dispatcher.add_handler(CommandHandler("add", add))
dispatcher.add_handler(CommandHandler("random", random))
dispatcher.add_handler(CommandHandler("tts", tts))
updater.start_polling()

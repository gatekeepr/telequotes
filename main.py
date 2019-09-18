from telegram.ext import Updater, CommandHandler
from random import randrange
import logging, csv


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

token = open("config.txt","r").read().strip()
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

def countquotes(filename):
    with open(filename) as f:
        return sum(1 for line in f)

def add(update, context):

    print(update.message.reply_to_message)

    text = update.message.reply_to_message.text
    date = str(update.message.reply_to_message.date.now())
    user = update.message.reply_to_message.from_user.username

    print(text)
    print(date)
    print(user)

    with open('quotes.csv', 'a', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'username', 'date', 'quote']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        counter = countquotes('quotes.csv')
        writer.writerow({
            'id' : counter,
            'username' : user,
            'date' : date,
            'quote' : text
        })

def random(update, context):

    counter = countquotes('quotes.csv')
    pseudorandom = randrange(counter-1)

    with open('quotes.csv', 'r', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'username', 'date', 'quote']
        reader = csv.DictReader(csvfile, delimiter= ',')
        text="NULL"
        date="NEVER"
        user="ANON"

        for row in reader:
            if(reader.line_num - 2 == pseudorandom):
                 text = row['quote']
                 date = row['date']
                 user = row['username']


    finalstring = user + " @ " + date + ": \n" + text
    context.bot.send_message(chat_id=update.message.chat_id, text=finalstring)



dispatcher.add_handler(CommandHandler('add' , add))
dispatcher.add_handler(CommandHandler('random' , random))
updater.start_polling()

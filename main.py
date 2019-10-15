from telegram.ext import Updater, CommandHandler
from random import randrange
import logging, csv


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
token = open("config.txt","r").read().strip()
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


#counts all lines in the quotefile
def countquotes(filename):
    with open(filename) as f:
        return sum(1 for line in f)

#adds a quote to the database
def add(update, context):

    text = update.message.reply_to_message.text
    date = str(update.message.reply_to_message.date.now())
    user = update.message.reply_to_message.from_user.first_name

    #debug output
    print(user)
    print(date)
    print(text)



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


#sends a fully random quote if no keyword is passed
def random(update, context):

    mode = 1
    counter = countquotes('quotes.csv')
    pseudorandom = randrange(counter-1)

    #keyword specified in message, save it
    if(len(update.message.text.partition(' ')[2]) > 2):
        keyword = update.message.text.partition(' ')[2]
        mode = 2

    with open('quotes.csv', 'r', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'username', 'date', 'quote']
        reader = csv.DictReader(csvfile, delimiter= ',')
        candidates = []

        #keyword specified
        if(mode == 2):
            for row in reader:
                quote = row['quote']
                if keyword in quote:
                    candidates.append(row)
            counter = len(candidates)
            pseudorandom = randrange(counter)
            for row in candidates:
                if(candidates.index(row) == pseudorandom):
                    text = row['quote']
                    date = row['date']
                    user = row['username']

        #no keyword
        else:
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

from telegram.ext import Updater, CommandHandler
from random import randrange
import logging, csv

# initialising
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
token = open("config.txt", "r").read().strip()
legalusers = int(open("legalusers.txt", "r").read().strip())
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


# counts all lines in the quotefile
def countquotes(filename):
    with open(filename) as f:
        return sum(1 for line in f)


# adds a quote to the database
def add(update, context):

    if update.message.chat.id != legalusers:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Sorry, this is a private Bot!"
        )
    else:

        # collect information from message
        text = update.message.reply_to_message.text
        date = str(update.message.reply_to_message.date.now())
        user = update.message.reply_to_message.from_user.first_name

        # debug output
        print(user)
        print(date)
        print(text)

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

    if update.message.chat.id != legalusers:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Sorry, this is a private Bot!"
        )
    else:
        mode = 1
        amount = 1
        cycleAmount = 0
        # keyword specified in message, save it
        if len(context.args[0]) > 2:
            # if a number is also passed as second argument cycle multiple times
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

            counter = countquotes("quotes.csv")
            pseudorandom = randrange(counter - 1)

            with open("quotes.csv", "r", encoding="utf-8") as csvfile:
                fieldnames = ["id", "username", "date", "quote"]
                reader = csv.DictReader(csvfile, delimiter=",")
                candidates = []

                # keyword specified
                if mode == 2:
                    for row in reader:
                        quote = row["quote"]
                        if keyword in quote:
                            candidates.append(row)
                    counter = len(candidates)
                    # no quote found containing the keyword
                    if counter == 0:
                        context.bot.send_message(
                            chat_id=update.message.chat_id, text="Nothing found!"
                        )
                        return
                    else:
                        pseudorandom = randrange(counter)
                        for row in candidates:
                            if candidates.index(row) == pseudorandom:
                                text = row["quote"]
                                date = row["date"]
                                user = row["username"]

                # no keyword
                else:
                    for row in reader:
                        if reader.line_num - 2 == pseudorandom:
                            text = row["quote"]
                            date = row["date"]
                            user = row["username"]

            finalstring = user + " @ " + date + ": \n" + text
            context.bot.send_message(chat_id=update.message.chat_id, text=finalstring)
            cycleAmount += 1


dispatcher.add_handler(CommandHandler("add", add))
dispatcher.add_handler(CommandHandler("random", random))
updater.start_polling()

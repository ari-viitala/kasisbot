# -*- coding: utf-8 -*-

"""
A bot to interface Spexcript.
"""

import os
import subprocess
import pathlib
import datetime

import makespex

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging


from config import TELEGRAM_BOT_TOKEN, AUTHORIZED_CHAT_ID

# Sent messages are saved here to enable replying.
sent_messages = {}

if not os.path.isdir("./files"):
    os.mkdir("./files")

if not os.path.isdir("./temp"):
    os.mkdir("./temp")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def error(bot, update, error):
    """Log Errors caused by Updates."""

    logger.warning('Update "%s" caused error "%s"', update, error)


def start(update, context):
    """Send a message when the command /start is issued."""

    update.message.reply_text(
        """Fyysikkospeksin käsistiimin bottikäyttöliittymä Spexcript käsikirjoitusladontaohjelmistolle. Saat tarkemmat ojeet kirjoittamalla /help."""
    )


def help(update, context):
    """List the commands used by the bot"""

    with open("help.txt") as f:
        text = f.read()

    update.message.reply_text(text, parse_mode="Markdown")


def whoami(update, context):
    """Displays chat's ID"""

    id = update.effective_message.chat.id
    context.bot.send_message(id, "The ID of this chat is: {}".format(id))


def is_chat_member(update, context):
    """Check if message comes from a member of käsistiimi"""

    try:
        context.bot.get_chat(AUTHORIZED_CHAT_ID).get_member(update.effective_user.id)
        return True
    except:
        update.message.reply_test("Ominaisuus käytössä vain käsistiimin jäsenille.")
        return False


def model_file(update, context):
    """Send the model syntax as a file."""

    context.bot.send_document(update.effective_chat.id, document=open("malli.txt"))


def history(update, context):
    """Show a listing of previous versions."""

    if not is_chat_member(update, context):
        return

    files = [f for f in os.listdir("./files") if ".pdf" in f]
    files = [(f, pathlib.Path(f"./files/{f}").stat().st_mtime) for f in files]
    files = sorted(files, key=lambda x: -x[1])

    files = [f[0] for f in files]

    try:
        files = files[: int(context.args[0])]
    except:
        pass

    text = "*Viimeiset käsikset:*\n```\n" + "\n".join(files) + "```"

    update.effective_message.reply_text(text, parse_mode="Markdown")


def recompile(update, context):
    """Resend a saved file."""

    if not is_chat_member(update, context):
        return

    if len(context.args) > 0:
        if os.path.isfile(f"./files/{context.args[0]}"):
            file = context.args[0].split(".")[0]
        else:
            update.message.reply_text("Tiedostoa ei löydy")
            return

    else:
        files = [f for f in os.listdir("./files") if ".pdf" in f]
        files = [(f, pathlib.Path(f"./files/{f}").stat().st_mtime) for f in files]
        files = sorted(files, key=lambda x: -x[1])

        file = files[0][0]

    files = [f for f in os.listdir("./files") if file in f]

    for f in files:
        context.bot.send_document(
            update.effective_chat.id, document=open(f"./files/{f}", "rb")
        )


def handle_compile(update, context):
    """Handles saving the temporary files if appropriate."""

    caption = update.effective_message.caption
    caption = caption.lower() if caption else ""

    if update.effective_chat.type == "group" and "@kassaribot" not in caption:
        return

    save = False
    success = True

    if "tallenna" in caption and is_chat_member(update, context):
        save = True

    success = compile(update, context)

    if save and success:
        files = [f for f in os.listdir("./temp/")]
        for f in files:
            os.rename(f"./temp/{f}", f"./files/{f}")

    for f in os.listdir("./temp/"):
        os.remove(f"./temp/{f}")


def drive_compile(update, context):
    if not is_chat_member(update, context):
        return

    try:
        text = makespex.read_manuscript()
    except Exception as e:
        print(e)
        print("Virhe ladattaessa käsistä Drivestä")
        return

    save = len(context.args) > 0

    if save:
        name = context.args[0] + ".txt"
    else:
        name = f"drive_compile_{datetime.datetime.now().isoformat()[:19]}.txt"

    with open(f"./temp/{name}", "w+") as f:
        f.write(text)

    try:
        subprocess.run(["python", "-m" "spexcript", f"./temp/{name}"], timeout=10)
    except:
        update.effective_message.reply_text("Tiedoston kääntäminen ei onnistunut.")
        for f in os.listdir("./temp/"):
            os.remove(f"./temp/{f}")
        return 0

    try:
        context.bot.send_document(
            update.effective_chat.id,
            document=open(f"./temp/{name.split('.')[0]}.pdf", "rb"),
        )
    except:
        update.effective_message.reply_text("Tiedosto ei kääntynyt.")

    if save:
        files = [f for f in os.listdir("./temp/")]
        for f in files:
            os.rename(f"./temp/{f}", f"./files/{f}")

    for f in os.listdir("./temp/"):
        os.remove(f"./temp/{f}")

    return True


def compile(update, context):
    """Compiles the document in update using Spexcript."""

    try:
        name = update.effective_message.document.file_name

        if name == "malli.txt":
            pass
        else:
            name = (
                name.split(".")[0]
                + "_"
                + datetime.datetime.now().isoformat()[:10]
                + ".txt"
            )

        update.effective_message.document.get_file().download(
            custom_path=f"./temp/{name}"
        )
    except:
        update.effective_message.reply_text(
            "Jotain meni pieleen tiedoston lataamisessa."
        )
        return False

    try:
        subprocess.run(["python", "-m" "spexcript", f"./temp/{name}"], timeout=10)
    except:
        update.effective_message.reply_text("Tiedoston kääntäminen ei onnistunut.")
        return False

    try:
        context.bot.send_document(
            update.effective_chat.id,
            document=open(f"./temp/{name.split('.')[0]}.pdf", "rb"),
        )
    except:
        update.effective_message.reply_text("Tiedosto ei kääntynyt.")
        return False

    return True


def main():
    """Main polling loop that contains all the callback handlers"""

    updater = Updater(token=TELEGRAM_BOT_TOKEN)

    dp = updater.dispatcher

    # Add handlers to the dispatchers. This defines what the bot does when it receives messages.
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("whoami", whoami))
    dp.add_handler(CommandHandler("historia", history))

    dp.add_handler(CommandHandler("malli", model_file))
    dp.add_handler(CommandHandler("kasis", recompile))
    dp.add_handler(CommandHandler("kaanna_drive", drive_compile))

    dp.add_handler(MessageHandler(Filters.document, handle_compile))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()

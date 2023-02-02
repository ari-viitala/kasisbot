# Kasisbot

A bot that combines Google drive, Telegram and Spexcript for a smooth spex development workflow.
Wow!

## Installation

*These instructions have been tested on 30.1.2023 on WSL Ubuntu 20.04.1 LTS with Python 3.8.5.*

Clone the repository

```console
git clone https://github.com/summis/kasisbot.git
cd kasisbot
```

Enable virtual environment and install dependecies with

```console
python -m venv .venv
source venv/bin/activate
pip install -r requirements.txt
```

Install Latex packages required by spexcript

```console
sudo apt-get install texlive-full=2019.20200218-1 texlive-lang-european=2019.20200218-1
```

Create a new configuration file for the bot

```console
cp config.example.py config.py
```

Now you have to fill `TELEGRAM_BOT_TOKEN` variable in the file by creating a new Telegram bot.

- Find `@BotFather` in Telegram
- Create a new bot with `/newbot` command and follow instructions
- Give the token given by BotFather as value for the variable

This already allows to test bot functionality.

- Make sure that virtual environment is activated with `source venv/bin/activate`
- Start bot with `python kasisbot.py`
- Start private chat with bot
- Download example input file received with `/malli` command
- Send file back to bot. Bot should return you a compiled PDF file

Integrating both with Google Drive requires additional steps.
Fill `AUTHORIZED_CHAT_ID` variable.

- Add bot to the Telegram group whose members should be able to use the bot.
Only one group is supported
- Type command `/whoami` and set the returned id as value for the variable

Only members of the authorized chat are allowed to compile document from Google Drive.
To enable access

- Create new project in [Google Cloud resource management page](https://console.cloud.google.com/cloud-resource-manager)
- Create new credentials in [Google Cloud credential page](https://console.developers.google.com/apis/credentials)
  - Make sure that the project that you just created is selected
  - Press "Create credentials" -button
    - Select "OAuth client Id"
    - In "Test users" page add yourself with you Google account as test user
    - When the "OAuth client created" pop up appears download the JSON file.
Rename it as "credentials.json" and place it to root folder of this repository
- Copy the ID of the folder in your Google Drive (can be found in URL) from which you want the bot to search for files
  - Add one document to the folder and copy contents of `malli.txt` to that document
- Run `python makespex.py`
  - You should get error message that tells the API being disabled. In the error message is a link to page where you can enable access to Google Drive
  - Try running command again. Now bot complains about Google Docs API being disabled. Follow same procedure than in previous point
  - Third time everything should work and contents of the file should be printed to console

## Running bot in production

University's servers (e.g. kosh) can be used for running the bot.
They may be occasionally restarted which causes a need for manual restarts.
Alternatively any other hosting solution can be used.
These intructions assume that you have first locally successfully run the bot

- Task ssh connection to the production server `ssh your-aalto-user-name@kosh.aalto.fi`
- Clone repo, create virtual environment, install dependencies and install Latex packages like instructed before
- Copy `config.py` and `token.json` to production with `scp config.py token.json your-aalto-user-name@kosh.aalto.fi:path/to/folder/kasisbot`
- Start bot as a background process with `tmux new -s kasisbot -d "source .venv/bin/activate && python kasisbot.py"`

## File structure in Drive

Bot reads files in the configured folder in alphabetical order and combines their contents to a one file that is compiled to PDF.
Subdirectories are not allowed.
Having other content in files than text is not allowed.
Bot tries to compile document without any syntax checks so writing correct Spextex in user responsibility.

It is probably good idea to split long manuscript to many files to make navigating easier.

## Spexcript syntax

```text
Hyvin lyhyt syntaksikertaus alla:
 - hahmoilla lyhenteet, esim. DP, N
 - tää on olennaisesti Latexia, eli % aloittaa kommentin
 - erikoismerkkikomboilla saa aikaan eksoottisia virheilmoituksia
 - repliikki alkaa merkillä < ja puhujan lyhenteellä sen perään (ilman välilyöntiä)
 - näyttämöohje merkillä < jonka perään välilyönti,
 - hahmon voi mainita merkillä @ jonka perään nimilyhenne. 

 
Keinotekoinen esimerkki:
 
### Radiotentti % kohtauksen nimi, ei välttämätön

@N:n radioshow, @DP vieraana. % kohtauskuvaus, voi esim. kopioida suoraan kohtausluettelosta tai täydentää myöhemmin
 
< Radiostudiossa @N ja @DP. % näyttämöohje
 
$ Radioshown tunnussävelmä % ääniefekti tms
 
<N Tervetuloa, @DP! % repliikki
 
<DP Kiitos. % repliikki
 
$$ Radiohaastattelu laulaen. % biisi
```

See also `malli.txt`

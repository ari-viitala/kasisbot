## Kasisbot

This is a bot for Fyysikkospeksi's manuscript team. This bot interfaces the [Spexcript](https://pypi.org/project/spexcript/), a software that can compile pretty theter manuscripts using a simple markdown language. 

### Installation

```
git clone https://github.com/ari-viitala/kasisbot.git
cd telegram-messaging-bot

virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

In addition you'll need a TeX Live to compile the documents.
```
sudo apt-get install texlive-full
sudo apt-get install texlive-lang-european
```
In addition you'll have to change the bot token and the chat from which the bot is used from `kasisbot.py`.

Run the bot with
```
python kasisbot.py
```

### Usage

More detailed instructions in the bot.

### Troubleshooting

If you are having trouble getting your file compiled try compiling them manually with:
```
python -m spexcript malli.txt
```



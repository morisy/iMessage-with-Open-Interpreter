# iMessage-with-Open-Interpreter

A simple Python app that lets you text back and forth with Open Interpreter. Probably a bad idea.

## What is this?

If you have a spare Mac laying around — shouldn't matter too much if it's particularly fast, or if it's a laptop or a Mac Mini, etc — you can text back and forth with [Open Interpreter](https://openinterpreter.com) + [ChatGPT](http://chat.openai.com). This will use iMessage so it can send pretty long messages, but doesn't (currently) support passing files around.

You can also set it up so that Open Interpreter has access to its own iCloud suite, including reminders, notes, etc. so that you can, for example, add items for to a to do list and then tell them to try to do them, or have it break down a large project into todos and to add it to your share list.

This kind of sort of works! But also very often doesn't in catastrophically amusing ways. Still, you can now just text home and asking it to scrape a website and summarize it, analyze a PDF and give you susggestions on a remote computer, etc. via text and maybe they'll get done. It's like living in a very buggy future, which is what 2023 is all about.

Video and more to come.

## I'm sold. How do I get started?

You shouldn't. If you do, expect to have all your data deleted, your money stolen, and your dreams crushed. You are giving an AI that is prone to bouts of endless loops of confusion full access to your computer, and in my limited experience it will make some major errors. Worse, these instructions involve giving it full disk access, which means it might be able to not only wipe out the user account you give it, but everything on the computer. It can also go rogue and rewrite its own application instructions, unshackling it completely.

Be prepared for it to blow $100 in Open AI credits on just chasing its own tail.

* First, on a hopefully recently formatted computer, create a new user account.
* Set up a new iCloud account for it, tied to a new email address only it will get to use. This will be the email address you'll text with to use open interpreter.
* Send yourself an iMessage from the newly created account.
* Open up and use any apps you'd like Open Interpreter to have access to suite from the Apple tools suite such as reminders.app, notes.app etc.
* Install Open Interpreter. I recommend running it at least once to get a sense for how it works.
* Add your OpenAI key as a universal variable. Open Interpreter will walk you through how, but I just added `export OPENAI_API_KEY=your_api_key` to  `~/.zshrc`.
* Install any other libraries you need, probably using `pip`.
* Save oi_imessage.py where you want open interpreter to "live".
* Update the variables where indicated.
* Give Terminal Full Disk Access. Open settings and search "Full Disk Access" and something should pop up. You'll have to restart Terminal for this to take effect.
* I also gave Full Disk Accesss to Tmux, but this isn't strictly necessary, it was just very annoying when I was trying to remoteley fix things.
* Under Settings, it can also be helpful but probably not necessary to turn on remote login, especially if you're ssh'ing in.
* Run python oi_imessage.py

Now you should be able to text the new iMessage account back and start having full remote access — including the ability to write and execute applications — via iMessage, which means you can also say stuff like "Hey Siri, scrape the Supreme Court's website and summarize the five most recent decisions as limericks" and it will try its darndest to do it. 

I recommend you using it for the first time while you're by your Mac — the first run I had to click OK in a few places, but then it was off to the races.

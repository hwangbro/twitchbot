import pyttsx3
engine = pyttsx3.init()
engine.setProperty('voice', engine.getProperty('voices')[1].id)
engine.setProperty('volume', 0.4)
engine.setProperty('rate', 200)

def say(text):
	engine.say(text)
	engine.runAndWait()

if __name__ == '__main__':
	say('hwangbroxd says: the quick brown fox jumped over the lazy dogs')

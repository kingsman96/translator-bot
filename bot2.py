from pygoogletranslation import Translator
import telebot, datetime, time
from time import sleep
from telebot import types
from gtts import gTTS

TOKEN='INSERT HERE BOT TOKEN (FROM @BOTFATHER)'

bot = telebot.TeleBot(token=TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    logger(message)
    msg_id = message.message_id
    chat_id = message.chat.id
    msg = message.text
    text = "This will never be sent."
    if msg == "/start":
        text = "Hi! I'm a Translator Bot.\nType /help to understand how to use me."
    elif msg == "/help":
        text = ('HOW TO USE ME?\nTap the next sentence to copy it:\n\n<code>/tr src+dest'
                +'+some_text</code>.\n\nNow paste it into the typing bar and instead of'
                +' <b>some_text</b> put what you want to translate, instead of <b>src'
                +'</b> put the language you want to translate from (<i>autodetect</i> by '
                +'default) and finally replace <b>dest</b> with the language you want to'
                +' translate into (<i>english</i> by default).\nE.g. <code>/tr it+The'
                +' pen is on the table</code>.\n\nOr type the sentence you'
                +' want to translate (or forward it to the bot) and then reply to '
                +'that message with a dot followed by the language you want to '
                +'translate into (eg <code>.en</code>).\nFor a faster usage it\'s '
                +'available the inline mode, id est you can type <code>@botusername '
                +'dest sentence</code> to translate <i>sentence</i> into <i>dest</i>.'
                +'\n\nType /lang to see available '
                +'languages and how to encode them, in <b>src</b> or <b>dest</b> field.')
    bot.send_message(chat_id, text, parse_mode="HTML", reply_to_message_id=msg_id)

# hard translator
@bot.message_handler(commands=['tr', 'lang'])
def main(message):
    logger(message)
    msg_id = message.message_id
    chat_id = message.chat.id
    msg = message.text
    if msg == '/lang':
        f = '<b>AVAILABLE LANGUAGES</b>\n\n<b>language</b>: <code>code</code>\n'
        for l in LANGUAGES:
            f = f + LANGUAGES[l] + ': <code>' + str(l) + "</code>\n"
        bot.reply_to(message, f, parse_mode="HTML")
    elif msg[0:3] == '/tr':
        # if there is a valid input
        if len(msg) > 8:
            # separate input to extract param
            formula = msg[4:].split("+")
            # if source language is explicit, three parameters
            if len(formula) == 3:
                source = formula[0]
                destination = formula[1]
                sentence = formula[2]
            # if it isn't, there are less parameters
            else:
                source = "auto"
                destination = formula[0]
                sentence = formula[1]
            try:
                # here i sent a temporary message to use the cool editing message method
                sent = bot.reply_to(message, "<i>I'm translating...</i>", parse_mode = "HTML")
                sent_message_id = sent.message_id
                # calling of the core function that translate
                # returns (source, destination, text_translated)
                transl = transl_it(sentence, src=source, dest=destination)
                # text formatting
                transl = ("Tanslated from: <b>" + str(transl[0]) + "</b>.\nTranslated into: <b>"
                          + str(transl[1]) + "</b>.\nTranslation:\n<code>"+ transl[2] +"</code>")
                bot.edit_message_text(chat_id=chat_id, message_id=sent_message_id,
                                      text=transl, parse_mode="HTML")
            except:
                # this is the handling of the error
                bot.edit_message_text(chat_id=chat_id, message_id=sent_message_id,
                                      text="<i>It's embarrassing, there was a problem...</i>", parse_mode = "HTML")
        else:
            # this occours when bad syntax or parameters are used
            bot.reply_to(message, "<i>Check what you have typed... i can't uderstand it :("
                                 +"\n...or ask for</i> /help!", parse_mode = "HTML")
# speaker tts
@bot.message_handler(commands=['gtts'])
def googleTTS(message, dot=False):
    logger(message)
    chat_id = message.chat.id
    msg_id = message.message_id
    if message.reply_to_message.text != None:
        params = (message.text).split(' ')
        if len(params) == 2 or dot:
            if dot:
                src = message.text[1:]
            else:
                src = params[1]
            if src in LANGUAGES:
                try:
                    sentence = message.reply_to_message.text
                    tts = gTTS(text=sentence, lang=src)
                    url = tts.get_urls()[0]
                    bot.send_voice(chat_id, voice=url,
                        reply_to_message_id=message.reply_to_message.message_id)
                except Exception as e:
                    print("Exception: " + str(e))
            else:
                bot.reply_to(message, "Error: invalid source language.")
        else:
            bot.reply_to(message, "Error: invalid syntax.\nTry <code>/gtts en</"
                         +"code> by replying to this message.",
                         parse_mode='HTML')
    else:
        bot.reply_to(message, "Error: invalid syntax.\nTo use this command you "
                     +"have to reply to a text message.\nFor example, reply tho"
                     +" this message with <code>/gtts en</code>",
                     parse_mode='HTML')

# dot translator
@bot.message_handler(func=lambda message:True)
def general_msg_handler(message):
    logger(message)
    if message.content_type == 'text' and message.text[0]=='.':
        text = message.text
        chat_id = message.chat.id
        if len(text) > 2:
            try:
                sent = bot.reply_to(message.reply_to_message, "<i>I'm translating...</i>", parse_mode = "HTML")
                sent_message_id = sent.message_id
                sent_from_bot = sent.chat.id
                if message.reply_to_message.text != None:
                    sentence = message.reply_to_message.text
                elif message.reply_to_message.caption != None:
                    sentence = message.reply_to_message.caption
                # returns (source, destination, text_translated)
                translation = transl_it(sentence, src="auto", dest=text[1:])
                # if he doesn't understand input language
                if translation[0] == False:
                    raise NameError('failed to detect source language')
                bot.edit_message_text(chat_id=chat_id, message_id=sent_message_id,
                                      text=translation[2], parse_mode="HTML")
            except Exception as e:
                # this is the handling of the error
                alarm = "<i>It's embarrassing, there was a problem...</i>\n<pre>" + str(e) +"</pre>"
                bot.edit_message_text(chat_id=chat_id, message_id=sent_message_id,
                                      text=alarm, parse_mode = "HTML")

    elif message.content_type == 'text' and message.text[0]=='#':
        if message.reply_to_message.text != None:
            googleTTS(message, dot=True)
    else:
        print(False)

# this function handle inline translator
@bot.inline_handler(lambda query: len(query.query) > 2)
def query_text(inline_query):
    dest = (inline_query.query).split(" ")[0]
    sentence = inline_query.query[len(dest):]
    # returns (source, destination, text_translated)
    transl = transl_it(sentence, src="auto", dest=dest)
    if transl[0] == transl[1]:
        dest = 'False'
    else:
        dest = LANGUAGES[dest] + " (src: " + transl[0] + ")"
    text = transl[2]
    r = types.InlineQueryResultArticle(inline_query.id, title=dest,
                          input_message_content=types.InputTextMessageContent(text),
                          description=text)
    # the result of a query always is a list of object
    bot.answer_inline_query(inline_query.id, [r])

# this function helps you with debug in terminal
def logger(message):
    text = message.text
    content_type = message.content_type
    date = str(datetime.datetime.now())
    date2 = date[0:10]
    time2 = date[11:19]
    user = str(message.chat.id)
    timedateid = "date:clock#id " + date2 + ":" + time2 + '#' + user + ': '
    if content_type == 'text':
        print('Got command @' + timedateid + text)
    else:
        print('Got message @' + timedateid + str(content_type))

# this function is the core of translator bot
def transl_it(text, src, dest):
    try:
        # create a new object
        translator = Translator()
        # text is what you want to transalte, src the source language,
        # id est the language of the sentence, dest is the destination language
        a = translator.translate(text, src=src, dest=dest)
        # this is a manipulation to extract basic info from the output
        translated = (LANGUAGES[a.src], LANGUAGES[a.dest], a.text)
        return translated
    except Exception as ee:
        #print(ee)
        # this is the handling of the error, that bad input text can lead
        confidence = translator.detect(text)
        translated = (False, False, "error: " + str(ee) + "\n" + str(confidence))
        return translated

# available languages: keys are language code, values are language name
LANGUAGES = {
    'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic',
    'hy': 'armenian', 'az': 'azerbaijani', 'eu': 'basque','be': 'belarusian',
    'bn': 'bengali', 'bs': 'bosnian', 'bg': 'bulgarian', 'ca': 'catalan',
    'ceb': 'cebuano', 'ny': 'chichewa', 'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)', 'co': 'corsican', 'hr': 'croatian',
    'cs': 'czech', 'da': 'danish', 'nl': 'dutch', 'en': 'english',
    'eo': 'esperanto', 'et': 'estonian', 'tl': 'filipino', 'fi': 'finnish',
    'fr': 'french', 'fy': 'frisian', 'gl': 'galician', 'ka': 'georgian',
    'de': 'german', 'el': 'greek', 'gu': 'gujarati', 'ht': 'haitian creole',
    'ha': 'hausa', 'haw': 'hawaiian', 'iw': 'hebrew', 'hi': 'hindi',
    'hmn': 'hmong', 'hu': 'hungarian', 'is': 'icelandic', 'ig': 'igbo',
    'id': 'indonesian', 'ga': 'irish', 'it': 'italian', 'ja': 'japanese',
    'jw': 'javanese', 'kn': 'kannada', 'kk': 'kazakh', 'km': 'khmer',
    'ko': 'korean', 'ku': 'kurdish (kurmanji)', 'ky': 'kyrgyz', 'lo': 'lao',
    'la': 'latin', 'lv': 'latvian', 'lt': 'lithuanian', 'lb': 'luxembourgish',
    'mk': 'macedonian', 'mg': 'malagasy', 'ms': 'malay', 'ml': 'malayalam',
    'mt': 'maltese', 'mi': 'maori', 'mr': 'marathi', 'mn': 'mongolian',
    'my': 'myanmar (burmese)', 'ne': 'nepali', 'no': 'norwegian', 'ps': 'pashto',
    'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese', 'pa': 'punjabi',
    'ro': 'romanian', 'ru': 'russian', 'sm': 'samoan', 'gd': 'scots gaelic',
    'sr': 'serbian', 'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi',
    'si': 'sinhala', 'sk': 'slovak', 'sl': 'slovenian', 'so': 'somali',
    'es': 'spanish', 'su': 'sundanese', 'sw': 'swahili', 'sv': 'swedish',
    'tg': 'tajik', 'ta': 'tamil', 'te': 'telugu', 'th': 'thai', 'tr': 'turkish',
    'uk': 'ukrainian', 'ur': 'urdu', 'uz': 'uzbek', 'vi': 'vietnamese',
    'cy': 'welsh', 'xh': 'xhosa', 'yi': 'yiddish','yo': 'yoruba', 'zu': 'zulu',
    'fil': 'Filipino', 'he': 'Hebrew', 'auto': 'auto', '': 'idk'}

# sorting dictionary of languages by value
{k: v for k, v in sorted(LANGUAGES.items(), key=lambda item: item[1])}

#Keep main program running while bot runs threaded
exit = False
if __name__ == "__main__":
    print("\n_ _ _ ok, i'm ready _ _ _\n")#print
    while not exit:
        try:
            bot.polling()
            time.sleep(1)
        except KeyboardInterrupt:
            bot.stop_polling()
            exit = True
        break

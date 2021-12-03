#! /bin/python3
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
import operator, collections, time, telepot, psutil, os

TOKEN='123456789-ABCDEF' # botfather'dan alınan token
adminchatid=[123456789] # yönetici şahısların chatid'si
memorythreshold=85  # uyarı veriecek bellek yüzdesi
interval=120  # verilerin yenilenme sıklığı

blacklist = [line.strip() for line in open("/home/erena/Belgeler/monitorbot/blacklist.txt", 'r')]

bashid=[]
uploadid=[]
def cputemp():
    drc=os.popen("""sensors -j | jq --raw-output '."coretemp-isa-0000"."Core 0" | to_entries | .[] | select(.key | match("input")) | .value'""").read()
    return int(drc)
def status():
    battery=psutil.sensors_battery()
    memory=psutil.virtual_memory()
    disk=psutil.disk_usage('/')
    zaman="%.2f saattir çalışıyorum" % (((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()) / 3600)
    pil="prize takılı"+("yım" if battery.power_plugged else " değilim")+f", %{round(battery.percent)} şarjım var"
    bellek="belleğimin %" + str(memory.percent) + "sini (" + str(round(memory.used / 1000000000,2)) +" gb) kullanıyorum"
    diskKull="diskimin %" + str(disk.percent) + "sini (" + str(round(disk.used / 1000000000,2)) +" gb) kullanıyorum"
    cpu=f"işlemcimi %{str(psutil.cpu_percent())} kullanyorum. (bu arada kendisi {cputemp()} °C)"
    pids=psutil.pids()
    pidsreply='işlemcimi en çok kullanan işlemler şunlar:\n'
    procs={}
    for pid in pids:
        p=psutil.Process(pid)
        try:
            pmem=p.memory_percent()
            if pmem>0.5:
                if p.name() in procs:
                    procs[p.name()] += pmem
                else:
                    procs[p.name()]=pmem
        finally:
            sortedprocs=sorted(procs.items(), key=operator.itemgetter(1), reverse=True)
    for proc in sortedprocs:
        pidsreply += proc[0] + " %" + ("%.2f" % proc[1]) + "\n"
    return f"{zaman}\n{pil}\n{bellek}\n{diskKull}\n{cpu}\n\n{pidsreply}"

def clearid(chat_id):
    if chat_id in bashid: bashid.remove(chat_id)
    if chat_id in uploadid: uploadid.remove(chat_id)

class BotClass(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(BotClass, self).__init__(*args, **kwargs)
        self._answerer=telepot.helper.Answerer(self)
        self._message_with_inline_keyboard=None
    def on_chat_message(self, msg):
        content_type, _, chat_id=telepot.glance(msg)
        if chat_id in adminchatid:
            if content_type == 'text':
                if msg['text'] == "exit" and (chat_id in bashid or chat_id in uploadid):
                    clearid(chat_id)
                    bot.sendMessage(chat_id, "tabi.", reply_markup={'hide_keyboard': True})
                elif chat_id in bashid:
                    bot.sendChatAction(chat_id, 'typing')
                    p=Popen(msg['text'], shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    output=p.stdout.read()
                    if output != b'':
                        bot.sendMessage(chat_id, output, disable_web_page_preview=True)
                    else:
                        bot.sendMessage(chat_id, "çalıştı ama çıktı vermedi.")
                elif chat_id in uploadid:
                    bot.sendChatAction(chat_id, 'typing')
                    try:
                        bot.sendDocument(chat_id,open(msg['text'],'rb'))
                    except:
                        bot.sendMessage(chat_id, "yok ki öyle bişey")
                    clearid(chat_id)
                elif msg['text'] == '/start': bot.sendMessage(chat_id,"merhaba")
                elif msg['text'] == '/status':
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, status(), disable_web_page_preview=True)
                elif msg['text'] == "/uyudunmu": bot.sendMessage(chat_id, "hayır :)")
                elif msg['text'] == "/uzayli":
                    bot.sendChatAction(chat_id, 'typing')
                    os.popen("play /home/erena/Belgeler/scifi.mp3 > /dev/null 2>&1")
                    bot.sendMessage(chat_id, "peki")
                elif msg['text'] == "/ip":
                    bot.sendChatAction(chat_id, 'typing')
                    os.system("""echo "[`date`] `/home/erena/Belgeler/duckdns.sh`" > /tmp/duckdns.log""")
                    bot.sendMessage(chat_id, "ip adresim bu: "+os.popen("curl ifconfig.me -s").read()+"\n\nayrıca insanolanbiri.duckdns.org'u da güncelledim, onun çıktısı da bu:\n"+os.popen("cat /tmp/duckdns.log").read())
                elif msg['text'] == "/bash":
                    bot.sendMessage(chat_id, "çalıştıracağın komutları gönder. canın sıkıldığında `exit` yaz.")
                    bashid.append(chat_id)
                elif msg['text'] == "/upload":
                    bot.sendMessage(chat_id, "hangi dosyayı göndereyim?")
                    uploadid.append(chat_id)
                elif "teşekkürler" in msg['text'].lower(): bot.sendMessage(chat_id, "bir şey değil :)")
                elif msg['text'].lower() == "boşver" or msg['text'].lower() == "boş ver": bot.sendMessage(chat_id, "peki")
                else: bot.sendMessage(chat_id, "anlamadım?")
        else:
            try:
                if msg['text'] == '/start': bot.sendMessage(chat_id,"merhaba")
                elif msg['text'] == '/status':
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, status(), disable_web_page_preview=True)
                elif msg['text'] == "/uyudunmu": bot.sendMessage(chat_id, "hayır :)")
                elif msg['text'] == "/bash" or msg['text'] == "/upload" or msg['text'] == "/ip": bot.sendMessage(chat_id, "olmaz")
                elif "teşekkürler" in msg['text'].lower(): bot.sendMessage(chat_id, "bir şey değil :)")
                elif any(kelime in msg['text'].lower() for kelime in blacklist): bot.sendMessage(chat_id, "bana niye küfrediyosun afasdsfkgjhgklhfkljfdcjcvrht")
                elif msg['text'] == "31": bot.sendMessage(chat_id, "çok komik\n\ngülmekten ölüyorum şu an")
                elif msg['text'].lower() == "boşver" or msg['text'].lower() == "boş ver": bot.sendMessage(chat_id, "peki")
                else: bot.sendMessage(chat_id, "anlamadım?")
            except:
                bot.sendMessage(chat_id, "büyük başarısızlıklar sözkonusu")
            finally:
                time.sleep(0.5)
                bot.sendMessage(chat_id, f"ayrıca burada ne işin var {(msg.get('from')).get('first_name').lower()}?")
                os.popen(f"echo {msg} >> /home/erena/Belgeler/monitorbot/telegram.log")
bot=BotClass(TOKEN)
bot.message_loop()
t=0
while True:
    if t == interval:
        t=0
        memck=psutil.virtual_memory()
        battery=psutil.sensors_battery()
        mempercent=memck.percent
        if cputemp() >= 85:
            for adminid in adminchatid: bot.sendMessage(adminid, f"işlemcim çok sıcak, {cputemp()} °C")
        if mempercent>memorythreshold: 
            for adminid in adminchatid: bot.sendMessage(adminid, "benim bellek doldu sanırım bi baksana\n%.2f gb. az bence."%(memck.available / 1000000000))
        if battery.power_plugged==False and battery.percent<=25:
            for adminid in adminchatid: bot.sendMessage(adminid, f"pilim bitmek üzere.\n%{round(battery.percent)} şarjım kaldı.")
    time.sleep(10)
    t += 10

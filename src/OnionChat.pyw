import Tkinter, socks, datetime, time, socket, ConfigParser, ast, base64, pygame
from Crypto.Cipher import AES
from thread import start_new_thread
import stem.process

config = ConfigParser.RawConfigParser()
config.read('OnionChat.ini')
onions = []

with open("contacts.ini") as fp:
    onions = [ast.literal_eval(line) for line in fp if line.strip()]

tor_ip = config.get('Settings', 'tor_ip')
tor_port = int(config.get('Settings', 'tor_port'))
chat_port = int(config.get('Settings', 'chat_port'))
my_chatname = config.get('Settings', 'my_chatname')
secret = config.get('Settings', 'aes_key')
aes_encryption = config.getboolean('Settings', 'enable_encryption')

BLOCK_SIZE = 32
PADDING = '{'
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
cipher = AES.new(secret)

tor_process = stem.process.launch_tor(
    tor_cmd='.\\Tor\\tor.exe', torrc_path='.\\Tor\\torrc.txt',
     take_ownership = True ) #completion_percent = 0,

def onion_send(onion, str, curd):
    try:
        s = socks.socksocket();
        s.setproxy(socks.PROXY_TYPE_SOCKS5, tor_ip, tor_port);
        s.connect((onion[0], chat_port));
        if aes_encryption:
            s.send(EncodeAES(cipher, (curd + str + '\n').encode("utf-8")));
        else:
            s.send((curd + str + '\n').encode("utf-8"));
        s.close();
    except (RuntimeError, TypeError, NameError):
        pass


def text_send(onion,str):
    try:
        s = socks.socksocket();
        s.setproxy(socks.PROXY_TYPE_SOCKS5, tor_ip, tor_port);
        s.connect((onion[0], chat_port));
        if aes_encryption:
            s.send(EncodeAES(cipher, (str).encode("utf-8")));
        else:
            s.send((str).encode("utf-8"));
        s.close();
    except (RuntimeError, TypeError, NameError):
        pass

def onion_status(env):
    onlinestr = '...loading online status...'
    online = 1
    while True:
        app.labelVariable.set(onlinestr)
        onlinestr = ''
        for onion in onions:
            try:
                s = socks.socksocket();
                s.setproxy(socks.PROXY_TYPE_SOCKS5, tor_ip, tor_port);
                s.settimeout(5)
                s.connect((onion[0], chat_port));
                if online > 0:
                    s.send(EncodeAES(cipher, ("[" + my_chatname + " is online]\n").encode("utf-8")));
                    online = 0
                s.close();
                onlinestr += onion[1] + ' online \n'
            except:
                pass

def onion_rev():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('localhost', chat_port))
    serversocket.listen(5)
    while True:
        connection, address = serversocket.accept()
        buf = connection.recv(50000)
        if len(buf) > 0:
            start_new_thread(play_sound, ());
            if aes_encryption:
                try:
                    app.T.insert(Tkinter.END, DecodeAES(cipher, (buf)))
                except (RuntimeError, TypeError, NameError, ValueError):
                    app.T.insert(Tkinter.END, (buf).decode("utf-8"))
            else:
                app.T.insert(Tkinter.END, buf)
        app.T.yview(Tkinter.END)

def offline():
    tor_process.kill()
    app.destroy()

def play_sound():
    if app.sound_on:
        pygame.mixer.init()
        pygame.mixer.music.load("echo.wav")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

class simpleapp_tk(Tkinter.Tk):

    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid( )
        self.entryVariable = Tkinter.StringVar()
        self.S = Tkinter.Scrollbar(self)
        self.T = Tkinter.Text(self)  # , height=20, width=50
        self.S.config(command=self.T.yview)
        self.T.config(yscrollcommand=self.S.set)
        self.T.grid(column=0, row=0, sticky='EW')
        self.entry = Tkinter.Entry(self, textvariable=self.entryVariable)
        self.entry.grid(column=0, row=1, sticky='EW')
        self.entry.bind("<Return>", self.OnPressEnter)
        self.entryVariable.set(u"")
        self.button = Tkinter.Button(self, text=u"Send",
                                     command=self.OnButtonClick)
        self.button.grid(column=1, row=1)
        self.labelVariable = Tkinter.StringVar()
        self.label = Tkinter.Label(self, textvariable=self.labelVariable,
                                   anchor="w", fg="black", bg="white")
        self.label.grid(column=1, row=0, columnspan=2)
        self.VC = Tkinter.Checkbutton(self, text="Encryption", command=self.toggle_encryption)
        self.VC.grid(column=1, row=0, sticky="NW")
        self.SoundCheck = Tkinter.IntVar;
        self.SC = Tkinter.Checkbutton(self, text = "Sound", command=self.toggle_sound, onvalue=1, offvalue=0 )
        self.SC.grid(column=1, row=0, sticky="SW")
        self.sound_on = False
        self.grid_columnconfigure(0, weight=1)
        self.resizable(False, False)
        self.update()
        self.geometry('800x415-5+40')
        self.entry.focus_set()

        self.protocol("WM_DELETE_WINDOW", offline)
        self.SC.toggle();
        self.toggle_sound();
        if aes_encryption:
            self.VC.toggle();


        start_new_thread(onion_rev, ());
        start_new_thread(onion_status, (self.entryVariable,));

    def OnButtonClick(self):
        self.OnPressEnter(0)

    def toggle_sound(self):
        self.sound_on = not self.sound_on

    def toggle_encryption(self):
        global aes_encryption
        aes_encryption = not aes_encryption

    def OnPressEnter(self, event):
        curdate = str(datetime.datetime.fromtimestamp(time.time()).strftime('[%H:%M:%S] ')) + my_chatname + ': '
        for onion in onions:
            start_new_thread(onion_send, (onion, self.entryVariable.get(), curdate));
        self.entryVariable.set(u"")
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('Onion Chat')
    app.mainloop()
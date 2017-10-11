#!/usr/bin/python2
"""
    Qt5 GUI front-end to the Lightron chat.
    Copyright (C) 2016-2017 Glen Harpring
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5 import QtCore, QtGui, QtWidgets


#from HTMLParser import HTMLParser
import sys,os,httplib,urllib,urllib2,math,time,json,traceback
global getChat,useragent
getChat = httplib.HTTPSConnection('lightron.org')
class ChatBrowser(QtWidgets.QTextBrowser):
	def loadResource(self,type,name):
		if type == 1:
			return urllib2.urlopen(str(name.toString())).read()
		if type == 2 or type == 3:
			if not str(name.toString()) in self.cache:
				if 'https://lightron.org/inc/images/flags/' in name.toString():
					flag = name.toString().split("https://lightron.org/inc/images/flags/")[1].split(".")[0];
					self.cache[str(name.toString())] = QtGui.QImage("/usr/share/locale/l10n/"+flag+"/flag.png")
				else:
					print "Downloading "+name.toString()+" of type "+str(type)+" into memory..."
					try:
						self.cache[str(name.toString())] = QtGui.QImage.fromData(urllib2.urlopen(str(name.toString())).read(),os.path.splitext(name.toString())[1].upper())
						print "[DONE]"
					except:
						print "[FAIL]"
						return False
			return self.cache[str(name.toString())]
useragent = "Mozilla/5.0 QTextBrowser/Qt5 LTChatGUI/beta";
class main(object):
	def setup(self, MainWindow):
		global USERNAME,WHOSONLINE,curronline,PING,CHATS,wait,COOKIE,mself,FIRST
		mself=self
		COOKIE="";USERNAME = "Guest";WHOSONLINE = curronline = "";CHATS = "Loading...";PING = '?';wait=3;self.prevCHATS="";FIRST=True;
		self.thread = QtCore.QThread() #Create a generic thread for now
		self.chatstyle = """
html
{
	width: 293px;
	
	font-size: 11px;
	font-family: verdana, sans-serif;
	line-height: 18px;
}

.message
{
	width: 205px;
	float: left;
}

.send
{
	width: 60px;
	padding: 0px;
	margin-top: 2px;
}

.message
{
	width: 98%;
	border-bottom: 1px solid #CCC;
}

.user
{
	font-size: 12px;
	font-weight: bold;
	font-family: Arial;
	padding-right:3px;
}

.timestamp
{
	color: #555;
	font-size: 10px;
	margin-left: 30px;
}

.delete
{
	float: right;
	margin-right: 10px;
}"""
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(335,400)
		MainWindow.setWindowTitle("Lightron Chat GUI")
		
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
		self.gridLayout.setObjectName("gridLayout")
		
		self.label = QtWidgets.QLabel(self.centralwidget)
		self.label.setObjectName("label")
		self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
		
		self.label_3 = QtWidgets.QLabel(self.centralwidget)
		self.label_3.setObjectName("label_3")
		self.gridLayout.addWidget(self.label_3, 1, 1, 1, 2)
		
		self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton_2.setObjectName("pushButton_2")
		self.pushButton_2.setText("Options")
		self.pushButton_2.clicked.connect(self.showOptions)
		self.gridLayout.addWidget(self.pushButton_2, 1, 3, 1, 1)
		
		self.textBrowser = ChatBrowser(self.centralwidget)
		self.textBrowser.setObjectName("textBrowser")
		self.textBrowser.cache = {}
		self.textBrowser.setOpenExternalLinks(True)
		self.gridLayout.addWidget(self.textBrowser, 2, 0, 1, 4)
		
		self.pushButton = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton.setObjectName("pushButton")
		self.pushButton.setText("Send")
		self.pushButton.clicked.connect(self.send)
		self.gridLayout.addWidget(self.pushButton, 3, 3, 1, 1)
		
		self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
		self.lineEdit.setObjectName("lineEdit")
		self.gridLayout.addWidget(self.lineEdit, 3, 0, 1, 3)
		
		self.label_2 = QtWidgets.QLabel(self.centralwidget)
		self.label_2.setObjectName("label_2")
		self.label_2.setOpenExternalLinks(True)
		self.gridLayout.addWidget(self.label_2, 5, 0, 1, 4)
		MainWindow.setCentralWidget(self.centralwidget)
		
		self.updateTimer = QtCore.QTimer(MainWindow)
		self.updateTimer.timeout.connect(self.update)
		self.updateTimer.start(4000)
		self.updated();self.update()
		
		QtCore.QMetaObject.connectSlotsByName(MainWindow)
	def update(self):
		if not self.thread.isRunning():
			self.prevCHATS = CHATS
			self.thread = UpdatingChat()
			self.thread.finished.connect(self.updated)
			self.thread.start()
	def send(self):
		global COOKIE
		postdata = urllib.urlencode({'input':str(self.lineEdit.text())})
		try:
			con = httplib.HTTPSConnection("lightron.org")
			con.request("POST","/Ajax/Chat",postdata,{"User-Agent":useragent,"Cookie":COOKIE,"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"})  
			ChatsResponse = con.getresponse()
		except:
			pass;
		self.lineEdit.setText("")
		self.updated();self.update()
	def showOptions(self):
		self.options = QtWidgets.QMenu()
		if USERNAME == "Guest":
			self.optionsLogin = self.options.addAction("Login")
			self.optionsLogin.triggered.connect(self.login)
		else:
			self.optionsProfile = self.options.addAction("Profile")
			self.optionsProfile.triggered.connect(self.profile)
			self.optionsLogout = self.options.addAction("Logout")
			self.optionsLogout.triggered.connect(self.logout)
		self.options.addSeparator()
		self.optionsStats = self.options.addAction("Statitics")
		self.optionsStats.triggered.connect(self.stats)
		self.optionsAbout = self.options.addAction("About")
		self.optionsStats.triggered.connect(self.about)
		#self.optionsToC = self.options.addAction("License Agreement")
		#self.optionsToC.triggered.connect(self.gpl)
		
		self.options.exec_(QtGui.QCursor().pos())
	def updated(self):
		global USERNAME,COOKIE
		if USERNAME == "Guest":
			self.label.setText("Please sign in to chat.")
			out=True
		else:
			self.label.setText("Hello, "+USERNAME+"!")
			out=False
		self.pushButton.setHidden(out)
		self.lineEdit.setHidden(out)
		self.label_3.setText(str(PING)+"ms")
		self.label_2.setText(WHOSONLINE)
		self.label_2.setToolTip(curronline)
		if CHATS == "":
				print "Returned chat appears to be blank."
			
		elif not self.prevCHATS == CHATS:
			self.textBrowser.setHtml('<style type="text/css">'+self.chatstyle+'</style>\n<div class="chat"><div class="chat-output">'+str(CHATS)+"</div></div>")
	def login(self):
		login()
	def completeLogin(self):
		global USERNAME, COOKIE
		postdata = urllib.urlencode({'username':loginDia.lineEdit.text(),'password':loginDia.lineEdit_2.text()}) 
		try:
			con = httplib.HTTPSConnection("lightron.org")
			con.request("POST","/Authentication",postdata,{"User-Agent":useragent,"Cookie":COOKIE,"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}) 
		except:
			QtWidgets.QMessageBox.critical(MainWindow,'LTChat','Unable to login. Are you connected to the internet?',QtWidgets.QMessageBox.Ok)
			return;
		data = con.getresponse()
		datar = str(data.read())
		print datar
		if not datar == "1":
			if not datar.isdigit():
				QtWidgets.QMessageBox.critical(MainWindow,'LTChat','Returned "'+datar.rstrip('\n')+'"',QtWidgets.QMessageBox.Ok)
			else:
				QtWidgets.QMessageBox.warning(MainWindow,'LTChat','Username and/or password invalid.',QtWidgets.QMessageBox.Ok)
				loginDia.lineEdit_2.selectAll()
		else:
			#self.lineEdit.setText(str(data))
			#COOKIE = data.getheader('Cookie') 
			USERNAME = loginDia.lineEdit.text()
			loginDia.hide()
			self.update()
	def logout(self):
		global USERNAME, COOKIE
		USERNAME = "Guest";COOKIE="";
		self.updated()
	def profile(self):
		profile()
	def stats(self):
		return;
	def about(self):
		return;
	def changepass(self):
		return;
class LoginDialog(QtWidgets.QDialog):
	def __init__(self):
		super(LoginDialog,self).__init__()
		self.setup()
	def setup(self):
		self.setWindowTitle("Login to LTChat")
		self.resize(335,80)
		
		self.gridLayout = QtWidgets.QGridLayout(self)
		self.gridLayout.setObjectName("gridLayout")
		spacerItem = QtWidgets.QSpacerItem(260, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
		self.pushButton = QtWidgets.QPushButton(self)
		self.pushButton.setObjectName("pushButton")
		self.pushButton.setText("Login!")
		self.pushButton.setShortcut("Enter, Return")
		self.pushButton.clicked.connect(mself.completeLogin)
		self.gridLayout.addWidget(self.pushButton, 2, 1, 1, 1)
		self.lineEdit = QtWidgets.QLineEdit(self)
		self.lineEdit.setObjectName("lineEdit")
		self.lineEdit.setPlaceholderText("Username")
		self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 2)
		self.lineEdit_2 = QtWidgets.QLineEdit(self)
		self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
		self.lineEdit_2.setObjectName("lineEdit_2")
		self.lineEdit_2.setPlaceholderText("Password")
		self.gridLayout.addWidget(self.lineEdit_2, 1, 0, 1, 2)

		QtCore.QMetaObject.connectSlotsByName(self)
		
class profileDialog(QtWidgets.QDialog):
	def __init__(self):
		super(profileDialog,self).__init__()
		self.setup()
	def setup(self):
		self.setWindowTitle("My Profile - LTChat")
		self.resize(335,80)
		try:
			con = httplib.HTTPSConnection("lightron.org")
			con.request("POST","/Authentication",urllib.urlencode({'action':'userControlPanel'}),{"User-Agent":useragent,"Cookie":COOKIE,"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}) 
		except:
			QtWidgets.QMessageBox.critical(MainWindow,'LTChat','Unable to login. Are you connected to the internet?',QtWidgets.QMessageBox.Ok)
			return;
		self.gridLayout = QtWidgets.QGridLayout(self)
		self.gridLayout.setObjectName("gridLayout")
		spacerItem = QtWidgets.QSpacerItem(260, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
		self.pushButton = QtWidgets.QPushButton(self)
		self.pushButton.setObjectName("pushButton")
		self.pushButton.setText("Close")
		self.pushButton.setShortcut("Enter, Return")
		self.pushButton.clicked.connect(self.close)
		self.gridLayout.addWidget(self.pushButton, 2, 1, 1, 1)
		self.profileImage = QtWidgets.QLabel()
		image = "https://lightron.org/inc/images/avatar/101.png"
		self.proImage = QtGui.QPixmap.fromImage(mself.textBrowser.loadResource(2,QtCore.QUrl(image)))
		self.profileImage.setPixmap(self.proImage)
		self.gridLayout.addWidget(self.profileImage, 0, 0, 1, 2)
		QtCore.QMetaObject.connectSlotsByName(self)


class UpdatingChat(QtCore.QThread):
	def run(self):
		global USERNAME,WHOSONLINE,curronline,PING,CHATS,wait,getChat,FIRST,COOKIE
		if FIRST:
			try:
				con = httplib.HTTPSConnection("lightron.org")
				con.request("GET","/","",{"User-Agent":useragent})
				data = con.getresponse()
			except httplib.ssl.SSLError:
				ex_type, ex, tb = sys.exc_info()
				CHATS = "<body><p><strong>Error:</strong> SSL Certificate Error!</p> <p>"+traceback.format_exc(tb)+"</p></body>"
				PING = "inf"; WHOSONLINE = ""; curronline = "can't tell"
				del tb; return;
			except:
				CHATS = "<p><strong>Error:</strong> Loading failed, is your internet connected?</p>"
				PING = "inf"; WHOSONLINE = ""; curronline = "can't tell"
				return;
			FIRST = False;
			cookieheader = data.getheader('Set-Cookie');
			if cookieheader is None:
				cookieheader = "";
			COOKIE = cookieheader.split(" ")[0]
		wait=wait+1
		defheader = {"User-Agent":useragent,"Cookie":COOKIE,"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8","X-Requested-With":"XMLHttpRequest"}
		getChat = httplib.HTTPSConnection('lightron.org')
		pullr = urllib.urlencode({"action":"pull","max-id":"0"})
		try:
			timebefore=time.time(); getChat.request("POST","/Ajax/Chat",pullr,defheader); timeafter=time.time()
			PING = int((float(timeafter)-float(timebefore))*1000)
		except:
			return;
		try:
			ChatsRespons = getChat.getresponse().read()
			#print ChatsRespons;
		except:
			if CHATS is "": CHATS = "<p><strong>Error:</strong> Unable to receive chats. Is your internet connection working?</p>"
			PING = "inf"; WHOSONLINE = ""; curronline = "can't tell"
		try:
			ChatsResponse = json.loads(ChatsRespons)
			#print ChatsResponse;
		except: 
			return
		thechatshtm = ChatsResponse["output"].replace("margin: 0px 4px -1px 0px;","margin-right:4px;margin-bottom:-1px;")
		#WHOSONLINE = ChatsResponse["chatters"].replace("padding: 0px 4px;\">","\"> ")
		WHOSONLINE = ChatsResponse["online"]
		if len(ChatsResponse["online"].split(":")) > 1:
			curronline = ChatsResponse["online"].split(":")[1].replace("padding: 0px 4px;\">","\"> ")
		else:
			curronline = "nobody"
		CHATS = str(thechatshtm.replace("<a href=\"/","<a href=\"https://lightron.org/").replace("<img src=\"/","<img src=\"https://lightron.org/").replace('class=\"avatar\"','" width="12" height="12"').replace('style=\"height: 10px; margin: 0px 4px -1px 0px;\"','"width="21" height="14"')) 
		#self.updated()
		#print "Updated!"

		
def login():
	global loginDia
	loginDia = LoginDialog()
	loginDia.setWindowModality(QtCore.Qt.ApplicationModal)
	loginDia.show()
def profile():
	global profileDia
	profileDia = profileDialog()
	profileDia.setWindowModality(QtCore.Qt.ApplicationModal)
	profileDia.show()

app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = main()
ui.setup(MainWindow)
MainWindow.show()
sys.exit(app.exec_())

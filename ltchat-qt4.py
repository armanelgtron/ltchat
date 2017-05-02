#!/usr/bin/python2
"""
    Qt4 GUI front-end to the Lightron chat.
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
try:
	from PyQt4 import QtCore, QtGui
except ImportError: #Fallback to PySide is basically PyQt4 and is still included in the latest Ubuntu releases.
	from PySide import QtCore, QtGui
from HTMLParser import HTMLParser
import sys,os,httplib,urllib,urllib2,math,time,json
global getChat
getChat = httplib.HTTPSConnection('lightron.org')
class ChatBrowser(QtGui.QTextBrowser):
	def loadResource(self,type,name):
		if type == 1:
			return urllib2.urlopen(str(name.toString())).read()
		if type == 2 or type == 3:
			if not str(name.toString()) in self.cache:
				print "Downloading "+name.toString()+" of type "+str(type)+" into memory..."
				try:
					self.cache[str(name.toString())] = urllib2.urlopen(str(name.toString())).read()
					print "[DONE]"
				except:
					print "[FAIL]"
					return False
			if type == 2:
				return QtGui.QImage.fromData(self.cache[str(name.toString())],os.path.splitext(name.toString())[1].upper())
			elif type == 3:
				return self.cache[str(name.toString())]

class main(object):
	def setup(self, MainWindow):
		global USERNAME,WHOSONLINE,PING,CHATS,wait,COOKIE,mself,FIRST
		mself=self
		COOKIE="";USERNAME = "Guest";WHOSONLINE = "";CHATS = "Loading...";PING = '?';wait=3;self.prevCHATS="";FIRST=True;
		self.thread = QtCore.QThread() #Create a generic thread for now
		self.chatstyle = """
.chat
{
	width: 293px;
	
	font-size: 11px;
	font-family: verdana, sans-serif;
	line-height: 18px;
}

.chat .input .message
{
	width: 205px;
	float: left;
}

.chat .input .send
{
	width: 60px;
	padding: 0px;
	margin-top: 2px;
}

.chat .output
{
	clear: both;
	margin-top: 5px;
	
	width: 100%;
	height: 350px;
	
	overflow-x: hidden;
	overflow-y: scroll;
}

.chat .output img
{
	max-width: 100%;
	max-height: 200px;
}

.chat .message
{
	width: 98%;
	border-bottom: 1px solid #CCC;
}

.chat .user
{
	font-size: 12px;
	font-weight: bold;
	font-family: Arial;
	padding-right:3px;
}

.chat .timestamp
{
	color: #555;
	font-size: 10px;
	margin-left: 30px;
}

.chat .delete
{
	float: right;
	margin-right: 10px;
}"""
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(335,400)
		MainWindow.setWindowTitle("Lightron Chat GUI")
		
		self.centralwidget = QtGui.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.gridLayout = QtGui.QGridLayout(self.centralwidget)
		self.gridLayout.setObjectName("gridLayout")
		
		self.label = QtGui.QLabel(self.centralwidget)
		self.label.setObjectName("label")
		self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
		
		self.label_3 = QtGui.QLabel(self.centralwidget)
		self.label_3.setObjectName("label_3")
		self.gridLayout.addWidget(self.label_3, 1, 1, 1, 2)
		
		self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
		self.pushButton_2.setObjectName("pushButton_2")
		self.pushButton_2.setText("Options")
		QtCore.QObject.connect(self.pushButton_2,QtCore.SIGNAL("clicked()"),self.showOptions)
		self.gridLayout.addWidget(self.pushButton_2, 1, 3, 1, 1)
		
		self.textBrowser = ChatBrowser(self.centralwidget)
		self.textBrowser.setObjectName("textBrowser")
		self.textBrowser.cache = {}
		self.textBrowser.setOpenExternalLinks(True)
		self.gridLayout.addWidget(self.textBrowser, 2, 0, 1, 4)
		
		self.pushButton = QtGui.QPushButton(self.centralwidget)
		self.pushButton.setObjectName("pushButton")
		self.pushButton.setText("Send")
		QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"),self.send)
		self.gridLayout.addWidget(self.pushButton, 3, 3, 1, 1)
		
		self.lineEdit = QtGui.QLineEdit(self.centralwidget)
		self.lineEdit.setObjectName("lineEdit")
		self.gridLayout.addWidget(self.lineEdit, 3, 0, 1, 3)
		
		self.label_2 = QtGui.QLabel(self.centralwidget)
		self.label_2.setObjectName("label_2")
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
		con = httplib.HTTPSConnection("lightron.org")
		con.request("POST","/Chat",postdata,{"User-Agent":"Mozilla/5.0 QTextBrowser/Qt4 LTChatGUI/beta","Cookie":COOKIE,"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"})  
		ChatsResponse = con.getresponse()
		self.lineEdit.setText("")
		self.updated();self.update()
	def showOptions(self):
		self.options = QtGui.QMenu()
		if USERNAME == "Guest":
			self.optionsLogin = self.options.addAction("Login")
			QtCore.QObject.connect(self.optionsLogin,QtCore.SIGNAL("triggered()"),self.login)
		else:
			self.optionsProfile = self.options.addAction("Profile")
			QtCore.QObject.connect(self.optionsProfile,QtCore.SIGNAL("triggered()"),self.profile)
			self.optionsLogout = self.options.addAction("Logout")
			QtCore.QObject.connect(self.optionsLogout,QtCore.SIGNAL("triggered()"),self.logout)
		self.options.addSeparator()
		#self.optionsToC = self.options.addAction("License Agreement")
		#QtCore.QObject.connect(self.optionsToC,QtCore.SIGNAL("triggered()"),self.gpl)
		
		self.options.exec_(QtGui.QCursor().pos())
	def gpl(self):
		webbrowser.open('https://www.gnu.org/licenses/gpl-3.0-standalone.html')
	def updated(self):
		global USERNAME, COOKIE
		if USERNAME == "Guest":
			self.label.setText("Please sign in to chat.")
			out=True
		else:
			self.label.setText("Hello, "+USERNAME+"!")
			out=False
		self.pushButton.setHidden(out)
		self.lineEdit.setHidden(out)
		#self.label_3.setText("")
		self.label_2.setText(""+WHOSONLINE+"; "+str(PING)+"ms")
		if CHATS == "":
				print "Returned chat appears to be blank."
			
		elif not self.prevCHATS == CHATS:
			self.textBrowser.setHtml('<style type="text/css">'+self.chatstyle+'</style>\n<div class="chat"><div class="chat-output">'+str(CHATS)+"</div></div>")
	def login(self):
		login()
	def completeLogin(self):
		global USERNAME, COOKIE
		postdata = urllib.urlencode({'loginType':'login','username':loginDia.lineEdit.text(),'password':loginDia.lineEdit_2.text()}) 
		con = httplib.HTTPSConnection("lightron.org")
		con.request("POST","/Authentication",postdata,{"User-Agent":"Mozilla/5.0 QTextBrowser/Qt4 LTChatGUI/beta","Cookie":COOKIE,"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"}) 
		data = con.getresponse()
		datar = str(data.read())
		if not datar == "1":
			QtGui.QMessageBox.warning(MainWindow,'LTChat','Username and/or password invalid.',QtGui.QMessageBox.Ok)
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
	def changepass(self):
		return;
class LoginDialog(QtGui.QDialog):
	def __init__(self):
		super(LoginDialog,self).__init__()
		self.setup()
	def setup(self):
		self.setWindowTitle("Login to LTChat")
		self.resize(335,80)
		
		self.gridLayout = QtGui.QGridLayout(self)
		self.gridLayout.setObjectName("gridLayout")
		spacerItem = QtGui.QSpacerItem(260, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
		self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
		self.pushButton = QtGui.QPushButton(self)
		self.pushButton.setObjectName("pushButton")
		self.pushButton.setText("Login!")
		self.pushButton.setShortcut("Enter, Return")
		QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"),mself.completeLogin)
		self.gridLayout.addWidget(self.pushButton, 2, 1, 1, 1)
		self.lineEdit = QtGui.QLineEdit(self)
		self.lineEdit.setObjectName("lineEdit")
		self.lineEdit.setPlaceholderText("Username")
		self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 2)
		self.lineEdit_2 = QtGui.QLineEdit(self)
		self.lineEdit_2.setEchoMode(QtGui.QLineEdit.Password)
		self.lineEdit_2.setObjectName("lineEdit_2")
		self.lineEdit_2.setPlaceholderText("Password")
		self.gridLayout.addWidget(self.lineEdit_2, 1, 0, 1, 2)

		QtCore.QMetaObject.connectSlotsByName(self)
		
class profileDialog(QtGui.QDialog):
	def __init__(self):
		super(profileDialog,self).__init__()
		self.setup()
	def setup(self):
		self.setWindowTitle("My Profile - LTChat")
		self.resize(335,80)
		
		self.gridLayout = QtGui.QGridLayout(self)
		self.gridLayout.setObjectName("gridLayout")
		spacerItem = QtGui.QSpacerItem(260, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
		self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
		self.pushButton = QtGui.QPushButton(self)
		self.pushButton.setObjectName("pushButton")
		self.pushButton.setText("Close")
		self.pushButton.setShortcut("Enter, Return")
		QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"),self.close)
		self.gridLayout.addWidget(self.pushButton, 2, 1, 1, 1)
		self.profileImage = QtGui.QLabel()
		image = "https://lightron.org/inc/images/avatar/101.png"
		self.proImage = QtGui.QPixmap.fromImage(mself.textBrowser.loadResource(2,QtCore.QUrl(image)))
		self.profileImage.setPixmap(self.proImage)
		self.gridLayout.addWidget(self.profileImage, 0, 0, 1, 2)
		QtCore.QMetaObject.connectSlotsByName(self)


class UpdatingChat(QtCore.QThread):
	def run(self):
		global USERNAME,WHOSONLINE,PING,CHATS,wait,getChat,FIRST,COOKIE
		if FIRST:
			FIRST = False;
			con = httplib.HTTPSConnection("lightron.org")
			con.request("GET","/","",{"User-Agent":"Mozilla/5.0 QTextBrowser/Qt4 LTChatGUI/beta"})
			data = con.getresponse()
			COOKIE = data.getheader('Set-Cookie').split(" ")[0]
		wait=wait+1
		defheader = {"User-Agent":"Mozilla/5.0 QTextBrowser/Qt4 LTChatGUI/beta","Cookie":COOKIE}
		getChat = httplib.HTTPSConnection('lightron.org')
		timebefore=time.time(); getChat.request("GET","/Chat","",defheader); timeafter=time.time()
		ChatsResponse = json.loads(getChat.getresponse().read())
		thechatshtm = ChatsResponse["output"]
		WHOSONLINE = ChatsResponse["chatters"]
		CHATS = str(thechatshtm.replace("<a href=\"/","<a href=\"https://lightron.org/").replace("<img src=\"/","<img src=\"https://lightron.org/").replace('class=\"avatar\"','" width="12" height="12"').replace('style=\"height: 10px; margin: 0px 4px -1px 0px;\"','"width="10" height="10"')) 
		PING = int((float(timeafter)-float(timebefore))*1000)
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

app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = main()
ui.setup(MainWindow)
MainWindow.show()
sys.exit(app.exec_())

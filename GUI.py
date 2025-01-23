from tabnanny import check
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor, QBrush, QFont,QPixmap, QIcon
from PyQt5.QtCore import Qt
import PIL.Image as Image
import io
import base64
import random
import time
import json

class TreeView:
  def __init__(self, tabs, tab_name, tabIdx, sio, pcList):
    #---Tabs 클래스에서 받아오는 변수
    self.tabs=tabs  
    self.tab_name=tab_name
    self.tabIdx=tabIdx
    self.sio=sio
    self.pcList=pcList  #이걸 굳이 객체 변수로 생성할 필요가 있나? 그냥 전달받은 그대로 사용해도 되지 않나..
    self.nameList=[]
    self.rowId={}
    self.cap_time_label={}

    with open(f"nameList\{self.tab_name}.json", 'r', encoding="utf-8") as file:
      jsonObj=json.load(file)
      self.nameList=jsonObj.get(f"{self.tab_name}_nameList")   

  def createTreeView(self):
    self.emitVal=[] #클라이언트로 보낼 데이터

    #---트리뷰 생성---
    self.treeWidget = QTreeWidget()
    self.treeWidget.headerItem().setTextAlignment(0, Qt.AlignHCenter)
    self.treeWidget.headerItem().setTextAlignment(1, Qt.AlignHCenter)
    self.treeWidget.headerItem().setTextAlignment(2, Qt.AlignHCenter)
    self.treeWidget.setRootIsDecorated(False)
    self.treeWidget.setHeaderLabels(["  Name", "Status", "Log"] )
    self.treeWidget.setAlternatingRowColors(True)
    self.treeWidget.setMinimumHeight(195)
    self.treeWidget.setColumnWidth(0,120)
    self.treeWidget.setColumnWidth(1,100) 

    #---버튼---
    self.setAccount = QPushButton("Set Account")
    self.setAccount.setShortcut("F1")
    self.setAccount.setToolTip("단축키(F1)")
    
    self.btn1 = QPushButton('모닝')
    self.btn2 = QPushButton('우편')
    self.btn3 = QPushButton('사냥')
    self.btn4 = QPushButton('게임실행')
    self.btn5 = QPushButton('아이템분해')
    self.btn6 = QPushButton('이벤트상점')

    self.btn7 = QPushButton('격전의섬')
    self.btn8 = QPushButton('파괴된성채')
    self.btn9 = QPushButton('사망체크')
    self.btn10 = QPushButton('크루마')
    self.btn11 = QPushButton('스킬북분해')
    self.btn12 = QPushButton('아이템삭제')

    self.btn13 = QPushButton('시즌패스')
    self.btn14 = QPushButton('고급')
    self.btn15 = QPushButton('희귀')
    self.btn16 = QPushButton('일괄사용')
    self.btn17 = QPushButton('40M')
    self.btn18 = QPushButton('제한없음')

    self.client_status_label=QLabel("Client Status: Offline")
    self.client_status_label.setStyleSheet("color:red")

    self.statusChkLabel=QLabel('Status Check:OFF')
    self.statusChkLabel.setStyleSheet("color:red")

    for name in self.nameList:
      self.cap_time_label[name]=QLabel('00:00')

    # 이미지 캡쳐 이름 라벨 생성
    self.cap_names={}
    for name in self.nameList:
      self.capture_name=QLabel(f"{name[:4]}")
      self.cap_names[name]=self.capture_name
      
    # 이미지 캡쳐 픽스맵 생성
    self.pixMaps_1={}
    self.pixMaps_2={}
    for name in self.nameList:
      self.pixMap1=QLabel()
      self.pixMap2=QLabel()
      self.pixMaps_1[name]=self.pixMap1
      self.pixMaps_2[name]=self.pixMap2
    
    def setAccOnPressed():
      self.treeWidget.clear() #트리뷰 초기화
      self.rowId={} #setAcc할때마다 초기화, #key:케릭명, value:Row의 id값이 저장되어서 원하는 케릭명에 log를 추가할 수 있게 해줌
      self.client_status_Chk(0)
      
      keyChk=self.pcList.get(self.tab_name)
      if(keyChk==None):
        print("없는 키 검색")
      else:
        self.sio.emit("PC_status",self.nameList,to=self.pcList[self.tab_name])

      for name in self.nameList: #트리뷰 케릭명 세팅
          self.rowId[name] = QTreeWidgetItem(self.treeWidget,[name, "", ""])
          self.rowId[name].setCheckState(0,Qt.Checked)
          self.rowId[name].setTextAlignment(1,Qt.AlignHCenter)
          self.tabs.tabBar().setTabTextColor(self.tabIdx-1,QColor("black"))

    def postBox(): 
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[1]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def normalHunting():
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[2]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.emitVal.append(0) #옵션 인자 (일반사냥 옵션)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def morning():
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[3]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def dungeonFire(): 
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[4]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def menuClick():  
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[5]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]
    
    def dungeonLand():
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            self.nameList.append(name)
      self.emitVal=[6]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def deathChk():  
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[7]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.emitVal.append(2) #옵션 인자 (두 번째 이미지캡쳐 옵션)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def eventDungeon():
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[8]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def decomposeItem():  
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[9]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.emitVal.append(1) #옵션 인자 (우호도 옵션)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def decomposeBook():  
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[10]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.emitVal.append(1) #옵션 인자 (우호도 옵션)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def gameExec():
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            self.emitVal.append(name)
      self.sio.emit("execGame",self.emitVal, to=self.pcList[self.tab_name])
      self.emitVal=[] #초기화
    
    

    
    def greenItem():  
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[12]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.emitVal.append(2) #옵션 인자 (두 번째 이미지캡쳐 옵션)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def blueItem():  
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[13]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.emitVal.append(2) #옵션 인자 (두 번째 이미지캡쳐 옵션)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def useItem():  
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[14]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.emitVal.append(2) #옵션 인자 (두 번째 이미지캡쳐 옵션)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def seasonPass():
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[15]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def fourty():
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[23]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def unlimit():
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[24]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    def itemDel():
      nameList=[]
      for name in self.nameList:
        acc=self.rowId.get(name)
        if(acc==None):  
          print("없는 키 검색!!")
        else:
          if(acc.checkState(0)!=0): #(체크되어 있으면 2 아니면 0을 반환)
            nameList.append(name)
      self.emitVal=[26]  #실행할 함수 선택 데이터
      self.emitVal.append(nameList)
      self.sio.emit("statusChk",0,to=self.pcList[self.tab_name])  #상태체크 중지
      self.sio.emit("button_schedule",self.emitVal, to=self.pcList[self.tab_name])
      #초기화
      self.emitVal=[] 
      nameList=[]

    #버튼 연결
    self.setAccount.clicked.connect(setAccOnPressed)
    self.btn1.clicked.connect(morning)
    self.btn2.clicked.connect(postBox)
    self.btn3.clicked.connect(normalHunting)
    self.btn4.clicked.connect(gameExec)
    self.btn5.clicked.connect(decomposeItem)
    self.btn6.clicked.connect(menuClick)
    self.btn7.clicked.connect(dungeonFire)
    self.btn8.clicked.connect(dungeonLand)
    self.btn9.clicked.connect(deathChk)
    self.btn10.clicked.connect(eventDungeon)
    self.btn11.clicked.connect(decomposeBook)
    self.btn12.clicked.connect(itemDel)
    self.btn13.clicked.connect(seasonPass)
    self.btn14.clicked.connect(greenItem)
    self.btn15.clicked.connect(blueItem)
    self.btn16.clicked.connect(useItem)
    self.btn17.clicked.connect(fourty)
    self.btn18.clicked.connect(unlimit)



    #---버튼 레이아웃---
    self.btnBox_1 = QHBoxLayout()
    self.btnBox_1.addWidget(self.btn1)
    self.btnBox_1.addWidget(self.btn2)
    self.btnBox_1.addWidget(self.btn3)
    self.btnBox_1.addWidget(self.btn4)
    self.btnBox_1.addWidget(self.btn5)
    self.btnBox_1.addWidget(self.btn6)
    
    self.btnBox_2 = QHBoxLayout()
    self.btnBox_2.addWidget(self.btn7)
    self.btnBox_2.addWidget(self.btn8)
    self.btnBox_2.addWidget(self.btn9)
    self.btnBox_2.addWidget(self.btn10)
    self.btnBox_2.addWidget(self.btn11)
    self.btnBox_2.addWidget(self.btn12)

    self.btnBox_3 = QHBoxLayout()
    self.btnBox_3.addWidget(self.btn13)
    self.btnBox_3.addWidget(self.btn14)
    self.btnBox_3.addWidget(self.btn15)
    self.btnBox_3.addWidget(self.btn16)
    self.btnBox_3.addWidget(self.btn17)
    self.btnBox_3.addWidget(self.btn18)

    #---트리뷰 Layout---
    self.hTreeViewBox_1 = QHBoxLayout()
    self.hTreeViewBox_1.addWidget(self.client_status_label)
    self.hTreeViewBox_1.addStretch(1)
    self.hTreeViewBox_1.addWidget(self.setAccount)
    self.hTreeViewBox_1.addStretch(1)

    self.hTreeViewBox_2 = QHBoxLayout()
    self.hTreeViewBox_2.addWidget(self.statusChkLabel)
    self.hTreeViewBox_2.addStretch(1)
    
    #픽스맵 레이아웃
    self.capture_name_box=QHBoxLayout() #픽스맵 라벨 레이아웃
    
    for name in self.nameList:
      self.capture_name_box.addWidget(self.cap_names[name])
      
    self.pixMap_layout_1=QHBoxLayout()  #첫 번째 픽스맵
    for name in self.nameList:
      self.pixMap_layout_1.addWidget(self.pixMaps_1[name])

    self.pixMap_layout_2=QHBoxLayout()  #두 번째 픽스맵
    for name in self.nameList:
      self.pixMap_layout_2.addWidget(self.pixMaps_2[name])


    self.capture_time_label = QHBoxLayout()
    for name in self.nameList:
      self.capture_time_label.addWidget(self.cap_time_label[name])
    
    self.hTreeViewBox_2.addStretch(1)
    self.vTreeViewBox = QVBoxLayout()
    self.vTreeViewBox.addWidget(self.treeWidget)
    self.vTreeViewBox.addLayout(self.hTreeViewBox_1)
    self.vTreeViewBox.addLayout(self.hTreeViewBox_2)  
    self.vTreeViewBox.addLayout(self.btnBox_1)  
    self.vTreeViewBox.addLayout(self.btnBox_2)
    self.vTreeViewBox.addLayout(self.btnBox_3)  
    self.vTreeViewBox.addLayout(self.capture_name_box)  
    self.vTreeViewBox.addLayout(self.capture_time_label)
    self.vTreeViewBox.addLayout(self.pixMap_layout_1)  
    self.vTreeViewBox.addLayout(self.pixMap_layout_2)  


    return self.vTreeViewBox  

  def client_status_Chk(self, status):
    if(status==1):
      self.client_status_label.setText('Client Status:Online')
      self.client_status_label.setStyleSheet("color:green")
    else:
      self.client_status_label.setText('Client Status:Offline')
      self.client_status_label.setStyleSheet("color:red")
  
  def statusChk(self,status):
    if(status==1):
      self.statusChkLabel.setText('Status Check:ON')
      self.statusChkLabel.setStyleSheet("color:green")
    else:
      self.statusChkLabel.setText('Status Check:OFF')
      self.statusChkLabel.setStyleSheet("color:red")

  def addLog(self, acc, time, log):
    if(acc in self.rowId):  #아이디 잘못 입력할수도 있으니가 아이디가 존재하는지 체크해준다. (여기가 아니라 클라에서 체크해야할것같은데...)
      self.rowId[acc].setText(2,"O")
      self.rowId[acc].setTextAlignment(2,Qt.AlignHCenter)
      self.rowId[acc].addChild(QTreeWidgetItem(self.rowId[acc],["",time,log]))  
      tabIdx=self.tabIdx-1
      self.tabs.tabBar().setTabTextColor(tabIdx,QColor("red"))
    else:
      print("없는 아이디")
  
  def captureImage_1(self, imgData, pcName, name, cap_time):
    output=base64.b64decode(imgData)
    img=Image.open(io.BytesIO(output))
    img.save(f"img\{pcName}img{name}.png")

    self.pixMaps_1[name].setPixmap(QPixmap(f"img\{pcName}img{name}.png")) 

    self.cap_time_label[name].setText(cap_time) 

  def captureImage_2(self, imgData, pcName, nameList):
    i=0
    for name in nameList:
      output=base64.b64decode(imgData[i])
      img=Image.open(io.BytesIO(output))
      img.save(f"img\{pcName}img{name}.png")
      i+=1
      
    for name in nameList:
      self.pixMaps_2[name].setPixmap(QPixmap(f"img\{pcName}img{name}.png")) 

  def status_message(self, acc, statusData):
    # 아래 self.rowId 이 부분에서 에러가 나는데..
    if(acc in self.rowId):  #아이디 잘못 입력할수도 있으니가 아이디가 존재하는지 체크해준다. (여기가 아니라 클라에서 체크해야할것같은데...)
      self.rowId[acc].setText(1,statusData)
      self.rowId[acc].setTextAlignment(2,Qt.AlignHCenter)
      if(statusData=="X"):
        self.tabs.tabBar().setTabTextColor(self.tabIdx,QColor("red"))
    else:
      print("없는 아이디")
  
class Tabs:
  def __init__(self, sio, pcList):
    self.sio=sio
    self.pcList=pcList

  def createTabs(self, numOfTabs):
    self.tabs=QTabWidget()
    self.treeView={}

    def addTabfct(tab_name, tabIdx):  
      self.tab = QWidget()
      self.treeView[tab_name]=TreeView(self.tabs, tab_name, tabIdx, self.sio, self.pcList)
      self.tab.setLayout(self.treeView[tab_name].createTreeView()) #트리뷰를 탭에 세팅
      self.tabs.addTab(self.tab, tab_name)  #탭 생성 (탭에들어갈 위젯, 탭 이름)
    
    #탭 12개 생성
    for i in range(1,numOfTabs+1):
      if (i<10):
        addTabfct(f"PC0{i}", i)
      else:
        addTabfct(f"PC{i}", i)

    #그룹박스 생성
    self.treeViewbox = QVBoxLayout()
    self.treeViewbox.addWidget(self.tabs)
    self.treeGroupbox = QGroupBox('Account and Log')  
    self.treeGroupbox.setLayout(self.treeViewbox)

    return self.treeGroupbox

class ScheduleTable:
  def __init__(self,sio, pcList):
    self.sio=sio
    self.pcList=pcList
    self.column=0
    self.tableTitleWidget1=[] #스케쥴 상태 변경때 타이틀 텍스트 색 변경 할때 접근하기 위해 할당해줌.
    self.tableTitleWidget2=[]
    self.tableTitleWidget3=[]
    self.setTime=[0,0,0] #스케쥴 시간
  
  def scheduleStatus(self, status):
      if(status==1):
        self.scheduleSetLabel.setText('Schedule:ON')
        self.scheduleSetLabel.setStyleSheet("color:green")
      else:
        self.scheduleSetLabel.setText('Schedule:OFF')
        self.scheduleSetLabel.setStyleSheet("color:red")

  def createScheduleTable(self):
    self.groupbox = QGroupBox('스케쥴')

    #---테이블 생성 함수---
    def setTableTitle(tableInfo, table_title_list): 
      table = QTableWidget()
      table.setRowCount(3)
      table.setColumnCount(5)
      table.setEditTriggers(QAbstractItemView.NoEditTriggers)  #테이블 편집 못함
      table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) #수평헤더고 크기가 위젯에 맞춰짐
      table.verticalHeader().setVisible(False)
      table.horizontalHeader().setVisible(False)
      table.setMaximumHeight(92)
      
      self.column=0 #컬럼 초기화
      if(tableInfo=="table1"):
        for title in table_title_list:
          tableTitle=QTableWidgetItem(title)
          self.tableTitleWidget1.append(tableTitle)
          tableTitle.setTextAlignment(Qt.AlignCenter)
          table.setItem(0, self.column, tableTitle)
          self.column+=1
      elif(tableInfo=="table2"):
        for title in table_title_list:
          tableTitle=QTableWidgetItem(title)
          self.tableTitleWidget2.append(tableTitle)
          tableTitle.setTextAlignment(Qt.AlignCenter)
          table.setItem(0, self.column, tableTitle)
          self.column+=1
      else:
        for title in table_title_list:
          tableTitle=QTableWidgetItem(title)
          self.tableTitleWidget3.append(tableTitle)
          tableTitle.setTextAlignment(Qt.AlignCenter)
          table.setItem(0, self.column, tableTitle)
          self.column+=1

      return table
    
    self.label1 = QLabel('우편 및 모닝')
    self.label1.setAlignment(Qt.AlignCenter)
    postBox_title=["모닝루틴", "오전 우편", "오후 우편", "저녁 우편", "밤 우편"]
    self.table1=setTableTitle("table1", postBox_title)
  
    self.label2 = QLabel('사냥')
    self.label2.setAlignment(Qt.AlignCenter)
    hunt_title=["우호도","일반사냥","일반사냥","일반사냥","일반사냥"]
    self.table2=setTableTitle("table2", hunt_title)

    self.label3 = QLabel('던전')
    self.label3.setAlignment(Qt.AlignCenter)
    dungeon_title=["몽환의섬","버림받은땅","던전","던전","던전"]
    self.table3=setTableTitle("table3", dungeon_title)
    
    #스케쥴 설정 버튼
    def scheduelTime():
      #시간 생성
      min=[]
      for i in range(5):
        min.append(str(random.randint(10, 59))) 
      
      #나중에 스케쥴 타임 조정 할 수 있게 만들자
      def setSchedule(table, hour):
        column=0
        retTime=[]
        for i in range(5):
          minute=random.choice(min)
          hour=hour%24
          if(hour<10):
            time=f"0{hour}:{minute}"
            schedule_time=QTableWidgetItem(time)  #테이블 세팅을 위한 시간
            retTime.append(time)  #클라이언트에게 보내기위한 시간
          else:
            time=f"{hour}:{minute}"
            schedule_time=QTableWidgetItem(f"{hour}:{minute}")
            retTime.append(time)

          schedule_time.setTextAlignment(Qt.AlignCenter)
          table.setItem(1, column, schedule_time)
          self.tableTitleWidget1[column].setForeground(QBrush(QColor(0,0,0)))
          self.tableTitleWidget2[column].setForeground(QBrush(QColor(0,0,0)))
          self.tableTitleWidget3[column].setForeground(QBrush(QColor(0,0,0)))
          self.table1.setItem(2, column, QTableWidgetItem(""))
          self.table2.setItem(2, column, QTableWidgetItem(""))
          self.table3.setItem(2, column, QTableWidgetItem(""))
          hour+=4
          column+=1

        return retTime

      self.setTime[0]=setSchedule(self.table1,5)
      self.setTime[1]=setSchedule(self.table2,14) 
      self.setTime[2]=setSchedule(self.table3,10) 
      self.sio.emit("scheduleRoutine", self.setTime)
      self.scheduleStatus(1)

    def checkStatusRun():
      self.sio.emit("statusChk",1)
    def checkStatusCancel():
      self.sio.emit("statusChk",0)

    #---스케쥴 테이블 라벨---
    self.scheduleSetLabel=QLabel('Schedule:OFF')
    self.scheduleSetLabel.setStyleSheet("color:red")
    self.setScheduleBtn = QPushButton('스케쥴설정') 
    self.setScheduleBtn.clicked.connect(scheduelTime)
    self.statusChkRun = QPushButton('run')
    self.statusChkRun.clicked.connect(checkStatusRun)
    self.statusChkCancel = QPushButton('cancel')
    self.statusChkCancel.clicked.connect(checkStatusCancel)

    #---스케쥴 테이블 레이아웃---
    self.btnBox = QHBoxLayout()
    self.btnBox.addStretch(1)
    self.btnBox.addWidget(self.setScheduleBtn)
    self.btnBox.addWidget(self.scheduleSetLabel)
    self.btnBox.addStretch(1)
    self.runBox = QHBoxLayout()
    self.runBox.addStretch(1)
    self.runBox.addWidget(self.statusChkRun)
    self.runBox.addWidget(self.statusChkCancel)
    self.runBox.addStretch(1)
    vTableBox = QVBoxLayout()
    vTableBox.addWidget(self.label1)
    vTableBox.addWidget(self.table1) #루틴 스케쥴 테이블
    vTableBox.addWidget(self.label2)
    vTableBox.addWidget(self.table2) #사냥 스케쥴 테이블
    vTableBox.addWidget(self.label3)
    vTableBox.addWidget(self.table3) #던전 스케쥴 테이블
    vTableBox.addLayout(self.btnBox)
    vTableBox.addLayout(self.runBox)
    self.groupbox.setLayout(vTableBox)

    return self.groupbox
  
  def table_schedule_status(self, data):
    if(data["table"]=="table1"):
      if(data["status"]=="수행중"):
        stat=QTableWidgetItem(data["status"])
        stat.setTextAlignment(Qt.AlignCenter) 
        self.table1.setItem(2, data["column"], stat)
        self.tableTitleWidget1[data["column"]].setForeground(QBrush(QColor(255,0,0))) #수행중. 텍스트를 빨간색
      else:
        stat=QTableWidgetItem(data["status"])
        stat.setTextAlignment(Qt.AlignCenter) 
        self.table1.setItem(2, data["column"], stat)
        self.tableTitleWidget1[data["column"]].setForeground(QBrush(QColor(42,181,56))) #완료. 텍스트 초록색
    elif(data["table"]=="table2"):
      if(data["status"]=="수행중"):
        stat=QTableWidgetItem(data["status"])
        stat.setTextAlignment(Qt.AlignCenter)
        self.table2.setItem(2, data["column"], stat)
        self.tableTitleWidget2[data["column"]].setForeground(QBrush(QColor(255,0,0))) #수행중. 텍스트를 빨간색
      else:
        stat=QTableWidgetItem(data["status"])
        stat.setTextAlignment(Qt.AlignCenter)
        self.table2.setItem(2, data["column"], stat)
        self.tableTitleWidget2[data["column"]].setForeground(QBrush(QColor(42,181,56))) #완료. 텍스트 초록색
    else:
      if(data["status"]=="수행중"):
        stat=QTableWidgetItem(data["status"])
        stat.setTextAlignment(Qt.AlignCenter)
        self.table3.setItem(2, data["column"], stat)
        self.tableTitleWidget3[data["column"]].setForeground(QBrush(QColor(255,0,0))) #수행중. 텍스트를 빨간색
      else:
        stat=QTableWidgetItem(data["status"])
        stat.setTextAlignment(Qt.AlignCenter)
        self.table3.setItem(2, data["column"], stat)
        self.tableTitleWidget3[data["column"]].setForeground(QBrush(QColor(42,181,56))) #완료. 텍스트 초록색

#---Main Window Layout---
class MyApp(QWidget):
  def __init__(self, treeview_group, table_group):
    super().__init__()
    self.setWindowTitle('LineageW')
    self.setGeometry(1920, 740, 630, 990)
    self.setWindowIcon(QIcon("lineage_icon.png"))

    #앱 전체 레이아웃
    self.appLayout = QVBoxLayout()
    self.appLayout.addWidget(treeview_group)
    self.appLayout.addStretch(1)
    self.appLayout.addWidget(table_group)
    self.setLayout(self.appLayout) 



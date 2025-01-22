from platform import java_ver
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread,QObject
from GUI import *
import threading
import socketio
from gevent import pywsgi
import datetime
import time
from PyQt5.QtCore import pyqtSignal

class SignalGenerator(QObject):
  register_pc_signal = pyqtSignal(object, object)
  schedule_status_signal = pyqtSignal(object, object)
  pc_status_signal = pyqtSignal(object, object)
  log_event_signal = pyqtSignal(object, object)
  statusMessage__signal= pyqtSignal(object, object)
  tableScheduleStatus_signal= pyqtSignal(object, object)
  capture_img_signal = pyqtSignal(object, object)
  checkStatusRev_signal= pyqtSignal(object, object)

if __name__ == '__main__':
  sio = socketio.Server(async_mode='gevent')
  socketApp = socketio.WSGIApp(sio)
  pcList={}

  def runServer(socketApp): #스레드에서 서버 실행
    pywsgi.WSGIServer(('192.168.50.113', 6000), socketApp).serve_forever()
    # pywsgi.WSGIServer(('127.0.0.1', 5000), socketApp).serve_forever()


  serverThread=threading.Thread(target=runServer, args=(socketApp,))
  serverThread.daemon=True
  serverThread.start()

 #---웹 소켓 이벤트---
  @sio.event
  def connect(sid, environ):
    print('connected client: ', sid)
  
  @sio.event
  def disconnect(sid):
    print('disconnected client: ', sid)

  signal_generator = SignalGenerator()
  
  @sio.event  #PC 목록을 세팅함
  def registerPC(sid, pc_id):
    signal_generator.register_pc_signal.emit(sid,pc_id)

  def registerPC_run(sid, pc_id):
    pcList[pc_id]=sid
    print("PC_LIST: ", pcList)
    sio.emit("accountRes",tabs.treeView[pc_id].nameList,to=pcList[pc_id])
    tabs.treeView[pc_id].statusChk(0) #statusChk off
    tabs.treeView[pc_id].client_status_Chk(0) #PC status off

  signal_generator.register_pc_signal.connect(registerPC_run)
  
  @sio.event
  def scheduleStatus(sid,data): #스케쥴이 ON, OFF 상태를 나타냄
    signal_generator.schedule_status_signal.emit(sid,data)

  def scheduleStatus_run(sid,data):
    for pcName in pcList:  
      if(pcList[pcName] == sid):
        keyChk=tabs.treeView.get(pcName)
        if(keyChk==None):
          print("없는 키 검색")
        else:
          if (scheduleTable.setTime==[0,0,0]):
            scheduleTable.scheduleStatus(0) 
          else:
            scheduleTable.scheduleStatus(1) 
            sio.emit("scheduleRoutine", scheduleTable.setTime,to=pcList[pcName])
  signal_generator.schedule_status_signal.connect(scheduleStatus_run)


  @sio.event  
  def PC_status(sid,client_status):
    signal_generator.pc_status_signal.emit(sid,client_status)

  def PC_status_run(sid,client_status):
    for pcName in pcList:  #sid를 이용해 어떤 PC의 데이터인지 구분한다
      if(pcList[pcName] == sid):
        if(client_status==1):
          tabs.treeView[pcName].client_status_Chk(client_status)  #1이 오면 온라인 그외
        else:
          pass

  signal_generator.pc_status_signal.connect(PC_status_run)

  @sio.event
  def logEvent(sid, logData):
    signal_generator.log_event_signal.emit(sid,logData)

  def logEvent_run(sid,logData):
    #현재 시간
    now = datetime.datetime.now()
    nowDatetime=now.strftime('%Y-%m-%d %H:%M')
    for pcName in pcList:  #클라를 sid로 구분한 후에 그에 맞는 탭 객체에 accData를 저장해준다.
      if(pcList[pcName] == sid):
        tabs.treeView[pcName].addLog(logData["charName"], nowDatetime,logData["log"])
    # tabs.treeView["원하는탭이름"].addLog("원하는케릭명", 시간, "원하는 Log내용")
  signal_generator.log_event_signal.connect(logEvent_run)

  @sio.event
  def statusMessage(sid,data): #케릭의 진행 상태를 나타냄(케릭이 켜져있지않으면 꺼져있는것도 나타냄)
    signal_generator.statusMessage__signal.emit(sid,data)

  def statusMessage_run(sid,data):
    for pcName in pcList:  
      if(pcList[pcName] == sid):
        tabs.treeView[pcName].status_message(data["charName"],data["status"])
  signal_generator.statusMessage__signal.connect(statusMessage_run)
  
  @sio.event
  def tableScheduleStatus(sid,data):  #스케쥴 수행중, 완료를 나타냄 
    signal_generator.tableScheduleStatus_signal.emit(sid,data)
  def tableScheduleStatus_run(sid,data):
    scheduleTable.table_schedule_status(data)  
  signal_generator.tableScheduleStatus_signal.connect(tableScheduleStatus_run)

  
  @sio.event
  def checkStatusRev(sid,data): #상태 체크 ON, OFF를 나타냄
    signal_generator.checkStatusRev_signal.emit(sid, data)

  def checkStatusRev_run(sid,data):
    for pcName in pcList:  
      if(pcList[pcName] == sid):
        keyChk=tabs.treeView.get(pcName)
        if(keyChk==None):
          print("없는 키 검색")
        else:
          tabs.treeView[pcName].statusChk(data) 
  signal_generator.checkStatusRev_signal.connect(checkStatusRev_run)
  

  @sio.event
  def capture_img(sid,data): #이미지 캡쳐 [캡쳐이미지, 캡쳐함수선택, 이름, 시간]    
    signal_generator.capture_img_signal.emit(sid,data)
  
  def capture_img_run(sid,data):
    for pcName in pcList:  
      if(pcList[pcName] == sid):
        if(data[1]==0):
          tabs.treeView[pcName].captureImage_1(data[0], pcName, data[2], data[3]) 
        else: #(data[1]==1)
          tabs.treeView[pcName].captureImage_2(data[0], pcName, data[2])
  
  signal_generator.capture_img_signal.connect(capture_img_run)

  #---GUI 생성---
  app = QApplication(sys.argv)
  #트리뷰탭
  tabs=Tabs(sio, pcList)
  tabLayout=tabs.createTabs(10)

  #스케쥴 테이블
  scheduleTable=ScheduleTable(sio, pcList)
  scheduleTableLayout=scheduleTable.createScheduleTable()

  myApp = MyApp(tabLayout, scheduleTableLayout)
  myApp.show()
  sys.exit(app.exec_())

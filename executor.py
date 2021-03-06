# encoding=utf8
# The task base
import gevent
import string  
import hashlib 
import random
from task import *

class TaskExecutor(object):
    
    ali = None 
    def __call__(self, task):
        
        raise NotImplementedError


class EchoTaskExecutor(TaskExecutor):

    id = 'edc.echo'
    def __call__(self,opType, task):

        print "EchoTaskExecutor start",opType
        #print gevent.getcurrent()
        gevent.sleep(30)

        print "EchoTaskExecutor end"
        return "ok"
 

class AddTaskExecutor(TaskExecutor):

    id = 'edc.add'
    def __call__(self, opType,task):


        print "AddTaskExecutor start",opType
        #print gevent.getcurrent()
        gevent.sleep(30)
        print "AddTaskExecutor end"

        return "ok"
 


class CrackMd5Executor(TaskExecutor):
    '''强制破解md5
       支持数字＋字母（区分大小写）
    '''

    id = 'edc.crackmd5'
    def __call__(self, opType,task):

        if opType=='compute':
            ptask = PTask()
            self.ptaskId = task['PTaskId']
            self.subTaskId = task['_id']
            bizInfo = task['bizInfo']
            
            self.apt=string.printable[:-38]
            self.md5input = bizInfo['md5']
            self.md5len = int(bizInfo['md5len'])+1    #生成字符的位数  

            self.index = 0
            self.tmpIndex = 0
            self.total = 52**self.md5len

            #每次打乱字符串顺序
            apts = list(self.apt)
            random.shuffle(apts)

            self.apt = ''.join(apts)

            print "CrackMd5Executor start",opType,bizInfo,self.apt

            for j in range(1,self.md5len):  
                ret = self.crack("",j)  
                if ret :
                    print "CrackMd5Executor success",ret

                    #强制完成
                    self.ali.finishPTask(self.ptaskId)
                    return ret

            return ''
        else:
            print "merge result",task

            for cursor in task:
                print cursor

        return "ok"

 
    def crack(self,s,num):
        '''破解算法
        '''  
        m=hashlib.md5()  
        m.update(s)  
        md5temp=m.hexdigest()  

        self.index += 1
        self.tmpIndex += 1

        if self.tmpIndex==10000:
            self.tmpIndex = 0
            process = (self.index*100)/(self.total*1.0)
            self.ali.updateProcess(self.subTaskId,process)
            print "%s process %f" % (self.subTaskId,process)

        print s,md5temp
        if md5temp==self.md5input:  
            self.ali.updateProcess(self.subTaskId,100)
            print 'crack success:',s,md5temp

            return s
        
        if len(s)==num:  
            return ''

        if self.ali.checkFinished(self.ptaskId):
            self.ali.updateProcess(self.subTaskId,100)
            return '_eof_'

        for i in self.apt:  
            ret = self.crack(s+i,num)  
            if ret:return ret
            gevent.sleep(0)


EXECUTORS = {
    EchoTaskExecutor,
    AddTaskExecutor,
    CrackMd5Executor

 }
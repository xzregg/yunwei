#/usr/bin/env python
# coding: utf-8


import time,datetime
TimeFormat='%Y-%m-%d %H:%M:%S'

def StrTimeToDateTime(Str):
    return  datetime.datetime.strptime(Str,TimeFormat)  
def DateTimeToStrTime(Datetime):
	return datetime.datetime.strftime(Datetime,TimeFormat)
    
def UnixTimeToStrTime(UnixTime):
    t=time.localtime(UnixTime)
    return time.strftime(TimeFormat,t) 
	
def get_nowtime_str():
	return time.strftime(TimeFormat,time.localtime())	


def get_today_str():
	return datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
	
def datediff(op,d1,d2):
	f='%Y-%m-%d %H:%M:%S'
	#转换为struct_time类型
	t1=time.strptime(d1,f)
	t2=time.strptime(d2,f)
	if op=="yy":
		return abs(t1.tm_year-t2.tm_year)
	elif op=="mm":
		t1=t1.tm_year*12+t1.tm_mon
		t2=t2.tm_year*12+t2.tm_mon
		return abs(t1-t2)
	elif op=="dd":
		t1=int(time.mktime(t1))
		t2=int(time.mktime(t2))
		return abs((t1-t2)/86400)		
	elif op=="hh":
		t1=int(time.mktime(t1))
		t2=int(time.mktime(t2))
		return abs((t1-t2)/3600)	
	elif op=="min":
		t1=int(time.mktime(t1))
		t2=int(time.mktime(t2))
		return abs((t1-t2)/60)	
	elif op=="ss":
		t1=int(time.mktime(t1))
		t2=int(time.mktime(t2))
		return abs(t1-t2)			
	else:
		print '''datediff(('yy'|'mm'|'dd'|'hh'|'min'|'ss'),'2012-12-1 0:0:0','2012-12-1 0:0:0')'''
		
def dateadd(op,a,d):
	f='%Y-%m-%d %H:%M:%S'
	t1=time.strptime(d,f)
	# 转换为datetime类型
	t1=datetime.datetime(*t1[:6])
	if op=="yy":
		i=t1.year+a
		t1=t1.replace(year=i)
		return datetime.datetime.strftime(t1,f)
	elif op=="mm":
		i=t1.year*12+t1.month+a
		y=i/12
		m=i%12
		t1=t1.replace(month=m if m!=0 else 12, year=y if m!=0 else y-1) 
		return datetime.datetime.strftime(t1,f)		
	elif op=="dd":
		i=a*86400
		t1=time.mktime(t1.timetuple())
		return time.strftime(f,time.localtime(t1+i))			
	elif op=="hh":
		i=a*3600
		t1=time.mktime(t1.timetuple())
		return time.strftime(f,time.localtime(t1+i))		
	elif op=="min":
		i=a*60
		t1=time.mktime(t1.timetuple())
		return time.strftime(f,time.localtime(t1+i))	
	elif op=="ss":
		i=a
		t1=time.mktime(t1.timetuple())
		return time.strftime(f,time.localtime(t1+i))		
	else:
		print '''datedadd(('yy'|'mm'|'dd'|'hh'|'min'|'ss'),1,'2012-12-1 0:0:0')'''
		
		
		
		

if __name__ == '__main__':
#	t1=raw_input('请输入第1个日期')
#	t2=raw_input('请输入第2个日期')
	t1='2013-9-9 9:9:0'
	t2='2013-9-9 20:9:9'
	i=4
	print datediff('yy',t1,t2)
	print datediff('mm',t1,t2)
	print datediff('dd',t1,t2)
	print datediff('min',t1,t2)
	print datediff('ss',t1,t2)
	print '---%s---'% t1
	print dateadd('yy',i,t1),i,'year'
	print dateadd('mm',i,t1),i,'mouth'
	print dateadd('dd',i,t1),i,'day'
	print dateadd('hh',i,t1),i,'hours'
	print dateadd('min',i,t1),i,'min'
	print dateadd('ss',i,t1),i,'s'


#coding:utf-8
import re
    
class Myrequest():
    '''
    伪造一个request,用于传递参数
    '''
    def __init__(self,request=None):
        self.POST={}
        self.GET={}
        self.method="POST"
        self.session={}
        if request:
            keys=request.REQUEST.keys()
            values=GetPost(request,keys)
            self.POST=dict(map(lambda k,v:(k,v),keys,values))
            
def GetPost(request,keys=[],islist=[]):
    '''
    @keys 
    @islist
    '''
    R=dict(request.GET)
    R.update(dict(request.POST))
    l=[ v[0] if  not i in islist and v.__len__()==1 else v  for i,v in enumerate([ R.get(k,'') for k in keys]) ]
    return  l[0] if keys.__len__()==1 else l
    #return map(lambda v:v[0] if  v.__len__()==1 else v,[ R.get(k,'') for k in keys])#单项去列表
    #return map(lambda i,v:v[0] if not i in islist and v.__len__()==1 else v,range(len(keys)),[ R.get(k,'') for k in keys])#单项不去列表

    
def isDateTimeFormat(str):
        return not re.match(r'^((((1[6-9]|[2-9]\d)\d{2})-(0?[13578]|1[02])-(0?[1-9]|[12]\d|3[01]))|(((1[6-9]|[2-9]\d)\d{2})-(0?[13456789]|1[012])-(0?[1-9]|[12]\d|30))|(((1[6-9]|[2-9]\d)\d{2})-0?2-(0?[1-9]|1\d|2[0-8]))|(((1[6-9]|[2-9]\d)(0[48]|[2468][048]|[13579][26])|((16|[2468][048]|[3579][26])00))-0?2-29-)) (20|21|22|23|[0-1]?\d):[0-5]?\d:[0-5]?\d$',str) is None


def MakeURL(func):
    #获取行数和函数名
    #print sys._getframe().f_code.co_name
    #print sys._getframe().f_back.f_code.co_name
    m=func.__module__.split('.')
    m.append(func.__name__)
    url=u'/%s/'%'/'.join([ m[o] for o in (0,-2,-1)])
    return url
    
def MakeAjaxButton(label,ajaxurl,html,method,Random='',confirm='',follow='',closesec=''):
    '''
    @label HTML的标签名
    @ajaxur 异步获取的url
    @html  按钮的标题
    @method 打开方法open或者load,open载入框架，load加载内容继承js脚本
    '''
    return u" <%s class='ajax_%s'  href='javascript:void(0);' ajaxurl='%s' method='%s' confirm='%s' follow='%s' closesec='%s'>%s</%s>"%(label,Random,ajaxurl,method,confirm,follow,closesec,html,label)
    #return u" <%s class='_ajax'  href='javascript:void(0);' ajaxurl='%s' method='%s'>%s</%s>"%(label,Random,method,html,label)



class Table():
        def __init__(self,table={'':[]},alias={'':[]},thcss=[],checkbox=""):#返回table的html代码]
            if not alias:
                alias=table			
            self.tablename=table.keys()[0]
            self.Atablename=alias.keys()[0]
            self.thvalue,self.alias=table.values()[0],alias.values()[0]
            self.checkbox=checkbox
            self.th=[]
            self.thcss=thcss if thcss else []
            self.row=[]
            self.thNum=len(self.thvalue)
            self.rownum=1
            if len(self.thcss)!=len(self.thvalue):
                self.thcss+=['' for i in range(len(self.thvalue)-len(self.thcss))]

        def th_add(self,value,alias='',thcss=''):
            Alias=alias or value 
            self.thvalue.append(value)
            self.alias.append(Alias)
            self.thcss.append(thcss)
            self.thNum+=1
        
        def row_add(self,rowid="",row=[],tdattr=[]):#增加一行，可以编辑的列
            self.row.append({'row':row,'tdattr':tdattr,'rowid':rowid})
            self.rownum+=1
        
        def _make_th(self):
            th=""
            if self.checkbox:
                th+=(u'''<th  id="checkall_th" style="width:20px">%s<input type='checkbox' class='checkall' name='checkall' value='%s'/></th>'''%(checkbox,checkbox))
            th+=u''.join(map(lambda v,c,a:u'<th id="%s" style="%s">%s</th>'%(v,c,a),self.thvalue,self.thcss,self.alias))
            return th
        def _make_td(self):#生成td
            td=[]
            tn=self.tablename
            thN=self.thNum
            for tr in self.row:
                row=tr['row'];rowid=tr['rowid'];tdattr=tr['tdattr']
                if len(tdattr)<len(row):
                    tdattr+=[ '' for o in range(len(row)-len(tdattr)) ]
                td.append(u'<tr id="%s__%s__%s">' % (tn,'id',rowid))
                for s in xrange(thN):
                    if s>=len(row):#超出的列部分输出None
                        attr=u''
                        html=u''
                    else:
                        html=row[s]
                        attr=tdattr[s]
                        html=html.replace('\n','<br>') if isinstance(html,unicode) and html.find('<')!=0 else html
                    td.append(u'<td %s>%s</td>' % (attr,html))
                td.append(u"</tr>")
            return u''.join(td)
        
        def done(self):
            self.html=''.join([u'<table cellpadding="0" cellspacing="0" border="0" class="display"  id="%s">' % self.tablename,
                            u"<thead><tr>",
                            self._make_th(),
                            u"</tr></thead><tbody>",
                            self._make_td(),
                            u"</tbody></table>"])
            return self.html
    

def MakeTable(th=[],td=[]):
        T=Table(table={'':[]},alias={'':[]});thnum=len(th)
        for t in th:
            T.th_add(t)
        row=[];endnum=len(td)
        for i,v in enumerate(td):
            row.append(v)
            if (i+1)%thnum==0:
                T.row_add('',row)
                row=[]
                continue
            if (i+1)==endnum:
                T.row_add('',row)
        return T.done()
def MakeRaio(name,html=[],value=[],selected=0):
    s=[]
    for i,v in enumerate(value):
        checked=u'checked="checked"' if i==selected else ''
        s.append(u'<input type="radio" id="%s_%s" name="%s" value="%s" %s ><label for="%s_%s">%s</label>'%(i,name,name,v,checked,i,name,html[i]))
    return ''.join(s)
    
def MakeAmark(html,href):
    return u'<a href="%s">%s</a>'%(href,html)
    
def MakeSelect(Name,html=[],value=[],selected=0,label=''):
    s=[u'<label>%s</label><select id="id_%s" name="%s" >'%(label,Name,Name)]
    for n,v in enumerate(value):
        Selected='selected=selected' if n==selected else ''
        s+=[u'<option value="%s" %s >%s</option>'%(v,Selected,html[n])]
    s+=[u'</select>']
    return ''.join(s)
        
def MakeCheckbox(value,html,checked=False):
    checked="checked='true'" if checked==True else ''
    return u"<div style='display:Inline;float:left'><input type='checkbox' class='checkbox' name='checkbox' value='%s' %s/>%s</div>"%(value,checked,html)
    
def MakeInput(type,name,value,sytle):
        return '<input  type="%s" name="%s" value="%s" style="%s" >'%(type,name,value,sytle)

def MakeTextarea(name,value,style):
        return '<textarea  name="%s" style="%s"  >%s</textarea>'%(name,style,value)

        
        
class InputTable():
    def __init__(self,value=[],column=2):

        th=[ '' for x in xrange(column)]
        tdall=[]
        for x in value:
            if x[0]=="textarea":
                tdall.append(x[2])#增加标题
                tdall.append(MakeTextarea(x[1],x[3],x[4]))
            elif x[0]=="checkbox":
                tdall.append(MakeCheckbox(x[1],x[2],x[3]))
            elif x[0]=='select':
                tdall.append(x[2])#增加标题
                tdall.append(MakeSelect(x[1],x[3],x[4],x[5]))
            else:
                tdall.append(x[2])#增加标题
                tdall.append(MakeInput(x[0],x[1],x[3],x[4]))
        self.table=MakeTable(th,tdall)
    def append(self,s,after=False):
        if after:
            self.table+=s
        else:
            self.table=s+self.table
    def done(self):

        return self.table
    

import re
##过滤HTML中的标签
#将HTML中标签等信息去掉
#@param htmlstr HTML字符串.
def filter_tags(htmlstr):
    #先过滤CDATA
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>')#HTML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s=replaceCharEntity(s)#替换实体
    return s

##替换常用HTML字符实体.
#使用正常的字符替换HTML中特殊的字符实体.
#你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
#@param htmlstr HTML字符串.
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES={'nbsp':' ','160':' ',
                'lt':'<','60':'<',
                'gt':'>','62':'>',
                'amp':'&','38':'&',
                'quot':'"','34':'"',}
    
    re_charEntity=re.compile(r'&#?(?P<name>\w+);')
    sz=re_charEntity.search(htmlstr)
    while sz:
        entity=sz.group()#entity全称，如&gt;
        key=sz.group('name')#去除&;后entity,如&gt;为gt
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
            sz=re_charEntity.search(htmlstr)
        except KeyError:
            #以空串代替
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr

def removeHtmlMark(htmlstr):
    return replaceCharEntity(filter_tags(htmlstr))

    
    
    
    
    

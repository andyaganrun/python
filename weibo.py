#coding=utf8
import urllib.parse
import urllib.request
import http.cookiejar
import base64
import re
import json
import hashlib
import rsa
import binascii 
import time

cj = http.cookiejar.LWPCookieJar()
cookie_support = urllib.request.HTTPCookieProcessor(cj)
opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
urllib.request.install_opener(opener)

postdata={
    'entry':'weibo',
    'gateway':'1',
    'from':'',
    'savestate':'0',
    'useticket':'1',
    'pagerefer':'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
    'pcid':'',
    'door':'',
    'vsnf':'1',
    'su':'',
    'service':'miniblog',
    'servicetime':'',
    'nonce':'',
    'pwencode':'rsa2',
    'rsakv':'',
    'sp':'',
    'encoding':'utf-8',
    'prelt':'',
    'url':'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
    'returntype':'META'
    }

def get_servertime():
    url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.11)'

    data = urllib.request.urlopen(url).read()
    data = data.decode('utf8')
    p = re.compile('\((.*)\)')
    try:
        json_data = p.search(data).group(1)
        data = json.loads(json_data)
        servertime = str(data['servertime'])
        nonce = data['nonce']
        pubkey = data['pubkey']
        rsakv = data['rsakv']
        return servertime, nonce, pubkey, rsakv
    except:
        print('Get severtime error!')
        return None

def get_pwd(pwd, servertime, nonce, pubkey):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537)
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)
    message = message.encode('utf8')
    passwd = rsa.encrypt(message, key)
    passwd = binascii.b2a_hex(passwd)
    return passwd

def get_user(username):
    username_ = urllib.parse.quote(username)
    username_ = username_.encode('utf8')
    username = base64.encodestring(username_)[:-1]
    return username

def sendMiniBlog(text):
    timestamp = int(time.time()*1000)
    url = 'http://weibo.com/aj/mblog/add?_wv=5&__rnd=' + str(timestamp)

    postdata = {
        'text':text,  
        'pic_id':'',  
        'rank':1, #rank1:自己可见，rank0:公开  
        'rankid':'',  
        '_surl':'',  
        'hottopicid':'',  
        'location':'home',  
        'module':'stissue',  
        '_t':0,  
    }

    postdata = urllib.parse.urlencode(postdata)
    postdata = postdata.encode('utf8')
    
    headers = {'Referer':'http://weibo.com/u/1785845443?wvr=5&wvr=5&lf=reg'}  
    req  = urllib.request.Request(
        url = url,
        data = postdata,
        headers = headers
    )

    try:
        text = urllib.request.urlopen(req).read()
        text = text.decode('utf8')
        print('Send weibo success!')
    except:
        print('Send weibo error!')

def login_weibo(username, pwd):
    url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)'
    try:
        servertime, nonce, pubkey, rsakv = get_servertime()
    except:
        return
    global postdata
    postdata['servertime'] = servertime
    postdata['nonce'] = nonce
    postdata['rsakv'] = rsakv
    postdata['su'] = get_user(username)
    postdata['sp'] = get_pwd(pwd, servertime, nonce, pubkey)
    
    postdata = urllib.parse.urlencode(postdata)
    postdata = postdata.encode('utf8')
    
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0'}
    
    req  = urllib.request.Request(
        url = url,
        data = postdata,
        headers = headers
    )
    text = urllib.request.urlopen(req).read()
    text = text.decode('gbk')
    p = re.compile('location\.replace\(\'(.*)\'\)')
    try:
        login_url = p.search(text).group(1)
        urllib.request.urlopen(login_url)
        print('login success')
    except:
        print('Login error!')
        
def main():
    username = 'abc@163.com' #邮箱
    pwd = '123456'  #密码
    login_weibo(username, pwd)

    text = 'haha!'
    sendMiniBlog(text)
    
main()

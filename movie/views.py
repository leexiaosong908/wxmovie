from django.shortcuts import render,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str
import hashlib
import xml.etree.ElementTree as ET
import time
from movie.models import Movie

# Create your views here.
# 验证服务器地址
TOKEN = 'wxmovie'
appID = 'wx945ecc4a67e7c9c8'
appsecret = '6507d64831dc045c28dbdb58de9c6f3e'

# 微信服务器验证
def checkSignatrue(request):
    signature = request.GET.get("signature")
    timestamp = request.GET.get("timestamp")
    nonce = request.GET.get("nonce")
    echoStr = request.GET.get("echostr")
    #token为微信验证TOKEN
    token = TOKEN
    tmpList = [token,timestamp,nonce]
    tmpList.sort()
    tmpStr = "%s%s%s"%tuple(tmpList)
    tmpStr = hashlib.sha1(tmpStr.encode('utf-8')).hexdigest()
    if tmpStr == signature:
        return echoStr
    else:
        return None

# 处理微信请求
@csrf_exempt
def handleRequest(request):
    if request.method == "GET":
        response = HttpResponse(checkSignatrue(request),content_type='text/plain')
        return response
    # 接收和响应数据
    elif request.method == "POST":
        # 获取POST数据
        requestMsg = smart_str(request.body)
        # 从POST数据中读取信息
        msg = ET.fromstring(requestMsg)
        toUsername = msg.find("ToUserName").text
        fromUsername = msg.find("FromUserName").text
        msgType = msg.find("MsgType").text
        # 判断消息类型
        if msgType == 'text':
            text = msg.find("Content").text
            try:
                response = textResponse(request, fromUsername, toUsername, text)
                return response
            except:
                return HttpResponse('success')
        else:
            return HttpResponse('success')
    else:
        return None
        
        
# 接收文本消息的响应
def textResponse(request, fromUser, toUser, text):
    if text[:2] == '电影':
        data = Movie.objects.filter(title__icontains=str(text[2:]))
        count = data.count()
        if count == 0:
            content = {
                "fromUser": fromUser,
                "toUser": toUser,
                "date": str(int(time.time()))
            }
            xmlMsg = render(request, 'nomovieResponse.xml',
                            context=content, content_type='application/xml')
            return xmlMsg
        else:
            if count > 8:
                result = data[:8]
                num = 8
            else:
                result = data
                num = count
            content = {
                "fromUser": fromUser,
                "toUser": toUser,
                "date": str(int(time.time())),
                "num": num,
                "result": result
            }
            xmlMsg = render(request, 'movieResponse.xml',
                            context=content, content_type='application/xml')
            return xmlMsg
    else:
        content = {
                "fromUser": fromUser,
                "toUser": toUser,
                "date": str(int(time.time()))
            }
        xmlMsg = render(request, 'otherResponse.xml',context=content, content_type='application/xml')
        return xmlMsgs
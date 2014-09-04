import sys
import xbmcplugin, xbmcgui, xbmcaddon
import re, os, time
import urllib, urllib2, httplib2
import json
import HTMLParser
import datetime

addon_handle = int(sys.argv[1])

ROOTDIR = xbmcaddon.Addon(id='plugin.video.nbcsnliveextra').getAddonInfo('path')
FANART = ROOTDIR+"/fanart.jpg"
ICON = ROOTDIR+"/icon.png"
#ROOT_URL = 'http://stream.nbcsports.com/data/mobile/upcoming.json'

def CATEGORIES():                
    addDir('Live and Upcoming Events','/upcoming',1,ICON,FANART)
    addDir('Featured','/featured',2,ICON,FANART)
    #addDir('Live','/Live',0,ICON,FANART)
    

def UPCOMING():            
    req = urllib2.Request('http://stream.nbcsports.com/data/mobile/upcoming.json')
    req.add_header('User-Agent', 'NBCSports/742 CFNetwork/672.0.8 Darwin/14.0.0')
    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close()            
        
    today_date_nbcsn_format = int(datetime.date.today().strftime("%Y%m%d"))
    #Get any live video and add it
    LIVE()

    for item in json_source:        
        if int(item['start'][0:8]) == today_date_nbcsn_format:
            url = item['iosStreamUrl']
            name = item['title']            
            menu_name = name        
            info = item['info'] 
            if info <> "":
                menu_name = menu_name + " - " + info
            imgurl = "http://hdliveextra-pmd.edgesuite.net/HD/image_sports/mobile/"+item['image']+"_m50.jpg"
            addLink(menu_name,url,name,imgurl,FANART) 

def FEATURED():            
    req = urllib2.Request('http://stream.nbcsports.com/data/mobile/featured-2013.json')
    req.add_header('User-Agent', 'NBCSports/742 CFNetwork/672.0.8 Darwin/14.0.0')
    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close()            
        
    today_date_nbcsn_format = int(datetime.date.today().strftime("%Y%m%d"))
    video_source = json_source['replay']

    for item in video_source:        
        url = item['iosStreamUrl']
        name = item['title']            
        menu_name = name        
        info = item['info'] 
        if info <> "":
            menu_name = menu_name + " - " + info
        imgurl = "http://hdliveextra-pmd.edgesuite.net/HD/image_sports/mobile/"+item['image']+"_m50.jpg"
        addLink(menu_name,url,name,imgurl,FANART) 

def LIVE():            
    req = urllib2.Request('http://stream.nbcsports.com/data/mobile/live.json')
    req.add_header('User-Agent', 'NBCSports/742 CFNetwork/672.0.8 Darwin/14.0.0')
    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close()            
        
    today_date_nbcsn_format = int(datetime.date.today().strftime("%Y%m%d"))
    #video_source = json_source['replay']

    for item in json_source:        
        url = item['iosStreamUrl']
        name = item['title']            
        menu_name = name        
        info = item['info'] 
        if info <> "":
            menu_name = menu_name + " - " + info
        imgurl = "http://hdliveextra-pmd.edgesuite.net/HD/image_sports/mobile/"+item['image']+"_m50.jpg"
        addLink(menu_name,url,name,imgurl,FANART) 

def addLink(name,url,title,iconimage,fanart):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage,)
 
    liz.setProperty('fanart_image',fanart)
    liz.setProperty("IsPlayable", "true")
    liz.setInfo( type="Video", infoLabels={ "Title": title } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok

def addDir(name,url,mode,iconimage,fanart=None,page=1): 
    params = get_params()      
    ok=True
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&page="+urllib.quote_plus(str(page))
    liz=xbmcgui.ListItem(name, iconImage=ICON, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty('fanart_image', fanart)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)    
    return ok


def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]
                            
    return param


params=get_params()
url=None
name=None
mode=None
year=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    year=urllib.unquote_plus(params["year"])
except:
    pass

print "Mode: "+str(mode)
#print "URL: "+str(url)
print "Name: "+str(name)
print "Year:"+str(year)


if mode==None or url==None or len(url)<1:
        #print ""                
        CATEGORIES()        
elif mode==1:
        UPCOMING()
elif mode==2:
        FEATURED()

xbmcplugin.endOfDirectory(addon_handle)
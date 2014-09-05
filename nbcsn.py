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
ROOT_URL = 'http://stream.nbcsports.com/data/mobile/'

def CATEGORIES():                
    addDir('Live and Upcoming Events','/upcoming',1,ICON,FANART)
    addDir('Featured',ROOT_URL+'featured-2013.json',4,ICON,FANART)
    addDir('On NBC Sports','/replays',3,ICON,FANART)
    #addDir('Live','/Live',0,ICON,FANART)
    

def UPCOMING():                
    #LIVE    
    SCRAPE_VIDEOS(ROOT_URL+'live.json')
    #UPCOMING
    SCRAPE_VIDEOS(ROOT_URL+'upcoming.json')

def GET_ALL_SPORTS():
    req = urllib2.Request(ROOT_URL+'configuration-2013.json')
    req.add_header('User-Agent', 'NBCSports/742 CFNetwork/672.0.8 Darwin/14.0.0')
    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close()    

    try:
        for item in json_source['sports']:        
            code = item['code']
            name = item['name']                  
            addDir(name,ROOT_URL+code+'.json',4,ICON,FANART)
    except:
        pass

##########################################
#This has been replaced by GET_ALL_SPORTS
##########################################
def REPLAYS():    
    addDir('Dew Tour',ROOT_URL+'dewtour.json',4,ICON,FANART)    
    addDir('European Tour',ROOT_URL+'euro-2013.json',4,ICON,FANART)
    addDir('F1',ROOT_URL+'f1-2013.json',4,ICON,FANART)
    addDir('Horse Racing',ROOT_URL+'horses-2013.json',4,ICON,FANART)
    addDir('IndyCar',ROOT_URL+'indy-2013.json',4,ICON,FANART)
    addDir('Major League Soccer',ROOT_URL+'mls-2013.json',4,ICON,FANART)    
    addDir('National Dog Show',ROOT_URL+'dogshow-2013.json',4,ICON,FANART)
    addDir('NFL',ROOT_URL+'nfl.json',4,ICON,FANART)
    addDir('NHL',ROOT_URL+'nhl-2013.json',4,ICON,FANART)
    addDir('Notre Dame',ROOT_URL+'nd-2013.json',4,ICON,FANART)
    addDir('PGA Tour',ROOT_URL+'pga-2013.json',4,ICON,FANART)
    addDir('Premier League',ROOT_URL+'premier-league.json',4,ICON,FANART)
    addDir('Pro Motocross',ROOT_URL+'moto-2013.json',4,ICON,FANART)
    addDir('Tennis',ROOT_URL+'tennis-2013.json',4,ICON,FANART)    


def SCRAPE_VIDEOS(url):            
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'NBCSports/742 CFNetwork/672.0.8 Darwin/14.0.0')
    response = urllib2.urlopen(req)   
    json_source = json.load(response)                       
    response.close()            

    try:       
        for item in json_source:         
            BUILD_VIDEO_LINK(item)
    except:
        pass

    try:
        for item in json_source['replay']:        
            BUILD_VIDEO_LINK(item)
    except:
        pass

    try:
        for item in json_source['showCase']:        
            BUILD_VIDEO_LINK(item)
    except:
        pass

    try:       
        for item in json_source['spotlight']:         
            BUILD_VIDEO_LINK(item)
    except:
        pass    


def BUILD_VIDEO_LINK(item):
    url = item['iosStreamUrl']
    #url = url.replace('manifest(format=m3u8-aapl-v3)','QualityLevels(3490000)/Manifest(video,format=m3u8-aapl-v3,audiotrack=audio_en_0)')                     
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
        ####NOT USED###
        FEATURED()
elif mode==3:
        #REPLAYS()
        GET_ALL_SPORTS()
elif mode==4:
        SCRAPE_VIDEOS(url)
xbmcplugin.endOfDirectory(addon_handle)
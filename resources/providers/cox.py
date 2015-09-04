import sys
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import re, os, time
import urllib, urllib2, httplib2
import json
import HTMLParser
import time
import cookielib
import base64
import string, random
from resources.globals import *



class COX():  
  
    def __init__(self):
        self.REFERER_URL = ''
        self.TARGET = ''
        self.ON_SUCCESS = ''
        self.ON_FAILURE = ''


    def GET_IDP(self):        
        if not os.path.exists(ADDON_PATH_PROFILE):
            os.makedirs(ADDON_PATH_PROFILE)
        
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))
        
        #IDP_URL= 'https://sp.auth.adobe.com/adobe-services/authenticate?requestor_id=nbcsports&redirect_url=http://stream.nbcsports.com/nbcsn/index_nbcsn-generic.html?referrer=http://stream.nbcsports.com/liveextra/&domain_name=stream.nbcsports.com&mso_id=TWC&noflash=true&no_iframe=true'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))    
        opener.addheaders = [ ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                            ("Accept-Language", "en-us"),
                            ("Proxy-Connection", "keep-alive"),
                            ("Connection", "keep-alive"),
                            ("User-Agent", UA_IPHONE)]
        
        resp = opener.open(IDP_URL)
        idp_source = resp.read()
        resp.close()
        #print idp_source
        #cj.save(ignore_discard=True);                
        SAVE_COOKIE(cj)        

      
        url = FIND(idp_source,'"0;url=','"')
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj)) 
        opener.addheaders = [ ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                            ("Accept-Language", "en-us"),
                            ("Proxy-Connection", "keep-alive"),
                            ("Connection", "keep-alive"),
                            ("User-Agent", UA_IPHONE),
                            ("Referer", IDP_URL)]
        
        resp = opener.open(url)
        login_source = resp.read()
        resp.close()        

        SAVE_COOKIE(cj)

        login_source = login_source.replace('\n',"")        

        print "RESP.GETURL() ==="        
        #print HTMLParser.HTMLParser().unescape(resp.geturl())
        self.REFERER_URL = resp.geturl()

        last_url = urllib.unquote(resp.geturl())
        last_url = last_url.replace('-','')
        print last_url
        
        saml_request = FIND(last_url,'SAMLRequest=','&')
        print "SAML REQUEST"
        print saml_request

        relay_state = FIND(last_url,'RelayState=','&')
        print "RELAY STATE"
        print relay_state

        saml_submit_url = FIND(login_source,'action="','"')

        self.TARGET = FIND(login_source,'<input type="hidden" name="target" value="','"')
        self.ON_SUCCESS = FIND(login_source,'<input type="hidden" name="onsuccess" value="','"')
        self.ON_FAILURE = FIND(login_source,'<input type="hidden" name="onfailure" value="','"')


        return saml_request, relay_state, saml_submit_url
    
    def LOGIN(self, saml_request, relay_state, saml_submit_url):
        ###################################################################
        #Post username and password to idp        
        ###################################################################        
        
        cj = cookielib.LWPCookieJar()
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))    
        opener.addheaders = [ ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("Accept-Language", "en-us"),
                            ("Content-Type", "application/x-www-form-urlencoded"),
                            ("Proxy-Connection", "keep-alive"),
                            ("Connection", "keep-alive"),
                            ("Referer", self.REFERER_URL),
                            ("User-Agent", UA_IPHONE)]

        
        login_data = urllib.urlencode({'username' : USERNAME,
                                       'password' : PASSWORD,
                                       'CallerID' : 'tvonline',
                                       'x' :  '82',
                                       'y' :  '13',
                                       'target' :  self.TARGET,
                                       'onsuccess' :  self.ON_SUCCESS,
                                       'onfailure' :  self.ON_FAILURE,                                       
                                       'DeviceID' :  ''
                                       })
        
        try:
            resp = opener.open(saml_submit_url, login_data)
            print resp.getcode()
            print resp.info()
            #idp_source = resp.read()
            if resp.info().get('Content-Encoding') == 'gzip':
                buf = StringIO(resp.read())
                f = gzip.GzipFile(fileobj=buf)
                idp_source = f.read()
            else:
                idp_source = resp.read()
                
            resp.close()
            
            saml_response = FIND(idp_source,'<input type="hidden" name="SAMLResponse" value="','"')  
            saml_response = HTMLParser.HTMLParser().unescape(saml_response)                                                        
            relay_state = FIND(idp_source,'<input type="hidden" name="RelayState" value="','"')

         
        except:
            saml_response = ""
            relay_state = ""
        
        return saml_response, relay_state

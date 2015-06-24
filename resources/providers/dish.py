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


class DISH():    

    def LOGIN(self, saml_request, relay_state, saml_submit_url):            
        first_bookend_url = self.POST_SAML_REQUEST(saml_request, relay_state, saml_submit_url)                
        social_login_url = self.FIRST_BOOKEND(first_bookend_url)        
        saml_response, relay_state = self.SOCIAL_LOGIN(social_login_url)

        return saml_response, relay_state

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
        SAVE_COOKIE(cj)

        idp_source = idp_source.replace('\n',"")        

        saml_request = FIND(idp_source,'<input type="hidden" name="SAMLRequest" value="','"')
        #print saml_request

        relay_state = FIND(idp_source,'<input type="hidden" name="RelayState" value="','"')

        saml_submit_url = FIND(idp_source,'action="','"')
        
        
        print saml_submit_url
        #print relay_state
        return saml_request, relay_state, saml_submit_url
   
    def POST_SAML_REQUEST(self, saml_request, relay_state, saml_submit_url):
        ###################################################################
        #Post username and password to idp        
        ###################################################################                     
        #cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))
        
        cj = cookielib.LWPCookieJar()
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))    
        opener.addheaders = [ ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("Accept-Language", "en-us"),
                            ("Content-Type", "application/x-www-form-urlencoded"),
                            ("Proxy-Connection", "keep-alive"),
                            #("Connection", "keep-alive"),
                            ("Origin", "https://sp.auth.adobe.com"),
                            ("Referer", IDP_URL),
                            ("User-Agent", UA_IPHONE)]

        
        login_data = urllib.urlencode({'SAMLRequest' : saml_request,
                                       'RelayState' : relay_state,                                       
                                       })
        
        resp = opener.open(saml_submit_url, login_data)
        idp_source = resp.read()
        #print resp.geturl()
        #print resp.info()
        #print resp.getcode()
        resp.close()
        cj.save(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True);

        first_bookend_url = resp.geturl()+ "&history=1"

        return first_bookend_url
        
        #print idp_source
        

    def FIRST_BOOKEND(self,first_bookend_url):        
        cj = cookielib.LWPCookieJar()
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))    
        opener.addheaders = [ ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("Accept-Language", "en-us"),
                            ("Content-Type", "application/x-www-form-urlencoded"),
                            ("Proxy-Connection", "keep-alive"),
                            ("Connection", "keep-alive"),                            
                            ("Origin", "https://identity1.dishnetwork.com"),
                            ("Referer", first_bookend_url),
                            ("User-Agent", UA_IPHONE)]

        
        resp = opener.open(first_bookend_url)
        idp_source = resp.read()
        print resp.geturl()
        print resp.info()
        #print resp.getcode()
        resp.close()
        #print idp_source
        #cj.save(ignore_discard=True);
        cj.save(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True);
        social_login_url = resp.geturl()

        return social_login_url
        



    
    def SOCIAL_LOGIN(self,social_login_url):        
        cj = cookielib.LWPCookieJar(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'))
        cj.load(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True)
        
        ck = cookielib.Cookie(version=0, name='s_cc', value='true', port=None, port_specified=False, domain='identity1.dishnetwork.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
        cj.set_cookie(ck)
        ck = cookielib.Cookie(version=0, name='s_sq', value='synacortveauth%3D%2526pid%253DFederated%252520Login%2526pidt%253D1%2526oid%253Dauthsynacor_identity1.dishnetwork.com%2526oidt%253D3%2526ot%253DSUBMIT', port=None, port_specified=False, domain='identity1.dishnetwork.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
        cj.set_cookie(ck)
        
       
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))    
        opener.addheaders = [ ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("Accept-Language", "en-us"),
                            ("Content-Type", "application/x-www-form-urlencoded"),
                            ("Proxy-Connection", "keep-alive"),
                            ("Connection", "keep-alive"),                            
                            ("Referer", social_login_url),
                            ("Origin", "https://identity1.dishnetwork.com"),                            
                            ("User-Agent", UA_IPHONE)]


        
        login_data = urllib.urlencode({'username' : USERNAME,
                                       'password' : PASSWORD,
                                       'login_type' : 'username,password',                                       
                                       'source' : 'authsynacor_identity1.dishnetwork.com',
                                       'source_button' : 'authsynacor_identity1.dishnetwork.com',
                                       'remember_me' : 'yes'
                                       })
       
       
        resp = opener.open(social_login_url,login_data)        

        #final_response = resp.read()       

        print "RESP.GETURL() ==="
        print resp.geturl()
        
        last_url = resp.geturl()

        print "RESP.INFO() ==="
        print resp.info()
        
        print "RESP.GETCODE() ==="
        print resp.getcode()

        #final_response = resp.read().decode('utf-8')
        #print "RESP.READ() ==="
        #print final_response
        if resp.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(resp.read())
            f = gzip.GzipFile(fileobj=buf)
            final_response = f.read()
        
        resp.close()
        print "FINAL RESPONSE"
        print final_response

        final_response = final_response.replace('\n',"")         
        discovery_url = FIND(final_response,'location.href = "','"')
        #Set-Cookie: dishnetworkIdPAuthToken=_c21b23175bc892b059442bc83c8673d136fa0a49a7; expires=Sun, 20-Sep-2015 01:09:12 GMT; path=/; secure; httponly
        #     https://identity1.dishnetwork.com/saml/module.php/authSynacor/DiscoveryAssociationsResume.php?AuthState=_3f1b976cc3bd753a301f6833441498686bfbae2252:https://identity1.dishnetwork.com/saml/saml2/idp/SSOService.php?spentityid=https://saml.sp.auth.adobe.com&cookieTime=1434935346&RelayState=_dbef1c01-9685-48cc-b14b-ec04ecf94f7f&RequesterID=["nbcsports"]&NameIDFormat=urn:oasis:names:tc:SAML:2.0:nameid-format:transient
        #;url=https://identity1.dishnetwork.com/saml/module.php/authSynacor/DiscoveryAssociationsResume.php?AuthState=_3a83533c78dd5f209c527de83dc3bf84d8566b012d%3Ahttps%3A%2F%2Fidentity1.dishnetwork.com%2Fsaml%2Fsaml2%2Fidp%2FSSOService.php%3Fspentityid%3Dhttps%253A%252F%252Fsaml.sp.auth.adobe.com%26cookieTime%3D1434822289%26RelayState%3D_0c70f098-ba6a-452a-bbf1-c41a3684bbb1%26RequesterID%3D%255B%2522nbcsports%2522%255D%26NameIDFormat%3Durn%253Aoasis%253Anames%253Atc%253ASAML%253A2.0%253Anameid-format%253Atransient" />
        #discovery_url = FIND(final_response,'url=','"')
        
        

        saml_response = ''
        relay_state = ''

        if discovery_url != '':
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))    
            opener.addheaders = [ ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                                ("Accept-Encoding", "gzip, deflate"),
                                ("Accept-Language", "en-us"),
                                ("Content-Type", "application/x-www-form-urlencoded"),
                                ("Proxy-Connection", "keep-alive"),
                                ("Connection", "keep-alive"),                            
                                ("Referer", last_url),
                                ("Origin", "https://identity1.dishnetwork.com"),
                                #("Cookie", cookies + " s_cc=true; s_sq=synacortveauth%3D%2526pid%253DFederated%252520Login%2526pidt%253D1%2526oid%253Dauthsynacor_identity1.dishnetwork.com%2526oidt%253D3%2526ot%253DSUBMIT"),
                                ("User-Agent", UA_IPHONE)]
           
            resp = opener.open(discovery_url)
            idp_source = resp.read()
            print resp.geturl()
            last_url = resp.geturl()
            #print idp_source
            resp.close()


            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))    
            opener.addheaders = [ ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                                ("Accept-Encoding", "gzip, deflate"),
                                ("Accept-Language", "en-us"),
                                ("Content-Type", "application/x-www-form-urlencoded"),
                                ("Proxy-Connection", "keep-alive"),
                                ("Connection", "keep-alive"),                            
                                ("Referer", last_url),
                                ("Origin", "https://identity1.dishnetwork.com"),
                                #("Cookie", cookies + " s_cc=true; s_sq=synacortveauth%3D%2526pid%253DFederated%252520Login%2526pidt%253D1%2526oid%253Dauthsynacor_identity1.dishnetwork.com%2526oidt%253D3%2526ot%253DSUBMIT"),
                                ("User-Agent", UA_IPHONE)]
           
            resp = opener.open(last_url+"&history=3")
            if resp.info().get('Content-Encoding') == 'gzip':
                buf = StringIO(resp.read())
                f = gzip.GzipFile(fileobj=buf)
                idp_source = f.read()

            #idp_source = resp.read()
            print resp.geturl()
            last_url = resp.geturl()
            print idp_source
            resp.close()             

            saml_response = FIND(idp_source,'<input type="hidden" name="SAMLResponse" value="','"')
            relay_state = FIND(idp_source,'<input type="hidden" name="RelayState" value="','"')

            #Set Global header fields         
            ORIGIN = 'https://identity1.dishnetwork.com'
            REFERER = last_url

            #cj.save(os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp'),ignore_discard=True);
            SAVE_COOKIE(cj)

        print saml_response
        print relay_state
                
        
        return saml_response, relay_state

        

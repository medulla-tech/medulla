import os
from pyquery import PyQuery as pq
import urllib,urllib2
import re,string
import logging
import tempfile
import time

# Twisted
from twisted.python import threadable; threadable.init(1)
from twisted.internet.threads import deferToThread
deferred = deferToThread.__get__ #Create an alias for deferred functions

# BackupPC DB
from pulse2.database.backuppc import BackuppcDatabase

logger = logging.getLogger()

# Error consts
_FORMAT_ERROR = {'err':14,'errtext':'Incorrect format, check if the version of BackupPC is supported'}
_CONNECTION_ERROR = {'err':10,'errtext':'Unable to connect to BackupPC server.'}
_ENCODING_ERROR = {'err':19,'errtext':'Encoding error.'}
_UNKNOWN_ERROR = {'err':20,'errtext':'Unable to perform selected action, unknown error occured.'}

# Global vars
download_status = {}

# ==========================================================================
# BACKUP SERVER I/O FUNCTIONS
# ==========================================================================

def getBackupServerByUUID(uuid):
    """
    @param uuid: Machine uuid
    @type uuid: str
    
    @returns: the Backup Server URL for the specified UUID
    @rtype: str
    """
    #return 'localhost/backuppc/index.cgi'
    from pulse2.managers.location import ComputerLocationManager
    try:
        entity_uuid = ComputerLocationManager().getMachinesLocations([uuid])[uuid]['uuid']
        parent_entities = [entity_uuid] + ComputerLocationManager().getLocationParentPath(entity_uuid)
    except:
        logger.error("Cannot get Entity for this UUID (%s)" % uuid)
        return ''
    url = ''
    for _uuid in parent_entities:
        url = BackuppcDatabase().get_backupserver_by_entity(_uuid)
        if url: return url
    # If we're here, Backup host not mapped
    logger.error("Cannot get BackupServer for this UUID (%s), please check Entity <> BackupServer mappings." % uuid)
    return ''
   
   
def dictToURL(params):   
    s = ''
    for k in params.keys():
        if type(params[k]) == type([]):
            for val in params[k]:
                s+= '&%s=%s' % (k,val)
            del params[k]
    return urllib.urlencode(params)+s

def send_request(params,url=''):
    """Send a request to BackupPC web interface.
    params [dict]: params to be transmitten.
    url : (Default empty) BackupPC Server url, if not specified 
    get the default server for the host entity.
    If success, returns HTML response.
    """
    # Getting BackupServer URL
    url = url or getBackupServerByUUID(params['host'].upper())
    if not url: return
    # Host to lower case
    if 'host' in params: params['host'] = params['host'].lower()
    # Converting params dict to an http query string
    params_str = dictToURL(params)
    # Sending a POST request
    try:
        response = urllib2.urlopen(url,params_str)
        return unicode(response.read(),'utf8').encode('ascii', 'xmlcharrefreplace')
    except:
        logger.error("Unable to connect to BackupPC server : %s" % url)
        return ''


# ==========================================================================
# GLOBAL PARSING FUNCTIONS
# ==========================================================================

def getTableByTitle(html,title):
    d = pq(html)
    # Searching for the right title
    titles = d('div.h2')
    div = []
    for i in xrange(len(title)):
        if titles.eq(i).text() == title:
            div = titles.eq(i)
            break
    if div:
        return div.nextAll().filter('table').eq(0)
    else:
        return []

def getTableHeader(table):
    header = table.find('.tableheader').find('td')
    hd = []
    for i in xrange(len(header)):
        hd += [header.eq(i).text()]
    return hd

def getTableContent(table):
    count = len(table.find('tr'))
    # Init filecount var and files dictionnary
    lines = []
    for i in xrange(count):
        if table.find('tr').eq(i).attr('class')=='tableheader':
            continue
        cols = table.find('tr').eq(i).find('td')
        line = []
        for i in xrange(len(cols)):
            line += [cols.eq(i).text()]
        lines += [line]
    return [list(i) for i in zip(*lines)]

  
def getHTMLerr(html):    
    d = pq(html)
    page_title = d('title').text()
    if page_title == 'BackupPC: Error':
        # Printing error text
        logger.warning(d('.h1').text())
        return {'err':15,'errtext':d('.h1').text()}
    

# ==========================================================================
# MAIN BACKUPPC FUNCTIONS
# ==========================================================================

def get_host_list(pattern=""):
    """Get all configured hosts on BackupPC server.
    pattern (optional): to specify if a search is done.
    """
    html=send_request({},'localhost/backuppc/index.cgi')
    if not html:
        return _CONNECTION_ERROR
    d = pq(html)
    hosts=[]
    options=d('select:first').find('option')
    if not options:
        return _FORMAT_ERROR
    for i in xrange(len(options)):
        if options.eq(i).attr('value') != '#' and pattern in options.eq(i).text():
            hosts = hosts + [options.eq(i).text()]
    return {'err':0,'data':hosts}
    

def get_backup_list(host):
    """Get available restore point for the specified host.
    host: host name or UUID (depending on your config).
    """
    html=send_request({'host':host})
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html): 
        return getHTMLerr(html)
    tb_bak_sum = getTableByTitle(html,'Backup Summary')   
    if tb_bak_sum:
        bk_list = getTableContent(tb_bak_sum)
        return {'err':0,'data':bk_list}
    else:
        return _FORMAT_ERROR
 
   
   
def get_share_names(host,backup_num):
    # Setting params
    params = {}
    params['action'] = 'browse'
    params['host'] = host
    params['num'] = backup_num
    # Sending request
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html): 
        return getHTMLerr(html)
    # Setting a pquery object on html
    d = pq(html)
    # isolating sharestable
    sharestable = d('table:first').find('table:first')
    if not sharestable:
        return _FORMAT_ERROR
    lines = sharestable.find('tr')
    #init share names array
    share_names = []
    for i in xrange(len(lines)):
            if lines.eq(i).text()[0]=='/':
                    share_names = share_names + [lines.eq(i).text()]
    return {'err':0,'data':share_names}
              


def list_files(host,backup_num,share_name,dir,filter,recursive=0):
    """Returns .
    pattern (optional): to specify if a search is done.
    """
    # Setting params
    params = {'action':'browse','host':host,'num':backup_num,'share':share_name}
    params['dir'] = dir if recursive == 2 else dir.encode('utf8','ignore')
    # Sending request
    html = send_request(params)
    if not html: return _CONNECTION_ERROR
    if getHTMLerr(html): return getHTMLerr(html)
    # Setting a pquery object on html response
    d = pq(html)
    # Isolating filetable
    filetable = d('table:first').find('table:last')
    if not filetable: return _FORMAT_ERROR
    # Init filecount var and files dictionnary
    linecount = len(filetable.find('tr'))
    result = [[],[],[],[],[],[],[]]
    for i in xrange(1,linecount):
        cols = filetable.find('tr').eq(i).find('td')
        if len(cols) == 6:
            if filter in cols.eq(0).text():
                # Attributes
                result[0] += [cols.eq(0).text()]
                result[1] += [cols.eq(0).find('input').val()]
                result[2] += [cols.eq(3).text()]
                result[3] += [cols.eq(1).text()]
                result[4] += [cols.eq(2).text()]
                result[5] += [cols.eq(4).text()]
                result[6] += [cols.eq(5).text()]
            # if recursive is on, we add directories to dirs array to browse them
            if recursive and cols.eq(1).text()=='dir':
                subdir = urllib.unquote(cols.eq(0).find('input').val())
                sub = list_files(host,backup_num,share_name,subdir,filter,2)
                if not sub['err']:
                    for i in xrange(len(sub['data'])):
                        result[i]+=sub['data'][i]
    return {'err':0,'data':result}


def get_file_versions(host,share_name,filepath):
    # Result array
    backup_nums = []
    datetimes = []
    # Getting available restore points for the host
    restore_points = get_backup_list(host)
    if restore_points['err']:
        return restore_points
    # Define filename and file path
    filename = os.path.basename(filepath)
    dir = os.path.dirname(filepath)
    # Testing if file is available in that restore point
    for i in xrange(len(restore_points['data'][0])):
        point = restore_points['data'][0][i]
        datetime = restore_points['data'][4][i]
        list = list_files(host,point,share_name,dir,filename)
        if 'data' in list.keys() and filename in list['data'][0]:
            backup_nums+= [point]
            datetimes+= [datetime]
    return {'err':'0','backup_nums':backup_nums,'datetimes':datetimes}


# ==========================================================================
# RESTORE FUNCTIONS
# ==========================================================================

@deferred
def download_file(filepath,params):
    url = getBackupServerByUUID(params['host'])
    # Host to lower case
    if 'host' in params: params['host'] = params['host'].lower()
    # Converting params dict to an http get string
    try:
        params_str = urllib.urlencode(params)
    except:
        return _ENCODING_ERROR
    #
    try:
        response = urllib.urlretrieve(url,filepath,None,params_str)
        os.chmod(filepath,511)
        #Testing HTTP headers and checking for errors
        regex= 'attachment; filename="(.+)"'
        if 'content-disposition' in response[1].dict and re.match(regex,response[1].dict['content-disposition']):
            return {'err':0,'filepath':filepath}
        else:
            if response[1].type == 'text/html':
                html = open(response[0], 'r').read()
                return getHTMLerr(html) or _UNKNOWN_ERROR
            else:
                logger.warning('Unable to restore file, unkown error occured')
                return _UNKNOWN_ERROR
    except:
            logger.warning('Unable to download file from BackupPC server')
            return {'err':17,'errtext':'Unable to download file from BackupPC server'}


def get_download_status():
    global download_status
    return download_status


def restore_file(host,backup_num,share_name,files):
    """
    @param host: Host uuid
    @type host: str
    @param backup_num: Backup Number
    @type backup_num: str
    @param share_name: Selected ShareName
    @type share_name: str
    @param files: Files to restore
    @type files: str,list
    
    Launch a Download thread of the specified file from the Backup Server.
    If <files> is a List, a ZIP archive is generated.
    
    @returns: Temporary Path to the restored file
    @rtype: str
    """
    # Define deferred callback and failure functions
    def _success(result):
        # Set download status to 1 (finished) for this download entry
        global download_status
        download_status[destination].update({'status':1})
        download_status[destination].update(result)
    def _failure(failure):
        logger.error(str(failure))
    # 
    # Generating temp filepath
    #tempfile.tempdir = config.getTempDir()          # Setting temp dir
    tempfiledir = tempfile.mkdtemp()
    os.chmod(tempfiledir,511)
    if isinstance(files,list):
        destination= os.path.join(tempfiledir,'restore-%d.zip' % int(time.time()))
        # Setting params
        params = {'action':'Restore','host':host,'num':backup_num,'type':'2'}
        params.update({'share':share_name,'relative':'1','compressLevel':'5'})
        # Files list
        params['fcbMax']=len(files)+1
        for i in xrange(len(files)):
                params['fcb'+str(i)] = urllib.unquote(files[i])
    else:
        destination = os.path.join(tempfiledir,os.path.basename(files))
        # Setting params
        params = {'action':'RestoreFile','host':host,'num':backup_num,'share':share_name}
        params['dir'] = files.encode('utf-8')
    # Updating download_status (0 = running) dict
    global download_status
    download_status[destination] = {'status':0}
    # Setting a callback on download file functions
    download_file(destination,params).addCallback(_success).addErrback(_failure)
    return destination


def restore_files_to_host(host,backup_num,share_name,files,hostDest='',shareDest='',pathHdr='/'):
    # Setting params
    params = {'action':'Restore','host':host,'num':backup_num,'type':'4'}
    params['share'] = share_name.encode('utf8','ignore')
    if hostDest:
        params['hostDest'] = hostDest.encode('utf8','ignore')
    else:
        params['hostDest'] = host.lower()
    if shareDest:
        params['shareDest'] = shareDest.encode('utf8','ignore')
    else :
        params['shareDest'] = share_name
    params['pathHdr'] = pathHdr.encode('utf8','ignore')
    # Files list
    params['fcbMax']=len(files)+1
    for i in xrange(len(files)):
            params['fcb'+str(i)] = files[i].encode('utf8','ignore')
    # Converting params dict to an http get string
    html = send_request(params)
    if not html: return _CONNECTION_ERROR
    if getHTMLerr(html): 
        return getHTMLerr(html)
    else:
        return {'err':0}

# ==========================================================================
# HOST CONFIG FUNCTIONS
# ==========================================================================

def get_host_config(host,backupserver=''):
    # Function to convert _zZ_ to dict
    def underscores_to_dict(cfg):        
        for key in cfg.keys():
            if '_zZ_' in key:
                keys = string.split(key,'_zZ_')
                root = cfg
                for i in xrange(len(keys)-1):
                    nkey = keys[i]
                    if not nkey in root: 
                        root[nkey]={}
                    root=root[nkey]
                root[keys[-1]] = cfg[key]
                del cfg[key]
    host_config = {}
    general_config = {}
    overrides = {}
    params = {}
    params['action'] = 'editConfig'
    params['host'] = host
    html = send_request(params,backupserver)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html): 
        return getHTMLerr(html)
    d=pq(html)
    inputs=d('form[name=editForm]').find('input')
    if not inputs:
        return _FORMAT_ERROR
    for i in xrange(len(inputs)):
        key = inputs.eq(i).attr('name')
        value = inputs.eq(i).val()
        # Isolating host config params
        if 'v_zZ_' in key:          
            host_config[key.replace('v_zZ_','')]= value
        # Isolating general config params
        elif 'orig_zZ_' in key:
            general_config[key.replace('orig_zZ_','')]= value
        # Isolating overrides
        elif 'override_' in key:
            overrides[key.replace('override_','')] = value
    underscores_to_dict(host_config)
    underscores_to_dict(general_config)
    return {'err':'0', 'host_config':host_config, \
            'general_config':general_config, 'overrides': overrides}



def set_host_config(host,config,globalconfig=0,backupserver=''):
    # Function used to format params
    def dict_to_underscores(cfg):
        for z in cfg.keys():
            if type(cfg[z])==type({}):
                for h in cfg[z].keys():
                    cfg[z+'_zZ_'+h] = cfg[z][h]
                del cfg[z]
                dict_to_underscores(cfg)
                break
            if type(cfg[z])==type([]):
                for h in xrange(len(cfg[z])):
                    cfg[z+'_zZ_'+str(h)] = cfg[z][h]
                del cfg[z]
                dict_to_underscores(cfg)
                break
    if not host and not globalconfig: return
    params = {}
    params['host'] = host
    params['action'] = 'editConfig'
    params['saveAction'] = 'Save'
    _config = config.copy()
    __config = config.copy()
    # Setting overrides
    for p in __config.keys():
        params['override_'+p] = '1'
    # Formatting config dict
    dict_to_underscores(__config)
    # Setting overrides and params
    for p in __config:
        params['v_zZ_'+p] = __config[p]
    # TODO : fix this for all params
    if 'BackupFilesExclude' in _config:
        params['vflds.BackupFilesExclude'] = _config['RsyncShareName']
    # Sending HTTP request
    html = send_request(params,backupserver)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html): 
        return getHTMLerr(html)
    return {'err':0}
    
    
def set_backup_for_host(uuid):
    server_url = getBackupServerByUUID(uuid)
    if not server_url: return
    config = get_host_config('',server_url)['general_config']
    newid = str(int(max(config['Hosts'].keys()))+1)
    config['Hosts'][newid] = {'host':uuid,'dhcp':'0','user':'root','moreUsers':'0'}
    res = set_host_config('',config,1,server_url)
    if res['err']: return res
    # Checking if host has been added, then add it to DB
    config = get_host_config('',server_url)['general_config']
    is_added = 0
    for i in config['Hosts']:
        if config['Hosts'][i]['host'].lower() == uuid.lower():
            is_added = 1
            break
    if not is_added:
        logger.error("Unable to set host on BackupPC server")
        return {'err':22,'errtext':'Unable to set host on BackupPC server'}
    # Setting nmblookup cmds and Rsync cmds in conf
    # TODO : read NmbLookupCmd from ini file
    config = {}
    config['NmbLookupCmd'] = '/usr/bin/python /usr/bin/pulse2-uuid-resolver -A $host -f -g'
    config['NmbLookupFindHostCmd'] = '/usr/bin/python /usr/bin/pulse2-uuid-resolver $host'
    config['RsyncClientCmd'] = '$sshPath -q -x -o StrictHostKeyChecking=no -l root $hostIP $rsyncPath $argList+'
    config['RsyncClientRestoreCmd'] = '$sshPath -q -x -o StrictHostKeyChecking=no -l root $hostIP $rsyncPath $argList+'
    config['XferMethod'] = 'rsync'
    config['PingCmd'] = '/bin/true'
    set_host_config(uuid,config)
    # Adding host to the DB
    try:
        BackuppcDatabase().add_host(uuid)
    except:
        logger.error("Unable to add host to database")
        return {'err':23,'errtext':'Unable to add host to database'}
    

# ==========================================================================
# SERVER, HOST INFO AND BACKUP LOGS
# ==========================================================================

def get_host_log(host):
    params = {}
    params['host'] = host
    params['action'] = 'view'
    params['type'] = 'LOG'
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html): 
        return getHTMLerr(html)
    d=pq(html)
    if not d('pre:first'):
        return _FORMAT_ERROR
    else:
        return d('pre:first').text()


def get_xfer_log(host,backupnum):
    params = {}
    params['host'] = host
    params['action'] = 'view'
    params['type'] = 'XferErr'
    params['num'] = backupnum
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html): 
        return getHTMLerr(html)
    d=pq(html)
    if not d('pre:first'):
        return _FORMAT_ERROR
    else:
        return {'err':0,'data':d('pre:first').text()}

def apply_backup_profile(profileid):
    # Hosts corresponding to selected profile
    hosts = BackuppcDatabase().get_hosts_by_backup_profile(profileid)
    # Getting profile settings
    profile = BackuppcDatabase().edit_backup_profile(profileid,{})
    # Define config dict
    config = {}
    config['RsyncShareName'] = profile['sharenames'].split('\n')
    excludes = profile['excludes'].split('||')
    for i in xrange(len(excludes)):
        excludes[i] = excludes[i].split('\n')
    config['BackupFilesExclude'] = dict(zip(config['RsyncShareName'],excludes))
    for host in hosts:
        set_host_config(host,config)
    # TODO : Error treatment
    return 0


def apply_period_profile(profileid):
    # Hosts corresponding to selected profile
    hosts = BackuppcDatabase().get_hosts_by_period_profile(profileid)
    # Getting profile settings
    profile = BackuppcDatabase().edit_period_profile(profileid,{})
    # Define config dict
    config = {}
    config['FullPeriod'] = profile['full']
    config['IncrPeriod'] = profile['incr']
    # Blackout periods
    periods = profile['exclude_periods'].split('\n')
    #
    config['BlackoutPeriods'] = []
    #
    for period in periods:
        m = re.search('([0-9.]+)=>([0-9.]+):([^:]+)',period)
        config['BlackoutPeriods'] += [{ \
        'hourBegin':m.group(1), \
        'hourEnd': m.group(2), \
        'weekDays' : m.group(3) \
        }]
    #
    for host in hosts:
        set_host_config(host,config)
    # TODO : Error treatment
    return 0

# ====================================================================
# BACKUP ACTIONS
# ====================================================================

def start_full_backup(host):
    params = {}
    params['host'] = host
    params['action'] = 'Start_Full_Backup'
    params['doit'] = '1'
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html): 
        return getHTMLerr(html)
    return {'err':0}


def start_incr_backup(host):
    params = {}
    params['host'] = host
    params['action'] = 'Start_Incr_Backup'
    params['doit'] = '1'
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html): 
        return getHTMLerr(html)
    return {'err':0}


def stop_backup(host,backoff=''):
    params = {}
    params['host'] = host
    params['action'] = 'Stop_Dequeue_Backup'
    params['doit'] = '1'
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html): 
        return getHTMLerr(html)
    return {'err':0}


def get_host_status(host):
    params = {'host':host}
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html): 
        return getHTMLerr(html)
    result = {'err':0,'status':[]}
    d = pq(html)
    if d('ul:first').find('li'):
        statuslines = d('ul:first').find('li').text()
    else:
        statuslines = ''
    # Status strings
    if 'no ping' in statuslines:
        result['status'] += ['no ping']
    if 'backup failed' in statuslines:
        result['status'] += ['backup failed']
    if 'done' in statuslines:
        result['status'] += ['done']
    if '(idle)' in statuslines:
        result['status'] += ['idle']
    if 'in progress' in statuslines:
        result['status'] += ['in progress']
    if 'canceled by user' in statuslines:
        result['status'] += ['canceled']
    if len(result['status']) == 0:
        result['status'] += ['nothing']
    try:
        tb_summary = getTableByTitle(html,'Backup Summary')
        xfer_summary = getTableByTitle(html,'Xfer Error Summary')
        size_summary = getTableByTitle(html,'File Size/Count Reuse Summary')
        if not (tb_summary and xfer_summary and size_summary):
            return _FORMAT_ERROR
        # Contents
        tb_summary = getTableContent(tb_summary)
        xfer_summary = getTableContent(xfer_summary)
        size_summary = getTableContent(size_summary)
        #
        result['data'] = { \
            'backup_nums':tb_summary[0], \
            'start_dates':tb_summary[4], \
            'durations':tb_summary[5], \
            'ages':tb_summary[6], \
            'xfer_errs':xfer_summary[3], \
            'total_file_count':size_summary[2], \
            'total_file_size':size_summary[3], \
            'new_file_count':size_summary[7], \
            'new_file_size':size_summary[8]
        }
    except:
        result['data'] = {}
    return result

from win32com import client as w32comCl
import json
import _winreg
import sys
from collections import namedtuple
from platform import platform

ssDefault = 0
ssManagedServer = 1
ssWindowsUpdate = 2
ssOthers = 3


# Create Microsoft update COM Session
#global session
session = w32comCl.Dispatch("Microsoft.Update.Session")


def pprinttable(rows):
    if len(rows) > 1:
        headers = rows[0]._fields
        lens = []
        for i in range(len(rows[0])):
            lens.append(len(max([str(x[i]) for x in rows] + [headers[i]],key=lambda x:len(str(x)))))
        formats = []
        hformats = []
        for i in range(len(rows[0])):
            if isinstance(rows[0][i], int):
                formats.append("%%%dd" % lens[i])
            else:
                formats.append("%%-%ds" % lens[i])
            hformats.append("%%-%ds" % lens[i])
        pattern = " | ".join(formats)
        hpattern = " | ".join(hformats)
        separator = "-+-".join(['-' * n for n in lens])
        print hpattern % tuple(headers)
        print separator
        for line in rows:
            print pattern % tuple(line)
    elif len(rows) == 1:
        row = rows[0]
        hwidth = len(max(row._fields,key=lambda x: len(x)))
        for i in range(len(row)):
            print "%*s = %s" % (hwidth,row._fields[i],row[i])

def fetchW32ComArray(arr):
    """
    Convert a win32com dispatch array to a simple python list

    @param arr: Array to fetch
    @type circuits: win32comCollection

    @return: converted list
    @rtype: list
    """
    result = []
    for i in xrange(arr.Count):
        result.append(arr.Item(i))
    return result


def disableWindowsUpdate():
    """
    This function disables windows updates by setting
    the corresponding key in Windows Registry

    @return: True if success or False
    @rtype: bool
    """
    def setRegistryValue(root, key, param_name, newValue = None):
        root = getattr(_winreg, root)
        handle = _winreg.OpenKey(root, key, 0, _winreg.KEY_READ | _winreg.KEY_WRITE) #_winreg.KEY_WOW64_32KEY
        (value, type) = _winreg.QueryValueEx(handle, param_name)
        if newValue is not None:
            _winreg.SetValueEx(handle, param_name, 0, type, newValue)
            #_winreg.SetValue(root, key, param_name, 0, type, newValue)
        (value, type) = _winreg.QueryValueEx(handle, param_name)
        return value

    # wu_state possible values
    # 1 = Don't check
    # 2 = Check but don't download
    # 3 = Download but don't install
    # 4 = Download and install

    wu_state = 1 # Disable Windows Update
    key = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update'

    new_state = setRegistryValue('HKEY_LOCAL_MACHINE', key, 'AUOptions', wu_state)

    return new_state == wu_state


def showUpdateInfo(uuid, online=True):
    # Create an Update Searcher instance
    searcher = session.CreateupdateSearcher()
    searcher.Online = online

    searchResult = searcher.Search("UpdateID='%s'" % uuid)

    updates = fetchW32ComArray(searchResult.Updates)

    if not updates:
        print "Update not found"

    update = updates[0]

    # Printing update info
    print "======================================================"
    print "Update ID \t\t: %s" % update.Identity.UpdateID
    print "Title \t\t\t: %s" % update.Title
    print "Kb Numbers \t\t: %s" % ' '.join(fetchW32ComArray(update.KBArticleIDs))
    print "Type \t\t\t: %s" % update.Type
    print "Need reboot \t\t: %s" % update.InstallationBehavior.RebootBehavior > 0
    print "Request user input\t: %s" % update.InstallationBehavior.CanRequestUserInput
    print "Info URL \t\t: %s" % fetchW32ComArray(update.MoreInfoUrls)[0]
    print "Is installed \t\t: %s" % update.IsInstalled


def searchAvaiableUpdates(online=True, returnResultList=False):
    # Create an Update Searcher instance
    searcher = session.CreateupdateSearcher()
    searcher.Online = online

    # Init updates dict
    header = 'uuid,KB_Number,type,is_installed'.split(',')
    header_verbose = 'uuid,title,KB_Number,type,need_reboot,request_user_input,info_url,is_installed'.split(',')
    content = []
    content_verbose = []
    result = {'header' : header, 'content' : content}
    result_verbose = {'header' : header_verbose, 'content' : content_verbose}

    # Return OS version
    if 'windows-xp' in platform().lower():
        result_verbose['os_class'] = 1
    elif 'windows-vista' in platform().lower():
        result_verbose['os_class'] = 2
    elif 'windows-7' in platform().lower():
        result_verbose['os_class'] = 3

    # Searching not available and not installed updates
    # Search criterions : http://msdn.microsoft.com/en-us/library/windows/desktop/aa386526(v=vs.85).aspx
    # search by UpdateID
    searchResult = searcher.Search("IsInstalled=0 or IsInstalled=1")

    if returnResultList:
        return fetchW32ComArray(searchResult.Updates)

    for i in xrange(searchResult.Updates.Count):
        update = searchResult.Updates.Item(i)
        # See Iupdate class: http://msdn.microsoft.com/en-us/library/windows/desktop/aa386099(v=vs.85).aspx
        _item = []
        _item_verbose = []
        #update.InstallationBehavior.RebootBehavior > 0
        #update.InstallationBehavior.CanRequestUserInput

        # UUID
        _item.append(update.Identity.UpdateID)
        _item_verbose.append(update.Identity.UpdateID)

        # Title
        #_item.append(update.Title) #.encode('utf-8').decode('ascii', 'ignore')
        _item_verbose.append(update.Title) #.encode('utf-8').decode('ascii', 'ignore')

        # Description
        #_item.append(update.Description) #.encode('utf-8').decode('ascii', 'ignore')
        #_item_verbose.append(update.Description) #.encode('utf-8').decode('ascii', 'ignore')

        #_item.append(update.EulaText)
        #_item_verbose.append(update.EulaText)

        # Kb_number
        _item.append(' '.join(fetchW32ComArray(update.KBArticleIDs)))
        _item_verbose.append(' '.join(fetchW32ComArray(update.KBArticleIDs)))

        # Type
        _item.append(update.Type)
        _item_verbose.append(update.Type)

        # Need reboot
        _item_verbose.append(update.InstallationBehavior.RebootBehavior > 0)

        # Request user input
        _item_verbose.append(update.InstallationBehavior.CanRequestUserInput)

        # Info URL
        #_item.append(fetchW32ComArray(update.MoreInfoUrls)[0])
        _item_verbose.append(fetchW32ComArray(update.MoreInfoUrls)[0])

        # Is_installed
        _item.append(update.IsInstalled)
        _item_verbose.append(update.IsInstalled)

        content.append(_item)
        content_verbose.append(_item_verbose)

    return (result, result_verbose)


def installUpdates(uuid_list):
    # Searching cached updates
    cachedUpdates = searchAvaiableUpdates(online=False, returnResultList=True)

    # Creating update installer object
    updatesToDownload = w32comCl.Dispatch("Microsoft.Update.UpdateColl")
    selectedUpdates = []

    for update in cachedUpdates:
        # Get update kb numbers
        kbNumbers = fetchW32ComArray(update.KBArticleIDs)
        # Adding KB prefix to kbNumbers
        kbNumbers = [str(x) for x in kbNumbers]
        intersection = set(kbNumbers) & set(uuid_list)

        # If update is not in uuid_list
        # and uuid_list doesnt contain this update KBnumber, skip it
        if not update.Identity.UpdateID in uuid_list and not intersection:
            continue

        # If update need to interact with user, we skip it
        if update.InstallationBehavior.CanRequestUserInput:
            print "The update %s needs user interaction, skipping it." % ' '.join(kbNumbers)
            continue

        # TODO: Check if installed or not

        # If update needs a licence acceptation, we accept it
        # user accept EULA when he put it in install list
        if not update.EulaAccepted:
            update.AcceptEula()

        # Adding update to updatesToDownload list
        print 'Adding "%s" to install list' % update.Title
        updatesToDownload.Add(update)
        selectedUpdates.append(update)

    if updatesToDownload.Count == 0:
        print "No update to install"
        return

    # ================================================================
    # DOWNLOAD STEP
    # ================================================================

    # Create an update downloader instance
    downloader = session.CreateUpdateDownloader()
    # Adding selected update to downloader instance
    downloader.Updates = updatesToDownload
    # Start download
    print "Starting download ..."
    downloader.Download()

    # ================================================================
    # INSTALLATION STEP
    # ================================================================

    # Creating update to install collection
    updatesToInstall = w32comCl.Dispatch("Microsoft.Update.UpdateColl")

    # This var will be set if there reboot is required for an update
    reboot_after = False

    for update in selectedUpdates:
        # If update is not downloaded, skipping it
        if not update.IsDownloaded:
            print 'Update "%s" was not downloaded' % update.Title
            continue

        # Testing if update needs reboot
        if update.InstallationBehavior.RebootBehavior > 0:
            reboot_after = True

        # Adding update to installation list
        updatesToInstall.Add(update)

    if updatesToInstall.Count == 0:
        print "No updates to install, leaving."
        return

    print "Installing updates ..."

    # Creating update installer instance
    installer = session.CreateUpdateInstaller()
    # installer.RebootRequiredBeforeInstallation
    installer.Updates = updatesToInstall

    # Launch installation
    installationResult = installer.Install()

    if installationResult.RebootRequired:
        print "Rebooting computer is required."

    returnCode = installationResult.ResultCode

    if returnCode == 2 or returnCode == 3:
        print "Installation success"
    elif returnCode == 4:
        print "Installation failed"
    elif returnCode == 5:
        "Installation aborted"
    else:
        print "Unkown error (%d)" % returnCode

    """
    installationResult.RebootRequired = True/False
    installationResult.ResultCode
      orcNotStarted           = 0,
      orcInProgress           = 1,
      orcSucceeded            = 2,
      orcSucceededWithErrors  = 3,
      orcFailed               = 4,
      orcAborted              = 5
    """

    return returnCode


# Disabling windows update service
# ugly try, except, but not really important to continue
try:
    if not disableWindowsUpdate():
        print "Cannot disable Windows Update Service"
except:
    print "Cannot disable Windows Update Service"

args = sys.argv

if len(args) < 2:
    print "pulse-update-manager 0.4 for win32"
    print "Usage : \tpulse-update-manager [options] [update_list]"
    print ""
    print "Options:"
    print "  -l, --list : List all updates available for this machine"
    print "  --offline : List mode, list cached updates (offline mode)"
    print "  --json : List mode, output in JSON format"
    print "  -i, --install : Install specified updates (uuid or kb_number)"
    print ""
    print ""
    print "Examples:"
    print "  pulse-update-manager -l --offline --json"
    print "  pulse-update-manager --install 2791765 2741517"
    sys.exit(0)

command = args[1]

# Specific update info
if command == '-d' or command == '--detail':
    if (len(args) < 3):
        print "You must specify update UUID"
        sys.exit(0)
    online = not ('--offline' in args)
    showUpdateInfo(args[2], online)

# Update install switches
if '-i' in args or '--install' in args:
    installUpdates(args[1:])

# Update listing switches
if '--list' in args or '-l' in args:
    # Search all available updates
    print "Searching for updates ..."
    #
    online = not ('--offline' in args)

    (result, result_verbose) = searchAvaiableUpdates(online)

    if '--json' in args:
        # Printing JSON
        print "===JSON_BEGIN==="
        print json.dumps(result_verbose)
        print "===JSON_END==="
    elif '--otherformat' in args:
        pass
    else:
        # Printing table
        Row = namedtuple('Row', result['header'])
        pprinttable([Row(*item) for item in result['content']])


sys.exit(0)

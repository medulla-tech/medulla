$computerName = "."
$wmi = [WMI] ""
get-wmiobject Win32_UserProfile -computername $computerName | foreach-object {
  $userAccount = [WMI] ("\\$computerName\root\cimv2:Win32_SID.SID='{0}'" -f $_.SID)
  $userName = "{0}\{1}" -f $userAccount.ReferencedDomainName,$userAccount.AccountName
  new-object PSObject -property @{
    "Name" = $userName
    "LastUseTime" = $_.LastUseTime
  }
} | sort-object LastUseTime -descending | ?{!($_ | select-string "NT AUTHORITY")} | ?{!($_ | select-string "NT SERVICE")} | ?{!($_ | select-string "Administrator")} | ?{!($_ | select-string "Administrateur")} | ?{!($_ | select-string "default")} | ?{!($_ | select-string "pulse")} | Select-Object -first 1

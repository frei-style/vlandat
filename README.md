# vlandat

Parser for Cisco IOS VLAN database files.

## About

This is a module and a utility to get some information from a vlan.dat.

More details about the file structure and the reverse engineering are available here: [Wiki: vlan.dat](https://wiki.defect.ch/os/ios/vlan.dat)

## Examples

### Utility Usage

```
$ ./vlandat.py -f vlan.dat 
VTP Version                     : 1
Configuration Revision          : 3
Number of existing VLANs        : 7
VTP Operating Mode              : server
VTP Domain Name                 : 
VTP Password                    : 
VTP Pruning Mode                : disabled
VTP V2 Mode                     : disabled
MD5 digest                      : 0x17 0xFA 0xF9 0xF6 0x7A 0x7B 0x81 0xB3
                                  0x09 0xDE 0x5A 0x9C 0x5E 0x4B 0x72 0xCE
Configuration last modified by 192.168.100.4 at 1993-03-02 02:55:30

  ID Name                             Type  MTU  SAID   State     Ring Parent RemoteSPAN STP  Bridge STE BackupCRF ARE BridgeMode Trans1 Trans2
   1 default                          enet  1500 100001 active       0      0          0 none      0   0 disabled    0 none            0      0
  10 GastWlan                         enet  1500 100010 active       0      0          0 none      0   0 disabled    0 none            0      0
  13 Voice                            enet  1500 100013 active       0      0          0 none      0   0 disabled    0 none            0      0
1002 fddi-default                     fddi  1500 101002 active       0      0          0 none      0   0 disabled    0 none            0      0
1003 token-ring-default               trcrf 1500 101003 active       0      0          0 none      0   7 disabled    7 none            0      0
1004 fddinet-default                  fdnet 1500 101004 active       0      0          0 ieee      0   0 disabled    0 none            0      0
1005 trnet-default                    trbrf 1500 101005 active       0      0          0 ibm       0   0 disabled    0 none            0      0
```

### Module Usage

Import the module.
```
>>> import vlandat
```

Parse the data from file vlan.dat.
```
>>> vlan_dat = vlandat.VLANdat("vlan.dat")
```

List all VLANs with ID
```
>>> [(vlan.vlan, vlan.name) for vlan in vlan_dat.vlans if vlan.type == vlandat.VLANType.enet]
[(1, 'default'), (333, 'affe'), (666, 'entensuppe'), (999, 'banane')]
```

Show VTP mode.
```
>>> vlan_dat.vtp_mode
<VTPMode.server: 2>
```

Get the name of the VTP mode as string.
```
>>> vlan_dat.vtp_mode.name
'server'
```

## Links

* [defect.ch Wiki - vlan.dat](https://wiki.defect.ch/os/ios/vlan.dat)
* [RedNectar's Blog: decoding vlan.dat](https://rednectar.net/2010/12/06/decoding-vlan-dat/)
* [Marco Rizzi Blog: Playing with vlan.dat](https://rizzitech.blogspot.com/2010/08/playing-with-vlandat.html)

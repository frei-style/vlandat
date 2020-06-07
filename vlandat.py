#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module provides the ability to get information from a Cisco IOS
VLAN database file"""
import argparse
import os
import struct
import ipaddress
from enum import Enum
from datetime import datetime
from collections import namedtuple

__author__ = "Manuel Frei"
__credits__ = ["Manuel Frei"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Manuel Frei"
__email__ = "github@frei-style.net"
__status__ = "Prototype"

VLAN = namedtuple("VLAN", ["id", "name", "type", "mtu", "said", "state",
                           "ring_number", "parent_vlan", "remote_span",
                           "stp_type", "bridge", "ste", "backup_crf_mode",
                           "are", "bridge_mode", "translational_vlan_1",
                           "translational_vlan_2"])
VLAN.__doc__ = """Represents the configuration of a VLAN.

:param int id: ID, VLAN number
:param str name: Name, if configured, of the VLAN
:param VLANState state: Status of the VLAN (active or suspend, act/lshut or
                        sus/lshut, or act/ishut or sus/ishut)
:param VLANType type: Type, Media type of the VLAN
:param int said: SAID, Security association ID value for the VLAN
:param int mtu: MTU, Maximum transmission unit size for the VLAN
:param int parent_vlan: Parent VLAN, if one exists
:param int ring_number: RingNo, Ring number for the VLAN, if applicable
:param int bridge: BrdgNo, Bridge number for the VLAN, if applicable
:param STPType stp_type: Stp, Spanning Tree Protocol type that is used on
                         the VLAN
:param BridgeMode bridge_mode: BrdgMode, Bridging mode for this
                               VLAN-possible values are SRB and SRT;
                               the default is SRB
:param are: AREHops, Maximum number of hops for All-Routes Explorer
            frames-possible values are 1 through 13; the default is 7
:param int ste: STEHops, Maximum number of hops for Spanning Tree Explorer
                frames-possible values are 1 through 13; the default is 7
:param int backup_crf_mode: Backup CRF, Status of whether the TrCRF is a
                            backup path for traffic
:param int remote_span: Remote SPAN VLAN, RSPAN status
:param int translational_vlan_1: Types of translational bridges that the VLAN
                                 in the VLAN column is configured to translate
                                 to. Translational bridge VLANs must be a VLAN
                                 media type different from the affected VLAN;
                                 if two VLANs are specified, each one must be
                                 a different type
:param int translational_vlan_2: See translational_vlan_1
"""


class VLANType(Enum):
    """VLAN Type

    * 1: enet (Ethernet)
    * 2: fddi (FDDI)
    * 3: trcrf (TrCRF, Token Ring Concentrator Relay Function)
    * 4: fdnet (FDDI network entity title [NET])
    * 5: trbrf (TrBRF, Token Ring Bridge Relay Function)
    """
    enet = 1
    fddi = 2
    trcrf = 3
    fdnet = 4
    trbrf = 5


class VTPMode(Enum):
    """VTP Mode

    * 1: client
    * 2: server
    * 3: transparent
    """
    client = 1
    server = 2
    transparent = 3


class BridgeMode(Enum):
    """Bridge Mode (Token Ring)

    * 0: none
    * 1: srt (SRT, source-route transparent)
    * 2: srb (SRB, source-route bridge)
    """
    none = 0
    srt = 1
    srb = 2


class VLANState(Enum):
    """VLAN Status

    * 1: active
    * 2: suspended
    """
    active = 1
    suspended = 2


class PruningMode(Enum):
    """Pruning Mode

    * 1: enabled
    * 2: disabled
    """
    enabled = 1
    disabled = 2


class V2Mode(Enum):
    """VTP V2 Mode

    * 1: enabled
    * 2: disabled
    """
    enabled = 1
    disabled = 2


class BackupCRFMode(Enum):
    """Backup CRF Mode (Token Ring)

    * 0: disabled
    * 1: enabled
    """
    disabled = 0
    enabled = 1


class STPType(Enum):
    """STP (Spanning Tree Protocol) Type

    * 0: none
    * 1: ieee
    * 2: ibm
    """
    none = 0
    ieee = 1
    ibm = 2


class VLANdat:
    """Represents the whole VLAN database content"""

    __slots__ = ["_file_content", "_pointer", "endianness", "vlan_dat_file",
                 "pream", "vtp_version", "vtp_mode_nr", "vtp_mode",
                 "domain_name_len", "domain_name", "revision_nr",
                 "last_modified_by_int", "last_modified_by",
                 "last_update_interface", "last_modified_time_stamp",
                 "last_modified_time", "md5_hash", "vtp_password_len",
                 "vtp_password", "vlan_count", "pruning_mode", "v2_mode",
                 "vlans", "pruning_mode_id", "v2_mode_id"]

    def __init__(self, vlan_dat_file):
        self._file_content = None
        self._pointer = 0
        self.endianness = ">"
        self.vlan_dat_file = vlan_dat_file
        self.pream = ""
        self.vtp_version = ""
        self.vtp_mode_nr = ""
        self.vtp_mode = VTPMode(1)
        self.domain_name_len = 0
        self.domain_name = ""
        self.revision_nr = 0
        self.last_modified_by_int = 0
        self.last_modified_by = ""
        self.last_update_interface = ""
        self.last_modified_time_stamp = ""
        self.last_modified_time = ""
        self.md5_hash = ""
        self.vtp_password_len = 0
        self.vtp_password = ""
        self.vlan_count = 0
        self.pruning_mode = PruningMode(2)
        self.v2_mode = V2Mode(2)
        self.vlans = []

        self._parse_vlan_dat()

    def _parse_vlan_dat(self):
        self._pointer = 0
        with open(self.vlan_dat_file, mode="rb") as f:
            self._file_content = f.read()

            self.pream = self._read_byte(4).hex()  # always 0xbadb100d
            self.vtp_version = self._read_int() - 1  # check this
            self.vtp_mode_nr = self._read_char()
            self.vtp_mode = VTPMode(self.vtp_mode_nr)
            self.domain_name_len = self._read_char()
            self.domain_name = self._read_str(32)[:self.domain_name_len]

            self._read_byte(2)  # unknown, mostly b'\x00\x00'

            self.revision_nr = self._read_int()
            self.last_modified_by_int = self._read_int()
            self.last_modified_by = ipaddress.ip_address(
                self.last_modified_by_int)
            self.last_update_interface = self._read_int()
            self.last_modified_time_stamp = self._read_str(12)

            # strptime throw an exception if month or day are 0
            self.last_modified_time = ""
            if (self.last_modified_time_stamp[2:4] == 0 or
                    int(self.last_modified_time_stamp[4:6]) == 0):
                self.last_modified_time = "unknown"
            else:
                self.last_modified_time = datetime.strptime(
                    self.last_modified_time_stamp, "%y%m%d%H%M%S"
                    ).strftime('%Y-%m-%d %H:%M:%S')

            self.md5_hash = self._read_byte(16).hex()
            self.vtp_password_len = self._read_char()
            self.vtp_password = self._read_str(64)[:self.vtp_password_len]

            self._read_byte(1)  # unknown, probably vlan count

            self.vlan_count = self._read_short()

            self.pruning_mode_id = self._read_char()
            self.pruning_mode = PruningMode(self.pruning_mode_id)

            self.v2_mode_id = self._read_char()
            self.v2_mode = V2Mode(self.v2_mode_id)

            self._read_byte(6)  # unknown

            for i in range(0, self.vlan_count):
                vlan_name_len = self._read_char()
                vlan_name = self._read_str(32)[:vlan_name_len]
                self._read_byte(1)  # unknown
                vlan_type_nr = self._read_char()
                vlan_type = VLANType(vlan_type_nr)
                vlan_state_id = self._read_char()
                vlan_state = VLANState(vlan_state_id)
                vlan_mtu = self._read_short()
                vlan_id = self._read_short()
                vlan_said = self._read_int()
                ring_number = self._read_short()
                bridge = self._read_char()
                stp_type_id = self._read_char()
                stp_type = STPType(stp_type_id)
                parent_vlan = self._read_short()
                translational_vlan_1 = self._read_short()
                translational_vlan_2 = self._read_short()
                bridge_mode_id = self._read_char()
                bridge_mode = BridgeMode(bridge_mode_id)
                are = self._read_char()
                ste = self._read_char()
                backup_crf_mode_id = self._read_char()
                backup_crf_mode = BackupCRFMode(backup_crf_mode_id)
                remote_span = self._read_char()
                self._read_byte(1)  # unknown, mostly b'\x00'

                self.vlans.append(
                    VLAN(id=vlan_id, name=vlan_name,
                         type=vlan_type, mtu=vlan_mtu, said=vlan_said,
                         state=vlan_state, ring_number=ring_number,
                         parent_vlan=parent_vlan,
                         remote_span=remote_span, stp_type=stp_type,
                         bridge=bridge,
                         ste=ste,
                         backup_crf_mode=backup_crf_mode,
                         are=are,
                         bridge_mode=bridge_mode,
                         translational_vlan_1=translational_vlan_1,
                         translational_vlan_2=translational_vlan_2))

            """
            # yet unknown token ring and fddi data

            #nr_bytes = len(self._file_content)
            #nr_remaining_bytes = len(self._file_content[self._pointer:])
            #nr_24b_blocks = nr_remaining_bytes / 24

            #print("Remaining Bytes (" + str(nr_remaining_bytes) + "/" +
            # str(nr_bytes) + ") [24-Byte blocks: " + str(nr_24b_blocks) + "]")
            #a = binascii.hexlify(self._file_content[self._pointer:]
            #                    ).decode("utf-8")

            #x = " ".join([a[i:i+2] for i in range(0, len(a), 2)])
            #print(x)
            """

            # free memory
            self._file_content = None
            self._pointer = None

    def __str__(self):
        output = []

        if len(self.md5_hash) == 32:
            md5_hash = self.md5_hash.upper()
            md5_hash_part_1 = " ".join([(f"0x{md5_hash[i:i+2]}")
                                        for i in range(0, 16, 2)])
            md5_hash_part_2 = " ".join([(f"0x{md5_hash[i:i+2]}")
                                        for i in range(16, 32, 2)])
        else:
            md5_hash_part_1 = self.md5_hash
            md5_hash_part_2 = ""

        vtp_mode = self.vtp_mode.name
        pruning_mode = self.pruning_mode.name

        output.append(f"VTP Version                     : {self.vtp_version}")
        output.append(f"Configuration Revision          : {self.revision_nr}")
        output.append(f"Number of existing VLANs        : {self.vlan_count}")
        output.append(f"VTP Operating Mode              : {vtp_mode}")
        output.append(f"VTP Domain Name                 : {self.domain_name}")
        output.append(f"VTP Password                    : {self.vtp_password}")
        output.append(f"VTP Pruning Mode                : {pruning_mode}")
        output.append(f"VTP V2 Mode                     : {self.v2_mode.name}")
        output.append(f"MD5 digest                      : {md5_hash_part_1}")
        output.append(f"                                  {md5_hash_part_2}")
        output.append("Configuration last modified by " +
                      f"{self.last_modified_by} at {self.last_modified_time}")
        output.append("")
        output.append(f"{'ID':>4} {'Name':<32} {'Type':<5} {'MTU':<4} " +
                      f"{'SAID':<6} {'State':<9} {'Ring':<4} {'Parent':<6} " +
                      f"{'RemoteSPAN':<10} {'STP':<4} {'Bridge':<6} " +
                      f"{'STE':<3} {'BackupCRF':<9} {'ARE':<3} " +
                      f"{'BridgeMode':<10} {'Trans1':<6} {'Trans2':<6}")

        for vlan in self.vlans:
            vlan_type = vlan.type.name
            vlan_state = vlan.state.name
            vlan_stp_type = vlan.stp_type.name
            vlan_backup_crf_mode = vlan.backup_crf_mode.name
            vlan_bridge_mode = vlan.bridge_mode.name
            output.append(f"{vlan.id:>4} {vlan.name:<32} " +
                          f"{vlan_type:<5} {vlan.mtu:>4} {vlan.said:>6} " +
                          f"{vlan_state:<9} {vlan.ring_number:>4} " +
                          f"{vlan.parent_vlan:>6} {vlan.remote_span:>10} " +
                          f"{vlan_stp_type:<4} {vlan.bridge:>6} " +
                          f"{vlan.ste:>3} {vlan_backup_crf_mode:<9} " +
                          f"{vlan.are:>3} {vlan_bridge_mode:<10} " +
                          f"{vlan.translational_vlan_1:>6} " +
                          f"{vlan.translational_vlan_2:>6}")

        return "\n".join(output)

    def _read_byte(self, byte_len):
        data = struct.unpack(f"{self.endianness}{byte_len}s",
                             self._file_content[
                                 self._pointer:self._pointer+byte_len])[0]
        self._pointer += byte_len
        return data

    def _read_str(self, byte_len):
        data = self._read_byte(byte_len)
        return data.decode("utf-8")

    def _read_char(self):
        byte_len = 1
        data = struct.unpack(f"{self.endianness}{byte_len}B",
                             self._file_content[
                                 self._pointer:self._pointer+byte_len])[0]
        self._pointer += byte_len
        return data

    def _read_short(self):
        byte_len = 2
        data = struct.unpack(f"{self.endianness}H",
                             self._file_content[
                                 self._pointer:self._pointer+byte_len])[0]
        self._pointer += byte_len
        return data

    def _read_int(self):
        byte_len = 4
        data = struct.unpack(f"{self.endianness}I",
                             self._file_content[
                                 self._pointer:self._pointer+byte_len])[0]
        self._pointer += byte_len
        return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Displays the content of vlan.dat from Cisco IOS.")

    parser.add_argument(
        "-f",
        "--file",
        action="store",
        required=True,
        help="file path of the vlan.dat to parse and show."
    )

    args = parser.parse_args()

    if os.path.exists(args.file):
        vlandat = VLANdat(args.file)
        print(vlandat)
    else:
        print("[ERROR] File not found.")

# vim: set ts=4 sw=4 et

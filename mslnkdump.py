#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import for Python3.X compartibility
from __future__ import print_function

import sys
import os
import struct

#--------------------------------------------------------------------------------
# Constants
#--------------------------------------------------------------------------------
LNKFLG_HasLinkTargetIDList				= 0x00000001
LNKFLG_HasLinkInfo					= 0x00000002
LNKFLG_HasName						= 0x00000004
LNKFLG_HasRelativePath					= 0x00000008
LNKFLG_HasWorkingDir					= 0x00000010
LNKFLG_HasArgument					= 0x00000020
LNKFLG_HasIconLocation					= 0x00000040
LNKFLG_ISUnicode					= 0x00000080
LNKFLG_ForceNoLinkInfo					= 0x00000100
LNKFLG_HasExpString					= 0x00000200
LNKFLG_RunInSeparateProcess				= 0x00000400
LNKFLG_Unused1						= 0x00000800
LNKFLG_HasDarwinID					= 0x00001000
LNKFLG_RunAsUser					= 0x00002000
LNKFLG_HasExpIcon					= 0x00004000
LNKFLG_NoPidAlias					= 0x00008000
LNKFLG_Unused2						= 0x00010000
LNKFLG_RunWithShimLayer					= 0x00020000
LNKFLG_ForceNoLinkTrack					= 0x00040000
LNKFLG_EnableTargetMetadata 				= 0x00080000
LNKFLG_DisableLinkPathTracking 				= 0x00100000
LNKFLG_DisableKnownFolderTracking 			= 0x00200000
LNKFLG_DisableKnownFolderAlias 				= 0x00400000
LNKFLG_AllowLinkToLink					= 0x00800000
LNKFLG_UnaliasOnSave					= 0x01000000
LNKFLG_PreferEnvironmentPath 				= 0x02000000
LNKFLG_KeepLocalIDListForUNCTarget 			= 0x04000000

LNKINFFLG_VolumeIDAndLocalBasePath 			= 0x00000001
LNKINFFLG_CommonNetworkRelativeLinkAndPathsuffix 	= 0x00000002

EXTDAT_SIG_ConsoleDataBlock				= 0xA0000002
EXTDAT_SIG_ConsoleFEDataBlock				= 0xA0000004
EXTDAT_SIG_DarwinDataBlock				= 0xA0000006
EXTDAT_SIG_EnvironmentVariableDataBlock			= 0xA0000001
EXTDAT_SIG_IconEnvironmentDataBlock			= 0xA0000007
EXTDAT_SIG_KnownFolderDataBlock				= 0xA000000B
EXTDAT_SIG_PropertyStoreDataBlock			= 0xA0000009
EXTDAT_SIG_ShimDataBlock				= 0xA0000008
EXTDAT_SIG_SpecialFilderDataBlock			= 0xA0000005
EXTDAT_SIG_TrackerDataBlock				= 0xA0000003
EXTDAT_SIG_VistaAndAboveIDListDataBlock			= 0xA000000c

#--------------------------------------------------------------------------------
class LinkTargetIDList(object):
	def __init__(self, fd, LinkFlags):
		self.IDListSize = 0	# 2B
		self.IDList = None

		if LinkFlags & LNKFLG_HasLinkTargetIDList:
			try:
				self.IDListSize = int(struct.unpack('<H', fd.read(2))[0])
				buf = fd.read(self.IDListSize)
				self.unpack(buf)

			except struct.error as e:
				print("Something error", e)
				quit()

	def unpack(self, buf):
		buf = fd.read(self.IDListSize)
		self.IDList = self._IDList(buf)

	class _ItemID(object):
		def __init__(self, buf):
			self.ItemIDSize = 0
			self.Data = None
			
			self.unpack(buf)

		def unpack(self, buf):
			try:
				i = 0
				self.ItemIDSize = int(struct.unpack('<H', buf[i:i+2])[0])
				i += 2
				self.Data = buf[i:self.ItemIDSize-2]
				i += self.ItemIDSize-2

			except struct.error as e:
				print("Something error", e)
				quit()

	class _IDList(object):
		def __init__(self, buf):
			self.ItemIDList = None
			self.TerminalID = 0
			
			self.unpack(buf)

		def unpack(self, buf):
			try:
				i = 0
				self.ItemIDList = self._ItemID(buf)
				i += self.ItemIDList.ItemIDSize
				self.TerminalID = int(struct.unpack('<H', buf[i:2])[0])
				i += 2

			except struct.error as e:
				print("Something error", e)
				quit()

class LinkInfo(object):
	def __init__(self, fd, LinkFlags):
		self.LinkInfoSize = 0
		self.LinkInfoHeaderSize = 0
		self.LinInfoFlags = 0

		self.VolumeIDOffset = 0
		self.LocalBasePathOffset = 0
		self.CommonNetworkRelativeLinkOffset = 0
		self.CommonPathSuffixOffset = 0

		self.LocalBasePathOffsetUnicode = 0
		self.CommonPathSuffixOffsetUnicode = 0

		self.VolumeID = None
		self.LocalBasePath = ""
		self.CommonNetworkRelativeLink = None

		if LinkFlags & LNKFLG_HasLinkInfo:
			try:
				self.LinkInfoSize= int(struct.unpack('<I', fd.read(4))[0])
				buf = fd.read(self.LinkInfoSize - 4)
				self.unpack(buf)

			except struct.error as e:
				print("Something error", e)
				quit()

	def unpack(self, buf):
		try:
			i = 0
			self.LinkInfoHeaderSize = int(struct.unpack('<I', buf[i:i+4])[0])
			i += 4
			self.LinkInfoFlags = int(struct.unpack('<I', buf[i:i+4])[0])
			i += 4
			self.VolumeIDOffset = int(struct.unpack('<I', buf[i:i+4])[0])
			i += 4
			self.LocalBasePathOffset = int(struct.unpack('<I', buf[i:i+4])[0])
			i += 4
			self.CommonNetworkRelativeLinkOffset = int(struct.unpack('<I', buf[i:i+4])[0])
			i += 4
			self.CommonPathSuffixOffset = int(struct.unpack('<I', buf[i:i+4])[0])
			i += 4

			if self.LinkInfoHeaderSize >= 0x24:
				self.LocalBasePathOffsetUnicode = int(struct.unpack('<I', buf[i:i+4])[0])
				i += 4
				self.CommonPathSuffixOffsetUnicode = int(struct.unpack('<I', buf[i:i+4])[0])
				i += 4

			# If VolumeID, LocalBasePath, LocalBasePathUnicode Field is present
			if self.LinkInfoFlags & LNKINFFLG_VolumeIDAndLocalBasePath:
				# for VolumeID field
				self.VolumeID = self._VolumeID(buf[i:])
				i += self.VolumeID.VolumeIDSize

				# for LocalBasePath field
				self.LocalBasePath = buf[i:].split(b'\x00')[0]
				i += len(self.LocalBasePath)

			# for CommonNetworkRelativeLink
			self.CommonNetworkRelativeLink = self._CommonNetworkRelativeLink(buf[i:])

		except struct.error as e:
			print("Something error", e)
			quit()

	class _VolumeID(object):
		def __init__(self, buf):
			self.VolumeIDSize = 0			# 4B
			self.DriveType = 0			# 4B
			self.DriveSerialNumber = 0		# 4B
			self.VolumeLabelOffset = 0		# 4B
			self.VolumeLabelOffsetUnicode = 0	# 4B

			self.Data = None

			self.unpack(buf)

		def unpack(self, buf):
			try:
				i = 0
				self.VolumeIDSize = int(struct.unpack('<I', buf[i:i+4])[0])
				i += 4

				if self.VolumeIDSize < 0x10:
					print("VolumeIDSize is too small")
					quit()

				self.DriveType = int(struct.unpack('<I', buf[i:i+4])[0])
				i += 4
				self.DriveSerialNumber = int(struct.unpack('<I', buf[i:i+4])[0])
				i += 4
				self.VolumeLabelOffset = int(struct.unpack('<I', buf[i:i+4])[0])
				i += 4
				self.VolumeLabelOffsetUnicode = int(struct.unpack('<I', buf[i:i+4])[0])
				i += 4

				if self.VolumeLabelOffset == 0x14:
					self.Data = buf[i:self.VolumeLabelOffsetUnicode]
					i += self.VolumeLabelOffsetUnicode
				else:
					self.Data = buf[i:self.VolumeLabelOffset]

			except struct.error as e:
				print("Something error", e)
				quit()

	class _CommonNetworkRelativeLink(object):
		def __init__(self, buf):
			self.CommonNetworkRelativeLinkSize = 0	# 4B
			self.CommonNetworkRelativeLinkFlags = 0 # 4B
			self.NetNameOffset = 0			# 4B
			self.DeviceNameOffset = 0		# 4B
			self.NetworkProviderType = 0		# 4B
			self.NetNameOffsetUnicode = 0		# 4B
			self.DeviceNameOffsetUnicode = 0	# 4B

			self.NetName = ""
			self.DeviceName = ""
			self.NetNameUnicode = ""
			self.DeviceNameUnicode = ""

			self.unpack(buf)

		def unpack(self, buf):
			try:
				i = 0
				self.CommonNetworkRelativeLinkSize = int(struct.unpack('<I', buf[i:i+4])[0])
				i += 4
				self.CommonNetworkRelativeLinkFlags = int(struct.unpack('<I', buf[i:i+4])[0])
				i += 4
				self.NetNameOffset = int(struct.unpack('<I', buf[i:i+4])[0])
				i += 4
				self.DeviceNameOffset = int(struct.unpack('<I', buf[i:i+4])[0])
				i += 4
				self.NetworkProviderType = int(struct.unpack('<I', buf[i:i+4])[0])
				i += 4

				# String Field
				if self.NetNameOffset > 0:
					self.NetName = buf[self.NetNameOffset:].split(b'\x00')[0]

				if self.DeviceNameOffset > 0:
					self.DeviceName = buf[self.DeviceNameOffset:].split(b'\x00')[0]

				if self.NetNameOffset > 0x14:
					self.NetNameOffsetUnicode = int(struct.unpack('<I', buf[i:i+4])[0])
					i += 4
					self.DeviceNameOffsetUnicode = int(struct.unpack('<I', buf[i:i+4])[0])
					i += 4

					if self.NetNameOffsetUnicode > 0:
						self.NetNameUnicode = buf[self.NetNameOffsetUnicode:].split(b'\x00')[0]

					if self.DeviceNameOffsetUnicode > 0:
						self.DeviceNameUnicode = buf[self.DeviceNameOffsetUnicode:].split(b'\x00')[0]

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

#--------------------------------------------------------------------------------
class ShellLinkHeader(object):
	def __init__(self, fd):
		self.HeaderSize = 0		# 4B
		self.LinkCLSID = 0		# 16B	
		self.LinkFlags = 0		# 4B
		self.FileAtteributes = 0	# 4B
		self.CreationTime = 0		# 8B
		self.AccessTime = 0		# 8B
		self.WriteTime = 0		# 8B
		self.FileSize = 0		# 4B
		self.IconIndex = 0		# 4B
		self.ShowCommand = 0		# 4B
		self.HotKey = 0			# 2B
		self.Reserved1 = 0		# 2B
		self.Reserved2 = 0		# 4B
		self.Reserved3 = 0		# 4B

		try:
			self.HeaderSize = int(struct.unpack('<I', fd.read(4))[0])
			if self.HeaderSize != 76:
				print("Something error", e, self.__class__)
				quit(1)

			buf = fd.read(self.HeaderSize - 4)
			self.unpack(buf)

		except struct.error as e:
			print("Something error", e, self.__class__)
			quit()

	def unpack(self, buf):
		try:
			i = 0
			self.LinkCLSID = struct.unpack("<16c", buf[i:i+16])[0]
			i += 16 
			self.LinkFlags = int(struct.unpack("<I", buf[i:i+4])[0])
			i += 4
			self.FileAtteributes = int(struct.unpack("<I", buf[i:i+4])[0])
			i += 4
			self.CreationTime = int(struct.unpack("<Q", buf[i:i+8])[0])
			i += 8
			self.AccessTime = int(struct.unpack("<Q", buf[i:i+8])[0])
			i += 8
			self.WriteTime = int(struct.unpack("<Q", buf[i:i+8])[0])
			i += 8
			self.FileSize = int(struct.unpack("<I", buf[i:i+4])[0])
			i += 4
			self.IconIndex = int(struct.unpack("<I", buf[i:i+4])[0])
			i += 4
			self.ShowCommand = int(struct.unpack("<I", buf[i:i+4])[0])
			i += 4
			self.HotKey = int(struct.unpack("<H", buf[i:i+2])[0])
			i += 2
			self.Reserved1 = int(struct.unpack("<H", buf[i:i+2])[0])
			i += 2
			self.Reserved2 = int(struct.unpack("<I", buf[i:i+4])[0])
			i += 4
			self.Reserved3 = int(struct.unpack("<I", buf[i:i+4])[0])
			i += 4

		except struct.error as e:
			print("Something error", e, self.__class__)
			quit()

#--------------------------------------------------------------------------------
class StringData(object):
	def __init__(self, fd, LinkFlags):
		self.NameString = None
		self.RelativePath = None
		self.WorkingDir = None
		self.CommandLineArguments = None
		self.IconLocation = None
		
		if LinkFlags & LNKFLG_HasName:
			self.NameString = self._StringData(fd)

		if LinkFlags & LNKFLG_HasRelativePath:
			self.RelativePath = self._StringData(fd)

		if LinkFlags & LNKFLG_HasWorkingDir:
			self.WorkingDir = self._StringData(fd)

		if LinkFlags & LNKFLG_HasArgument:
			self.CommandLineArguments = self._StringData(fd)

		if LinkFlags & LNKFLG_HasIconLocation:
			self.IconLocation = self._StringData(fd)

	class _StringData(object):
		def __init__(self, fd):
			self.CountCharacters = 0
			self.String = ""

			try:
				self.CountCharacters = int(struct.unpack("<H", fd.read(2))[0])
				self.String = fd.read(self.CountCharacters)

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()
#--------------------------------------------------------------------------------
class ExtraData(object):
	def __init__(self, fd, LinkFlags):
		self.ConsoleProps = None
		self.ConsoleFEProps = None
		self.DarwinProps = None
		self.EnvironmentProps = None
		self.IconEnvironmentProps = None
		self.KnownFolderProps = None
		self.PropertyStoreProps = None
		self.ShimProps = None
		self.SpecialFolderProps = None
		self.TrackerProps = None
		self.VistaAndAboveIDListProps = None
		self.TerminalBlock = 0

		while True:
			try:
				BlockSize = int(struct.unpack("<I", fd.read(4))[0])

				if BlockSize < 0x4:
					self.TerminalBlock = BlockSize
					break

				BlockSignature = int(struct.unpack("<I", fd.read(4))[0])
				buf = fd.read(BlockSize - 8)

				if BlockSignature == EXTDAT_SIG_ConsoleDataBlock:
					self.ConsoleProps = self._ConsoleDataBlock(buf)
					self.ConsoleProps.BlockSize = BlockSize
					self.ConsoleProps.BlockSignature = BlockSignature

				if BlockSignature == EXTDAT_SIG_ConsoleFEDataBlock:
					self.ConsoleFEProps = self._ConsoleDataFEBlock(buf)
					self.ConsoleFEProps.BlockSize = BlockSize
					self.ConsoleFEProps.BlockSignature = BlockSignature

				if BlockSignature == EXTDAT_SIG_DarwinDataBlock:
					self.DarwinProps = self._DarwinDataBlock(buf)
					self.DarwinProps.BlockSize = BlockSize
					self.DarwinProps.BlockSignature = BlockSignature

				if BlockSignature == EXTDAT_SIG_EnvironmentVariableDataBlock:
					self.EnvironmentProps = self._EnvironmentVariableDataBlock(buf)
					self.EnvironmentProps.BlockSize = BlockSize
					self.EnvironmentProps.BlockSignature = BlockSignature

				if BlockSignature == EXTDAT_SIG_IconEnvironmentDataBlock:
					self.IconEnvironmentProps = self._IconEnvironmentDataBlock(buf)
					self.IconEnvironmentProps.BlockSize = BlockSize
					self.IconEnvironmentProps.BlockSignature = BlockSignature

				if BlockSignature == EXTDAT_SIG_KnownFolderDataBlock:
					self.KnownFolderProps = self._KnownFolderDataBlock(buf)
					self.KnownFolderProps.BlockSize = BlockSize
					self.KnownFolderProps.BlockSignature = BlockSignature

				if BlockSignature == EXTDAT_SIG_PropertyStoreDataBlock:
					self.PropertyStoreProps = self._PropertyStoreDataBlock(buf)
					self.PropertyStoreProps.BlockSize = BlockSize
					self.PropertyStoreProps.BlockSignature = BlockSignature

				if BlockSignature == EXTDAT_SIG_ShimDataBlock:
					self.ShimProps = self._ShimDataBlock(buf)
					self.ShimProps.BlockSize = BlockSize
					self.ShimProps.BlockSignature = BlockSignature

				if BlockSignature == EXTDAT_SIG_SpecialFilderDataBlock:
					self.SpecialFolderProps = self._SpecialFolderDataBlock(buf)
					self.SpecialFolderProps.BlockSize = BlockSize
					self.SpecialFolderProps.BlockSignature = BlockSignature

				if BlockSignature == EXTDAT_SIG_TrackerDataBlock:
					self.TrackerProps = self._TrackDataBlock(buf)
					self.TrackerProps.BlockSize = BlockSize
					self.TrackerProps.BlockSignature = BlockSignature

				if BlockSignature == EXTDAT_SIG_VistaAndAboveIDListDataBlock:
					self.VistaAndAboveIDListProps = self._VistaAndAboveIDListDataBlock(buf)
					self.VistaAndAboveIDListProps.BlockSize = BlockSize
					self.VistaAndAboveIDListProps.BlockSignature = BlockSignature

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

	class _ConsoleDataBlock(object):
		def __init__(self, buf):
			self.BlockSize = 0
			self.BlockSignature = 0
			self.FillAttributes = 0		#(2 bytes)
			self.PopupFillAttributes = 0	#(2 bytes)
			self.ScreenBufferSizeX = 0	#(2 bytes)
			self.ScreenBufferSizeY = 0	#(2 bytes)
			self.WindowSizeX = 0 		#(2 bytes)
			self.WindowSizeY = 0 		#(2 bytes)
			self.WindowOriginX = 0		#(2 bytes)
			self.WindowOriginY = 0		#(2 bytes)
			self.Unused1 = 0 		#(4 bytes)
			self.Unused2 = 0 		#(4 bytes)
			self.FontSize = 0		#(4 bytes)
			self.FontFamily = 0		#(4 bytes)
			self.FontWeight = 0		#(4 bytes)
			self.FaceName = ""		#(64 bytes)
			self.CursorSize = 0		#(4 bytes)
			self.FullScreen = 0		#(4 bytes)
			self.QuickEdit = 0 		#(4 bytes)
			self.InsertMode = 0 		#(4 bytes)
			self.AutoPosition = 0 		#(4 bytes)
			self.HistoryBufferSize = 0 	#(4 bytes)
			self.NumberOfHistoryBuffers = 0	#(4 bytes)
			self.HistoryNoDup = 0		#(4 bytes)
			self.ColorTable = 0		#(64 bytes)

			self.unpack(buf)

		def unpack(self, buf):
			try:
				i = 0
				self.FillAttributes = struct.unpack("<H", buf[i:i+2])[0]
				i += 2
				self.PopupFillAttributes = int(struct.unpack("<H", buf[i:i+2])[0])
				i += 2
				self.ScreenBufferSizeY = int(struct.unpack("<H", buf[i:i+2])[0])
				i += 2
				self.ScreenBufferSizeX = int(struct.unpack("<H", buf[i:i+2])[0])
				i += 2
				self.WindowSizeX = int(struct.unpack("<H", buf[i:i+2])[0])
				i += 2
				self.WindowSizeY = int(struct.unpack("<H", buf[i:i+2])[0])
				i += 2
				self.WindowOriginX = int(struct.unpack("<H", buf[i:i+2])[0])
				i += 2
				self.WindowOriginY = int(struct.unpack("<H", buf[i:i+2])[0])
				i += 2
				self.Unused1 = int(struct.unpack("<I", buf[i:i+4])[0])
				i += 4
				self.Unused2 = int(struct.unpack("<I", buf[i:i+4])[0])
				i += 4
				self.FontSize = int(struct.unpack("<I", buf[i:i+4])[0])
				i += 4
				self.FontFamily = int(struct.unpack("<I", buf[i:i+4])[0])
				i += 4
				self.FontWeight = int(struct.unpack("<I", buf[i:i+4])[0])
				i += 4
				self.FaceName = struct.unpack("<64s", buf[i:i+64])[0]
				i += 64 
				self.CursorSize = struct.unpack("<I", buf[i:i+4])[0]
				i += 4
				self.FullScreen = struct.unpack("<I", buf[i:i+4])[0]
				i += 4
				self.QuickEdit = struct.unpack("<I", buf[i:i+4])[0]
				i += 4
				self.InsertMode = struct.unpack("<I", buf[i:i+4])[0]
				i += 4
				self.AutoPosition = struct.unpack("<I", buf[i:i+4])[0]
				i += 4
				self.HistoryBufferSize = struct.unpack("<I", buf[i:i+4])[0]
				i += 4
				self.NumberOfHistoryBuffers = struct.unpack("<I", buf[i:i+4])[0]
				i += 4
				self.HistoryNoDup = struct.unpack("<I", buf[i:i+4])[0]
				i += 4
				self.ColorTable = struct.unpack("<IIIIIIIIIIIIIIII", buf[i:i+64])[0]
				i += 64

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

	class _ConsoleDataFEBlock(object):
		def __init__(self, buf):
			self.BlockSize = 0
			self.BlockSignature = 0
			self.CodePage = 0

			self.unpack(buf)

		def unpack(self, buf):
			try:
				i = 0
				self.CodePage = struct.unpack("<I", buf[i:i+4])[0]
				i += 4

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

	class _DarwinDataBlock(object):
		def __init__(self, buf):
			self.BlockSize = 0
			self.BlockSignature = 0
			self.DarwinDataAnsi = ""
			self.DarwinDataUnicode = ""

			self.unpack(buf)

		def unpack(self, buf):
			try:
				i = 0
				self.DarwinDataAnsi = buf[i:i+260].split(b'\x00')[0]
				i += 260

				if len(buf) > i:
					self.DarwinDataUnicode = buf[i:i+520].split(b'\x00')[0]
					i += 520

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

	class _EnvironmentVariableDataBlock(object):
		def __init__(self, buf):
			self.BlockSize = 0
			self.BlockSignature = 0
			self.TargetAnsi = ""
			self.TargetUnicode = ""

			self.unpack(buf)

		def unpack(self, buf):
			try:
				i = 0
				self.TargetAnsi = buf[i:i+260].split(b'\x00')[0]
				i += 260

				if len(buf) > i:
					self.TargetUnicode = buf[i:i+520].split(b'\x00')[0]
					i += 520

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

	class _IconEnvironmentDataBlock(object):
		def __init__(self, buf):
			self.BlockSize = 0
			self.BlockSignature = 0
			self.TargetAnsi = ""
			self.TargetUnicode = ""

			self.unpack(buf)

		def unpack(self, buf):
			try:
				i = 0
				self.TargetAnsi = buf[i:i+260].split(b'\x00')[0]
				i += 260

				if len(buf) > i:
					self.TargetUnicode = buf[i:i+520].split(b'\x00')[0]
					i += 520

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

	class _KnownFolderDataBlock(object):
		def __init__(self, buf):
			self.BlockSize = 0
			self.BlockSignature = 0
			self.KnownFolderID = None
			self.Offset = 0

			self.unpack(buf)

		def unpack(self, buf):
			try:
				i = 0
				self.KnownFolderID = repr(buf[i:i+16])	# Folder GUID ID????
				i += 16
				self.Offset = buf[i:i+4]
				i += 4

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

	class _PropertyStoreDataBlock(object):
		def __init__(self, buf):
			self.BlockSize = 0
			self.BlockSignature = 0
			self.PropertyStore = None

			self.unpack(buf)

		def unpack(self, buf):
			try:
				self.PropertyStore = repr(buf)	# Maybe MS PROP Stone structure

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

	class _ShimDataBlock(object):
		def __init__(self, buf):
			self.BlockSize = 0
			self.BlockSignature = 0
			self.LayerName = None

			self.unpack(buf)

		def unpack(self, buf):
			try:
				self.LayerName = buf	# Maybe MS PROP Stone structure

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

	class _SpecialFolderDataBlock(object):
		def __init__(self, buf):
			self.BlockSize = 0
			self.BlockSignature = 0
			self.SpecialFolderID = 0
			self.Offset = 0

			self.unpack(buf)

		def unpack(self, buf):
			try:
				i = 0
				self.SpecialFolderID = struct.unpack("<I", buf[i:i+4])[0]
				i += 4
				self.Offset = struct.unpack("<I", buf[i:i+4])[0]
				i += 4

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

	class _TrackDataBlock(object):
		def __init__(self, buf):
			self.BlockSize = 0
			self.BlockSignature = 0
			self.Length = 0
			self.Version = 0
			self.MachineID = ""
			self.Droid = None
			self.DroidBirth = None

			self.unpack(buf)

		def unpack(self, buf):
			try:
				i = 0
				self.Length = struct.unpack("<I", buf[i:i+4])[0]
				i += 4
				self.Version = struct.unpack("<I", buf[i:i+4])[0]
				i += 4

				MachineIDlen = len(buf) - (32*2) - i
				self.MachineID = repr(buf[i:i+MachineIDlen])
				i += MachineIDlen

				self.Droid = repr(buf[i:i+32])
				i += 32

				self.DroidBirth = repr(buf[i:i+32])
				i += 32

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

	class _VistaAndAboveIDListDataBlock(object):
		def __init__(self, buf):
			self.BlockSize = 0
			self.BlockSignature = 0
			self.IDList = None

			self.unpack(buf)

		def unpack(self, buf):
			try:
				self.IDList = repr(buf)

			except struct.error as e:
				print("Something error", e, self.__class__)
				quit()

#--------------------------------------------------------------------------------
def print_dump(cls, basename):
	for k, v in vars(cls).iteritems():
		if '__dict__' in dir(v):
			#print('{0:s}'.format(k))
			print_dump(v, basename + k + '.')
		else:
			print('{0:s}{1:s} '.format(basename, k), end='')
			if isinstance(v, str):
				print('"{0:s}"'.format(v))	# String
			elif isinstance(v, int):
				print('{0:d}'.format(int(v)))	# Integer
			else:
				print(repr(v))			# else

#--------------------------------------------------------------------------------
def main():
	argvs = sys.argv
	argc = len(argvs)
	
	if (argc < 2):
		print('Usage: {0:s} *.lnk'.format(argvs[0]))
		quit()
	try:
		fd = open(argvs[1], 'rb')

	except IOError:
		print('Can not file:{0:s} open'.format(argvs[1]))
		quit()

	print("--------------------------------------------------------------------------------")
	print(" mslnkdump - MS Shell link file dump utility v0.1")
	print(" nyacom (C) 2017 www.nyacom.net")
	print("--------------------------------------------------------------------------------")
	print("")

	slh = ShellLinkHeader(fd)
	lnktgt = None
	lnkinfo = None
	strdata = None
	extdata = None
	
	lnktgt = LinkTargetIDList(fd, slh.LinkFlags)
	lnkinfo = LinkInfo(fd, slh.LinkFlags)
	strdata = StringData(fd, slh.LinkFlags)
	extdata = ExtraData(fd, slh.LinkFlags)

	# Non segment identificate flags
	if slh.LinkFlags & LNKFLG_ISUnicode:
		print("LinkFlag: IsUnicode is active")

	if slh.LinkFlags & LNKFLG_ForceNoLinkInfo:
		print("LinkFlag: ForceNoLinkInfo is active")

	if slh.LinkFlags & LNKFLG_HasExpString:
		print("LinkFlag: HasExpString is active")

	if slh.LinkFlags & LNKFLG_RunInSeparateProcess:
		print("LinkFlag: RunInSerapateProcess is active")

	if slh.LinkFlags & LNKFLG_Unused1:
		print("LinkFlag: Unused1 is active")

	if slh.LinkFlags & LNKFLG_HasDarwinID:
		print("LinkFlag: HasDarwinID is active")

	if slh.LinkFlags & LNKFLG_RunAsUser:
		print("LinkFlag: RunAsUser is active")

	if slh.LinkFlags & LNKFLG_HasExpIcon:
		print("LinkFlag: HasExpIcon is active")

	if slh.LinkFlags & LNKFLG_NoPidAlias:
		print("LinkFlag: NoPidAlias is active")

	if slh.LinkFlags & LNKFLG_Unused2:
		print("LinkFlag: Unused2 is active")

	if slh.LinkFlags & LNKFLG_RunWithShimLayer:
		print("LinkFlag: RunWithShimLayer is active")

	if slh.LinkFlags & LNKFLG_ForceNoLinkTrack:
		print("LinkFlag: ForceNoLinkTrack is active")

	if slh.LinkFlags & LNKFLG_EnableTargetMetadata:
		print("LinkFlag: EnableTargetMetadata is active")

	if slh.LinkFlags & LNKFLG_DisableLinkPathTracking:
		print("LinkFlag: DisableLinkPathTracking is active")

	if slh.LinkFlags & LNKFLG_DisableKnownFolderTracking:
		print("LinkFlag: DisableKnownFolderTracking is active")

	if slh.LinkFlags & LNKFLG_DisableKnownFolderAlias:
		print("LinkFlag: DisableKnownFolderAlias is active")

	if slh.LinkFlags & LNKFLG_AllowLinkToLink:
		print("LinkFlag: AllowLinkToLink is active")

	if slh.LinkFlags & LNKFLG_UnaliasOnSave:
		print("LinkFlag: UnaliasOnSave is active")

	if slh.LinkFlags & LNKFLG_PreferEnvironmentPath:
		print("LinkFlag: PreferEnvironmentPath is active")

	if slh.LinkFlags & LNKFLG_KeepLocalIDListForUNCTarget:
		print("LinkFlag: KeepLocalIDListForUNCTarget is active")

	print_dump(lnktgt, '')
	print_dump(lnkinfo, '')
	print_dump(strdata, '')
	print_dump(extdata, '')
	print("")

	fd.close()

#--------------------------------------------------------------------------------
if __name__ == '__main__':
	main()


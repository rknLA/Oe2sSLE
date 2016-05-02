# -*- coding: utf-8 -*-
"""
Copyright (C) 2015 Jonathan Taquet

This file is part of Oe2sSLE (Open e2sSample.all Library Editor).

Foobar is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Oe2sSLE.  If not, see <http://www.gnu.org/licenses/>
"""

import struct
import warnings

import RIFF

class RIFF_smpl(RIFF.ChunkData):
    _dataMinFmt = '<9I'
    _dataMinSize = struct.calcsize(_dataMinFmt)
    
    class LoopData:
        _dataFmt = '<6I'
        _dataSize = struct.calcsize(_dataFmt)
        
        """
        smpl_loop_types:
            0    : 'Forward',
            1    : 'Forward/Backward',
            2    : 'Backward',
            3-31 : 'Reserved',
            >31  : 'Specific'
        
        start, end: byte offsets
        """
        
        def __init__(self, smpl_master, loop_num):
            self.fields=dict()
            self.smpl = smpl_master
            offset=smpl_master._dataMinSize+loop_num*self._dataSize
            self.fields['identifier']=(offset, '<I')
            offset+=struct.calcsize('I')
            self.fields['type']=(offset, '<I')
            offset+=struct.calcsize('I')
            self.fields['start']=(offset, '<I')
            offset+=struct.calcsize('I')
            self.fields['end']=(offset, '<I')
            offset+=struct.calcsize('I')
            self.fields['fraction']=(offset, '<I')
            offset+=struct.calcsize('I')
            self.fields['playCount']=(offset, '<I')
            offset+=struct.calcsize('I')
            
    
        def __getattr__(self, name):
            if name in self.fields:
                loc, fmt = self.fields[name]
                size = struct.calcsize(fmt)
                unpacked = struct.unpack(fmt, self.smpl.rawdata[loc:loc+size])
                if len(unpacked) == 1:
                    return unpacked[0]
                else:
                    return unpacked
            else:
                raise AttributeError
    
        def __setattr__(self, name, value):
            if name != 'fields' and name in self.fields:
                loc, fmt = self.fields[name]
                size = struct.calcsize(fmt)
                self.__dict__['smpl'].rawdata[loc:loc+size] = struct.pack(fmt, value)
            else:
                self.__dict__[name] = value
        
    
    def __init__(self, file=None, chunkHeader=None):
        self.fields = dict()
        self.rawdata = bytearray(RIFF_smpl._dataMinSize)
        offset = 0
        self.fields['manufacturer']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['product']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['samplePeriod']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['MIDIUnityNote']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['MIDIPitchFraction']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['SMPTEFormat']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['SMPTEOffset']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['numSampleLoops']=(offset, '<I')
        offset += struct.calcsize('I')
        self.fields['numAdditionalBytes']=(offset, '<I')
        offset += struct.calcsize('I')

        self.loops = []
        
        if file:
            self.read(file,chunkHeader)
        else:
            self.reset()
        
#    def __len__(self):
#        return len(self.rawdata)
    
    def read(self, file, chunkHeader):
        if chunkHeader.id != b'smpl':
            raise TypeError("'smpl' chunk expected")
        self.rawdata[:] = file.read(chunkHeader.size)
        if len(self.rawdata) != chunkHeader.size:
            raise EOFError('Unexpected End Of File')
        for loopNum in range(self.numSampleLoops):
            self.loops.append(self.LoopData(self,loopNum))
        
    def reset(self):
        self.manufacturer = 0
        self.product = 0
        self.samplePeriod = 0
        self.MIDIUnityNote = 60 # default to Middle C
        self.MIDIPitchFraction = 0
        self.SMPTEFormat = 0
        self.numSampleLoops = 0
        self.numAdditionalBytes = 0
        self.loops = []

#    def write(self, file):
#        file.write(self.rawdata)

    def __getattr__(self, name):
        if name in self.fields:
            loc, fmt = self.fields[name]
            size = struct.calcsize(fmt)
            unpacked = struct.unpack(fmt, self.rawdata[loc:loc+size])
            if len(unpacked) == 1:
                return unpacked[0]
            else:
                return unpacked
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        if name != 'fields' and name in self.fields:
            loc, fmt = self.fields[name]
            size = struct.calcsize(fmt)
            self.__dict__['rawdata'][loc:loc+size] = struct.pack(fmt, value)
        else:
            self.__dict__[name] = value


    #TODO: easily add loop(s)

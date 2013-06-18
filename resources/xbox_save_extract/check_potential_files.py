"""
Copyright 2010 Jordan Fish, jrdn.fish AT gmail DOT com. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 """
#!/usr/bin/python

import hashlib
import sys
import time
import struct
import os
import subprocess

reader = open("<path_to_xbox360_hd_img>", "rb")

fileno = 0
for line in open("file_locations.txt"):
    line = line.strip()
    if line == "":
        continue
    
    pos = long(line)
    
    reader.seek(pos)
    data = reader.read(1024 * 1024 * 4)
    filetype = data[:4]
    fileno += 1

    reader.seek(pos)
    reader.seek(0x32C, 1)
    
    sha1 = reader.read(20)
    reader.seek(4, 1)

    if filetype == "CON ":
        sha1_bytes_length = 0xA000 - 0x0344
    else:
        sha1_bytes_length = 0xB000 - 0x0344

    found_sha1 = hashlib.sha1(reader.read(sha1_bytes_length))
    found_digest = found_sha1.digest()

    if found_digest != sha1:
        continue

    (mentry_id, content_type) = struct.unpack(">LL", reader.read(8))

    content_types = []
    if content_type == 0:
        content_types.append("(no type)")
    if content_type & 0x00000001:
        content_types.append("Game save")
    if content_type & 0x00000002:
        content_types.append("Game add-on")
    if content_type & 0x00030000:
        content_types.append("Theme")
    if content_type & 0x00090000:
        content_types.append("Video clip")
    if content_type & 0x000C0000:
        content_types.append("Game trailer")
    if content_type & 0x000D0000:
        content_types.append("XBox Live Arcade")
    if content_type & 0x00010000:
        content_types.append("Gamer profile")
    if content_type & 0x00020000:
        content_types.append("Gamer picture")
    if content_type & 0x00040000:
        content_types.append("System update")

    print fileno, filetype, pos, ",".join(content_types), found_sha1.hexdigest()

    if "Game save" in content_types and filetype == "CON ":
        out = open("file%s.bin" % fileno, "wb")
        out.write(data)
        out.close()

        subprocess.call(["./extract360.py", "file%s.bin" % fileno])
        #subprocess.call(["less", "file%s.bin.txt" % fileno])

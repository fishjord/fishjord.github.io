/*
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

*/

import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.EOFException;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

/**
 *
 * @author fishjord
 */
public class FileFinder {

    private static final int CON_ = 1129270816;
    private static final int LIVE = 1279874629;
    private static final int PIRS = 1346982483;

    public static void main(String[] args) throws IOException {
        if (args.length != 1) {
            System.err.println("USAGE: FileFinder <input_file.bin>");
            return;
        }

        int numHashes = 100;
        File f = new File(args[0]);
        DataInputStream is = new DataInputStream(new BufferedInputStream(new FileInputStream(f)));
        long hashesEvery = f.length() / numHashes;
        long nextHash = hashesEvery;

        for (int index = 0; index < numHashes; index++) {
            System.err.print("-");
        }
        System.err.println();

        long start = System.currentTimeMillis();
        long totalRead = 0;
        try {
            while (true) {
                try {

                    int read = is.readInt();
                    totalRead += 4;
                    switch (read) {
		    case CON_:
		    case LIVE:
		    case PIRS:
			System.out.println(read - 4);
                    }

                    if (totalRead > nextHash) {
                        System.err.print("#");
                    }
                } catch (EOFException ignore) {
                    break;
                }
            }
        } finally {
            System.err.println();
        }

        System.out.println("Read " + totalRead + " bytes in " + (System.currentTimeMillis() - start));
    }
}

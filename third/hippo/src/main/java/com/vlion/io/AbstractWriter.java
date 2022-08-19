package com.vlion.io;

import java.io.IOException;
import java.io.OutputStream;

public abstract class AbstractWriter implements Writer{
   protected OutputStream os = null;

    @Override
    public void write(String str, String charsetName) throws IOException {
        byte[] bytes = str.getBytes(charsetName);
        write(bytes);
    }

    @Override
    public void write(String str) throws IOException {
        byte[] bytes = str.getBytes();
        write(bytes);
    }

    @Override
    public void write(byte[] bytes) throws IOException {
        os.write(bytes);
    }

    @Override
    public void close() throws IOException {
        if (os != null) {
            os.flush();
            os.close();
        }
    }



}

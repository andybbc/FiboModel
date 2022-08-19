package com.vlion.io.hdfs;

import java.io.BufferedOutputStream;
import java.io.IOException;

public class HdfsTextWriter extends AbstractHDFSWriter {
    private String fileExtension = "";

    @Override
    protected void create() throws IOException {
        os = new BufferedOutputStream(fos);
    }

    @Override
    protected String getFileExtension() {
        return this.fileExtension;
    }

    @Override
    protected void addDir(String dirName) throws IOException {

    }

    @Override
    protected void addFileStart(String srcPathName) throws IOException {

    }

    @Override
    protected void addFileEnd() throws IOException {

    }
}

package com.vlion.io;

import com.vlion.io.hdfs.HdfsTextWriter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class IOFactory {
    private static Logger logger = LoggerFactory.getLogger(IOFactory.class);

    public static Writer getSingleFileHdfsWriter(){
        return new HdfsTextWriter();
    }

}

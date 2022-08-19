package com.vlion.io;

import java.io.IOException;
import java.util.List;

public interface Writer {
    /**
     * 创建文件,并返回实际创建的文件路径
     *
     * @param filePath,写入文件路径
     * @return
     * @throws IOException
     */
    String create(String filePath) throws IOException;


    /**
     * 读取文件列表,将内容写到create(filePath)创建的文件里
     *
     * @param srcFilePaths,要读取的文件路径列表
     * @throws IOException
     */
    void writeFiles(List<String> srcFilePaths) throws IOException;


    /**
     * 读取文件,将内容写到create(filePath)创建的文件里
     *
     * @param srcFilePath,要读取的文件路径
     * @throws IOException
     */
    void writeFiles(String srcFilePath) throws IOException;


    /**
     * 将字符串按指定编码写入到create(filePath)创建的文件里
     *
     * @param str
     * @param charsetName
     * @throws IOException
     */
    void write(String str, String charsetName) throws IOException;

    /**
     * 将字符串写入到create(filePath)创建的文件里
     *
     * @param str
     * @throws IOException
     */
    void write(String str) throws IOException;


    /**
     * 将字节流写入到create(filePath)创建的文件里
     *
     * @param bytes
     * @throws IOException
     */
    void write(byte[] bytes) throws IOException;

    /**
     * 关闭写入流,表示文件写入完成
     *
     * @throws IOException
     */
    void close() throws IOException;



}

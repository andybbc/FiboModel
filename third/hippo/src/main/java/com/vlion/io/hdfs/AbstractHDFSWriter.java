package com.vlion.io.hdfs;

import com.vlion.io.AbstractWriter;
import com.vlion.io.Writer;
import org.apache.commons.lang.StringUtils;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.util.List;

public abstract class AbstractHDFSWriter extends AbstractWriter implements Writer {
    protected FSDataOutputStream fos = null;
    protected String fileName;//写入文件名
    protected static final String PATH_SEPERATOR = "/";
    protected static final int BUFFER = 2048;
    protected FileSystem fs;

    @Override
    public String create(String filePath) throws IOException {
        Path oldPath = new Path(filePath);
        fileName = oldPath.getName();

        Path path = new Path(filePath + getFileExtension());

        Configuration configuration = new Configuration();
        fs = path.getFileSystem(configuration);

        fos = fs.create(path);
        create();

        return path.toString();
    }

    protected abstract void create() throws IOException;

    /**
     * 获取文件后缀名
     *
     * @return
     */
    protected abstract String getFileExtension();

    @Override
    public void writeFiles(List<String> srcFilePaths) throws IOException {
        for (String srcFilePath : srcFilePaths) {
            writeFiles(srcFilePath);
        }
    }

    @Override
    public void writeFiles(String srcFilePath) throws IOException {
        String basePath = "";

        if (StringUtils.isNotBlank(srcFilePath)) {
            write(new Path(srcFilePath), basePath);
        }
    }

    private void write(Path srcPath, String basePath) throws IOException {
        if (fs.isDirectory(srcPath)) {
            writeDir(srcPath, basePath);
        } else {
            writeFiles(srcPath, basePath);
        }
    }

    protected void writeDir(Path srcPath, String dir) throws IOException {
        FileStatus[] fileStatuses = fs.listStatus(srcPath);

        String dirName = dir + srcPath.getName() + PATH_SEPERATOR;

        if (fileStatuses.length < 1) {
            addDir(dirName);
        }

        for (FileStatus fileStatus : fileStatuses) {
            write(fileStatus.getPath(), dirName);
        }
    }

    /**
     * 加上空目录
     *
     * @param dirName
     * @throws IOException
     */
    protected abstract void addDir(String dirName) throws IOException;

    protected void writeFiles(Path srcPath, String dir) throws IOException {
        addFileStart(dir + srcPath.getName());
        BufferedInputStream bis = new BufferedInputStream(fs.open(srcPath));

        int count;
        byte data[] = new byte[BUFFER];
        while ((count = bis.read(data, 0, BUFFER)) != -1) {
            os.write(data, 0, count);
        }

        bis.close();
        addFileEnd();
    }

    /**
     * 添加文件前的操作,例如tar压缩时,创建archiveEntry
     *
     * @param srcPathName
     * @throws IOException
     */
    protected abstract void addFileStart(String srcPathName) throws IOException;

    /**
     * 添加文件后的操作,例如tar压缩时,关闭archiveEntry
     *
     * @throws IOException
     */
    protected abstract void addFileEnd() throws IOException;


    @Override
    public void close() throws IOException {
        super.close();

        if (fos != null) {
            fos.close();
        }
    }

}

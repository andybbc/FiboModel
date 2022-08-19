package com.vlion.util;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.math.BigInteger;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class HdfsUtil {
    private static Logger logger = LoggerFactory.getLogger(HdfsUtil.class);
    private static int securitySlashCnt = 3;
    //    private static FileSystem fs1;
    private static Configuration configuration = new Configuration();
    ;
    private static final int BYTE_BUFFER_SIZE = 4096;

//    static {
//        try {
//            configuration = new Configuration();
//            fs = FileSystem.get(configuration);
//        } catch (IOException e) {
//            logger.error("", e);
//        }
//    }

    public static void main(String[] args) throws IOException {
        mkdir("/tmp/fstest/1");
        mkdir("/tmp/fstest/2");
        rmFile("/tmp/fstest/2");
    }

    public static FileSystem getFs(Path path) throws IOException {
        return FileSystem.get(path.toUri(), configuration);
    }

    /**
     * 创建文件目录
     *
     * @param path
     */
    public static void mkdir(String path) throws IOException {
        mkdir(new Path(path));
    }

    public static void mkdir(Path path) throws IOException {
        getFs(path).mkdirs(path);
        logger.info("创建目录{}", path);
    }

    /**
     * 删除文件或者文件目录
     *
     * @param path
     */
    public static void rmFile(String path) throws IOException {
        Path file = new Path(path);
        FileSystem fs = getFs(file);

        if (fs.exists(file) && canDelete(file)) {
            delete(file, true);
        }
    }

    public static void cleanDir(String dir) throws IOException {
        Path path = new Path(dir);
        FileSystem fs = getFs(path);

        if (fs.isDirectory(path) && canDelete(path)) {
            logger.info("清理目录{}", dir);
            FileStatus[] fileStatuses = fs.listStatus(path);

            for (FileStatus fileStatus : fileStatuses) {
                delete(fileStatus.getPath(), true);
            }
        }
    }

    private static void delete(Path path, boolean recursive) throws IOException {
        FileSystem fs = getFs(path);
        fs.delete(path, recursive);
        logger.info("删除文件{}", path);
    }

    public static boolean canDelete(Path path) throws IOException {
        int slashCnt = getSlashCnt(path);//path上的/数量

        boolean flag = true;
        if (slashCnt < securitySlashCnt) {
            logger.warn(path + "的斜杠/数量少于" + securitySlashCnt + ",不能删除该路径");
            flag = false;
        }

        return flag;
    }

    public static int getSlashCnt(String file) throws IOException {
        return getSlashCnt(new Path(file));
    }

    /**
     * 获取path的/数量
     *
     * @param path
     * @return
     * @throws IOException
     */
    public static int getSlashCnt(Path path) throws IOException {
        int cnt = 0;
        if (path != null) {
            FileSystem fs2 = path.getFileSystem(configuration);
            Path path2 = fs2.makeQualified(path);
            String path2Str = path2.toString();

            path2Str = path2Str.substring(path2Str.indexOf("://") + 3);
            cnt = path2Str.split("/").length - 1;

            logger.info(path2 + "的/数量为" + cnt);
        }

        return cnt;
    }


    public static long getPathSize(String file) throws IOException {
        return getPathSize(new Path(file));
    }

    public static long getPathSize(Path path) throws IOException {
        long size;
        FileSystem fs = getFs(path);

        if (fs.isDirectory(path)) {
            size = getPathSizeDir(path);
        } else {
            size = getPathSizeFile(path);
        }

        return size;
    }

    private static long getPathSizeDir(Path dir) throws IOException {
        FileSystem fs = getFs(dir);
        FileStatus[] fileStatuses = fs.listStatus(dir);
        long size = 0;

        for (FileStatus fileStatus : fileStatuses) {
            size += getPathSize(fileStatus.getPath());
        }

        return size;
    }

    private static long getPathSizeFile(Path file) throws IOException {
        FileSystem fs = getFs(file);
        FileStatus fileStatus = fs.getFileStatus(file);
        return fileStatus.getLen();
    }

    /**
     * 将对象序列化到hdfs上
     *
     * @param obj
     * @param dir,目录
     * @throws IOException
     */
//    public static String writeObjectDir(Object obj, String dir) throws IOException {
//        String file = dir + "/" + StringUtil.uuid();
//        return writeObjectFile(obj, file);
//    }

    /**
     * 将对象序列化到hdfs上
     *
     * @param obj
     * @param file,文件
     * @throws IOException
     */
    public static String writeObjectFile(Object obj, String file) throws IOException {
        ObjectOutputStream oos = null;

        try {
            Path path = new Path(file);
            mkdir(path.getParent());

            FileSystem fs = getFs(path);
            oos = new ObjectOutputStream(fs.create(path));
            oos.writeObject(obj);
        } finally {
            if (oos != null) {
                try {
                    oos.close();
                } catch (IOException e) {
                    logger.error("", e);
                }
            }
        }

        return file;
    }

    public static String md5Hash(String file) throws NoSuchAlgorithmException, IOException {
        MessageDigest digest = MessageDigest.getInstance("MD5");

        FSDataInputStream fis = null;
        DigestInputStream blobStream = null;

        try {
            Path path = new Path(file);
            FileSystem fs = getFs(path);

            fis = fs.open(path);
            blobStream = new DigestInputStream(new BufferedInputStream(fis), digest);

            byte[] buffer = new byte[BYTE_BUFFER_SIZE];
            int num;
            do {
                num = blobStream.read(buffer);
            } while (num > 0);
        } finally {
            if (fis != null) {
                try {
                    fis.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }

            if (blobStream != null) {
                try {
                    blobStream.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }

        return new BigInteger(1, digest.digest()).toString(16);
    }

    public static FSDataOutputStream getFSDataOutputStream(String file) throws IOException {
        Path path = new Path(file);
        mkdir(path.getParent());

        FileSystem fs = getFs(path);
        return fs.create(path);
    }


    public static FSDataInputStream getFSDataInputStream(String file) throws IOException {
        Path path = new Path(file);
        FileSystem fs = getFs(path);

        FSDataInputStream fis = null;
        if (fs.exists(path)) {
            fis = fs.open(path);
        }

        return fis;
    }

}

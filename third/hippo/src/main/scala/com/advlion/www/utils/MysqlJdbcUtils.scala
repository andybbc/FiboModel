package com.advlion.www.utils

import java.sql.{Connection, DriverManager, PreparedStatement, ResultSet}
import java.util.Properties
import java.sql.SQLException

/**
  * Created by Admin on 2020/4/13.
  */
object MysqlJdbcUtils {
    val prop = new Properties()
    prop.load(this.getClass.getClassLoader.getResourceAsStream("mysql.properties"))
    val url: String = prop.getProperty("url")
    val dbtable: String  = prop.getProperty("dbtable")
    val user: String  = prop.getProperty("user")
    val password: String  = prop.getProperty("password")
    val driver: String  = prop.getProperty("driver")

    //激励的相关的jdbc连接信息
    val urlIncentives = prop.getProperty("url_incentives")
    val userIncentives = prop.getProperty("user_incentives")
    val passwordIncentives = prop.getProperty("password_incentives")

    //激励的相关的jdbc连接信息
    val urlIncentivesA = prop.getProperty("url_incentives_a")
    val userIncentivesA = prop.getProperty("user_incentives_a")
    val passwordIncentivesA = prop.getProperty("password_incentives_a")


    def main(args: Array[String]): Unit = {
      println(url)
      println(user)
      println(password)
      println(driver)
    }


    private var ct:Connection = null
    private var ps:PreparedStatement = null
    private var rs:ResultSet = null

    def executeUpdate(sql: String, parameters: Array[String]): Unit = {
        try {
            ct = DriverManager.getConnection(url, user, password)
            ps = ct.prepareStatement(sql)
            if (parameters != null) for (i <- 0 until parameters.length) {
                ps.setString(i + 1, parameters(i))
            }
            // 执行
            ps.executeUpdate
        } catch {
            case e: Exception =>
                e.printStackTrace()
                throw new RuntimeException(e.getMessage)
        } finally {close(rs, ps, ct)
        rs =null
            ps = null
            ct = null
        }
    }



    // 把关闭资源写成函数
    def close( rs: ResultSet, ps: PreparedStatement, ct: Connection): Unit = { // 关闭资源
        if (rs != null) {
            try rs.close
            catch {
                case e: SQLException =>
                    e.printStackTrace()
            }
        }
        if (ps != null) {
            try ps.close
            catch {
                case e: SQLException =>
                    e.printStackTrace()
            }
        }
        if (ct != null) {
            try ct.close
            catch {
                case e: SQLException =>
                    e.printStackTrace()
            }
        }
    }






}

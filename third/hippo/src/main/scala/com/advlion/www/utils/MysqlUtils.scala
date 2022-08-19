package com.advlion.www.utils



import java.sql.{Connection, DriverManager, PreparedStatement, Statement}

import com.advlion.www.log.{ProvinceSummary, Summary}
import org.apache.spark.sql.DataFrame

import scala.collection.mutable.ListBuffer


/**
  * Created by 22512 on 2020/4/25.
  */
object MysqlUtils {

  val url: String = MysqlJdbcUtils.url
  val user: String = MysqlJdbcUtils.user
  val password: String = MysqlJdbcUtils.password
  val driver: String = MysqlJdbcUtils.driver
  val uri: String = url + "?user=" + user + "&password=" + password
  println("uri===================="+uri)
  /**
    * 更新天表数据
    * @param dataFrame
    * @param table
    */
  def UpdateMysqlSummaryData(dataFrame: DataFrame,table:String){
    dataFrame.foreachPartition(row=> {
      val list = new ListBuffer[Summary]
      row.foreach(info => {
        val app_id = info(0).toString.toInt
        val user_id = info(1).toString.toInt
        val content_source_id = info(2).toString.toInt
        val time = info(3).toString
        val cr_imps = info(4).toString.toInt
        val cr_clicks = info(5).toString.toInt
        val ad_imps = info(6).toString.toInt
        val ad_clicks = info(7).toString.toInt
        val h5_request = info(8).toString.toInt
        val api_request = info(9).toString.toInt
        val properties_id = info(10).toString.toInt
        val real_tag_id = info(11).toString
        val channel = info(12).toString
        val code_advsource = info(13).toString
        val code_style_id = info(14).toString.toInt
        val city_id = info(15).toString.toInt
        val province_id = info(16).toString.toInt
        val put_platform_id = info(17).toString.toInt
        println("time==="+time)
        list.append(Summary(app_id, user_id, content_source_id, time, cr_imps, cr_clicks, ad_imps, ad_clicks, h5_request,
          api_request, properties_id, real_tag_id, channel, code_advsource, code_style_id, city_id, province_id, put_platform_id))

      })
      println("time===[[[[[[[[")
      insertSummary(list:ListBuffer[Summary],table:String)
    })
  }

  def insertSummary(list:ListBuffer[Summary],table:String):Unit ={
    var connect:Connection = null
    var pstmt:PreparedStatement = null
    println("********* kaishi111 UpdateMysqlSummaryData ****************")
    try{
      Class.forName(driver)
      connect = DriverManager.getConnection(uri)
      //      connect = getConnection(url)
      println("connect====================="+connect)
      connect.setAutoCommit(false)
      val sql =
        s"""
           |insert into $table(id,app_id,user_id,content_source_id,time,cr_imps,cr_clicks,ad_imps,ad_clicks,h5_request,api_request,
           |        properties_id,real_tag_id,channel,code_advsource,code_style_id,city_id,province_id,put_platform_id)
           |        values(?,?,?,'?',?,?,?,?,?,?,?,?,'?','?',?,?,?,?)
           |        on duplicate key update cr_imps = ?,cr_clicks = ?,ad_imps = ?,ad_clicks = ?,h5_request = ?,api_request = ?
         """.stripMargin
      println("===========================")
      println(sql)
      println("===========================")
      pstmt = connect.prepareStatement(sql)
      for(info <- list){
        pstmt.setInt(1, info.app_id)
        pstmt.setInt(2, info.user_id)
        pstmt.setInt(3, info.content_source_id)
        pstmt.setString(4, info.time)
        pstmt.setInt(5, info.cr_imps)
        pstmt.setInt(6, info.cr_clicks)
        pstmt.setInt(7, info.ad_imps)
        pstmt.setInt(8, info.ad_clicks)
        pstmt.setInt(9, info.h5_request)
        pstmt.setInt(10, info.api_request)
        pstmt.setInt(11, info.properties_id)
        pstmt.setString(12, info.real_tag_id)
        pstmt.setString(13, info.channel)
        pstmt.setString(14, info.code_advsource)
        pstmt.setInt(15, info.code_style_id)
        pstmt.setInt(16, info.city_Id)
        pstmt.setInt(17, info.province_id)
        pstmt.setInt(18, info.put_platform_id)

        println("user_id"+info.app_id)
        pstmt.addBatch()
      }
      println("更新数据")
      pstmt.executeBatch()
      connect.commit()
    }catch {
      case e:Exception => e.printStackTrace()
    }finally {
      release(connect, pstmt)
    }
  }

//  /**
//    * 更新省份表数据
//    * @param dataFrame
//    * @param table
//    */
//  def UpdateMysqlProvinceSummaryData(dataFrame: DataFrame,table:String){
//    dataFrame.foreachPartition(row=> {
//      val list = new ListBuffer[ProvinceSummary]
//      row.foreach(info => {
//        //
////        val app_id = info.getAs[Int]("app_id")
//        val app_id = info(0).toString.toInt
//        val user_id = info(1).toString.toInt
//        val content_source_id = info(2).toString.toInt
//        val time = info(3).toString
//        val cr_imps = info(4).toString.toInt
//        val cr_clicks = info(5).toString.toInt
//        val ad_imps = info(6).toString.toInt
//        val ad_clicks = info(7).toString.toInt
//        val h5_request = info(8).toString.toInt
//        val api_request = info(9).toString.toInt
//        val properties_id = info(10).toString.toInt
//        val real_tag_id = info(11).toString
//        val channel = info(12).toString
//        val code_advsource = info(13).toString
//        val code_style_id = info(14).toString.toInt
//        val province_id = info(15).toString.toInt
//        val put_platform_id = info(16).toString.toInt
//        list.append(ProvinceSummary(app_id, user_id, content_source_id, time, cr_imps, cr_clicks, ad_imps, ad_clicks, h5_request,
//          api_request, properties_id, real_tag_id, channel, code_advsource, code_style_id, province_id, put_platform_id))
//      })
//      insertProvinceSummary(list:ListBuffer[ProvinceSummary],table:String)
//    })
//  }
//
//  def insertProvinceSummary(list:ListBuffer[ProvinceSummary],table:String):Unit ={
//    Class.forName(driver)
//    var connect:Connection = null
//    var pstmt:PreparedStatement = null
//
//    try{
//      connect = DriverManager.getConnection(uri)
////      connect = getConnection(url)
//      connect.setAutoCommit(false)
//      val sql =
//        s"""
//           |insert into $table(id,app_id,user_id,content_source_id,time,cr_imps,cr_clicks,ad_imps,ad_clicks,h5_request,api_request,
//           |        properties_id,real_tag_id,channel,code_advsource,code_style_id,province_id,put_platform_id)
//           |        values(?,?,?,'?',?,?,?,?,?,?,'?','?','?',?,?,?,?)
//           |        on duplicate key update app_id = ?,user_id = ?,content_source_id = ?,time = '?',
//           |        cr_imps = ?,cr_clicks = ?,ad_imps = ?,ad_clicks = ?,h5_request = ?,api_request = ?,
//           |        properties_id = ?,real_tag_id = '?',channel = '?',code_advsource = '?',
//           |        code_style_id = ?,province_id = ?,put_platform_id = ?
//           |"""
//         .stripMargin
//        println(sql)
////      on duplicate key update cr_imps = ?,cr_clicks = ?,ad_imps = ?,ad_clicks = ?,h5_request = ?,api_request = ?
//
//      pstmt = connect.prepareStatement(sql)
//      for(info <- list){
//        pstmt.setInt(1, info.app_id)
//        pstmt.setInt(2, info.user_id)
//        pstmt.setInt(3, info.content_source_id)
//        pstmt.setString(4, info.time)
//        pstmt.setInt(5, info.cr_imps)
//        pstmt.setInt(6, info.cr_clicks)
//        pstmt.setInt(7, info.ad_imps)
//        pstmt.setInt(8, info.ad_clicks)
//        pstmt.setInt(9, info.h5_request)
//        pstmt.setInt(10, info.api_request)
//        pstmt.setInt(11, info.properties_id)
//        pstmt.setString(12, info.real_tag_id)
//        pstmt.setString(13, info.channel)
//        pstmt.setString(14, info.code_advsource)
//        pstmt.setInt(15, info.code_style_id)
//        pstmt.setInt(16, info.province_id)
//        pstmt.setInt(17, info.put_platform_id)
//        pstmt.addBatch()
//        pstmt.execute()
//      }
//      println("更新数据")
//      pstmt.executeBatch()
//      connect.commit()
//    }catch {
//      case e:Exception => e.printStackTrace()
//    }finally {
//      release(connect, pstmt)
//    }
//  }
//
////  def getConnection(url:String) = {
////    DriverManager.getConnection(url)
////  }
  def release(connection: Connection, pstmt: PreparedStatement): Unit = {
    try {
      if (pstmt != null) {
        pstmt.close()
      }
    } catch {
      case e: Exception => e.printStackTrace()
    } finally {
      if (connection != null) {
        connection.close()
      }
    }
  }
}

package com.advlion.www.analysis

import com.advlion.www.utils.{MysqlJdbcUtils, MysqlUtils}
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.storage.StorageLevel


/**
  * Created by Admin on 2020/4/8.
  * 数据汇总，并写入mysql
  */
object Summary {
  val url: String = MysqlJdbcUtils.url
  val user: String = MysqlJdbcUtils.user
  val password: String = MysqlJdbcUtils.password
  val driver: String = MysqlJdbcUtils.driver
  //小时表
  val hourTable = "new_stat"
//  val hourTableW = "new_stat_w"  //20200921改成中间表
  //天表
  val dayTable = "new_stat_day_tmp"
  //省份表
  val provinceTable = "new_stat_province_tmp"
  //tag_map 数据
  val tagMapTable = "tag_map_tmp"

  val dataComparisonTable = "data_comparison"

  //20200921新增表激励
  val appStartAnalysisTable = "app_start_analysis"
  val gameTimeAnalysisTable = "game_time_analysis"
  val userClickTable = "user_click_analysis"

  val userTimeAnalysisTable = "user_time_analysis"  //20201102新增明细,每天统计,覆盖前面的
  //激励视频相关的jdbc连接信息
  val urlIncentives = MysqlJdbcUtils.urlIncentives
  val userIncentives = MysqlJdbcUtils.userIncentives
  val passwordIncentives = MysqlJdbcUtils.passwordIncentives

  val urlIncentivesA = MysqlJdbcUtils.urlIncentivesA
  val userIncentivesA = MysqlJdbcUtils.userIncentivesA
  val passwordIncentivesA = MysqlJdbcUtils.passwordIncentivesA

  /**
    * 小时表汇总数据
    * @param spark spark
    */
  def hourSummary(spark:SparkSession,etlDate:String,etlHour:String): Unit = {
    val hourSummaryData = spark.sql(
      s"""
         |select
         |`app_id`,
         |`user_id`,
         |`content_source_id`,
         |'${etlDate} ${etlHour}:00:00' as time,
         |sum(cr_imps) as cr_imps,
         |sum(cr_clicks) as cr_clicks,
         |sum(ad_imps) as ad_imps,
         |sum(ad_clicks) as ad_clicks,
         |sum(h5_request) as h5_request,
         |sum(api_request) as api_request,
         |`properties_id`,
         |`real_tag_id`,
         |`channel`,
         |`code_advsource`,
         |`code_style_id`,
         |`city_id`,
         |`province_id`,
         |`put_platform_id`
         |from
         |(
         |    select	a.mediaID as app_id,
         |    		c.user_id as user_id,
         |    		a.contentID as content_source_id,
         |    		a.crImp as cr_imps,
         |    		a.crClk as cr_clicks,
         |    		a.adImp as ad_imps,
         |    		a.adClk as ad_clicks,
         |    		a.h5Req as h5_request,
         |    		a.apiReq as api_request,
         |    		a.mediaGateID as properties_id,
         |    		a.advSourceID as real_tag_id,
         |    		a.channel as channel,
         |    		a.advSource as code_advsource,
         |    		a.advTypeID as code_style_id,
         |    		a.cityID as city_id,
         |    		case when d.province_id is null then '0' else d.province_id end as province_id,
         |    		c.put_platform_id as put_platform_id
         |    from 	unionSummary a
         |    inner	join
         |    (
         |          select name
         |          from newsChennel
         |          union all
         |          select name
         |          from newsChennel_1
         |    ) b
         |    on	a.channel = b.name
         |    left	join app c
         |    on	a.mediaID = c.id
         |    left	join city d
         |    on	a.cityID = d.id
         |    where a.advTypeID != ''
         |    and a.mediaID != ''
         |    and c.user_id is not null
         |    and c.put_platform_id is not null
         |    and a.contentID regexp '^[\\-]{0,1}\\\\d+$$'
         |) t
         |group by
         |`user_id`,
         |`app_id`,
         |`properties_id`,
         |`content_source_id`,
         |`real_tag_id`,
         |`channel`,
         |`code_advsource`,
         |`city_id`,
         |`code_style_id`,
         |`put_platform_id`,
         |`province_id`
         |""".stripMargin)

    println("new state's count:"+hourSummaryData.count())

    hourSummaryData.createOrReplaceTempView("newStatView")

//    MysqlUtils.UpdateMysqlSummaryData(hourSummaryData:DataFrame,"new_stat_test":String)
    hourSummaryData.coalesce(1).write.mode("append")
//    hourSummaryData.write.mode("overwrite")
      .format("jdbc")
      .option("url",url)
      .option("user",user)
      .option("password",password)
      .option("dbtable",hourTable)
      .save()

//    //通过w表追加更新到正式表
//    MysqlJdbcUtils.executeUpdate(
//      s"""
//         |insert into ${hourTable}
//         |          (`app_id`,
//         |      `user_id`,
//         |      `content_source_id`,
//         |      `time`,
//         |       cr_imps,
//         |       cr_clicks,
//         |       ad_imps,
//         |      ad_clicks,
//         |       h5_request,
//         |       api_request,
//         |      `properties_id`,
//         |      `real_tag_id`,
//         |      `channel`,
//         |      `code_advsource`,
//         |      `code_style_id`,
//         |      `city_id`,
//         |      `province_id`,
//         |      `put_platform_id` )
//         |select
//         |     `app_id`,
//         |    `user_id`,
//         |    `content_source_id`,
//         |    `time`,
//         |     cr_imps,
//         |     cr_clicks,
//         |     ad_imps,
//         |    ad_clicks,
//         |     h5_request,
//         |     api_request,
//         |    `properties_id`,
//         |    `real_tag_id`,
//         |    `channel`,
//         |    `code_advsource`,
//         |    `code_style_id`,
//         |    `city_id`,
//         |    `province_id`,
//         |    `put_platform_id`
//         |from $hourTableW
//         |on duplicate key update
//         | app_id                  = values(    app_id             ),
//         |user_id                  = values(   user_id             ),
//         |content_source_id        = values(   content_source_id   ),
//         |time                     = values(   time                ),
//         | cr_imps                   = values(  cr_imps            ),
//         | cr_clicks                 = values(  cr_clicks          ),
//         | ad_imps                   = values(  ad_imps            ),
//         |ad_clicks                  = values( ad_clicks           ),
//         | h5_request                = values(  h5_request         ),
//         | api_request               = values(  api_request        ),
//         |properties_id            = values(   properties_id       ),
//         |real_tag_id              = values(   real_tag_id         ),
//         |channel                  = values(   channel             ),
//         |code_advsource           = values(   code_advsource      ),
//         |code_style_id            = values(   code_style_id       ),
//         |city_id                  = values(   city_id             ),
//         |province_id              = values(   province_id         ),
//         |put_platform_id          = values(   put_platform_id     )
//         |""".stripMargin,null)


  }

  /**
    * 天表数据汇总
    * @param spark
    * @param etlDate
    */
  def daySummary(spark:SparkSession,etlDate:String,etlHour:String): Unit ={
    val startTime = etlDate + " 00:00:00"
    val endTime = etlDate + " 23:00:00"

    val newStatDF = spark.read
      .format("jdbc")
      .option("url", url)
      .option("user", user)
      .option("password", password)
      .option("driver",driver)
      .option("dbtable", s"(select * from $hourTable where time >='$startTime' and time <='$endTime') as t")
      .load()
      .persist(StorageLevel.MEMORY_AND_DISK_SER)
    newStatDF.createOrReplaceTempView("newStat")
//    spark.sql("select * from newStat").show
    val daySummaryData = spark.sql(
      s"""
        |select	app_id,
        |		user_id,
        |		content_source_id,
        |		to_date(time) as time,
        |		sum(cr_imps) as cr_imps,
        |		sum(cr_clicks) as cr_clicks,
        |		sum(ad_imps) as ad_imps,
        |		sum(ad_clicks) as ad_clicks,
        |		sum(h5_request) as h5_request,
        |		sum(api_request) as api_request,
        |		properties_id,
        |		real_tag_id,
        |		channel,
        |		code_advsource,
        |		code_style_id,
        |		city_id,
        |		province_id,
        |		put_platform_id
        |from	newStat
        |where  time >= '$startTime'
        |and 	time <= '$endTime'
        |group 	by app_id,user_id,content_source_id,to_date(time),properties_id,real_tag_id,
        |channel,code_advsource,code_style_id,city_id,province_id,put_platform_id
      """.stripMargin)
//    daySummaryData.show()
    println("==============天表-===========")
    //MysqlUtils.UpdateMysqlSummaryData(daySummaryData:DataFrame,dayTable:String)
    daySummaryData.write.mode("overwrite")
      .format("jdbc")
      .option("url", url)
      .option("user", user)
      .option("password", password)
      .option("dbtable", dayTable) //表名
      .save()
  }

  //20200908,new_stat_province_tmp表添加uv,需要天distinct
  def provinceUVSummary(spark:SparkSession,etlDate:String) = {

    val apiReqUVDF=spark.sql(
      s"""
         |
         |select
         |	  a.mediaID as app_id,
         |    c.user_id as user_id,
         |    a.contentID as content_source_id,
         |    a.time,
         |    a.mediaGateID as properties_id,
         |    a.advSourceID as real_tag_id,
         |    a.channel as channel,
         |    a.advSource as code_advsource,
         |    a.advTypeID as code_style_id,
         |    case when d.province_id is null then '0' else d.province_id end as province_id,
         |    c.put_platform_id as put_platform_id,
         |    uv
         |from
         |(
         |  select
         |    '$etlDate' time, --天
         |    mediaID,
         |    mediaGateID,
         |    channel,
         |    cityID,
         |    '-1' contentID,
         |    '-1' advSource,
         |    '-1' advSourceID,
         |    '-1' advTypeID,
         |    count(distinct u_id) as uv
         |  from
         |  (
         |   select
         |         case when mediaID = ''  then '-1' else mediaID end mediaID,
         |   		case when mediaGateID = ''  then '-1' else mediaGateID end mediaGateID,
         |   		case when channel='' then '固定' else channel end channel,
         |   		case when cityID = ''  then '-1' else cityID end cityID,
         |     case when os in ('1','2') then coalesce(androidId,idfa) else cookie end as u_id -- uv用
         |   from   apiReqDay
         |   ) t
         |   group by mediaID,mediaGateID,channel,cityID
         |) a
         |inner	join
         |(
         |      select name
         |      from newsChennel
         |      union all
         |      select name
         |      from newsChennel_1
         |) b
         |on	a.channel = b.name
         |left	join app c
         |on	a.mediaID = c.id
         |left	join city d
         |on	a.cityID = d.id
         |where a.advTypeID != ''
         |and a.mediaID != ''
         |and c.user_id is not null
         |and c.put_platform_id is not null
         |
         |
         |""".stripMargin)

    apiReqUVDF.createOrReplaceTempView("apiReqUVDF")
  }


  /**
    * 省份表数据汇总
    * @param spark
    * @param etlDate
    * @param etlHour
    */
  def provinceSummary(spark:SparkSession,etlDate:String,etlHour:String): Unit ={
      provinceUVSummary(spark,etlDate)
//    val newDayStatDF = spark.read
//      .format("jdbc")
//      .option("url", url)
//      .option("dbtable", s"(select * from new_stat_day_test where time ='${etlDate}') as t")
//      .load()
//    newDayStatDF.createOrReplaceTempView("newDayStat")
    //直接从小时表中去读取数据，汇总
    val startTime = etlDate + " 00:00:00"
    val endTime = etlDate + " 23:00:00"
    val provinceSummaryData = spark.sql(
      s"""
         |select
         |t1.*,
         |if(t2.uv is null ,0,t2.uv) as uv
         |from
         |(
         |  select	app_id,
         |  		user_id,
         |  		content_source_id,
         |  		to_date(time) as time,
         |  		sum(cr_imps) as cr_imps,
         |  		sum(cr_clicks) as cr_clicks,
         |  		sum(ad_imps) as ad_imps,
         |  		sum(ad_clicks) as ad_clicks,
         |  		sum(h5_request) as h5_request,
         |  		sum(api_request) as api_request,
         |  		properties_id,
         |  		real_tag_id,
         |  		channel,
         |  		code_advsource,
         |  		code_style_id,
         |  		province_id,
         |  		put_platform_id
         |  from	newStat
         |  where	time >= '$startTime'
         |  and 	time <= '$endTime'
         |  group 	by app_id,user_id,content_source_id,to_date(time),properties_id,real_tag_id,channel,code_advsource,code_style_id,province_id,put_platform_id
         |) t1
         |left join
         |apiReqUVDF t2
         |on
         |t1.app_id=t2.app_id
         |and t1.user_id=t2.user_id
         |and t1.content_source_id=t2.content_source_id
         |and t1.time=t2.time
         |and t1.properties_id=t2.properties_id
         |and t1.real_tag_id=t2.real_tag_id
         |and t1.channel=t2.channel
         |and t1.code_advsource=t2.code_advsource
         |and t1.code_style_id=t2.code_style_id
         |and t1.province_id=t2.province_id
         |and t1.put_platform_id=t2.put_platform_id
         |
         |
      """.stripMargin)
    provinceSummaryData.createOrReplaceTempView("provinceSummary")
    //provinceSummaryData.show()
    //MysqlUtils.UpdateMysqlProvinceSummaryData(provinceSummaryData:DataFrame,"new_stat_province_test":String)
    provinceSummaryData.write.mode("overwrite")
      .format("jdbc")
      .option("url", url)
      .option("user", user)
      .option("password", password)
      .option("dbtable", provinceTable)
      .save()
  }

  /**
    * 更新tag_map 数据
    * @param spark
    */
  def tagMap(spark:SparkSession): Unit ={
    val tagMapDF = spark.sql(
      """
        |select	b.app_id,
        |		b.user_id,
        |		b.properties_id,
        |		b.tag_name,
        |		trim(b.tag_id) tag_id
        |from
        |(
        |	select	a.app_id,
        |			a.user_id,
        |			a.properties_id,
        |			a.tag_name,
        |			a.tag_id,
        |			row_number() over (partition by a.app_id,a.user_id,a.properties_id,a.tag_id order by 1) num
        |	from
        |		(
        |			select	app_id,
        |					user_id,
        |					properties_id,
        |					tag_name,
        |					tag_id
        |			from	overallReport
        |			where	app_id != -1
        |			and		user_id != -1
        |			and		properties_id != '-1'
        |			and		tag_name != '-1'
        |			and		tag_id != '-1'
        |			union 	all
        |			select	e.app_id,
        |					e.user_id,
        |					e.properties_id,
        |					e.tag_name,
        |					e.tag_id
        |			from
        |			(
        |   				select	c.app_id,
        |						c.user_id,
        |						c.properties_id,
        |						(case when c.real_tag_id = d.tag_id then d.tag_name else c.real_tag_id end) as tag_name,
        |						c.real_tag_id as tag_id
        |				from
        |					(
        |						select 	app_id,
        |								user_id,
        |								properties_id,
        |								real_tag_id,
        |								count(1)
        |						from 	provinceSummary
        |						where app_id != -1
        |						and		user_id != -1
        |						and		properties_id != -1
        |						and		real_tag_id != '-1'
        |						group 	by app_id,user_id,properties_id,real_tag_id
        |					) c
        |				left 	join  overallReport d
        |				on		c.real_tag_id = d.tag_id
        |			) e
        |		) a
        |) b
        |""".stripMargin)
    tagMapDF.show()
    tagMapDF.write.mode("overwrite")
      .format("jdbc")
      .option("url", url)
      .option("user", user)
      .option("password", password)
      .option("dbtable", tagMapTable)
      .save()
  }

  def dataComparison(spark:SparkSession): Unit ={
    spark.sql(
      """
        |select  app_id,
        |		user_id,
        |		time,
        |		sum(cr_imps) as cr_imps,
        |		sum(ad_imps) as ad_imps,
        |		sum(cr_clicks) as cr_clicks,
        |		sum(ad_clicks) as ad_clicks,
        |		sum(h5_request) as h5_request,
        |		sum(api_request) as api_request,
        |		properties_id,
        |		put_platform_id
        |from	newStatView
        |group by app_id,user_id,time,properties_id,put_platform_id
        |""".stripMargin)
        .write.mode("append")
        .format("jdbc")
        .option("url", url)
        .option("user", user)
        .option("password", password)
        .option("dbtable", dataComparisonTable)
        .save()
  }


  //20200918 分时段 APP 启动次数柱状图,从vlionserver-168
  def incentivesSummaryByDay(spark:SparkSession,etlDate:String): Unit ={
    //Incentives(ts:Long,`type`:Int,uid:String,obj:String,cnt:Long)

    //1.分时段 APP 启动次数柱状图
    val appStartFrame = spark.sql(
      s"""
         |select
         |  from_unixtime(ts,'${etlDate} HH:00:00') as time, -- 防止冲突,用当天的时间代替
         |  count(distinct uid) as login_uv,
         |  sum(if(uid !='anonymity',cnt,0)) as login_pv,
         |  sum(if(uid = 'anonymity',cnt,0)) as unlogin_pv
         |from
         |  incentives
         |where
         |  type=1
         |group by
         |  from_unixtime(ts,'${etlDate} HH:00:00')
         |
         |
         |""".stripMargin)

    appStartFrame.write.mode("append")
        .format("jdbc")
        .option("url", urlIncentives)
        .option("user", userIncentives)
        .option("password", passwordIncentives)
        .option("dbtable", appStartAnalysisTable)
        .save()


    //2.每日玩游戏时长分布图,按天
    val gameTimeFrame = spark.sql(
      s"""
         |select
         |  '${etlDate} 00:00:00' as date,
         |  count(if(game_seconds <=600,uid,null)) as less10,
         |  count(if(game_seconds > 600 and game_seconds <= 1800,uid,null)) as range30,
         |  count(if(game_seconds > 1800 and game_seconds <= 3600,uid,null)) as range60,
         |  count(if(game_seconds > 3600 and game_seconds <= 7200,uid,null)) as range120,
         |  count(if(game_seconds > 7200,uid,null)) as more120,
         |  coalesce(sum(if(uid !='anonymity',game_seconds ,0 )),0) as login_cnt,
         |  coalesce(sum(if(uid ='anonymity',game_seconds ,0 )),0)  as unlogin_cnt
         |from
         |(
         |select
         |  uid,
         |  sum(cnt) as game_seconds
         |from
         |  incentives
         |where
         |  type=2
         |group by uid
         |
         |) t
         |""".stripMargin)
    gameTimeFrame.write.mode("append")
        .format("jdbc")
        .option("url", urlIncentives)
        .option("user", userIncentives)
        .option("password", passwordIncentives)
        .option("dbtable", gameTimeAnalysisTable)
        .save()


    //3用户点击行为统计
    val userClickDF = spark.sql(
      s"""
        |select
        |   t1.date,
        |   t1.type,
        |   t1.action,
        |   case when t1.type = 3 then coalesce(t2.title,'')
        |   when t1.type = 4 then coalesce(t3.click_name,'')
        |   else ''
        |   end as name,
        |   t1.login_cnt,
        |   t1.unlogin_cnt
        |from
        |(
        |   select
        |     '${etlDate} 00:00:00' as date,
        |      obj as action,
        |      type,
        |      coalesce(sum(if(uid != 'anonymity',cnt,0)),0) as login_cnt,
        |      coalesce(sum(if(uid = 'anonymity' ,cnt ,0)),0) as unlogin_cnt
        |   from
        |      incentives
        |   where
        |      type in (3,4)
        |   group by
        |      obj,type
        |) t1
        |left join
        |taskInfo t2
        |   on t1.type=3 and t1.action = t2.id
        |left join
        |clickMatchTab t3
        |   on t1.type=4 and t1.action = t3.click_flag
        |
        |""".stripMargin)

    userClickDF.coalesce(1).write.mode("append")
        .format("jdbc")
        .option("url", urlIncentives)
        .option("user", userIncentives)
        .option("password", passwordIncentives)
        .option("dbtable", userClickTable)
        .save()
  }

  //20201027incentives增加相同日志,-A
  def incentivesASummaryByDay(spark:SparkSession,etlDate:String): Unit ={
    //Incentives(ts:Long,`type`:Int,uid:String,obj:String,cnt:Long)

    //1.分时段 APP 启动次数柱状图
    val appStartFrame = spark.sql(
      s"""
         |select
         |  from_unixtime(ts,'${etlDate} HH:00:00') as time, -- 防止冲突,用当天的时间代替
         |  count(distinct uid) as login_uv,
         |  sum(if(uid !='anonymity',cnt,0)) as login_pv,
         |  sum(if(uid = 'anonymity',cnt,0)) as unlogin_pv
         |from
         |  incentives_A
         |where
         |  type=1
         |group by
         |  from_unixtime(ts,'${etlDate} HH:00:00')
         |
         |
         |""".stripMargin)

    appStartFrame.write.mode("append")
        .format("jdbc")
        .option("url", urlIncentivesA)
        .option("user", userIncentivesA)
        .option("password", passwordIncentivesA)
        .option("dbtable", appStartAnalysisTable)
        .save()

    //2.每日玩游戏时长分布图,按天

    val userTimeFrame = spark.sql(
      s"""
         |
         |select
         |  uid,
         |  sum(cnt) as game_seconds,
         |  '${etlDate}' as date
         |from
         |  incentives_A
         |where
         |  type=2
         |group by uid
         |
         |""".stripMargin).cache()
    userTimeFrame.createOrReplaceTempView("userTime_A")

    userTimeFrame
        .write
        .mode("overwrite")
        .format("jdbc")
        .option("url", urlIncentivesA)
        .option("user", userIncentivesA)
        .option("password", passwordIncentivesA)
        .option("dbtable", userTimeAnalysisTable)
        .save()

    val gameTimeFrame = spark.sql(
      s"""
         |select
         |  '${etlDate} 00:00:00' as date,
         |  count(if(game_seconds <=600,uid,null)) as less10,
         |  count(if(game_seconds > 600 and game_seconds <= 1800,uid,null)) as range30,
         |  count(if(game_seconds > 1800 and game_seconds <= 3600,uid,null)) as range60,
         |  count(if(game_seconds > 3600 and game_seconds <= 7200,uid,null)) as range120,
         |  count(if(game_seconds > 7200,uid,null)) as more120,
         |  coalesce(sum(if(uid !='anonymity',game_seconds ,0 )),0) as login_cnt,
         |  coalesce(sum(if(uid ='anonymity',game_seconds ,0 )),0)  as unlogin_cnt
         |from
         |userTime_A t
         |""".stripMargin)
    gameTimeFrame.write.mode("append")
        .format("jdbc")
        .option("url", urlIncentivesA)
        .option("user", userIncentivesA)
        .option("password", passwordIncentivesA)
        .option("dbtable", gameTimeAnalysisTable)
        .save()


    //3用户点击行为统计
    val userClickDF = spark.sql(
      s"""
         |select
         |   t1.date,
         |   t1.type,
         |   t1.action,
         |   case when t1.type = 3 then coalesce(t2.title,'')
         |   when t1.type = 4 then coalesce(t3.click_name,'')
         |   else ''
         |   end as name,
         |   t1.login_cnt,
         |   t1.unlogin_cnt
         |from
         |(
         |   select
         |     '${etlDate} 00:00:00' as date,
         |      obj as action,
         |      type,
         |      coalesce(sum(if(uid != 'anonymity',cnt,0)),0) as login_cnt,
         |      coalesce(sum(if(uid = 'anonymity' ,cnt ,0)),0) as unlogin_cnt
         |   from
         |      incentives_A
         |   where
         |      type in (3,4)
         |   group by
         |      obj,type
         |) t1
         |left join
         |taskInfoA t2
         |   on t1.type=3 and t1.action = t2.id
         |left join
         |clickMatchTabA t3
         |   on t1.type=4 and t1.action = t3.click_flag
         |
         |""".stripMargin)

    userClickDF.coalesce(1).write.mode("append")
        .format("jdbc")
        .option("url", urlIncentivesA)
        .option("user", userIncentivesA)
        .option("password", passwordIncentivesA)
        .option("dbtable", userClickTable)
        .save()
  }

}

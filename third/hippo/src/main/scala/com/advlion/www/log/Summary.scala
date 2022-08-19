package com.advlion.www.log

/**
  * Created by 22512 on 2020/4/25.
  * 天表和省份表结果表
  */
case class Summary (app_id:Int,user_id:Int,content_source_id:Int,time:String,cr_imps:Int,cr_clicks:Int, ad_imps:Int,
                    ad_clicks:Int,h5_request:Int,api_request:Int,properties_id:Int,real_tag_id:String, channel:String,
                    code_advsource:String,code_style_id:Int,city_Id:Int,province_id:Int,put_platform_id:Int)
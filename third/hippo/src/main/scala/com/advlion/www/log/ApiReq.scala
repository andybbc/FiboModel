package com.advlion.www.log

/**
  * API请求日志,
  * @param timestamp
  * @param mediaID
  * @param mediaGateID
  * @param channel
  * @param cityID
  */
//case class ApiReq(timestamp: Int, mediaID: String, mediaGateID: String, channel: String, cityID: String)  //20200908添加满足uv的字段
case class ApiReq(timestamp: Int,
                  mediaID: String,
                  mediaGateID: String,
                  os:String,
                  imei:String,
                  androidId:String,
                  idfa:String,
                  channel: String,
                  cityID: String,
                  cookie:String
                 )
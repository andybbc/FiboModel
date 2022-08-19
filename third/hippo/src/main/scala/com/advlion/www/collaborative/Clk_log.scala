package com.advlion.www.collaborative

/**
  *
  * @param mediaId  媒体id(使用媒体入口id)  下标:3
  * @param channel  频道    下标:15
  * @param logType  日志类型 下标:18  1.新闻  2.广告
  * @param contentId 新闻id或广告位置,需要找到新闻id  下标:19
  * @param cookie   用户id 下标:20
  */
case class Clk_log(mediaId: String, channel: String, logType: String, contentId: String, cookie: String)

package com.advlion.www.log

/**
  * 媒体请求日志
  * @param timestamp
  * @param mediaID
  * @param mediaGateID
  * @param cityID
  */
case class H5Req(timestamp: Int, mediaID: String, mediaGateID: String, cityID: String)

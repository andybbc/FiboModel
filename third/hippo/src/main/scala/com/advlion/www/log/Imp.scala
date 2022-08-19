package com.advlion.www.log

/**
  * 曝光日志
  * @param timestamp
  * @param mediaID
  * @param mediaGateID
  * @param channel
  * @param contentID
  * @param advType
  * @param advSource
  * @param advSourceID
  * @param advTypeID
  * @param cityID
  */
case class Imp(timestamp: Int, mediaID: String, mediaGateID: String, channel: String, contentID: String, advType: String,
               advSource: String, advSourceID: String, advTypeID: String, cityID: String)

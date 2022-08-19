package com.advlion.www.log

/**
  * Created by Admin on 2020/4/8.
  */

/**
  * 点击日志
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
case class Clk(timestamp: Int, mediaID: String, mediaGateID: String, channel: String, contentID: String, advType: String,
               advSource: String, advSourceID: String, advTypeID: String,cityID: String)


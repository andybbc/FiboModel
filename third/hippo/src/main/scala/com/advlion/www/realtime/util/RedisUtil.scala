package com.advlion.www.realtime.util

import java.util.Properties

import redis.clients.jedis.{Jedis, JedisPool, JedisPoolConfig}

object RedisUtil {

    //1.创建配置信息对象
    private val properties:Properties = PropertiesUtil.load("config.properties")

    private val jedisPoolConfig:JedisPoolConfig = new JedisPoolConfig()
    jedisPoolConfig.setMaxTotal(100) //最大连接数
    jedisPoolConfig.setMaxIdle(20) //最大空闲
    jedisPoolConfig.setMinIdle(20) //最小空闲
    jedisPoolConfig.setBlockWhenExhausted(true) //忙碌时是否等待
    jedisPoolConfig.setMaxWaitMillis(500) //忙碌时等待时长 毫秒
    jedisPoolConfig.setTestOnBorrow(true) //每次获得连接的进行测试

    private val jedisPool:JedisPool = new JedisPool(jedisPoolConfig,properties.getProperty("redis.host"),Integer.valueOf(properties.getProperty("redis.port")))

    //直接得到一个Redis连接
    def getJedisClient:Jedis = {
        jedisPool.getResource
    }

}

local _M = {}

_M.mysql_cfg = {
    timeout  = 3 * 1000, -- 3sec
    ip       = '127.0.0.1',
    port     = '3306',
    database = 'db',
    user     = 'user',
    password = 'pwd',
    charset  = 'utf8',
    max_package_size = 1024 * 1024,
}

_M.redis_cfg = {
    host = '127.0.0.1',
    port = 6379,
    db   = 1,
}

return _M

local redis     = require('resty.redis')
local config    = require('common.config')

local ngx_log   = ngx.log
local ngx_ERR   = ngx.ERR

local redis_cfg = config.redis_cfg

local _redis_init = function()
    local red = redis:new()
    local ok, err = red:connect(redis_cfg.host, redis_cfg.port)
    if not ok then
        ngx_log(ngx_ERR, '=== REDIS-ERROR ===', err)
        return nil, err
    end

    return red
end

local _M = {
    redis_init  = _redis_init,
}

return _M

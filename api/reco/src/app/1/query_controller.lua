local json     = require("cjson")
local cfg      = require("common.config")
local utils    = require("common.utils")
local open     = require("utils.open")
local db_redis = require("utils.db_redis")

local _pcall      = pcall
local sformat     = string.format
local tconcat     = table.concat
local tappend     = utils.tappend
local tindex      = utils.tindex
local jencode     = json.encode
local jdecode     = json.decode
local ngx_log     = ngx.log
local ngx_BUG     = ngx.DEBUG
local ngx_ERR     = ngx.ERR
local ngx_time    = ngx.time
local ngx_timer   = ngx.timer.at
local ngx_re_gsub = ngx.re.gsub

local _M = {}

local function _params_check(p)
    if not p then
        return nil, 'Params is empty.'
    end

    return true
end

local function _params_filter()
    local args = open.get_args()
    if not args then
        ngx_log(ngx_ERR, "=== Params Error ===", err)
        return nil, err
    else
        ngx_log(ngx_BUG, "=== Params ===", jencode(args))
    end

    local ok, err = _params_check(args)
    if not ok then
        ngx_log(ngx_BUG, "Params Check Error: ", err)
        return nil, err
    end

    return args
end


local _get_data_from_redis = function(key, page, limit)
    local redis_cli = db_redis.redis_init()
    if not redis_cli then
        return 102, "Redis init error."
    else
        redis_cli:select(cfg.redis_cfg.db or 0)
    end

    local data = {}

    limit = tonumber(limit) or 10
    local start = (page or 0) * limit
    local stop  = start + limit -1

    -- 获取全部数据
    local re, err = redis_cli:lrange(key, start, stop)
    ngx_log(ngx_BUG, '===', key, jencode(re), "; start: ", start, ", stop: ", stop)
    if re and re ~= ngx_null then
        data = re
    end

    if data and #data >= limit then
        redis_cli:close()
        return data
    end

    -- 使用点击排序补充数据
    local re, err = redis_cli:lrange('TopN:all', start, stop)
    ngx_log(ngx_BUG, '=== TopN:all ', jencode(re))
    if re and re ~= ngx_null then
        local diff_n = 100 - #data
        for i = 1, diff_n do
            repeat
                if tindex(data, re[i]) then
                    break
                else
                    data[#data+1] = re[i]
                end
            until true
        end
    else
        redis_cli:close()
    end

    return data
end


-- 获取点击排序列表
local _top_handler = function(d)
    local top_key = sformat('TopN:%s', d['tag'] or 'all')
    local data = _get_data_from_redis(top_key, d.page, d.limit)

    return 0, 'OK', data
end


-- 获取算法排序列表
local _range_handler = function(d)
    local range_key = sformat('Range:%s', d['news_id'])
    local data = _get_data_from_redis(range_key, d.page, d.limit)

    return 0, 'OK', data
end


-- 路由函数
local _route = function()
    -- 参数检查
    local args, err = _params_filter()
    if not args then
        return 100, err
    end

    local act_tab = {
        ["topn"]  = _top_handler,     -- 查询点击排序
        ["range"] = _range_handler,   -- 查询算法排序
    }
    return act_tab[args._get["act"] or ""](args['_get'])
end

-- 入口函数
_M.entry = function()
    return open.response(_route())
end

return _M.entry()

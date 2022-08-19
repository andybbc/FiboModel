local cfg = require('common.config')
local md5 = require('resty.md5')
local str = require('resty.string')

local tinsert = table.insert
local tsort   = table.sort
local sformat = string.format
local ngx_log = ngx.log
local ngx_ERR = ngx.ERR
local ngx_BUG = ngx.DEBUG

local refuse = function ( msg )
    local message = msg or "Failed to auth."

    ngx.status = 403
    ngx.print( message )
    return ngx.exit(ngx.status)
end

local check_params = function ( p )
    if not p.auth or #p.auth == 0 then
        return false, "Params \"auth\" is nessary and not empty."
    end

    if not p.appkey or #p.appkey == 0 then
        return false, "Params \"appkey\" is nessary and not empty."
    end

    if not p.expire or #p.expire == 0 then
        return false, "Params \"expire\" is nessary and valid."
    end

    return true
end

local auth_md5 = function ( p )
    local md5_cli = md5:new()
    if not md5_cli then
        ngx_log(ngx_ERR, 'failed to create md5 object.')
        return false
    end

    local key_list = {}
    for k, _ in pairs(p) do
        if k ~= "auth" then
            tinsert(key_list, k)
        end
    end

    tsort(key_list)

    local s = ""
    for _, k in pairs(key_list) do
        s = s .. p[k]
    end

    local s_tab = {
        [""] = "",
    }
    
    local secret = s_tab[p.appkey] or cfg.auth_secret

    s = sformat("%s%s", s, secret)

    ngx_log(ngx_BUG, "=== MD5 str: ===", s)

    local ok = md5_cli:update(s)
    if not ok then
        ngx_log(ngx_ERR, 'failed to add data.')
        return false
    end

    local encode_str = md5_cli:final()
    encode_str = str.to_hex(encode_str)

    if p.auth == encode_str then
        return true
    else
        ngx_log(ngx_ERR, "=== MD5 encode_str: ===", s, "; ", encode_str)

        return false
    end
end

local auth_expire = function ( t )
    local now = ngx.now()
    t = tonumber(t)

    if (t - now >= -30) and (t - now <= cfg.auth_expire + 30) then
        return true
    else
        ngx_log(ngx_ERR, "=== time: ===", t, "; ", now)
        return false, 'Be expired.'
    end
end

local auth_request = function ( p )
    local ok, err = auth_expire( p.expire )
    if not ok then
        return false, err
    end

    return auth_md5( p )
end

local handle = function ()
    local uri_p = ngx.req.get_uri_args()
    local ok, err = check_params( uri_p )
    if not ok then
        refuse( err )
    end

    -- auth requrest
    local ok, err = auth_request( uri_p )
    if not ok then
        refuse( err )
    end
end

handle()

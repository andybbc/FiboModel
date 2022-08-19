-- local pkcs7  = require("resty.nettle.padding.pkcs7")
-- local des    = require("resty.nettle.des")
-- local upload = require("resty.upload")
local http   = require("resty.http")
local json   = require("cjson")

local config = require("common.config")

local schar       = string.char
local sgsub       = string.gsub
local ssub        = string.sub
local sformat     = string.format
local sbyte       = string.byte
local schar       = string.char
local smatch      = string.match
local tinsert     = table.insert
local tconcat     = table.concat
local os_time     = os.time
local math_floor  = math.floor
local math_random = math.random
local _tonumber   = tonumber
local _type       = type
local ngx_log     = ngx.log
local ngx_ERR     = ngx.ERR
local ngx_BUG     = ngx.DEBUG
local jencode     = json.encode
local jdecode     = json.decode

local _M = {}

-- 返回指定长度的随机字符串
_M.random_str = function(len)
    local t = {}
    for i = 0, len do
        if math_random(1, 3) == 1 then
            -- 大写字符
            t[#t+1] = schar(math_random(0, 26) + 65)
        elseif math_random(1, 3) == 2 then
            -- 小写字符
            t[#t+1] = schar(math_random(0, 26) + 97)
        else
            -- 10 个数字
            t[#t+1] = math_random(0, 10)
        end
    end
    return tconcat(t)
end

_M.diff_day = function (t1, t2)
    if not _tonumber(t1) or not _tonumber(t2) then return end

    return math_floor((t1 - t2) / (24 * 60 * 60))
end

_M.to_timestamp = function(date_str)
    if not date_str or _type(date_str) ~= "string" then return end

    local m = _M.split(date_str, " ")
    if not m and #m == 0 then return end

    local date, time = m[1], m[2]

    local m = _M.split(date, "-")
    if not m and #m == 0 then return end

    local y, m, d = m[1], m[2], m[3]

    local _h, _m, _s
    if time then
        local m = _M.split(time, ":")
        if not m and #m == 0 then return end

        _h, _m, _s = m[1], m[2], m[3]
    end

    return os_time{
        year  = _tonumber(y),
        month = _tonumber(m),
        day   = _tonumber(d),
        hour  = _tonumber(_h),
        min   = _tonumber(_m),
        sec   = _tonumber(_s)
    }
end

_M.tindex = function(t, o)
    if not o or not t or _type(t) ~= "table" then return end

    for index, v in pairs(t) do
        if v == o then
            return index
        end
    end
end

_M.tappend = function(t, o)
    t = t or {}
    t[#t+1] = o
    return t
end

_M.split = function(s, p)
    local rt = {}
    string.gsub(s, '[^' .. p ..']+', function(w) table.insert(rt, w) end )
    return rt
end

_M.strim = function(s)
    s = (string.gsub(s, "^%s*(.-)%s*$", "%1"))
    return (string.gsub(s, "^%s*(.-)%s*$", "%1"))
end

_M.hex2str = function(s)
    return (sgsub(s, "(.)", function(c) return sformat("%02x", sbyte(c)) end))
end

_M.str2hex = function(s)
    local h2b = {
        ["0"] = 0,
        ["1"] = 1,
        ["2"] = 2,
        ["3"] = 3,
        ["4"] = 4,
        ["5"] = 5,
        ["6"] = 6,
        ["7"] = 7,
        ["8"] = 8,
        ["9"] = 9,
        ["a"] = 10,
        ["b"] = 11,
        ["c"] = 12,
        ["d"] = 13,
        ["e"] = 14,
        ["f"] = 15,
        ["A"] = 10,
        ["B"] = 11,
        ["C"] = 12,
        ["D"] = 13,
        ["E"] = 14,
        ["F"] = 15,
    }
    return (sgsub(s, "(.)(.)", function(h, l)
        return schar(h2b[h]*16 + h2b[l])
    end))
end

_M.encrypt_des = function(s)
    local key = ssub(config.des_key, 1, 8)
    local ds, wk = des.new(key, 'ecb')
    return _M.hex2str(ds:encrypt(pkcs7.pad(s)))
end

_M.decrypt_des = function(s)
    local key = ssub(config.des_key, 1, 8)
    local ds, wk = des.new(key, 'ecb')
    return (pkcs7.unpad(ds:decrypt(_M.str2hex(s)), 8))
end

return _M

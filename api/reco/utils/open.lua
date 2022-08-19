local cjson    = require("cjson")
local http     = require("resty.http")
local resolver = require("resty.dns.resolver")

local config   = require("common.config")

local _pcall = pcall
local _type  = type

local jencode = cjson.encode
local jdecode = cjson.decode
local sformat = string.format

local ngx_log           = ngx.log
local ngx_BUG           = ngx.DEBUG
local ngx_ERR           = ngx.ERR
local ngx_re_gsub       = ngx.re.gsub
local ngx_re_find       = ngx.re.find
local ngx_timer_at      = ngx.timer.at
local ngx_read_body     = ngx.req.read_body
local ngx_get_headers   = ngx.req.get_headers
local ngx_get_uri_args  = ngx.req.get_uri_args
local ngx_get_body_data = ngx.req.get_body_data
local ngx_get_post_args = ngx.req.get_post_args

local _M = {}

-- 设置异步任务
_M.async_worker = function(delay, worker, ...)
    if not worker or _type(worker) ~= "function" then
        return nil, "Param \"worker\" is valid"
    end

    delay = delay or 0

    local args = {...}

    ngx_timer_at(delay, function(premature, ...)
        if not premature then
            local rst, err_msg = _pcall(worker, ...)
            if not rst then
                ngx_log(ngx_ERR, "async work:", err_msg)
            end
        end
    end, ...)
end

-- 设置定时任务
_M.timer_worker = function(delay, worker, ...)
    if not worker or _type(worker) ~= "function" then
        return nil, "Param \"worker\" is valid"
    end

    delay = delay or 0

    local timer_work
    timer_work = function(premature, ...)
        if not premature then
            local rst, err_msg = _pcall(worker, ...)
            if not rst then
                ngx_log(ngx_ERR, "timer work:", err_msg)
            end
            ngx_timer_at(delay, timer_work, ...)
        end
    end

    ngx_timer_at(delay, timer_work, ...)
end

-- 保持长连接
local _httpc_keepalive = function(httpc, err)
    if err then
        httpc:close()
    end
    local _, err1 = httpc:get_reused_times()
    if err1 then
        httpc:close()
    end
    -- 1分钟
    -- 1*60*1000
    httpc:set_keepalive(60000, 10000)
end

-- 动态DNS解析
local get_domain_ip_by_dns = function(domain)
    local r, err = resolver:new{
            nameservers = config.dns_nameservers or {'114.114.114.114'},
            retrans = 5,     -- 5 retransmissions on receive timeout
            timeout = 2000,  -- 2 sec
        }
    if not r then
        return nil, "failed to instantiate the resolver: " .. err
    end

    local answers, err = r:query(domain)
    if not answers then
        return nil, "failed to query the DNS server: " .. err
    end

    if answers.errcode then
        return nil, "server returned error code: " .. answers.errcode .. ": " .. answers.errstr
    end

    for i, ans in ipairs(answers) do
      if ans.address then
        return ans.address
      end
    end

    return nil, "not founded"
end

-- 异步 HTTP GET 请求
_M.http_get = function(_url, _header, _timeout, dns_resolver)
    local httpc = http.new()

    -- 设置超时
    httpc:set_timeout(_timeout or 2000)

    local ssl_verify = nil
    if _url:sub(1,5) == 'https' then
        ssl_verify = false
    end

    if dns_resolver then
        -- 获取域名
        local domain = ngx.re.match(url, [[//([\S]+?)/]])
        domain = (domain and 1 == #domain and domain[1]) or nil
        if not domain then
            ngx.log(ngx.ERR, "get the domain fail from url:", url)
        end

        -- 添加 Host 请求头
        if not headers then
            headers = {}
        end
        headers.Host = domain

        -- 解析
        local domain_ip, err = get_domain_ip_by_dns(domain)
        if not domain_ip then
            ngx.log(ngx.ERR, "get the domain[", domain ,"] ip by dns failed:", err)
        end

        url = ngx_re_gsub(url, "//"..domain.."/", sformat("//%s/", domain_ip))
    end

    local res, err = httpc:request_uri(_url, {
        method     = 'GET',
        headers    = _headers,
        ssl_verify = ssl_verify,
    })

    _httpc_keepalive(httpc, err)

    return res, err
end

-- 异步 HTTP POST 请求
function _M.http_post(url, headers, body, timeout, dns_resolver)
    local httpc = http.new()

    -- 设置超时
    httpc:set_timeout(timeout or 2000)

    local ssl_verify = nil
    if url:sub(1,5) == 'https' then
        ssl_verify = false
    end

    if dns_resolver then
        -- 获取域名
        local domain = ngx.re.match(url, [[//([\S]+?)/]])
        domain = (domain and 1 == #domain and domain[1]) or nil
        if not domain then
            ngx.log(ngx.ERR, "get the domain fail from url:", url)
        end

        -- 添加 Host 请求头
        if not headers then
            headers = {}
        end
        headers.Host = domain

        -- 解析
        local domain_ip, err = get_domain_ip_by_dns(domain)
        if not domain_ip then
            ngx.log(ngx.ERR, "get the domain[", domain ,"] ip by dns failed:", err)
        end

        url = ngx_re_gsub(url, "//"..domain.."/", sformat("//%s/", domain_ip))
    end

    local res, err = httpc:request_uri(url, {
        method = 'POST',
        body = body,
        headers = headers,
        ssl_verify = ssl_verify,
    })

    _httpc_keepalive(httpc, err)

    return res, err
end

-- 接收输入文件
_M.readfile = function()
    local chunk_size = 4096
    local form, err = upload:new(chunk_size)
    form:set_timeout(20000)
    local file = {}
    if not err then
        local key
        while true do
            local typ, res, err2 = form:read()
            if not typ then
                err = err2
                break
            end
            if typ == 'header' and res[1] == 'Content-Disposition' then
                local filename = smatch(res[2], 'filename="(.*)"')
                if filename then
                    file.name = filename
                end

                key = smatch(res[2], 'form%-data;% name="(%a*)"')
                if key == "file" then key = "body" end
            end
            if typ == 'header' and res[1] == 'Content-Type' then
                file['type'] = res[2]
            end
            if typ == 'body' and file then
                file[key] = (file[key] or '') .. res
            end
            if typ == "eof" then
                break
            end
        end
    end
    return file, err
end

-- 获取请求参数
_M.get_args = function()
    local ret = {
        _get  = nil,
        _post = nil,
    }
    -- URI 参数
    ret._get = ngx_get_uri_args()

    -- POST
    ngx_read_body()
    local c_type = ngx_get_headers()["content-type"]
    if ngx_re_find(c_type, "application/json", "jo") then
        local body = ngx_get_body_data()
        if body then
            local ok, _body = _pcall(jdecode, body)
            if ok then
                ret._post = _body
            else
                ngx_log(ngx_ERR, "=== ERROR: ", _body, "; encode-str: ", body)
            end
        end
    end
    if not ret._post then
        ret._post = ngx_get_post_args()
    end

    return ret
end

-- 响应函数
_M.response = function(code, msg, data, count)
    ngx.header['Content-Type'] = 'application/json; charset=utf-8'
    local content = jencode{
        code    = code,
        message = msg,
        data    = data,
        count   = count,
    }
    ngx.header['Content-Length'] = #(content or '')
    ngx.print(content)
    ngx.exit(200)
end

return _M

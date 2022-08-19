local mysql     = require('resty.mysql')
local config    = require('common.config')

local mysql_cfg = config.mysql_cfg

local ngx_log   = ngx.log
local ngx_ERR   = ngx.ERR
local ngx_BUG   = ngx.DEBUG
local tinsert   = table.insert
local tconcat   = table.concat

local _mysql_init = function ()
    local db, err = mysql:new()
    if not db then
        ngx_log(ngx_ERR, 'Failed to instantiate mysql: ', err)
        return
    end

    local ok, err, errcode, sqlstate = db:connect{
        host             = mysql_cfg.ip,
        port             = mysql_cfg.port or 3306,
        database         = mysql_cfg.database,
        user             = mysql_cfg.user,
        password         = mysql_cfg.password,
        charset          = mysql_cfg.charset or 'utf8',
        max_package_size = mysql_cfg.max_package_size or 1024 * 1024,
    }
    if not ok then
        ngx_log(ngx_ERR, 'Failed to connect: ', err, ': ', errcode, ': ', sqlstate)
        return
    end

    return db
end

local _mysql_query = function (sql, transcation)
    local mysql_cli = _mysql_init()
    if not mysql_cli then
        return
    end

    if transcation then
        local res, err, errcode, sqlstate = mysql_cli:query("BEGIN")
        if not res then
            ngx_log(ngx_ERR, 'Bad result #1: ', err, ': ', errcode, ': ', sqlstate)
            return nil, 'Query BEGIN error.'
        end
    end

    local s = #sql == 1 and sql[1] or tconcat(sql, " ")
    ngx_log(ngx_BUG, "=== SQL: ", s)

    local ret = {}
    local res, err, errcode, sqlstate = mysql_cli:query(s)
    if not res then
        ngx_log(ngx_ERR, 'Bad result #1: ', err, ': ', errcode, ': ', sqlstate, "; SQL: ", s)

        if transcation then
            local res, err, errcode, sqlstate = mysql_cli:query("ROLLBACK")
            if not res then
                ngx_log(ngx_ERR, 'Bad result #1: ', err, ': ', errcode, ': ', sqlstate)
                return nil, 'Query ROLLBACK error.'
            end
        end

        return nil, 'Query error.'
    else
        if #sql == 1 then
            if transcation then
                local res, err, errcode, sqlstate = mysql_cli:query("COMMIT")
                if not res then
                    ngx_log(ngx_ERR, 'Bad result #1: ', err, ': ', errcode, ': ', sqlstate)
                    return nil, 'Query COMMIT error.'
                end
            end

            mysql_cli:set_keepalive(10000, 50)
            return res
        end

        tinsert(ret, res)
    end

    local i = 2
    while err == 'again' do
        res, err, errcode, sqlstate = mysql_cli:read_result()
        if not res then
            ngx_log(ngx_ERR, 'Bad result #', i, ': ', err, ': ', errcode, ': ', sqlstate)

            if transcation then
                local res, err, errcode, sqlstate = mysql_cli:query("ROLLBACK")
                if not res then
                    ngx_log(ngx_ERR, 'Bad result #1: ', err, ': ', errcode, ': ', sqlstate)
                    return nil, 'Query ROLLBACK error.'
                end
            end

            return nil, 'Query error.'
        end

        if i >= 2 then
            tinsert(ret, res)
        end

        i = i + 1
    end

    if transcation then
        local res, err, errcode, sqlstate = mysql_cli:query("COMMIT")
        if not res then
            ngx_log(ngx_ERR, 'Bad result #1: ', err, ': ', errcode, ': ', sqlstate)
            return nil, 'Query COMMIT error.'
        end
    end

    mysql_cli:set_keepalive(10000, 50)
    return ret
end

local _M = {
    init  = _mysql_init,
    query = _mysql_query,
}

return _M

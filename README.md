### 目录结构   
- ├── bin 运行脚本   
- ├── data 数据，中间数据   
- ├── conf 配置文件   
- ├── src 源码   
- ├── ├── generate    数据生成   
- ├── ├── dataset    数据类   
- ├── ├── preprocess       数据处理   
- ├── ├── model   算法类   
- ├── ├── train    训练类   
- ├── ├── predict 预测类   
- ├── ├── evaluate    评估   
- ├── ├── combine    数据合并   
- ├── ├── utils   工具函数   
- ├── ├── task   任务类   
- ├── ├── tests   测试类   
   
   
---    
### xgboost ctr预估(rtb项目)   
#### 1.原始日志说明
[日志格式](docs/log_format.xlsx)
> 说明: 标黄的部分,301日志是曝光日志,302日志是点击日志   
> 需要训练的原始文件通过两个日志的reqid(第3个字段)关联,在曝光日志中出现点击日志标记为1(点击),否则为0(未点击)

#### 2.确定全部可用特征字段
根据观察和上游业务说明,选取如下特征字段和对应的是否点击字段   

|序号 |  字段   |类型| 说明  | 
|  ----  | ----  | --- | --- |
|0|是否点击|int|1:点击 0:未点击|
|1| androidid类型 |int| 为空:[0],不为空且不为32位:[1],不为空为32位:[2] |
|2| imei 类型  |int| 为空/000000000000000:[0],md5型的:[2],其他:[1] |
|3| mac 类型 |int|为空/00:00:00:00:00:00/02:00:00:00:00:00:[0],md5型的:[2],其他:[1] |  
|4| oaid 类型|int|为空/00000000-0000-0000-0000-000000000000:[0] 不为空:[1]|
|5| 经度 类型|int|为空:[0] 不为空:[1]|
|6|媒体编号|int|序号5,为空用[-1]代替|
|7|广告位id|int|序号6,为空用[-1]代替|
|8|地域|int|序号21,为空用[-1]代替|
|9|运营商|int|序号23,为空用[-1]代替|
|10|网络连接类型|int|序号24,为空用[-1]代替|
|11|时间段|int|按小时的时间段0-23,(20210129新增)|
|12|制造商|string|序号25,为空用'unknown'代替|
|13|brand|string|序号25,预处理后的品牌,未知用'unknown'代替|
|14|手机型号|string|序号32,为空用'unknown'代替 |
|15|手机型号(前1000次数最多的)|string|序号32,为空用'unknown'代替| 
|16|系统版本|string |序号33,为空用'unknown'代替|
|17|包名|string|序号29,为空用'unknown'代替|
|18|包名(前1000次数最多的)|string|序号29,为空用'unknown'代替|
|19|广告位类型| string|序号40,为空用'unknow'代替|
|20|广告位形状| string|序号42,43,如果都不为空,则concat(42,'_',43),否则'unknown'|
|21|制造商2|string|序号25,小写,取空格前,为空用'unknown'代替|

> 说明:
> 生成的文件列分成3种 第一列(点击1/未点击0)字段,中间部分为数值型的字段,可以直接参数训练和预测的,最后几列为string型的,方便preprocess转换为int型
> 文件不带表头

- 特征组   

|名称|列属性组合|
|  ----  | ----  |
|用户|[]|
|手机|[1, 2, 3, 4, 9, 10, 12, 13, 14]|
|媒体|[6, 15]|
|广告|[7]|
|上下文|[5, 8, 11]|

#### 3.配置文件说明
配置`conf/rtb/rtb.py`下的文件
1. `preprocess`文件预处理配置
    1. select_cols
       原始文件按自定义拆分特征,进行训练***按照如上的字段序号,第1列必选(0列)***.   
       如果不填或者只填[0],则原样输出所有字段   
       要按照从小到大的顺序      
       因为预测文件比训练少了最前面的label列,配置不动的情况下,待预测文件处理默认第一列为下标为1,所以只要符合这个文件格式,配置文件不需要修改,训练/预测都按照相同的规则拆分
    2. need_label_encode_cols_num    
       根据配置`select_cols`自定义选取的列生成文件的实际情况,最后有多少列需要数值化的string字段个数就填多少    
    3. dev    
       `True`:是否是开发环境(主要针对训练,主要区别是是否会根据label_encode后的文件进行拆分,成为`train`,`test`,`vali`3个文件,xgboost训练的时候指定auc参数)   
       `False`:不会拆分文件,并且训练的时候不会有auc
    4. file_separator   
       文件分隔符
    5. use_model_type  
        有`xgboost`/`xgboost_lr`两种方式    
        `xgboost`直接按照 xgboost来训练和预测结果,比较快   
        `xgboost_lr`是先通过xgboost训练完成的中间结果后再进行`LR`训练           
    
2.`model`训练参数
    完全根据 xgb.XGBClassifier(xxx) 中需要的参数,提取到conf中的

3. `xgb_fit_params`
    xgb_model.fit(xxx)的参数 

#### 4.脚本说明
`src/rtb`目录下的脚本   
- `preprocess_split_train.py`/`preprocess_split_predict`   
    最原始的特征文件,根据配置文件中的select_cols指定选择的列,供下游训练/预测
- `preprocess_train`/`preprocess_predict`
    将待预测的文件的一些string字段转换为数值,label_encode
    train:生成映射关系,生成输入模型文件
    predict:使用映射关系,生成输入模型文件
    
- `train_`
    训练文件,生成预测所需要文件
    - 只是xgboost方式:生成xgb_model.pkl模型文件,供预测使用
    - xgboost+lr方式:生成xgb_model.pkl,one_hot_encode中间文件,lr_model.pkl文件
    
- `predict_`
    除了从最原始文件预处理需要的label_encode文件,还需要如下训练后的文件       
    - 使用xgboost:   
       使用xgb_model.pkl文件
    - 使用xgboost+lr
       使用xgb_model.pkl文件,one_hot_encode中间文件,lr_model.pkl文件

- 其他
    - 为了方便观察label_encode的映射关系,现将映射关系输出到json
    - 一套流程
     preprocess_split_train -> preprocess_train -> train_   
     preprocess_split_predict -> preprocess_predict -> predict
     
> 具体实现内容看`scripts/rtb.sh`
> 现已将脚本放到算法服务器`/data/algorithm/algorithm6/`,可以直接执行观察结果


brand 特征通过制造商预处理逻辑:
```java

 public String evaluate(String producer) {
        if (producer == null) {
            return "unknown";
        }
        String originStr = producer.trim().toLowerCase();
        if (originStr.matches(".*huawei.*|.*-a[a-z]]\\d{2,3}|.*-tl\\d{2,3}|.*-tn\\d{2,3}|dig.*|pic.*|jer.*|sne.*|pra.*|ldn.*|are|fig.*|knt.*|ars.*|jny.*|rne.*|aqm.*|tah.*|art.*|spn.*|clt.*|jef.*|bac.*|ane.*|tas.*|lio.*|fla.*|lya.*|vog.*|pct.*||alp.*|pot.*|eml.*|mha.*|bla.*|sea.*|cdy.*|evr.*|els.*|eva.*|jsn.*|ele.*|par.*|bkl.*|pct.*|jkm.*|vtr.*|sea.*|ana.*|hma.*|vec.*|vky.*|wlz.*|hwi.*|was.*|stf.*|spn.*|ine.*|bnd.*|mar.*|vie.*|dub.*|lld.*|lon.*|glk.*|bln.*|duk.*|trt.*|vog*")) {
            return "huawei";
        } else if (originStr.matches("apple|.*iphone.*|ipad.*")) {
            return "apple";
        } else if (originStr.matches(".*oppo.*|p[a-z]{2,4}\\d{2,4}|r\\d[a-z].*")) {
            return "oppo";
        } else if (originStr.matches(".*vivo.*|v\\d{2,4}[a-z]{1,3}")) {
            return "vivo";
        } else if (originStr.matches(".*honor.*|yal.*|col.*|hlk.*|hry.*|bmh.*|oxf.*|ebg.*|tny.*|frd.*|cor.*|rvl.*|bkk.*|lra.*|jmm.*")) {
            return "honor";
        } else if (originStr.matches(".*xiaomi.*|^mi .*|mi\\d*.*|^mix .*|.*blackshark.*")) {
            return "xiaomi";
        } else if (originStr.matches("meizu|m\\d+ .*|16th.*|pro.*")) {
            return "meizu";
        } else if (originStr.matches("samsung.*|sm|sm-.*")) {
            return "samsung";
        } else if (originStr.matches(".*redmi.*")) {
            return "redmi";
        } else if (originStr.matches(".*oneplus.*|gm\\d+")) {
            return "oneplus";
        } else if (originStr.matches("gionee.*")) {
            return "gionee";
        } else if (originStr.matches("360.*")) {
            return "360";
        } else if (originStr.matches("meitu.*")) {
            return "meitu";
        } else if (originStr.matches("smartisan.*|os\\d+")) {
            return "smartisan";
        } else if (originStr.matches("nubia.*")) {
            return "nubia";
        } else if (originStr.matches(".*leeco.*|.*letv.*|.*lemobile.*|")) {
            return "leeco"; //乐视
        } else if (originStr.matches(".*lenovo.*")) {
            return "lenovo";
        } else if (originStr.matches("hisense.*")) {
            return "hisense";
        } else if (originStr.matches("zte.*")) {
            return "zte";
        } else if (originStr.matches("nokia.*")) {
            return "nokia";
        } else if (originStr.matches(".*coolpad.*")) {
            return "coolpad";
        } else if (originStr.matches("realme.*")) {
            return "realme";
        } else if (originStr.matches("motorola.*")) {
            return "motorola";
        } else if (originStr.matches("koobee.*")) {
            return "koobee";
        } else if (originStr.matches("sony.*")) {
            return "sony";
        } else if (originStr.matches("doov.*")) {
            return "doov";
        } else {
            return "unknown";
        }

    }

```
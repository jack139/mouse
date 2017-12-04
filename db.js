user  后台用户表：系统管理员(admin)、课题组管理员、实验员、老师

group 课题组
{
    name : 组名
    grp_id : 组id
    status : 状态： 1 正常 0 停用
}

house 鼠笼：只存储使用过的鼠笼，没用过的鼠笼不记录数据
{
    house_id : 鼠笼id
    pos : 鼠笼位置， 格式： 区|房|架|排|列
    type :  鼠笼类型： 繁殖／实验／使用
    grp_id : 所属课题组id
    uid : 实验员id
}

mouse 小鼠：数据只增不删，保留历史数据
{
    mouse_id : 小鼠id
    tag : 耳标
    sex : 性别
    status : 状态 ：新生／正常／杀死／死亡
    birth_d : 出生日期 yyyymmdd
    divide_d : 分笼日期 yyyymmdd
    death_d : 死亡日期 yyyymmdd
    father_id : 父小鼠id
    mother_id : 母小鼠id
    blood_id : 品系id
    house_id : 当前所在笼id
    test_record : [], 实验记录
    house_history : [], 居住鼠笼记录，记录鼠笼位置信息
    grp_id : 所属课题组id
    uid : 实验员id
}

bloodline 小鼠品系
{
    blood_id : 品系id
    name : 品系名称
    status : 状态 ： 准备中／计划中／已有
    owner_uid : 建立的课题组管理员id
    status_history : [], 状态变更记录
}

/* -------------- Indexes ---------------*/

/* 后台建索引 db.collection.createIndex( { a: 1 }, { background: true } ) */

db.sessions.createIndex({session_id:1},{ background: true })
db.sessions.createIndex({attime:1},{ background: true })

db.user.createIndex({privilege:1},{ background: true })
db.user.createIndex({uname:1},{ background: true })
db.user.createIndex({login:1, privilege:1},{ background: true })


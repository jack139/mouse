user  后台用户表：系统管理员(admin)、课题组管理员、实验员、老师
{
    uname
    passwd
    user_type : grp_user, grp_admin, tutor
    group_list : 所属课题组，tutor可以有多个值，grp_admin和grp_user只能有一个
}

groups 课题组
{
    name : 组名
    group_id : 组id
    status : 状态： 1 正常 0 停用
    note : 备注
    last_tick: 最后修改时间
}

shelf 笼架管理
{
    shelf_id : 笼架id，格式： 区-房-架
    row : 行数
    col : 列数
    group_id : 所属课题组id, 应该确认无在使用的鼠笼时才能修改所属课题组
    expired_d : 到期日期， yyyymm
    history : [], 课题组使用记录
    last_tick: 最后修改时间
    
}

house 鼠笼：只存储使用过的鼠笼，没用过的鼠笼不记录数据
{
    house_id : 鼠笼id，格式： 区-房-架-排-列
    shelf_id : 笼架id，格式： 区-房-架
    status : 鼠笼状态：0 停用 1 在使用
    type :  鼠笼类型： 繁殖／实验／使用
    type_list :  鼠笼可用类型： 繁殖／实验／使用（管理员修改）
    group_id : 所属课题组id，应该确认没有小鼠时才能修改所属课题组
    uname : 实验员id
    expired_d : 到期日期， yyyymm
    history : [], 使用记录
    last_tick: 最后修改时间

    create_d : 创立日期
    test_start_d : 实验开始日期
    test_will_end_d : 实验预计完成日期
    test_end_d : 实验实际完成日期
}

mouse 小鼠：数据只增不删，保留历史数据
{
    _id : 小鼠id
    tag : 耳标, 新生小鼠可能没有耳标值
    sex : 性别 F M 
    status : 状态 ：新生／正常／杀死／死亡
    birth_d : 出生日期 yyyymmdd
    divide_d : 分笼日期 yyyymmdd
    death_d : 死亡日期 yyyymmdd
    father_tag : 父小鼠耳标
    mother_tag : 母小鼠耳标
    blood_code : 品系id
    house_id : 当前所在笼id
    test_record : [], 实验记录
    house_history : [], 居住鼠笼记录，记录鼠笼位置信息
    group_id : 所属课题组id
    owner_uname : 实验员id
    last_tick: 最后修改时间
    gene_code : 基因型结果
}

bloodline 小鼠品系
{
    blood_code : 品系id，人工输入
    name : 品系名称
    status : 状态 ： 准备中／计划中／已有
    owner_uname : 建立的课题组管理员id
    status_history : [], 状态变更记录
    last_tick : 最后修改时间
    user_list : 可使用的用户
    group_id : 所属课题组id
}


credit 信用评分
{
    uname : 用户uname
    group_id : 所属课题组id
    credit : 此次信用分记录
    comment : 此次信用分说明
    date_t : 评分时间
}

/* -------------- Indexes ---------------*/

/* 后台建索引 db.collection.createIndex( { a: 1 }, { background: true } ) */

db.sessions.createIndex({session_id:1},{ background: true })
db.sessions.createIndex({attime:1},{ background: true })

db.user.createIndex({privilege:1},{ background: true })
db.user.createIndex({uname:1},{ background: true })
db.user.createIndex({login:1, privilege:1},{ background: true })


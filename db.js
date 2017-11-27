user  后台用户表：系统用户(admin)、平谷用户、商家用户


/* -------------- Indexes ---------------*/

/* 后台建索引 db.collection.createIndex( { a: 1 }, { background: true } ) */

db.sessions.createIndex({session_id:1},{ background: true })
db.sessions.createIndex({attime:1},{ background: true })

db.user.createIndex({privilege:1},{ background: true })
db.user.createIndex({uname:1},{ background: true })
db.user.createIndex({login:1, privilege:1},{ background: true })


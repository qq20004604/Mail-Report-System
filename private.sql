-- 创建 database
create schema if not exists report_db collate utf8mb4_general_ci;

-- 执行这行语句的时候，用root账号执行。意思是创建一个用户，允许他在任何ip访问 qq_robot这个数据库，密码是后面BY里面的
GRANT ALL ON report_db.* to report_admin@'%' IDENTIFIED BY '123456';
FLUSH PRIVILEGES;
## 说明

使用 virtualenv 模式，简单来说，就是用一个应用创建一套“隔离”的Python运行环境。所以这个 Python 环境里的依赖应该是干干净净（几乎啥都没有）。

我这里安装的 Django 是版本是 3.0.5

安装 Django

```
python -m pip install Django
```

生成应用

```
django-admin startproject Server
```

运行服务器（默认8000端口）

```
python manage.py runserver
```

创建应用

```
python manage.py startapp user
```

将模型文件 verify_code 的修改，生成一次迁移（简单来理解，就是将 verify_code.model 更改后，生成一个文件。之后，我们将会执行这个文件，并将变更应用到数据库里）。

这个意义在于，在开发过程中持续的改变数据库结构而不需要重新删除和创建表。（相当于只需要update就行了）

```
python manage.py makemigrations msg
```

将上面那一个模型的修改，在数据里创建对应的表

```
python manage.py migrate
```

创建管理员账号（然后输入账号、邮箱、密码）

```
python manage.py createsuperuser
```

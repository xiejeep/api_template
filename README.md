# 后端服务 API 文档

本文档详细说明了后端服务的架构、功能和API接口。

## 技术栈

- **框架**: Django 5.2, Django REST Framework
- **数据库**: SQLite (开发环境), 可迁移至PostgreSQL (生产环境)
- **认证**: JWT (JSON Web Token)
- **API文档**: Swagger UI, ReDoc, 本README文件

## 项目结构

```
backend/
├── accounts/            # 用户账户相关应用
│   ├── migrations/      # 数据库迁移文件
│   ├── admin.py         # 管理界面配置
│   ├── models.py        # 用户和验证码模型
│   ├── serializers.py   # 序列化器
│   ├── sms.py           # 短信服务
│   ├── urls.py          # URL路由
│   ├── views.py         # API视图
│   └── wechat.py        # 微信登录服务
├── api/                 # 业务API应用
│   ├── migrations/      # 数据库迁移文件
│   ├── admin.py         # 管理界面配置
│   ├── models.py        # 业务模型
│   ├── serializers.py   # 序列化器
│   ├── urls.py          # URL路由
│   └── views.py         # API视图
├── backend/             # 项目主应用
│   ├── exception_handler.py  # 自定义异常处理
│   ├── settings.py      # 项目设置
│   ├── urls.py          # 主URL路由
│   ├── utils.py         # 工具函数
│   └── wsgi.py          # WSGI配置
├── .env                 # 环境变量配置
├── db.sqlite3           # SQLite数据库
├── manage.py            # Django管理脚本
└── README.md            # 本文档
```

## 功能特性

1. **用户认证**
   - 手机号+密码登录
   - 手机号+验证码登录
   - 微信登录
   - 微信小程序登录
   - JWT认证，支持令牌刷新

2. **短信验证码**
   - 支持注册、登录、重置密码场景
   - 开发环境使用固定验证码(123456)
   - 预留第三方短信服务接入点

3. **统一API响应格式**
   - 统一的错误码和错误消息
   - 标准的数据结构
   - 分页信息

4. **数据库**
   - 默认使用SQLite
   - 支持无缝迁移至PostgreSQL

## 环境变量配置

项目使用`.env`文件管理环境变量，主要配置项如下：

```
# 数据库设置
DATABASE_URL=sqlite:///db.sqlite3
# 如果要切换到PostgreSQL，取消下面这行的注释并修改为你的PostgreSQL连接信息
# DATABASE_URL=postgres://user:password@localhost:5432/dbname

# 调试模式
DEBUG=True

# 密钥（生产环境中应该更改）
SECRET_KEY=your-secret-key

# 允许的主机
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS设置
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# 微信登录设置
# 注意: 微信网页登录和微信小程序登录共用同一套配置
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret
WECHAT_REDIRECT_URI=https://your-domain.com/api/auth/wechat/callback
```

## API文档

本项目提供了三种API文档查看方式：

1. **Swagger UI**: 交互式文档，可以直接在浏览器中测试API
   - 访问地址：`/swagger/`

2. **ReDoc**: 更清晰的文档展示方式，适合阅读
   - 访问地址：`/redoc/`

3. **JSON/YAML格式**: 可以导出为OpenAPI规范的JSON或YAML文件
   - 访问地址：`/swagger.json`或`/swagger.yaml`

## API接口

### 统一响应格式

所有API响应都遵循以下格式：

```json
{
  "code": 0,           // 错误码，0表示成功，非0表示错误
  "message": "成功",    // 错误消息或成功提示
  "data": { ... },     // 实际数据，可以是对象、数组或null
  "pagination": {      // 分页信息，如果不是分页请求则为null
    "page": 1,         // 当前页码
    "page_size": 10,   // 每页数量
    "total_pages": 5,  // 总页数
    "total_items": 42  // 总条数
  }
}
```

### 错误码定义

- `0`: 成功
- `1000`: 未知错误
- `1001`: 认证失败
- `1002`: 未认证
- `1003`: 权限不足
- `1004`: 资源不存在
- `1005`: 方法不允许
- `1006`: 验证错误
- `1007`: 请求频率超限
- `1008`: 数据完整性错误
- `2001`: 验证码发送失败
- `9999`: 服务器错误

### 认证相关接口

#### 注册

- **URL**: `/api/auth/register/`
- **方法**: POST
- **请求体**:
  ```json
  {
    "phone": "+8613800138000",
    "code": "123456",
    "password": "password123",
    "username": "user123"  // 可选
  }
  ```
- **响应**:
  ```json
  {
    "code": 0,
    "message": "注册成功",
    "data": {
      "user": {
        "id": 1,
        "username": "user123",
        "phone": "+8613800138000",
        "email": null,
        "is_phone_verified": true,
        "date_joined": "2025-04-18T12:00:00Z"
      }
    },
    "pagination": null
  }
  ```

#### 手机号+密码登录

- **URL**: `/api/auth/login/phone-password/`
- **方法**: POST
- **请求体**:
  ```json
  {
    "phone": "+8613800138000",
    "password": "password123"
  }
  ```
- **响应**:
  ```json
  {
    "code": 0,
    "message": "登录成功",
    "data": {
      "user": {
        "id": 1,
        "username": "user123",
        "phone": "+8613800138000",
        "email": null,
        "is_phone_verified": true,
        "date_joined": "2025-04-18T12:00:00Z"
      },
      "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    },
    "pagination": null
  }
  ```

#### 手机号+验证码登录

- **URL**: `/api/auth/login/phone-code/`
- **方法**: POST
- **请求体**:
  ```json
  {
    "phone": "+8613800138000",
    "code": "123456"
  }
  ```
- **响应**:
  ```json
  {
    "code": 0,
    "message": "登录成功",
    "data": {
      "user": {
        "id": 1,
        "username": "user123",
        "phone": "+8613800138000",
        "email": null,
        "is_phone_verified": true,
        "date_joined": "2025-04-18T12:00:00Z"
      },
      "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "is_new_user": false
    },
    "pagination": null
  }
  ```

#### 发送验证码

- **URL**: `/api/auth/send-code/`
- **方法**: POST
- **请求体**:
  ```json
  {
    "phone": "+8613800138000",
    "purpose": "register"  // 可选值: "register", "login", "reset_password"
  }
  ```
- **响应**:
  ```json
  {
    "code": 0,
    "message": "验证码发送成功",
    "data": {
      "expires_at": "2025-04-18T12:10:00Z"
    },
    "pagination": null
  }
  ```

#### 刷新令牌

- **URL**: `/api/auth/token/refresh/`
- **方法**: POST
- **请求体**:
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **响应**:
  ```json
  {
    "code": 0,
    "message": "成功",
    "data": {
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    },
    "pagination": null
  }
  ```

#### 获取用户信息

- **URL**: `/api/auth/profile/`
- **方法**: GET
- **请求头**: `Authorization: Bearer <access_token>`
- **响应**:
  ```json
  {
    "code": 0,
    "message": "获取用户信息成功",
    "data": {
      "user": {
        "id": 1,
        "username": "user123",
        "phone": "+8613800138000",
        "email": null,
        "is_phone_verified": true,
        "date_joined": "2025-04-18T12:00:00Z"
      }
    },
    "pagination": null
  }
  ```

#### 更新用户信息

- **URL**: `/api/auth/profile/`
- **方法**: PATCH
- **请求头**: `Authorization: Bearer <access_token>`
- **请求体**:
  ```json
  {
    "username": "new_username",
    "email": "user@example.com"
  }
  ```
- **响应**:
  ```json
  {
    "code": 0,
    "message": "更新用户信息成功",
    "data": {
      "user": {
        "id": 1,
        "username": "new_username",
        "phone": "+8613800138000",
        "email": "user@example.com",
        "is_phone_verified": true,
        "date_joined": "2025-04-18T12:00:00Z"
      }
    },
    "pagination": null
  }
  ```

#### 获取微信登录URL

- **URL**: `/api/auth/wechat/login-url/`
- **方法**: POST
- **请求体**:
  ```json
  {
    "redirect_url": "http://localhost:3000/auth/callback"
  }
  ```
- **响应**:
  ```json
  {
    "code": 0,
    "message": "获取微信登录URL成功",
    "data": {
      "login_url": "https://open.weixin.qq.com/connect/qrconnect?appid=wx123456789&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fauth%2Fwechat%2Fcallback&response_type=code&scope=snsapi_login&state=abcdef123456#wechat_redirect",
      "state": "abcdef123456"
    },
    "pagination": null
  }
  ```

#### 微信小程序登录

- **URL**: `/api/auth/wechat/mini-login/`
- **方法**: POST
- **请求体**:
  ```json
  {
    "code": "023HG9Ga1SQEKc0QSNGa1Hgpvc3HG9GR"
  }
  ```
- **响应**:
  ```json
  {
    "code": 0,
    "message": "微信小程序登录成功",
    "data": {
      "user": {
        "id": 1,
        "username": "微信用户_12345678",
        "phone": null,
        "email": null,
        "is_phone_verified": false,
        "date_joined": "2023-08-01T12:00:00Z",
        "wechat_nickname": null,
        "wechat_avatar": null
      },
      "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "is_new_user": true,
      "needs_phone_binding": true
    },
    "pagination": null
  }
  ```

### 任务相关接口

#### 获取任务列表

- **URL**: `/api/tasks/`
- **方法**: GET
- **查询参数**:
  - `page`: 页码，默认为1
  - `page_size`: 每页数量，默认为10
- **响应**:
  ```json
  {
    "code": 0,
    "message": "获取任务列表成功",
    "data": {
      "tasks": [
        {
          "id": 1,
          "title": "测试任务",
          "description": "这是一个测试任务",
          "status": "pending",
          "created_at": "2025-04-18T12:00:00Z",
          "updated_at": "2025-04-18T12:00:00Z"
        }
      ]
    },
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_pages": 1,
      "total_items": 1
    }
  }
  ```

#### 获取任务详情

- **URL**: `/api/tasks/{id}/`
- **方法**: GET
- **响应**:
  ```json
  {
    "code": 0,
    "message": "获取任务详情成功",
    "data": {
      "task": {
        "id": 1,
        "title": "测试任务",
        "description": "这是一个测试任务",
        "status": "pending",
        "created_at": "2025-04-18T12:00:00Z",
        "updated_at": "2025-04-18T12:00:00Z"
      }
    },
    "pagination": null
  }
  ```

#### 创建任务

- **URL**: `/api/tasks/`
- **方法**: POST
- **请求体**:
  ```json
  {
    "title": "新任务",
    "description": "这是一个新任务",
    "status": "pending"
  }
  ```
- **响应**:
  ```json
  {
    "code": 0,
    "message": "创建任务成功",
    "data": {
      "task": {
        "id": 2,
        "title": "新任务",
        "description": "这是一个新任务",
        "status": "pending",
        "created_at": "2025-04-18T13:00:00Z",
        "updated_at": "2025-04-18T13:00:00Z"
      }
    },
    "pagination": null
  }
  ```

#### 更新任务

- **URL**: `/api/tasks/{id}/`
- **方法**: PUT/PATCH
- **请求头**: `Authorization: Bearer <access_token>`
- **请求体**:
  ```json
  {
    "status": "completed"
  }
  ```
- **响应**:
  ```json
  {
    "code": 0,
    "message": "更新任务成功",
    "data": {
      "task": {
        "id": 1,
        "title": "测试任务",
        "description": "这是一个测试任务",
        "status": "completed",
        "created_at": "2025-04-18T12:00:00Z",
        "updated_at": "2025-04-18T13:30:00Z"
      }
    },
    "pagination": null
  }
  ```

#### 删除任务

- **URL**: `/api/tasks/{id}/`
- **方法**: DELETE
- **请求头**: `Authorization: Bearer <access_token>`
- **响应**:
  ```json
  {
    "code": 0,
    "message": "删除任务成功",
    "data": null,
    "pagination": null
  }
  ```

## 开发指南

### 安装依赖

主要依赖包包括：

```
django==5.2
djangorestframework==3.16.0
django-environ==0.11.2
django-cors-headers==4.3.1
djangorestframework-simplejwt==5.3.1
psycopg2-binary==2.9.9
phonenumbers==8.13.32
drf-yasg==1.21.10
```

安装所有依赖：

```bash
pip install -r requirements.txt
```

### 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 创建超级用户

```bash
python manage.py createsuperuser
```

### 运行开发服务器

```bash
python manage.py runserver
```

### 切换到PostgreSQL

1. 安装PostgreSQL数据库
2. 创建数据库和用户
3. 修改`.env`文件中的`DATABASE_URL`
4. 运行数据库迁移

```bash
python manage.py migrate
```

## 部署指南

### 生产环境配置

1. 修改`.env`文件：
   - 设置`DEBUG=False`
   - 更新`SECRET_KEY`
   - 更新`ALLOWED_HOSTS`
   - 配置数据库连接
   - 配置微信登录参数
   - 配置微信小程序登录参数

2. 收集静态文件：
   ```bash
   python manage.py collectstatic
   ```

3. 使用WSGI/ASGI服务器（如Gunicorn、uWSGI）运行应用

4. 配置Nginx作为反向代理

## 微信登录配置

微信网页登录和微信小程序登录共用相同的配置参数，在 `.env` 文件中配置以下参数：

```
# 微信登录设置
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret
WECHAT_REDIRECT_URI=https://your-domain.com/api/auth/wechat/callback
```

### 微信小程序客户端开发

在微信小程序中调用 `wx.login()` 获取临时登录凭证 code：

```javascript
wx.login({
  success: function(res) {
    if (res.code) {
      // 获取到登录凭证后发送到服务器
      wx.request({
        url: 'https://your-api-domain.com/api/auth/wechat/mini-login/',
        method: 'POST',
        data: {
          code: res.code
        },
        success: function(response) {
          if (response.data.code === 0) {
            // 登录成功，保存用户信息和token
            wx.setStorageSync('token', response.data.data.access);
            wx.setStorageSync('refresh_token', response.data.data.refresh);
            wx.setStorageSync('userInfo', response.data.data.user);
            
            // 如果是新用户，可能需要引导绑定手机号
            if (response.data.data.is_new_user && response.data.data.needs_phone_binding) {
              wx.navigateTo({
                url: '/pages/bindPhone/bindPhone'
              });
            } else {
              wx.switchTab({
                url: '/pages/index/index'
              });
            }
          } else {
            wx.showToast({
              title: '登录失败',
              icon: 'none'
            });
          }
        }
      });
    }
  }
});
```

## 安全注意事项

1. 在生产环境中更改默认的`SECRET_KEY`
2. 使用HTTPS保护API通信
3. 定期轮换JWT密钥
4. 限制API请求频率
5. 监控异常登录行为

## Docker和PostgreSQL部署

我们已经添加了Docker支持，可以使用Docker和PostgreSQL来部署应用。

### 准备工作

1. 安装Docker和Docker Compose
2. 配置环境变量

### 配置环境变量

1. 复制示例环境文件
   ```bash
   cp .env.example .env
   ```

2. 修改`.env`文件中的配置，特别是数据库连接信息:
   ```
   # PostgreSQL配置
   POSTGRES_USER=dify_user
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_DB=dify_db

   # 数据库URL
   DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
   ```

3. 修改其他配置，如`SECRET_KEY`、`ALLOWED_HOSTS`和微信登录信息

### 使用Docker Compose部署

1. 构建并启动服务
   ```bash
   docker-compose up --build -d
   ```

2. 创建超级用户
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

3. 访问应用
   - Web应用: http://localhost:8000
   - Admin界面: http://localhost:8000/admin

### 常用Docker命令

- 启动服务: `docker-compose up -d`
- 停止服务: `docker-compose down`
- 查看日志: `docker-compose logs -f web`
- 进入容器: `docker-compose exec web bash`
- 重启服务: `docker-compose restart web`

### 数据库管理

- 备份数据库:
  ```bash
  docker-compose exec db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup.sql
  ```

- 恢复数据库:
  ```bash
  cat backup.sql | docker-compose exec -T db psql -U ${POSTGRES_USER} ${POSTGRES_DB}
  ```

### 从SQLite迁移到PostgreSQL

如果您已经在使用SQLite，可以按照以下步骤迁移到PostgreSQL:

1. 备份SQLite数据
   ```bash
   python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json
   ```

2. 配置PostgreSQL连接
   - 修改`.env`文件，设置`DATABASE_URL`为PostgreSQL连接串

3. 应用数据库迁移
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. 导入数据
   ```bash
   docker-compose exec web python manage.py loaddata data.json
   ```

## 生产环境注意事项

1. 确保修改`SECRET_KEY`为随机值
2. 设置`DEBUG=False`
3. 配置`ALLOWED_HOSTS`为您的域名
4. 考虑使用HTTPS，可以通过Nginx配置SSL
5. 定期备份数据库
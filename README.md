# 后端服务 API 文档

本文档详细说明了后端服务的架构、功能和API接口。

## 技术栈

- **框架**: Django 5.2, Django REST Framework
- **数据库**: SQLite (开发环境), 可迁移至PostgreSQL (生产环境)
- **认证**: JWT (JSON Web Token)
- **API文档**: 本README文件

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
WECHAT_APP_ID=your-app-id
WECHAT_APP_SECRET=your-app-secret
WECHAT_REDIRECT_URI=http://localhost:8000/api/auth/wechat/callback
```

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

2. 收集静态文件：
   ```bash
   python manage.py collectstatic
   ```

3. 使用WSGI/ASGI服务器（如Gunicorn、uWSGI）运行应用

4. 配置Nginx作为反向代理

## 安全注意事项

1. 在生产环境中更改默认的`SECRET_KEY`
2. 使用HTTPS保护API通信
3. 定期轮换JWT密钥
4. 限制API请求频率
5. 监控异常登录行为

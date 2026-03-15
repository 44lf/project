# K12 智能教育平台

基于 OCR 的 K12 智能作业批改平台，支持学生上传作业图片、OCR 自动批改、低置信度转人工审核、学情分析看板等功能。

## 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite
- **前端**: Vue3 + Element Plus + ECharts
- **OCR**: Tesseract OCR + OpenCV

## 功能特性

### 学生端
- 上传作业图片（支持多种图片格式）
- 查看作业批改结果
- 个人学情分析看板
- 查看历史作业记录

### 教师端
- 人工审核低置信度作业
- 班级学情分析
- 学生成绩排名
- 重新批改作业

### 管理端
- 平台数据统计概览
- 用户管理（学生/教师/管理员）
- 作业和批改记录管理

### 核心功能
- **OCR 自动识别**: 使用 Tesseract OCR 识别作业图片中的文字
- **智能批改**: 基于识别结果自动评分
- **置信度阈值**: 低于设定阈值的作业自动转人工审核
- **学情分析**: 多维度数据统计和可视化展示

## 项目结构

```
k12-education-platform/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   └── api.py      # API 路由汇总
│   │   │   └── endpoints/      # API 端点
│   │   │       ├── auth.py     # 认证相关
│   │   │       ├── users.py    # 用户管理
│   │   │       ├── homework.py # 作业管理
│   │   │       ├── corrections.py  # 批改管理
│   │   │       ├── reviews.py  # 人工审核
│   │   │       └── dashboard.py    # 学情分析
│   │   ├── core/
│   │   │   └── config.py       # 配置文件
│   │   ├── db/
│   │   │   └── database.py     # 数据库连接
│   │   ├── models/             # 数据模型
│   │   │   ├── user.py
│   │   │   ├── homework.py
│   │   │   ├── correction.py
│   │   │   └── review.py
│   │   ├── schemas/            # Pydantic 模型
│   │   ├── services/           # 业务逻辑
│   │   │   ├── ocr_service.py
│   │   │   └── correction_service.py
│   │   └── utils/
│   │       └── security.py     # 安全工具
│   ├── uploads/                # 上传文件目录
│   │   ├── homework/           # 作业图片
│   │   └── ocr_results/        # OCR 结果
│   ├── tests/                  # 测试文件
│   ├── alembic/                # 数据库迁移
│   ├── main.py                 # 应用入口
│   ├── requirements.txt        # 依赖包
│   └── .env.example            # 环境变量示例
│
├── frontend/                   # Vue3 前端
│   ├── src/
│   │   ├── api/                # API 接口
│   │   │   ├── auth.js
│   │   │   ├── homework.js
│   │   │   ├── correction.js
│   │   │   ├── dashboard.js
│   │   │   └── request.js      # axios 封装
│   │   ├── components/         # 组件
│   │   │   └── common/
│   │   │       └── Layout.vue  # 布局组件
│   │   ├── router/             # 路由
│   │   │   └── index.js
│   │   ├── store/              # Pinia 状态管理
│   │   │   └── modules/
│   │   │       └── user.js
│   │   ├── views/              # 页面视图
│   │   │   ├── common/         # 通用页面
│   │   │   │   ├── Login.vue
│   │   │   │   └── NotFound.vue
│   │   │   ├── student/        # 学生页面
│   │   │   │   ├── Dashboard.vue
│   │   │   │   ├── Homework.vue
│   │   │   │   └── Upload.vue
│   │   │   ├── teacher/        # 教师页面
│   │   │   │   ├── Review.vue
│   │   │   │   └── ClassDashboard.vue
│   │   │   └── admin/          # 管理员页面
│   │   │       ├── Overview.vue
│   │   │       └── Users.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
└── README.md
```

## 快速开始

### 后端启动

1. 进入后端目录
```bash
cd backend
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 安装 Tesseract OCR
- **Windows**: 下载安装包 https://github.com/UB-Mannheim/tesseract/wiki
- **Mac**: `brew install tesseract tesseract-lang`
- **Linux**: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`

5. 启动服务
```bash
python main.py
```

后端服务将在 http://localhost:8000 启动

### 前端启动

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

前端服务将在 http://localhost:3000 启动

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 学生 | student1 | 123456 |
| 教师 | teacher1 | 123456 |
| 管理员 | admin | 123456 |

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看 Swagger API 文档

## 配置说明

### 后端配置 (.env)

```env
# 数据库配置
DATABASE_URL=sqlite:///./k12_education.db

# 安全配置
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 文件上传配置
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# OCR配置
OCR_CONFIDENCE_THRESHOLD=0.85
OCR_LANG=chi_sim+eng

# 人工审核配置
MANUAL_REVIEW_THRESHOLD=0.70
```

## 开发计划

- [x] 项目基础架构搭建
- [x] 用户认证系统
- [x] 作业上传功能
- [x] OCR 自动识别
- [x] 自动批改逻辑
- [x] 人工审核流程
- [x] 学情分析看板
- [ ] 作业模板管理
- [ ] 智能错题本
- [ ] 家长端小程序

## 许可证

MIT License

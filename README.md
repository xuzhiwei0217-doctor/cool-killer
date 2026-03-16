# Permission Auditor - 权限检查器

🦞 保护你的 OpenClaw 免受恶意 Skill 侵害！

## 快速开始

### 安装

```bash
# 克隆或复制到你的 skills 目录
cp -r permission-auditor ~/.openclaw/skills/
```

### 使用

在你的 OpenClaw 中直接说：

```
"检查所有 skill 的权限"
"扫描已安装的技能"
"安全审计"
```

## 功能特性

- 🔍 **自动扫描**: 扫描所有已安装的 Skill
- ⚠️ **风险评级**: 高/中/低三级风险评估
- 📋 **权限解释**: 每个权限能做什么，一目了然
- 🛡️ **安全建议**: 针对高风险权限提供处理建议
- 📊 **生成报告**: 导出详细的安全审计报告

## 风险等级

### 🔴 高风险权限
- `file_delete` - 可以删除你的文件
- `system_command` - 可以执行任意系统命令
- `browser_automation` - 可以控制你的浏览器
- `network_request` - 可以发送网络请求（可能泄露数据）

### 🟡 中风险权限
- `file_write` - 可以写入文件（可能修改配置）
- `env_variable_access` - 可以访问环境变量（可能包含密钥）

### 🟢 低风险权限
- `file_read` - 只能读取文件
- `text_processing` - 文本处理，无风险

## 输出示例

```
🦞 权限审计报告

扫描完成：发现 15 个 Skill

🔴 高风险：3 个
  - skill-a: 包含 file_delete, system_command
  - skill-b: 包含 browser_automation
  - skill-c: 包含 network_request

🟡 中风险：5 个
  ...

🟢 低风险：7 个
  ...

💡 建议:
  1. 审查所有高风险 Skill
  2. 禁用不信任的 Skill
  3. 定期运行审计
```

## 技术细节

### 扫描范围
- `~/.openclaw/skills/` 目录
- 所有包含 `SKILL.md` 的目录

### 检测方法
- 解析 `SKILL.md` 的 YAML front matter
- 检查 `metadata.requires` 字段
- 分析 `triggers` 关键词
- 评估风险等级

### 依赖
- Python 3.10+
- PyYAML

## 安全提示

⚠️ **重要**: 这个 Skill 本身只读权限，不会修改任何配置

✅ 安全使用：
- 只读扫描，不修改
- 本地运行，不上传数据
- 开源代码，可审计

## 开发

### 项目结构

```
permission-auditor/
├── SKILL.md              # OpenClaw Skill 描述
├── permission_auditor.py # 主程序
├── README.md             # 这个文件
└── requirements.txt      # Python 依赖
```

### 本地测试

```bash
# 安装依赖
pip install pyyaml

# 运行测试
python permission_auditor.py
```

## 反馈与支持

- GitHub: https://github.com/xuzhiwei0217-doctor/openclaw-skills
- 问题反馈：提交 Issue
- 功能建议：欢迎 PR

## 许可证

MIT License

---

**版本**: 1.0.0  
**更新日期**: 2026-03-16  
**作者**: xuzhiwei0217-doctor

# 个人部署说明（GitHub Actions）

本项目默认运行在 GitHub 提供的临时 Ubuntu runner 上，不需要让本地电脑持续
开机。仓库是公开 Fork，因此 Actions 日志和 `data` 分支中的加密文件也是公开
可访问的；任何凭证都只能存入 GitHub Actions Secrets，不能写入代码或提交。

## 部署前边界

- 仅处理本人有权访问的课程资料。
- 当前部署不启用 GitHub Pages；上游前端会在浏览器 `localStorage` 中保存 UIS 密码
  和 PAT，且尚不兼容独立 `DB_ENCRYPTION_KEY`。
- 不创建或填写前端所需的高权限 GitHub PAT。
- 不公开或转发录播、转录、PPT OCR 与课程摘要。
- 上游更新不会自动进入本 Fork；合并前应人工审查网络请求和 workflow 变更。

## 需要配置的 Secrets

进入自己的仓库：`Settings -> Secrets and variables -> Actions`，添加：

| Secret | 内容 |
|---|---|
| `STUID` | 复旦学号 |
| `UISPSW` | UIS 密码 |
| `COURSE_IDS` | 每日订阅课程 ID，多个用英文逗号分隔 |
| `COURSE_SESSION_RULES` | 可选；每行一门课程的课次白名单，例如 `35472=周一第1-2节|周三第6-8节` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key；首次只配置这一个模型服务即可 |
| `SMTP_EMAIL` | QQ 发件邮箱 |
| `SMTP_PASSWORD` | QQ 邮箱 SMTP 授权码，不是邮箱登录密码 |
| `RECEIVER_EMAIL` | 接收摘要的邮箱 |
| `DB_ENCRYPTION_KEY` | 独立随机数据库密钥，不能与 UIS 密码相同 |

在本地终端生成数据库密钥：

```bash
openssl rand -hex 32
```

只把输出粘贴到 `DB_ENCRYPTION_KEY` Secret。不要把输出发给别人，也不要写入
`.env` 后提交。丢失该密钥将无法解密已有数据库；更换它之前应先做好迁移。

Fork 的 Actions 如处于禁用状态，进入 `Actions` 页面，阅读提示后为该 Fork 启用
workflows。先不要运行任何 workflow，等下面的 Secrets 全部配置完成。

`COURSE_SESSION_RULES` 支持每行一个课程。没有出现在该 Secret 中的课程会处理全部
可播放课次；出现的课程只处理列出的星期和节次。多条规则使用 `|` 分隔，也可填写
`课程ID=全部`。格式错误时任务会在登录和调用模型前停止，且公开日志不会打印规则
内容。

每日任务优先使用完整的 iCourse 官方字幕；官方字幕缺失、接口失败或存在超过
20 分钟的缺口时自动回退本地 ASR。每门课程会单独发送一封邮件，正文保留 HTML
预览，并附带该课程本次新增摘要的 `.md` 文件。

## 首次试跑

1. 在 `COURSE_IDS` 中暂时只填一门课程。
2. 打开 `Actions -> Single Run -> Run workflow`。
3. 勾选官方字幕；课程 ID 会直接从 `COURSE_IDS` Secret 读取，不在公开参数中填写。
4. 运行后检查 Actions 日志中没有课程名、教师名、课次 ID、完整 URL 或邮箱地址。
5. 检查邮件和模型平台账单；确认无异常后，再把其他课程加入 `COURSE_IDS`。

首次运行默认会处理所选课程的所有已有录播；设置 `COURSE_SESSION_RULES` 后，只处理
符合白名单的课次。视频地址获取、开放时间处理、重试次数和任务调度保持不变。
GitHub 的 cron 不保证准点执行。

课程标题、转录/OCR 文本和摘要提示会发送给你配置的模型服务商；生成的摘要会发送
给邮箱服务商。请按课程资料的使用规则和对应服务商的隐私条款决定是否使用。

## 可选：导出或删除数据

公开仓库的手动 workflow 文本参数并不适合填写课程 ID。因此：

- `Export Course Summaries` 默认导出 `COURSE_IDS` 中的课程。如需只导出指定课程或
  课次，临时添加 `EXPORT_COURSE_IDS`、`EXPORT_SUB_IDS` Secrets。
- `Delete Course Data` 运行前必须临时添加 `DELETE_COURSE_IDS` Secret；如只删指定
  课次，再添加 `DELETE_SUB_IDS`。确认完成后删除这两个临时 Secrets。

## 停用

先在仓库 `Actions` 中禁用 workflows，再撤销模型 API Key 和 SMTP 授权码。若
出现 UIS 异地登录或异常认证重试，应立即停用 workflow 并更改 UIS 密码。

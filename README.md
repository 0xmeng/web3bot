# web3bot

这是个网页自动化bot,主要用于web3项目签到，目前只支持mac系统

## joyid钱包

- 自动领取每日奖励里的 签到 余额 交易 3个任务奖励
- 钱包之间两两互相发送matic
- 发送后自动返回未完成的任务再次领取

### 安装

```bash 00000000
pip install -r requirements.txt
```

### 运行

```bash 00000000
python joyid_bot.py
```

## 如何使用

1. 默认使用已经安装的chrome浏览器,运行脚本前退出所有已打开的谷歌浏览器,运行期间浏览器置顶
2. 先把所有要自动签到账号都登录进去
3. 添加所有要自动签到的账号到config.py文件的ACCTS数组中,账号名必须以Account开头
4. assets文件夹下为系统授权时的弹窗截图,可根据自己系统样式截图替换




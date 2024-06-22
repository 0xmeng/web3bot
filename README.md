# web3bot

这是个网页自动化bot,主要用于web3项目签到，目前只在mac下测试通过

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
sudo python joyid_bot.py
```

## 如何使用

1. 电脑上安装有chrome浏览器,运行钱推出所有已打开的谷歌浏览器,运行期间浏览器要置顶
2. 先把所有要自动签到账号都登录进去
3. 脚本用管理员权限运行
4. 修改config.py里的chrome为自己本地安装路径
5. 添加账号到ACCTS数组中,账号名必须以Account开头
6. assets文件夹下为系统授权时的弹窗截图,根据自己系统样式截图替换即可




# 浏览器安装地址
CHROME_PATH = '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'
# 浏览器监听端口
CHROME_PORT = '9223'

#做交易奖励,只支持matic，改为False不做这个奖励，只做签到和余额奖励
DO_TX = True
# 设置matic的市场价格，如果网络获取不到会取这个价格
MATIC_PRICE = 0.56
# 当账户金额小于5刀时不发送matic
STOP_UNDER_5USD = True

# 'ALL'：全量发送  'RANDOM'：随机发送数量 'CUSTOM':自定义发送数量
SEND_TYPE = 'ALL'
# 自定义发送matic数量，当SEND_TYPE='CUSTOM'的时候使用
CUSTOM_SEND_NUMBER = 9.5321

#钱包名称和地址，如果不做交易奖励，可以不填地址
#钱包按顺序两两互转，最后不足两个钱包的一个地址不执行划转任务，
ACCTS = [
    {
      "acct": "Account#1111",
      "evm_addr": "0x123123213123"
    },
    {
        "acct": "Account#2222",
        "evm_addr": "0x123123123123",
    }

]

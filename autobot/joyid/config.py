#passkey授权密码
AUTH_PASSWORD = '00000000'

#ui 文本 当ui 文本不是简体中文时在这里配置自己的语言
UI_TEXT = {
    # 'button_daily_rewards': "Daily rewards", #领取页面切换每日奖励页签按钮文本
    # 'title_reward1': 'Daily free reward', #奖励1的文本
    # 'title_reward2': "Balance Reward",#奖励2的文本
    # 'title_reward3': "Transaction reward",#奖励3的文本
    # 'button_claim': "Claim" #领取按钮文本
}

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
      "acct": "Account#4287",
      "evm_addr": "0x8abe1c05B8274144D7D0AEb50D43B7f2d527192c"
    }

]

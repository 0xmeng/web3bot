import asyncio
import os
import json
import traceback

import requests
from playwright.async_api import async_playwright
import random
import pyautogui
import config
import subprocess
from datetime import datetime, timedelta
import copy

LOCAL_CACHE_PATH = f'./json/cache.json'
STEALTH_PATH = '../js/stealth.min.js'
PAGE_REWARD = 'https://app.joy.id/quest'
PAGE_HOME = 'https://app.joy.id/'
PAGE_ACCTS = 'https://app.joy.id/accounts'
PAGE_MATIC_SEND = 'https://app.joy.id/send-evm-native/137'
URL_TOKEN_PRICE = 'https://api.joy.id/api/v1/supported_token_prices'
TIME_24HOUR = 60 * 60 * 24 * 1000
KEY_TIME_FINISH = "finish_date"

KEY_TX_SEND = "joyid.tx.send"
KEY_TX_RECEIVE = "joyid.tx.receive"


async def random_sleep(min_limit=0.3, max_limit=1.5):
    """异步随机 sleep
    :param min_limit: 最小值
    :param max_limit: 最大值
    """
    rand = random.uniform(min_limit, max_limit)
    delay = float('{:04.3f}'.format(rand))
    print('sleep', delay)
    await asyncio.sleep(delay)


class JOYIDAuto:
    KEY_NAME_REWARD1 = "每日奖励"
    KEY_NAME_REWARD2 = "余额奖励"
    KEY_NAME_REWARD3 = "交易奖励"
    TEXT_BUTTONT_REWARDS = '每日奖励'

    def __init__(self):
        self.loggers = {}
        self.schedulers = {}
        self.playwright = None
        self.contexts = {}
        self.loop = asyncio.new_event_loop()
        self.current_acct = {}
        self.accts = []
        self.matic_price = 0
        self.caches = {}

    def run(self):

        # Schedule the browser start and screenshot loop in the asyncio event loop
        self.loop.create_task(self.start_browser())
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def init_data(self):
        # scheduler2 = TornadoScheduler(timezone='Asia/Shanghai')
        # scheduler2.add_job(self.take_screenshot, 'interval', seconds=5)
        # scheduler2.start()

        # await self.init()
        # for worker_idx in range(1):
        #     self.loggers[worker_idx] = Logger('joyid', worker_idx, f'./log/{worker_idx}.log')
        #     file_path = f'./json/{worker_idx}.json'
        #     self.check_storage_file(file_path)
        if config.UI_TEXT:
            rewards_page_title = config.UI_TEXT.get('button_daily_rewards')
            if rewards_page_title:
                self.TEXT_BUTTONT_REWARDS = rewards_page_title
            title_reward1 = config.UI_TEXT.get('title_reward1')
            if title_reward1:
                self.KEY_NAME_REWARD1 = title_reward1
            title_reward2 = config.UI_TEXT.get('title_reward2')
            if title_reward2:
                self.KEY_NAME_REWARD2 = title_reward2
            title_reward3 = config.UI_TEXT.get('title_reward3')
            if title_reward3:
                self.KEY_NAME_REWARD3 = title_reward3

        self.caches = self.check_storage_file(LOCAL_CACHE_PATH)
        self.accts = copy.deepcopy(config.ACCTS)

    async def start_browser(self):
        self.playwright = await async_playwright().start()
        try:
            while True:
                self.init_data()
                await self.__start_worker(0)
                await self.sleep_untill_next_utc()
                await asyncio.sleep(3)

        except Exception as e:
            print(traceback.format_exc())

    async def sleep_untill_next_utc(self):
        current_utc_time = datetime.utcnow()
        next_midnight = datetime.combine(current_utc_time.date() + timedelta(days=1), datetime.min.time())
        time_left = next_midnight - current_utc_time
        sleep_duration = time_left.total_seconds()

        # Sleep until the next midnight
        print(f"休息 {sleep_duration / 3600} 小时...")
        # time.sleep(sleep_duration)
        await asyncio.sleep(sleep_duration)

    def process_asyncio_events(self):
        try:
            self.loop.stop()
            self.loop.run_forever()
        except Exception as e:
            print(f"Error processing asyncio events: {e}")
        # finally:
        #     self.root.after(10, self.process_asyncio_events)

    async def __handle_res(self, res, page):
        try:
            if res.status != 200:
                return
            if res.url.startswith(URL_TOKEN_PRICE):
                res_text = await res.text()
                # print(res_text)
                res_data = json.loads(res_text)
                if res_data:
                    prices = res_data.get('prices')
                    if prices:
                        matic = prices.get('matic-network')
                        if matic:
                            usd = matic.get('usd')
                            if usd:
                                self.matic_price = usd
                                print("matic 当前价格：%s" % str(usd))
        except Exception as e:
            print(e)

    def check_storage_file(self, file_path, ):
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump({}, f)
                return {}
        else:
            with open(file_path, 'r') as f:
                return json.load(f)

    def get_current_acct(self, acct_name):
        for acct in self.accts:
            if acct.get('acct') == acct_name:
                self.current_acct = acct
                return acct

    def check_acct_finish(self, acct_name):
        for acct in self.accts:
            if acct.get('acct') == acct_name:
                acct_cache = self.caches.get(acct_name)
                last_utc_time = None
                current_utc_time = datetime.utcnow()
                if acct_cache:
                    last_reward_time = acct_cache.get(KEY_TIME_FINISH, "")
                    if last_reward_time:
                        last_utc_time = datetime.strptime(last_reward_time, "%Y-%m-%d %H:%M:%S")
                if last_utc_time is None or (last_utc_time and current_utc_time > last_utc_time):
                    return False

                if last_utc_time and current_utc_time <= last_utc_time:
                    return True

    async def get_acct(self, page, account_text):
        acct = self.get_current_acct(account_text)
        if acct:
            while page.url.startswith(PAGE_ACCTS):
                print(f"点击账号名称 {account_text}")
                await page.get_by_text(account_text).first.click()
                print(f"{account_text}开始任务")
                await asyncio.sleep(6)
            return acct

    async def select_acct(self, page, acct_name=None):
        await page.goto(url=PAGE_ACCTS, timeout=0)
        await asyncio.sleep(3)
        acct_eles = page.locator('p:has-text("Account")')
        count = await acct_eles.count()
        if count > 0:
            for i in range(count):
                acct_ele = acct_eles.nth(i)
                account_text = await acct_ele.inner_text()
                if acct_name and account_text != acct_name:
                    continue
                if acct_name and acct_name == account_text:
                    return await self.get_acct(page, account_text)
                else:
                    finished = self.check_acct_finish(account_text)
                    if not finished:
                        return await self.get_acct(page, account_text)
                    else:
                        print(f'跳过已完成的账号 {account_text}')

    async def get_matic_price(self, page):
        retry_count = 0
        while self.matic_price == 0:
            print('>>>> 马蹄价格没有获取到， 重新获取马蹄价格')
            await page.reload()
            await asyncio.sleep(5)
            retry_count += 1
            if retry_count >= 3:
                print('>>>> 马蹄价格没有渠道取配置文件的价格')
                self.matic_price = config.MATIC_PRICE
                break
        print(f'当前 matic 价格： {self.matic_price}')

    async def goto_reward_page(self, page):
        await page.goto(url=PAGE_REWARD, timeout=0)
        await asyncio.sleep(5)
        await page.get_by_text(self.TEXT_BUTTONT_REWARDS).first.click()
        await asyncio.sleep(5)

    async def __start_worker(self, worker_id):

        # chrome_path = f"{config.CHROME_PATH} --remote-debugging-port={config.CHROME_PORT}"
        # chrome_process = subprocess.Popen(chrome_path, shell=True)
        # # 启动 Chrome 并指定调试端口
        # user_home = os.path.expanduser('~')
        # chrome_user_data_dir = os.path.join(user_home, 'Library', 'Application Support', 'Google', 'Chrome')
        # chrome_command = [
        #     config.CHROME_PATH,
        #     # f'--user-data-dir={chrome_user_data_dir}',
        #     f'--remote-debugging-port={config.CHROME_PORT}',
        #     # '--no-sandbox',  # 可能需要添加这个参数
        #     # '--disable-gpu'
        # ]
        # 启动 Chrome（如果还没有运行的话）
        # subprocess.Popen([
        #     '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        #     '--remote-debugging-port=9222',
        #     '--user-data-dir=/Users/philar/Library/Application Support/Google/Chrome'
        # ])
        # await asyncio.sleep(10)
        # while True:
        #     try:
        #         browser = await self.playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{config.CHROME_PORT}")
        #         new_context = browser.contexts[0]
        #         page = new_context.pages[0]
        #         break
        #     except Exception as e:
        #         print(e)
        #     await asyncio.sleep(3)

        user_data_dir = os.path.expanduser('~/Library/Application Support/Google/Chrome')
        # # browser = await self.playwright.chromium.launch(
        # #     channel="chrome",  # 使用系统安装的 Chrome
        # #     headless=False,
        # #     args=[f'--user-data-dir={user_data_dir}']
        # # )
        # # new_context = await browser.new_context()
        # # page = await new_context.new_page()
        #

        new_context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=False
        )
        page = new_context.pages[0]

        page.on("response", lambda res: self.__handle_res(res, page))
        #
        to_acct = None
        while await self.select_acct(page, to_acct):

            await self.get_matic_price(page)
            await asyncio.sleep(5)

            await self.goto_reward_page(page)

            await self.check_rewards(page, False)

            target_acct = await self.check_tx_rewards(page)
            if target_acct:
                await self.goto_reward_page(page)
                await self.check_rewards(page, True)
                to_acct = target_acct.get('acct')
            else:
                to_acct = None

            self.check_all_finish()
            await asyncio.sleep(5)

        print(f"----{self.current_acct.get('acct', '')}完成所有任务-----")

        # await self.__wait_input(page, worker_id)

    def check_all_finish(self):
        finish = False
        if self.current_acct.get(self.KEY_NAME_REWARD1) and self.current_acct.get(
                self.KEY_NAME_REWARD2) and self.current_acct.get(self.KEY_NAME_REWARD3):
            finish = True
            self.current_acct['finished'] = finish
        if self.current_acct.get(self.KEY_NAME_REWARD1):
            acct_name = self.current_acct.get('acct')
            cache = self.caches.get(acct_name)
            if not cache:
                cache = {}
                self.caches[acct_name] = cache
            current_utc_time = datetime.utcnow()
            next_day = datetime.combine(current_utc_time.date() + timedelta(days=1), datetime.min.time())
            print(f"{next_day}")
            cache[KEY_TIME_FINISH] = f"{next_day}"
            with open(LOCAL_CACHE_PATH, 'w') as file:
                json.dump(self.caches, file, indent=4)
        return finish

    async def check_tx_rewards(self, page):
        try:
            if self.current_acct.get(KEY_TX_SEND):
                print('当前账号已经发送过代币')
                return
            if self.current_acct.get(KEY_TX_RECEIVE):
                print('当前账号已经接收过代币')
                return

            title = "领取"
            send_success = False
            while not send_success:
                await asyncio.sleep(2)
                claim_buttons = await page.locator(f'button:has-text("{title}")').element_handles()
                if (0 < len(claim_buttons) <= 3 and config.DO_TX) or self.current_acct.get("余额奖励"):
                    await page.goto(url=PAGE_MATIC_SEND, timeout=0)
                    await asyncio.sleep(5)
                    # Extract the text content from the element
                    matic_text = await page.inner_text('span:has-text("Max:")')
                    if not matic_text:
                        print('找不到Max:')
                        return
                    # Extract the number from the text
                    matic_number = float(matic_text.split('Max: ')[1].split(' MATIC')[0])
                    self.current_acct['balance'] = matic_number
                    if matic_number == 0:
                        print('余额为0')
                        return
                    print(f'当前账户剩余matic:{matic_number}')
                    if matic_number * self.matic_price < 5 and config.STOP_UNDER_5USD:
                        print('金额小于5刀，当前账户不发送matic')
                        return
                    else:
                        current_idx = None
                        acct_len = len(self.accts)
                        for idx in range(acct_len):
                            acct = self.accts[idx]
                            if acct.get("acct") == self.current_acct.get("acct"):
                                current_idx = idx
                                print("当前账号序号%d" % idx)
                                break
                        if current_idx is None:
                            print('>>>> 配置中找不到当前账号 %s' % self.current_acct.get("acct"))
                            return

                        target_acct = None
                        if current_idx % 2 == 0 and current_idx + 1 < acct_len:
                            target_acct = self.accts[current_idx + 1]
                        if current_idx % 2 != 0:
                            target_acct = self.accts[current_idx - 1]

                        if not target_acct:
                            print(">>>> 找不到要发送的目标账号")
                            return
                        print(target_acct)
                        if target_acct.get('finished'):
                            print(">>>> 目标账号以完成所有任务")
                            return
                        if target_acct and not target_acct.get('evm_addr'):
                            print(f">>>> 配置文件中{target_acct.get('acct')}没有配置evm_addr地址")
                            return
                        if target_acct:
                            acct = target_acct.get('acct')
                            print(f'{self.current_acct.get("acct")}发送到{acct}')
                            textarea_selector = 'textarea[name="toAddress"]'
                            await page.fill(textarea_selector, target_acct.get("evm_addr"))
                            await asyncio.sleep(2)
                            send_number = 0
                            if config.SEND_TYPE == 'ALL':
                                print(f'全量发送 {matic_number}')
                                send_number = matic_number
                            elif config.SEND_TYPE == 'RANDOM':
                                random_num = random.uniform(0.01, matic_number)
                                print(f'随机发送{random_num}')
                                send_number = random_num
                            elif config.SEND_TYPE == 'CUSTOM':
                                print(f'自定义发送 {config.CUSTOM_SEND_NUMBER}')
                                send_number = config.CUSTOM_SEND_NUMBER
                            if send_number > 0:
                                input_selector = 'input[name="amount"]'
                                await page.fill(input_selector, str(send_number))
                                await asyncio.sleep(2)
                                button_xpath = '//button[span[text()="发送"]]'
                                await page.click(f'xpath={button_xpath}')
                                await asyncio.sleep(5)

                                button_xpath = '//button[span[text()="确认"]]'
                                await page.click(f'xpath={button_xpath}')
                                await asyncio.sleep(5)

                                await self.input_auth_pwd()
                                await asyncio.sleep(10)

                                retry_count = 0
                                while not page.url.startswith(PAGE_HOME):
                                    print('等待确认成功')
                                    await asyncio.sleep(5)
                                    retry_count += 1
                                    if retry_count > 5:
                                        print('等待超时')
                                        break
                                if retry_count <= 5:
                                    print('发送成功 等1分钟')
                                    await asyncio.sleep(60)
                                    self.current_acct[KEY_TX_SEND] = True
                                    target_acct[KEY_TX_RECEIVE] = True
                                    return target_acct
                                else:
                                    print('发送失败刷新页面')
                                    await page.reload()
                                    await asyncio.sleep(5)

                                # Click the button
                else:
                    print('找不到领取按钮或今日奖励已经完成！')
                    break
        except Exception as e:
            print(e)

    async def input_auth_pwd(self):
        try:
            dialog_location = pyautogui.locateOnScreen('./assets/auth_input.png', confidence=0.8)
            if dialog_location:
                pyautogui.click(dialog_location)
            pyautogui.write(config.AUTH_PASSWORD, interval=0.2)
            pyautogui.press('enter')  # Move to the next field
            await asyncio.sleep(5)
        except:
            # print(traceback.format_exc())
            print("没有弹出授权窗口")

    async def wait_element(self, page, reward_name):
        wait_count = 0
        while wait_count < 12:
            reward_element = await page.query_selector(f'//p[text()="奖励 1"]')
            if not reward_element:
                print('等待页面加载。。。')
                await asyncio.sleep(5)
            else:
                break
            wait_count += 1

    async def check_reward_done(self, page, reward_name):
        try:
            reward_element = await page.query_selector(f'//p[text()="{reward_name}"]')
            if reward_element:
                parent = await reward_element.evaluate_handle('element => element.parentElement')
                if parent:
                    claim_button = await parent.query_selector('xpath=..//button[text()="领取"]')
                    if claim_button:
                        print(f"{reward_name} {await claim_button.inner_text()}")
                        return claim_button
                    else:
                        print(f"{reward_name} Button not found.")
            else:
                print(f"{reward_name} Reward element not found.")
        except:
            print(traceback.format_exc())

    async def do_reward(self, page, title):
        try:
            retry = 0
            while retry < 3:
                reward_button = await self.check_reward_done(page, title)
                if reward_button:
                    await reward_button.click()
                    await asyncio.sleep(5)
                    await self.input_auth_pwd()
                    print(f'{title} 尝试领取{retry + 1}次')
                else:
                    self.current_acct[title] = True
                    print(f'{title} 已经完成')
                    break
                retry += 1
                await asyncio.sleep(2)
        except:
            print(f'{title} 不成功')

    async def check_rewards(self, page, is_tx):
        try:
            if not self.current_acct.get(self.KEY_NAME_REWARD1) and not is_tx:
                await self.do_reward(page, self.KEY_NAME_REWARD1)
                print('---------')
            if not self.current_acct.get(self.KEY_NAME_REWARD2):
                await self.do_reward(page, self.KEY_NAME_REWARD2)
                print('---------')
            if not self.current_acct.get(self.KEY_NAME_REWARD3):
                await self.do_reward(page, self.KEY_NAME_REWARD3)

        except Exception as e:
            print(e)

    async def wait_for_input(self):
        return await asyncio.get_event_loop().run_in_executor(
            None, input, "Enter a value: "
        )

    async def __wait_input(self, page, worker_idx):
        while True:
            val = await self.wait_for_input()
            try:
                page = self.contexts[0].pages[0]
                if val.startswith('txt:'):
                    txt = val.split(':')[1]
                    if txt:
                        await page.get_by_text(txt).first.click()
                elif val.startswith('save'):
                    states = await page.context.storage_state(path=f'json/{worker_idx}.json')
                    print(states)

                await random_sleep(2, 3)
            except Exception as e:
                print(e)

    async def cleanup(self):
        await self.playwright.stop()


if __name__ == '__main__':
    joyid = JOYIDAuto()
    joyid.run()

import requests

# Clash API URL
CLASH_API_URL = "http://127.0.0.1"  # Replace with your Clash API address if different
SECRET = ""  # Set this if you configured a secret in config.yaml

CONFIG_PATH = r"G:\clash_copy\clash_configs" #启动时指定的配置文件目录

# 找到名称对应哪个文件 G:\clash_copyclash_configs\clash0\profiles
PROFILES_DICT = {
    "青云代理": "1740804478063.yml",
    "白兔代理": "1740804478063.yml",
    "熊猫代理": "1740804478063.yml",
}

# 根据自己修改的yml代理端口号修改, 第一个是mixed-port 第二个是external-controller
# 根据自己需要添加更多clash 端口，这里只设置了20个clash
CLASH_PORTS = [ #
                (59738, 59737),#clash0
                (64115, 64114),#clash1
                (64764, 64763),#clash2
                (65331, 65330),#clash3
                (49930, 49929),#clash4
                (50787, 50786),#clash5
                (51959, 51958),#clash6
                (52566, 52565),#clash7
                (53086, 53085),#clash8
                (53714, 53713),#clash9
                (7990, 9190),#clash10
                (52691, 52690),#clash11
                (55552, 55550),#clash12
                (57767, 57766),#clash13
                (62034, 62033),#clash14
                (49394, 49393),#clash15
                (52574, 52573),#clash16
                (56139, 56138),#clash17
                (60909, 60908),#clash18
                (63972, 63971),#clash19
               ]

class ClashAPI:
    def __init__(self, name='clash', index=0):
        if index >= len(CLASH_PORTS):
            index = 0
        ports = CLASH_PORTS[index]
        port = 9090
        api_port = 7890
        if name != 'clash':
            port = ports[1]
            api_port = ports[0]
        self.port = port
        self.name = name
        self.proxy = f"{CLASH_API_URL}:{api_port}"

    # Function to switch proxy
    def switch_proxy(self, group_name, proxy_name):
        url = f"{CLASH_API_URL}:{self.port}/proxies/{group_name}"
        headers = {}

        if SECRET:
            headers["Authorization"] = f"Bearer {SECRET}"

        # Data to switch the proxy
        data = {"name": proxy_name, "group": group_name}

        response = requests.put(url, json=data, headers=headers)
        if response.status_code == 204:
            print(f"成功切换到代理: {proxy_name} 组: {group_name}")
            return True
        else:
            print(
                f"切换代理失败.  {proxy_name} 组: {group_name} Status: {response.status_code}, Response: {response.text}")

    # Function to list proxies in a group
    def list_proxies(self, group_name):
        url = f"{CLASH_API_URL}:{self.port}/proxies/{group_name}"
        headers = {}

        if SECRET:
            headers["Authorization"] = f"Bearer {SECRET}"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            proxies = response.json().get("all", [])
            print(f"Proxies in group '{group_name}': {proxies}")
            return proxies
        else:
            print(f"Failed to fetch proxies. Status: {response.status_code}, Response: {response.text}")
            return []

    def get_configs(self):
        print('')
        url = f"{CLASH_API_URL}:{self.port}/configs"
        headers = {}

        if SECRET:
            headers["Authorization"] = f"Bearer {SECRET}"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(response)
            proxies = response.json().get("all", [])
            # print(f"Proxies in group '{group_name}': {proxies}")
            return proxies
        else:
            print(f"Failed to fetch proxies. Status: {response.status_code}, Response: {response.text}")
            return []

    def switch_config_proxy(self, group_name):
        url = f"{CLASH_API_URL}:{self.port}/configs/"
        headers = {}

        if SECRET:
            headers["Authorization"] = f"Bearer {SECRET}"

        profile = PROFILES_DICT.get(group_name)
        if not profile:
            print(f"找不到配置文件 {group_name}")
            return False

        path = rf"{CONFIG_PATH}\{self.name}\profiles\{profile}"
        # Data to switch the proxy
        data = {"path": f"{path}"}

        response = requests.put(url, json=data, headers=headers)
        if response.status_code == 200:
            print(f"成功切换到组: {group_name}")
            return True
        else:
            print(f"切换 组: {group_name} Status: {response.status_code}, Response: {response.text}")

    def check_name(proxy_name, proxies):
        for proxy in proxies:
            if proxy_name == proxy:
                return True


# Example usage
if __name__ == "__main__":
    group_name = "青云代理"
    proxy = "日本01"
    c = ClashAPI('clash0', 0)
    # clash切换到 青云代理 配置文件
    c.switch_config_proxy(group_name)
    # 打印所有dialing线路
    c.list_proxies(group_name)
    # 切换到 日本01 线路
    c.switch_proxy(group_name, proxy)

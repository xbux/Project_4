import uuid, random, string, asyncio, aiohttp, logging, calendar, time

from imapclient import IMAPClient
from faker import Faker

fake = Faker()

logging.getLogger('asyncio').setLevel(logging.CRITICAL)

class EMPRESA_API:
    
    def __init__(self):
        self.session = None
        
        self.emails_passwords = [_.strip() for _ in open("data/accounts.txt", "r").readlines() if _]
        self.emails = []
        self.email_index = -1
        
        self.proxys = [_.strip() for _ in open("data/proxies.txt", "r").readlines() if _]
        self.proxies = []
        self.proxy_index = -1
        
        self.device_id = uuid.uuid4()
        
        self.password = "GeneratedPass123!"
        
    def get_user_agent(self):
        def generate_string(n=10):
            letters = string.ascii_lowercase + '1234567890'
            return ''.join(random.choice(letters) for i in range(n))
        
        def generate_string_char(n=10):
            letters = string.ascii_lowercase
            return ''.join(random.choice(letters) for i in range(n))
        
        def generate_random_string_chars(stringLength=10):
            letters = string.ascii_lowercase + '1234567890'
            result = ''.join(random.choice(letters) for i in range(stringLength - 1))
            return generate_string_char(1) + result
        
        devices = ['Huawei', 'Xiaomi', 'Samsung', 'OnePlus', "ZTE", "LG", "Motorola"]
        dpis = ['480', '320', '640', '515', '120', '160', '240', '800']
        
        resolution = random.randrange(2, 9) * 180
        low_resolution = resolution - 180
        
        all_settings_of_user_agent = {
            'system': "Android",
            'Host': "Empresa-API",
            'manufacturer': f'{random.choice(devices)}',
            'model': f'{random.choice(devices)}-{generate_random_string_chars(4).upper()}',
            'android_version': random.randint(18, 25),
            'android_release': f'{random.randint(1, 7)}.{random.randint(0, 7)}',
            "cpu": f"{generate_string_char(2)}{random.randrange(1000, 9999)}",
            'resolution': f'{resolution}x{low_resolution}',
            'randomL': f"{generate_string(6)}",
            'dpi': f"{random.choice(dpis)}"}
        
        user_agent_new = {"user-agent": '{Host} 195.0.0.0.000 {system} ({android_version}/{android_release}; {dpi}dpi; {resolution}; {manufacturer}; {model}; {cpu}; {randomL}; en_US)'.format(
            **all_settings_of_user_agent)}
        
        return user_agent_new
    
    async def grab_proxy(self, proxy):
        self.proxies.append(proxy)
        print(f'[*] Proxies: {len(self.proxies)}', end="\r", flush=True)
        
    async def grab_account(self, account):
        self.emails.append(account)
        print(f'[*] Accounts: {len(self.emails)}', end="\r", flush=True)
        
    def get_proxy(self):
        self.proxy_index += 1
        if self.proxy_index >= len(self.proxies):
            self.proxy_index = 0
        return self.proxies[self.proxy_index]
    
    def get_email(self):
        self.email_index += 1
        if self.email_index >= len(self.emails):
            self.email_index = 0
        return self.emails[self.email_index]
    
    async def get_code_from_email(self, current_email):
        email_user, email_pass = current_email.split("|")[0], current_email.split("|")[1]
        try:
            for _ in range(10):
                with IMAPClient('outlook.office365.com', ssl=True) as server:
                    server.login(email_user, email_pass)
                    server.select_folder('INBOX')
                    messages = server.search(['FROM', "no-reply@empresa-api.com"])
                    
                    for uid, message_data in server.fetch(messages, 'RFC822').items():
                        email_message = message_data[b'RFC822']
                        message = email_message.decode("utf-8", errors="ignore")
                        
                        for line in message.splitlines():
                            if "Empresa-API code" in line:
                                self.verification_code = line.split(" ")[1].split(" ")[0]
                                print(f'[!!] your code is: {self.verification_code}')
                                return True, self.verification_code
            return False
        except Exception as exception:
            print(f'[ERROR] {exception}')
            return False
        
    async def verify_email(self, current_email):      
        data = {
            "phone_id": str(uuid.uuid4()),
            "guid": str(uuid.uuid4()),
            "device_id": str(self.device_id),
            "email": current_email.split("|")[0],
            "waterfall_id": str(uuid.uuid4()),
            "auto_confirm_only": "false" }
        
        headers = self.get_user_agent()
        url = "https://api.empresa-api.com/v1/accounts/send_verify_email/"
        
        async with self.session.post(url, headers=headers, data=data) as response:
            all_data = await response.text()
            if "email_sent" in all_data:
                print(f'[!!] email sent to: {current_email}')
                await self.get_code_from_email(current_email)
            else:
                print(all_data)
                
    async def get_code(self, current_email):
        email_user = current_email.split("|")[0]
        
        data = {
            "code": getattr(self, 'verification_code', ''),
            "device_id": str(self.device_id),
            "email": email_user,
            "waterfall_id": str(uuid.uuid4())}
        
        headers = self.get_user_agent()
        url = "https://api.empresa-api.com/v1/accounts/check_confirmation_code/"
        
        async with self.session.post(url, headers=headers, data=data) as response:
            all_data = await response.json()
            try:
                self.code_for_sign = all_data["signup_code"]
                print(f'[!!] code to signup is: {self.code_for_sign}')
                await self.create_account(current_email)
            except:
                pass
                
    async def create_account(self, current_email):
        proxy_url = f'http://{self.get_proxy()}'
        if_create = ["challenge", '"account_created":true']
        letters = string.ascii_lowercase + '1234567890'
        
        current_headers = {
            "user-agent": f'{fake.user_agent()}',
            "x-asbd-id": f'{random.randrange(100000, 999999)}',
            "x-csrftoken": f"{''.join(random.choice(letters) for i in range(32))}",
            "x-empresa-app-id": f'{random.randint(111111111111111, 999999999999999)}',
            "x-empresa-www-claim": '0',
            "x-empresa-ajax": f"{''.join(random.choice(letters) for i in range(12))}",
            "x-requested-with": 'XMLHttpRequest'}
            
        data = {
            "email": current_email.split("|")[0],
            "enc_password": f"#PWD_EMPRESA_BROWSER:0:{calendar.timegm(time.gmtime())}:{self.password}",
            "username": f"{''.join(random.choice(letters) for i in range(12))}",
            "first_name": "heasi",
            "month": "1",
            "day": "1",
            "year": "1999",
            "client_id": str(self.device_id),
            "seamless_login_enabled": "1",
            "tos_version": "row",
            "force_sign_up_code": getattr(self, 'code_for_sign', '')}
        
        url = "https://www.empresa-api.com/accounts/web_create_ajax/"
        
        try:
            for _ in range(10):
                async with self.session.post(url, headers=current_headers, data=data, proxy=proxy_url) as response:
                    response_data = await response.text()
                    #print(response_data)
                    if any(indicator in response_data for indicator in if_create):
                        print(f'[!!] Account register: {current_email}')
                        return True
            return False
        except Exception as exception:
            print(exception)
        
    async def get_all_proxies(self):
        tasks_to_complete = [self.grab_proxy(proxy) for proxy in self.proxys]
        await asyncio.gather(*tasks_to_complete)
        
    async def get_all_accounts(self):
        tasks_to_complete = [self.grab_account(account) for account in self.emails_passwords]
        await asyncio.gather(*tasks_to_complete)
        
    async def gathering_all_gathers(self):
        await self.get_all_proxies()
        print()
        await self.get_all_accounts()
        print()
        
    async def init(self):
        self.session = aiohttp.ClientSession(
            trust_env=True, 
            connector=aiohttp.TCPConnector(ssl=False))
        
        current_email = self.get_email()
        
        await self.verify_email(current_email)
        await self.get_code(current_email)
        
        await self.session.close()

start = EMPRESA_API()
print('[+] Automated Verification Client Register \n')
asyncio.run(start.gathering_all_gathers())
print()
asyncio.run(start.init())
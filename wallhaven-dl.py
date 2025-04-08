########################################################
#        Program to Download Wallpapers from           #
#                  alpha.wallhaven.cc                  #
########################################################

import os
import getpass
import re
import requests
import tqdm
import time
import urllib
import json

class WallhavenAPI:
    def __init__(self):
        """
        初始化 WallhavenAPI 类
        设置 API 密钥、基础 URL 和 cookies
        创建 Wallhaven 目录用于存储下载的壁纸
        """
        self.api_key = "eFutpkV99wrI6nD8yeMggg6iPOrWSCED"
        self.base_url = "https://wallhaven.cc/api/v1/search"
        self.cookies = dict()
        os.makedirs('Wallhaven', exist_ok=True)

    def get_category(self):
        """
        获取用户选择的壁纸类别
        显示所有可用的类别选项
        返回对应的类别代码
        
        Returns:
            str: 类别代码（如 '111' 表示所有类别）
        """
        print('''
        ****************************************************************
                                Category Codes

        all     - 所有壁纸
        general - 常规壁纸
        anime   - 动漫壁纸
        people  - 人物壁纸
        ga      - 常规和动漫壁纸
        gp      - 常规和人物壁纸
        ****************************************************************
        ''')
        ccode = input('输入类别: ').lower()
        ctags = {'all':'111', 'anime':'010', 'general':'100', 'people':'001', 'ga':'110', 'gp':'101' }
        return ctags[ccode]

    def get_purity(self):
        """
        获取用户选择的壁纸纯度级别
        显示所有可用的纯度选项
        返回对应的纯度代码
        
        Returns:
            str: 纯度代码（如 '100' 表示 SFW）
        """
        print('''
        ****************************************************************
                                Purity Codes

        sfw     - 适合工作场合的壁纸
        sketchy - 有争议的壁纸
        nsfw    - 不适合工作场合的壁纸
        ws      - 包含适合工作场合和有争议的壁纸
        wn      - 包含适合工作场合和不适合工作场合的壁纸
        sn      - 包含有争议和不适合工作场合的壁纸
        all     - 包含所有类型的壁纸
        ****************************************************************
        ''')
        pcode = input('输入纯度: ')
        ptags = {'sfw':'100', 'sketchy':'010', 'nsfw':'001', 'ws':'110', 'wn':'101', 'sn':'011', 'all':'111'}
        return ptags[pcode]

    def get_sorting(self):
        """
        获取用户选择的排序方式
        显示所有可用的排序选项
        返回对应的排序代码
        
        Returns:
            str: 排序代码（如 'relevance' 表示按相关性排序）
        """
        print('''
        ****************************************************************
                                Sorting Codes
        relevance - 相关性
        random    - 随机
        dateadded - 添加日期
        views     - 浏览量
        favorites - 收藏量
        toplist   - 排行榜
        hot       - 热门
        ****************************************************************
        ''')
        scode = input('输入排序: ')
        stags = {'relevance':'relevance', 'random':'random', 'dateadded':'date_added', 
                'views':'views', 'favorites':'favorites', 'toplist':'toplist', 'hot':'hot'}
        return stags[scode]

    def build_category_url(self):
        """
        构建按类别下载的 API URL
        组合类别和纯度参数
        
        Returns:
            str: 完整的 API URL
        """
        cat = self.get_category()
        pur = self.get_purity()
        return f"{self.base_url}?apikey={self.api_key}&categories={cat}&purity={pur}"

    def build_latest_url(self):
        """
        构建下载最新壁纸的 API URL
        设置时间范围为最近一个月
        组合排序参数
        
        Returns:
            str: 完整的 API URL
        """
        print('下载最新')
        top_list_range = '1M'
        sort = self.get_sorting()
        return f"{self.base_url}?apikey={self.api_key}&topRange={top_list_range}&sorting={sort}"

    def build_search_url(self):
        """
        构建搜索下载的 API URL
        处理用户输入的搜索关键词
        组合类别、纯度和排序参数
        
        Returns:
            str: 完整的 API URL
        """
        query = input('输入搜索标签 (多个标签用逗号分隔): ')
        keywords = [k.strip() for k in query.split(',')]
        encoded_query = '+'.join(urllib.parse.quote_plus(k) for k in keywords)
        
        cat = self.get_category()
        pur = self.get_purity()
        sort = self.get_sorting()
        
        return (f"{self.base_url}?apikey={self.api_key}"
                f"&q={encoded_query}"
                f"&categories={cat}"
                f"&purity={pur}"
                f"&sorting={sort}")

    def download_page(self, url, page_id, total_image):
        """
        下载指定页面的壁纸
        
        Args:
            url (str): 基础 API URL
            page_id (int): 要下载的页面编号
            total_image (str): 总图片数量（用于显示进度）
            
        功能：
        1. 请求指定页面的壁纸数据
        2. 解析返回的 JSON 数据
        3. 下载每张壁纸
        4. 处理下载过程中的各种异常
        5. 统计下载结果
        """
        full_url = f"{url}&page={page_id}"
        print(f"\n正在请求第 {page_id} 页, URL: {full_url}")
        
        try:
            urlreq = requests.get(full_url, cookies=self.cookies)
            urlreq.raise_for_status()  # 检查HTTP状态码
            
            if not urlreq.content:
                print(f"错误: 第 {page_id} 页API返回为空")
                return
                
            pages_images = json.loads(urlreq.content)
            if "data" not in pages_images:
                print(f"错误: 第 {page_id} 页API返回数据格式错误")
                print("返回内容:", pages_images)
                return
                
            page_data = pages_images["data"]
            if not page_data:
                print(f"提示: 第 {page_id} 页没有找到任何图片")
                return

            print(f"找到 {len(page_data)} 张图片")
            success_count = 0
            skip_count = 0
            fail_count = 0

            for i, image_data in enumerate(page_data):
                current_image = ((page_id - 1) * 24) + (i + 1)
                try:
                    image_url = image_data["path"]
                except KeyError:
                    print(f"错误: 第 {current_image} 张图片数据格式错误")
                    fail_count += 1
                    continue
                
                filename = os.path.basename(image_url)
                save_path = os.path.join('Wallhaven', filename)
                
                if os.path.exists(save_path):
                    print(f"跳过: {filename} 已存在 - {current_image} / {total_image}")
                    skip_count += 1
                    continue

                try:
                    imgreq = requests.get(image_url, cookies=self.cookies, timeout=30)
                    imgreq.raise_for_status()
                    
                    if imgreq.status_code == 200:
                        with open(save_path, 'wb') as image_file:
                            image_file.write(imgreq.content)
                        print(f"成功: 下载 {filename} - {current_image} / {total_image}")
                        success_count += 1
                    else:
                        print(f"失败: 无法下载 {filename} - 状态码: {imgreq.status_code}")
                        fail_count += 1
                except requests.exceptions.Timeout:
                    print(f"超时: 下载 {filename} 超时")
                    fail_count += 1
                except requests.exceptions.RequestException as e:
                    print(f"错误: 下载 {filename} 失败 - {str(e)}")
                    fail_count += 1
                except Exception as e:
                    print(f"未知错误: 下载 {filename} 失败 - {str(e)}")
                    fail_count += 1

            # 打印本页下载统计
            print(f"\n第 {page_id} 页下载统计:")
            print(f"- 成功下载: {success_count} 张")
            print(f"- 已存在跳过: {skip_count} 张")
            print(f"- 下载失败: {fail_count} 张")
            
        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: 第 {page_id} 页请求失败")
            print(f"错误信息: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: 第 {page_id} 页数据格式错误")
            print(f"错误信息: {str(e)}")
            if urlreq and urlreq.content:
                print("返回内容:", urlreq.content[:500])  # 只打印前500个字符
        except Exception as e:
            print(f"未知错误: 第 {page_id} 页处理失败")
            print(f"错误信息: {str(e)}")

def main():
    """
    主函数
    提供用户交互界面
    根据用户选择执行不同的下载模式
    """
    api = WallhavenAPI()
    
    choice = input('''选择您要下载图像的方式:
    
    输入 "category" 以从指定类别下载壁纸
    输入 "latest" 下载最新壁纸
    输入 "search" 以从搜索中下载壁纸

    输入选择: ''').lower()
    
    while choice not in ['category', 'latest', 'search']:
        if choice is not None:
            print('您输入的值不正确.')
        choice = input('输入选择: ')

    # 根据选择构建基础URL
    if choice == 'category':
        base_url = api.build_category_url()
    elif choice == 'latest':
        base_url = api.build_latest_url()
    else:  # search
        base_url = api.build_search_url()

    # 下载页面
    page_count = int(input('您要下载多少页: '))
    total_images = str(24 * page_count)
    print('要下载的壁纸数量: ' + total_images)
    
    for page in range(1, page_count + 1):
        api.download_page(base_url, page, total_images)

if __name__ == '__main__':
    main()

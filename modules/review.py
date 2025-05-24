"""
Created on Sun May 11 10:38:40 2025
 
@改author: x林俐婷

商品留言分析器(api)：# review.py

檔案開啟修改紀錄：
0522 5:03 pm. ver(by 洪力安)（直截爬前台）

0523 
11:03 am.  (by 洪力安)＋例外處理，啟動失敗時清楚顯示問題
12:03 am.  改版：api

0524 
11:12 am. 改版：api。class版本（chatGPT生成）
02:12 pm.  Cookie 
"""
'''


from config.config import settings
from view.utils import timer
from view.check_ip_pool import CheckIPAddress
from view.api_v4_get_shop_detail import ShopDetailCrawler
from view.api_v4_get_product_detail import ProductDetailCrawler


import logging


'''
import streamlit as st
import asyncio
import aiohttp
import logging
import pandas as pd
from datetime import datetime
from pydantic import BaseModel, ValidationError
import matplotlib.pyplot as plt
import seaborn as sns
import re
import json

# 設定 logging 格式與等級
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================= 使用說明 =================
def show_cookie_instructions():
    st.markdown("""
    (最後編輯：20250524 08:41pm)
    
**如何取得 Shopee Cookie：**

1. 開啟瀏覽器（建議 Chrome），進入 [蝦皮首頁](https://shopee.tw)。
2. 點右上角「登入」並完成登入（可用 Google、FB、手機號等方式）。
3. 登入後，按下鍵盤 `F12` 或點右鍵選「檢查」打開開發者工具。
4. 點選「Application」（中文可能是「應用程式」）分頁，再點左側「Cookies」展開，選擇 `https://shopee.tw`。
5. 在右側看到多組 cookie（如 SPC_EC、SPC_U、SPC_F 等），選一組全部複製（可全部 Ctrl+A, Ctrl+C），貼到下方「Cookie」欄位。
        cookie複製過來的格式：SPC_F=xxxxxx; SPC_U=yyyyyy; SPC_EC=zzzzzz; SPC_R_T_ID=aaaaaa; SPC_R_T_IV=bbbbbb; SPC_T_ID=cccccc; SPC_T_IV=dddddd; ...
        （可以請AI幫忙檢查複製內容是否符合格式）
6. 若用 Chrome 擴充套件如 EditThisCookie 也可一鍵複製所有 cookie。

> **警告：** 沒有貼 全新、馬上複製下來的Cookie，基本上跑不動。沒貼的話預設會用內建 Cookie（成功率0.01，因為我的帳號已經被蝦皮偵測到ㄌ）。

---
""", unsafe_allow_html=True)


# ================= 爬＆輸出檔案 =================

# 留言資料模型
class CommentData(BaseModel):
    cmtid: int
    author_username: str
    comment: str
    rating_star: int
    ctime: int
    comment_time_str: str  # 轉換後的時間字串

    @classmethod
    def from_api(cls, data: dict):
        ctime = data.get("ctime", 0)
        comment_time_str = datetime.utcfromtimestamp(ctime).strftime("%Y-%m-%d %H:%M:%S")
        return cls(
            cmtid=data.get("cmtid"),
            author_username=data.get("author_username", "匿名"),
            comment=data.get("comment", ""),
            rating_star=data.get("rating_star", 0),
            ctime=ctime,
            comment_time_str=comment_time_str,
        )

class ShopeeCommentCrawler:
    def __init__(self, cookie: str = "", product_url: str = "", proxy: str = None, base_api=None, retries=3, retry_delay=2):
        self.base_api = base_api or "https://shopee.tw/api/v2/item/get_ratings"
        self.headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "af-ac-enc-dat": "ed556fa01579fe18",
            "af-ac-enc-sz-token": "LFu9USeoQqRsXbyJoI5vkA==|6OZoc7UzEUXdy3tJvq1NoCnC6V/xwsVebuWnTPWwGTUff08xGmbMUKjqjp7r8/UCcbVyaktThVZcVPQYugo=|D/Ep+pK9EqptTiDz|08|3",
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "x-api-source": "pc",
            "x-requested-with": "XMLHttpRequest",
            "x-sap-ri": "f86e31684cf9afa65bc43f3a0601fecd62195ec66b4defec64d3",
            "x-sap-sec": "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",
            "x-shopee-language": "zh-Hant",
            "x-sz-sdk-version": "1.12.19"
        }
        # 依用戶傳入的網址填 referer
        if product_url:
            self.headers["referer"] = product_url

        # 依用戶 cookie 填 cookie
        if cookie:
            # 先去除 cookie 換行
            cookie = cookie.replace('\n', '').replace('\r', '')
            self.headers["cookie"] = cookie
            # 自動取得 csrftoken 補進 x-csrftoken
            match = re.search(r'csrftoken=([^;]+)', cookie)
            if match:
                self.headers["x-csrftoken"] = match.group(1)
            elif "x-csrftoken" in self.headers:
                del self.headers["x-csrftoken"]
        else:
            # 預設 cookie
            self.headers["cookie"] = "SPC_F=fXCf8Ud1RioYc8yRE1TmF7B5AWSaVHru; SPC_U=1549828388;"
            if "x-csrftoken" in self.headers:
                del self.headers["x-csrftoken"]

        self.proxy = proxy
        self.retries = retries
        self.retry_delay = retry_delay
        self.comments = []

        # 統一防呆，headers 裡面所有 value 都去除 \n \r
        for k, v in self.headers.items():
            if isinstance(v, str):
                self.headers[k] = v.replace('\n', '').replace('\r', '')

    

    async def fetch_comments(self, session, shopid, itemid, offset=0, limit=50):
        params = {
            "filter": 0,
            "flag": 1,
            "itemid": itemid,
            "limit": limit,
            "offset": offset,
            "shopid": shopid,
            "type": 0,
        }
        for attempt in range(1, self.retries + 1):
            resp = None
            api_raw_response = None
            try:
                async with session.get(self.base_api, params=params, proxy=self.proxy, timeout=10, headers=self.headers) as resp:
                    status = resp.status
                    api_raw_response = await resp.text()
                    if status == 403:
                        logger.error("HTTP 403 Forbidden：可能是IP被蝦皮封鎖、Cookie失效、或Header不完整")
                        return {"error": "HTTP 403 Forbidden：可能是IP被蝦皮封鎖、Cookie失效、或Header不完整", "api_raw_response": api_raw_response}
                    elif status == 429:
                        logger.error("HTTP 429 Too Many Requests：被蝦皮暫時限制，請降低抓取頻率或更換IP")
                        return {"error": "HTTP 429 Too Many Requests：被蝦皮暫時限制，請降低抓取頻率或更換IP", "api_raw_response": api_raw_response}
                    elif status == 401:
                        logger.error("HTTP 401 Unauthorized：Cookie 無效或未登入")
                        return {"error": "HTTP 401 Unauthorized：Cookie 無效或未登入", "api_raw_response": api_raw_response}
                    elif status != 200:
                        logger.warning(f"HTTP error {status} for offset {offset}, attempt {attempt}/{self.retries}")
                        return {"error": f"HTTP error code {status}，請檢查網路或Cookie/Header設置", "api_raw_response": api_raw_response}
                    else:
                        try:
                            data = json.loads(api_raw_response)
                        except Exception as e:
                            logger.error(f"API回應不是有效JSON：{e}")
                            return {"error": f"API回應不是有效JSON：{e}", "api_raw_response": api_raw_response}
                        if "data" not in data or data["data"] is None:
                            logger.error(f"API原始回應內容：{api_raw_response}")
                            logger.error("API回傳格式異常，可能是Header不足或Cookie失效")
                            return {"error": "API回傳格式異常，可能是Header不足或Cookie失效", "api_raw_response": api_raw_response}
                        if "ratings" in data["data"] and not data["data"]["ratings"]:
                            logger.info("API正常回傳但無留言，可能是商品無留言或留言未公開")
                            return {"error": "API正常回傳但無留言，可能是商品無留言或留言未公開", "api_raw_response": api_raw_response}
                        return {"data": data, "api_raw_response": api_raw_response}
            except Exception as e:
                if resp is not None:
                    try:
                        api_raw_response = await resp.text()
                        logger.error(f"API原始回應內容（非 JSON）：{api_raw_response}")
                    except Exception as ee:
                        logger.error(f"取得 resp.text() 時又發生錯誤：{ee}")
                else:
                    logger.error(f"尚未取得 response (resp is None)，可能是連線失敗或網路問題。Exception: {e}")
                logger.warning(f"Exception on fetch_comments attempt {attempt}/{self.retries} for offset {offset}: {e}")
            await asyncio.sleep(self.retry_delay)
        logger.error(f"Failed to fetch comments after {self.retries} attempts for offset {offset}")
        return {"error": "多次重試失敗，可能是網路問題或被蝦皮封鎖", "api_raw_response": api_raw_response}

    async def crawl_all_comments(self, shopid, itemid):
        api_raw_response = None
        async with aiohttp.ClientSession() as session:
            offset = 0
            limit = 50
            total_count = 1
            while offset < total_count:
                logger.info(f"Fetching comments offset {offset}")
                data = await self.fetch_comments(session, shopid, itemid, offset, limit)
                if isinstance(data, dict):
                    api_raw_response = data.get("api_raw_response", api_raw_response)
                    if "error" in data and data["error"]:
                        logger.error(f"⚠️ {data['error']}")
                        return self.comments, api_raw_response
                    data = data.get("data")
                if not data:
                    logger.error("⚠️ 蝦皮伺服器沒有回應，可能是被擋下（HTTP 錯誤或網路問題）")
                    return self.comments, api_raw_response

                total_count = data.get("data", {}).get("total", 0)
                ratings = data.get("data", {}).get("ratings", [])
                if not ratings:
                    logger.info("🔍 找不到任何留言，可能是商品沒有留言或未公開")
                    return self.comments, api_raw_response

                for rating in ratings:
                    try:
                        comment_obj = CommentData.from_api(rating)
                        self.comments.append(comment_obj.dict())
                    except ValidationError as ve:
                        logger.error(f"Validation error: {ve}")

                offset += limit
            logger.info(f"Total comments fetched: {len(self.comments)}")
        return self.comments, api_raw_response
    
    def analyze_comments(self):
        if not self.comments:
            logger.warning("無留言資料可分析")
            return None

        df = pd.DataFrame(self.comments)
        # 星等統計
        star_counts = df['rating_star'].value_counts().sort_index()
        logger.info("各星等留言數量：")
        logger.info(star_counts.to_string())

        # 留言時間趨勢圖
        df['comment_time_str'] = pd.to_datetime(df['comment_time_str'])
        df.set_index('comment_time_str', inplace=True)
        df_by_day = df.resample('D').size()

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(x=df_by_day.index, y=df_by_day.values, ax=ax)
        ax.set_title("留言時間趨勢（每日留言數）")
        ax.set_xlabel("日期")
        ax.set_ylabel("留言數")
        plt.tight_layout()

        return fig  # 回傳圖表

def run_async(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

    

def parse_shopee_url(url):
    m1 = re.search(r"i\.(\d+)\.(\d+)", url)
    m2 = re.search(r"product/(\d+)/(\d+)", url)
    if m1:
        return m1.group(1).strip(), m1.group(2).strip()
    elif m2:
        return m2.group(1).strip(), m2.group(2).strip()
    else:
        return None, None

async def main(product_url: str, cookie: str = "", proxy: str = None):
    shopid, itemid = parse_shopee_url(product_url)
    if not shopid or not itemid:
        error_msg = "❌ 無法解析商品網址，請確認格式為 https://shopee.tw/i.店家ID.商品ID 或 https://shopee.tw/product/店家ID/商品ID"
        logger.error(error_msg)
        return None, None, error_msg, None

    crawler = ShopeeCommentCrawler(cookie=cookie, product_url=product_url, proxy=proxy)
    # 下面這行要讓 crawl_all_comments 回傳 (comments, api_raw_response)
    comments, api_raw_response = await crawler.crawl_all_comments(shopid, itemid)

    if not comments or len(comments) == 0:
        return None, None, "❌ 未能成功取得留言，可能是商品被擋或沒有公開留言", api_raw_response

    try:
        fig = crawler.analyze_comments()
        df = pd.DataFrame(crawler.comments)
        return fig, df, None, api_raw_response  # 沒錯誤
    except Exception as e:
        logger.exception("分析過程發生錯誤")
        return None, None, f"❌ 分析留言時發生錯誤：{e}", api_raw_response

def run_review_report():
    st.header("🗣️ 蝦皮商品留言分析器")
    show_cookie_instructions()

    product_url = st.text_input("請輸入蝦皮商品網址（例如：https://shopee.tw/product/12345678/87654321 或 https://shopee.tw/i.12345678.87654321）")
    cookie = st.text_area(
        "請輸入 Cookie 字串（建議從瀏覽器複製貼上，熱門商品建議貼 Cookie，否則預設用內建 Cookie，成功率較低）",
        height=100
    )
    proxy = st.text_input("代理伺服器 Proxy（格式：http://IP:PORT，非必填）")
    
    cookie = cookie.replace('\n', '').replace('\r', '')




    if st.button("開始分析留言"):
        if not product_url:
            st.warning("請先輸入商品網址")
            return

        with st.spinner("分析中，請稍候..."):
            try:
                fig, df, error, api_raw_response = run_async(main(product_url, cookie, proxy))
                if error:
                    st.error(f"留言分析失敗：{error}")
                    st.expander("API 原始回應內容（debug用）").write(api_raw_response)
                    return
                if fig is None or df is None:
                    st.error("留言分析失敗：未知錯誤")
                    st.expander("API 原始回應內容（debug用）").write(api_raw_response)
                    return

                st.success("留言分析完成！")
                if fig is not None:
                    st.pyplot(fig)
                    plt.close(fig)
                st.subheader("留言樣本（前 10 筆）")
                if df is not None and not df.empty:
                    st.dataframe(df.head(10))
                    st.download_button("下載留言 CSV", data=df.to_csv(index=False).encode("utf-8-sig"),
                                       file_name="shopee_comments.csv", mime="text/csv")
                else:
                    st.warning("沒有留言樣本可顯示")
                st.expander("API 原始回應內容（debug用）").write(api_raw_response)
            except Exception as e:
                st.error(f"發生錯誤：{e}")

if __name__ == "__main__":
    run_review_report()
    
    
    
    

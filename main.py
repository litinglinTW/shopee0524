#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 11 10:48:00 2025

@author: cglinmacbook

名稱：蝦皮main.py


檔案開啟修改紀錄：
0520 08:27pm. 複製貼上新的
0524 
10:30am. 複製貼上新的
04:09pm. 加入商品留言分析器(api)：含有餅乾
0525 18:46
"""
import streamlit as st
import pandas as pd

from modules.login import login_page
from modules.restock_recommendation import generate_restock_recommendation
from modules.generate_purchase import generate_purchase_report
from modules.financial_report import run_financial_report
from modules.review import run_review_report


st.set_page_config(page_title="蝦皮財報分析工具", layout="wide")

st.title('蝦皮賣場管理工具 Shopee Assistant')


st.sidebar.title("📊 導覽選單")
page = st.sidebar.radio("請選擇頁面", [
    
    "財報分析",
    "商品留言分析器(api)",
    "補貨建議工具",
    "自動生成進貨紀錄"
])


def get_logged_in_driver():
    return st.session_state.get("driver")


#沒有自動登入功能，會被擋


#2
if page == "財報分析":
    st.title("📈 財報分析頁面")
    st.markdown("請依序上傳以下三個檔案：")

    pdf_file = st.file_uploader("PDF 財報檔案", type=["pdf"])
    excel_file = st.file_uploader("Excel 銷售報表", type=["xlsx"])
    template_file = st.file_uploader("Excel 財報模板檔案", type=["xlsx"])

    if st.button("開始分析財報"):
        if not pdf_file:
            st.error("❗ 請上傳 PDF 財報檔案")
        elif not excel_file:
            st.error("❗ 請上傳 Excel 銷售報表")
        elif not template_file:
            st.error("❗ 請上傳 Excel 財報模板")
        else:
            with st.spinner("分析與寫入資料中..."):
                result = run_financial_report(pdf_file, excel_file, template_file)

            if result["success"]:
                st.success(result["msg"])
                if "summary" in result:
                    st.subheader("撥款摘要")
                    st.write(result["summary"])
                if "sales" in result:
                    st.subheader("每日銷售額")
                    sales_df = pd.DataFrame(result["sales"], columns=["日期", "金額"])
                    st.dataframe(sales_df)
                if "report_bytes" in result and "sheet" in result:
                    st.download_button(
                        label="📥 下載財報 Excel 檔",
                        data=result["report_bytes"],
                        file_name=f"財報分析_{result['sheet']}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.error(result["msg"])
                st.subheader("PDF原文內容（debug用）")
                st.code(result.get("pdf_raw", ""))
                if "summary" in result:
                    st.subheader("撥款摘要（分析結果）")
                    st.write(result["summary"])
                if "sales" in result:
                    st.subheader("每日銷售額（分析結果）")
                    sales_df = pd.DataFrame(result["sales"], columns=["日期", "金額"])
                    st.dataframe(sales_df)

# 3. 熱銷商品分析
elif page == "商品留言分析器(api)":
    run_review_report()

#4
elif page == "補貨建議工具":
    st.title("📝 自動生成補貨建議")
    st.markdown("請上傳以下兩份報表")

    inventory_file = st.file_uploader("存貨報表（xlsx）", type=["xlsx"])
    sales_file = st.file_uploader("銷售報表（xlsx）", type=["xlsx"])

    if st.button("產生進貨建議"):
        if not inventory_file or not sales_file:
            st.error("❗ 請確認兩個檔案都已上傳")
        else:
            try:
                result = generate_restock_recommendation(inventory_file, sales_file)

                if result["success"]:
                    st.success("✅ 已產生進貨建議")
                    st.dataframe(result["data"])
                    st.download_button(
                        label="📥 下載建議 Excel",
                        data=result["bytes"],
                        file_name="進貨建議報表.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error(result["msg"])
            except Exception as e:
                st.error(f"🚨 發生錯誤：{e}")



#5
    
elif page == "自動生成進貨紀錄":
    st.title("📦 自動生成進貨紀錄報表")
    st.markdown("請依序上傳以下三個檔案：")

    purchase_file = st.file_uploader("1. 進貨報表（Excel 或 CSV）", type=["xlsx", "csv"])
    template_file = st.file_uploader("2. 進貨紀錄模板（Excel）", type=["xlsx"])
    mapping_file = st.file_uploader("3. 商品對應表 Mapping（Excel）", type=["xlsx"])

    if st.button("產生進貨紀錄報表"):
        if not purchase_file or not template_file or not mapping_file:
            st.error("❗ 請確認三個檔案都已上傳")
        else:
            with st.spinner("自動比對與產生報表中..."):
                try:
                    result = generate_purchase_report(purchase_file, template_file, mapping_file)

                    if result["success"]:
                        st.success(f"✅ 成功產出報表，工作表名稱：{result['sheet']}")
                        st.subheader("📋 預覽資料（前10筆）")
                        st.dataframe(result["preview"].head(10))

                        st.download_button(
                            label="📥 下載進貨紀錄 Excel",
                            data=result["report_bytes"],
                            file_name=f"進貨紀錄_{result['sheet']}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error(f"⚠️ 發生錯誤：{result['msg']}")

                except Exception as e:
                    st.error(f"🚨 報表處理失敗：{e}")

    else:
        st.info("請上傳三個檔案後，再按下上方按鈕開始生成報表。")



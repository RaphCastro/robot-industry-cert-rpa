from time import sleep
from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Images import Images
from RPA.Archive import Archive
import os

browser = Selenium()
http = HTTP()
tables = Tables()
pdf = PDF()
screenshot = Images()
archive = Archive()


def open_robot_order_website(url):
    browser.open_available_browser(url)
    browser.maximize_browser_window()
    browser.click_element("css:#root > header > div > ul > li:nth-child(2) > a")


def get_orders():
    url = "https://robotsparebinindustries.com/orders.csv"
    file_path = "orders.csv"
    http.download(url, file_path, overwrite=True)
    table = tables.read_table_from_csv(file_path)
    return table


def close_annoying_modal():
    try:
        browser.click_button_when_visible("css:button.btn.btn-dark")
        sleep(2.5)
    except Exception as e:
        print("Modal not found:", e)


def fill_the_form(row):
    browser.click_element_when_clickable("id:head")
    browser.select_from_list_by_value("id:head", row["Head"])
    browser.click_element_when_clickable(f"id:id-body-{row['Body']}")
    browser.input_text(
        "css:input.form-control[placeholder='Enter the part number for the legs']",
        row["Legs"],
    )
    browser.input_text("id:address", row["Address"])


def preview_robot():
    browser.click_button("id:preview")
    sleep(1.5)


def submit_order():
    try:
        browser.scroll_element_into_view("id:order")
        browser.click_button("id:order")
    except Exception:
        submit_order()


def store_receipt_as_pdf(order_number):
    receipt_path = f"output/receipts/receipt_{order_number}.pdf"
    os.makedirs(os.path.dirname(receipt_path), exist_ok=True)
    receipt_html = browser.get_element_attribute("id:receipt", "innerHTML")
    full_html = f"<html><body>{receipt_html}</body></html>"
    pdf.html_to_pdf(full_html, receipt_path)
    return receipt_path


def screenshot_robot(order_number):
    screenshot_path = f"output/screenshots/robot_{order_number}.png"
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    screenshot_path = browser.capture_element_screenshot(
        "id:robot-preview-image", screenshot_path
    )
    return screenshot_path


def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    pdf.add_files_to_pdf(files=[screenshot_path], target_document=pdf_path, append=True)


def go_to_order_another_robot():
    try:
        browser.click_button_when_visible("id:order-another")
    except Exception as e:
        print(f"An error ocurred: {e}")
        submit_order()
        go_to_order_another_robot()


def archive_receipts():
    receipts_path = "output/receipts"
    zip_path = "output/receipts_archive.zip"
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    archive.archive_folder_with_zip(receipts_path, zip_path)
    return zip_path


def main():
    orders = get_orders()
    open_robot_order_website("https://robotsparebinindustries.com")
    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        preview_robot()
        submit_order()
        print(f"Processed order: {order['Order number']}")
        pdf_path = store_receipt_as_pdf(order["Order number"])
        screenshot_path = screenshot_robot(order["Order number"])
        embed_screenshot_to_receipt(screenshot_path, pdf_path)
        go_to_order_another_robot()

    browser.close_browser()


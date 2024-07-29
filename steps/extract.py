from time import sleep
from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Images import Images
from RPA.Archive import Archive
import os

class RobotOrderAutomation:
    def __init__(self):
        self.browser = Selenium()
        self.http = HTTP()
        self.tables = Tables()
        self.pdf = PDF()
        self.screenshot = Images()
        self.archive = Archive()

    def open_robot_order_website(self, url):
        self.browser.open_available_browser(url)
        self.browser.maximize_browser_window()
        self.browser.click_element("css:#root > header > div > ul > li:nth-child(2) > a")

    def get_orders(self):
        url = "https://robotsparebinindustries.com/orders.csv"
        file_path = "orders.csv"
        self.http.download(url, file_path, overwrite=True)
        table = self.tables.read_table_from_csv(file_path)
        return table

    def close_annoying_modal(self):
        try:
            self.browser.click_button_when_visible("css:button.btn.btn-dark")
            sleep(2.5)
        except Exception as e:
            print("Modal not found:", e)

    def fill_the_form(self, row):
        self.browser.click_element_when_clickable("id:head")
        self.browser.select_from_list_by_value("id:head", row["Head"])
        self.browser.click_element_when_clickable(f"id:id-body-{row['Body']}")
        self.browser.input_text(
            "css:input.form-control[placeholder='Enter the part number for the legs']",
            row["Legs"],
        )
        self.browser.input_text("id:address", row["Address"])

    def preview_robot(self):
        self.browser.click_button("id:preview")
        sleep(1.5)

    def submit_order(self):
        try:
            self.browser.scroll_element_into_view("id:order")
            self.browser.click_button("id:order")
        except Exception:
            self.submit_order()

    def store_receipt_as_pdf(self, order_number, max_retries=20):
        retries = 0
        while retries < max_retries:
            try:
                receipt_path = f"output/receipts/receipt_{order_number}.pdf"
                os.makedirs(os.path.dirname(receipt_path), exist_ok=True)
                receipt_html = self.browser.get_element_attribute("id:receipt", "innerHTML")
                full_html = f"<html><body>{receipt_html}</body></html>"
                self.pdf.html_to_pdf(full_html, receipt_path)
                return receipt_path
            except Exception as e:
                print(f"An error occurred while storing receipt as PDF: {e}")
                retries += 1
                if retries >= max_retries:
                    print(f"Failed to store receipt as PDF after {max_retries} attempts")
                    break
                self.submit_order()
                print(f"Retrying... ({retries}/{max_retries})")

    def screenshot_robot(self, order_number):
        screenshot_path = f"output/screenshots/robot_{order_number}.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        screenshot_path = self.browser.capture_element_screenshot(
            "id:robot-preview-image", screenshot_path
        )
        return screenshot_path

    def embed_screenshot_to_receipt(self, screenshot_path, pdf_path):
        self.pdf.add_files_to_pdf(files=[screenshot_path], target_document=pdf_path, append=True)

    def go_to_order_another_robot(self):
        try:
            self.browser.click_button_when_visible("id:order-another")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.submit_order()
            self.go_to_order_another_robot()

    def archive_receipts(self):
        receipts_path = "output/receipts"
        zip_path = "output/receipts_archive.zip"
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)
        self.archive.archive_folder_with_zip(receipts_path, zip_path)
        return zip_path

    def execute(self):
        orders = self.get_orders()
        self.open_robot_order_website("https://robotsparebinindustries.com")
        for order in orders:
            self.close_annoying_modal()
            self.fill_the_form(order)
            self.preview_robot()
            self.submit_order()
            print(f"Processed order: {order['Order number']}")
            pdf_path = self.store_receipt_as_pdf(order["Order number"])
            screenshot_path = self.screenshot_robot(order["Order number"])
            self.embed_screenshot_to_receipt(screenshot_path, pdf_path)
            self.go_to_order_another_robot()
        
        self.archive_receipts()
        self.browser.close_browser()


if __name__ == "__main__":
    robot_order_automation = RobotOrderAutomation()
    robot_order_automation.main()

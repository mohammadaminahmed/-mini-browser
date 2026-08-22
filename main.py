import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar

from html.parser import HTMLParser

import os
import sys


# ============================================================
# HTML PARSER
# ============================================================

class WebParser(HTMLParser):

    def __init__(self):
        super().__init__()

        self.links = []
        self.images = []

        self.title = ""
        self.inside_title = False

    # --------------------------------------------------------
    # Detect HTML start tags
    # --------------------------------------------------------

    def handle_starttag(self, tag, attrs):

        attrs = dict(attrs)

        # <title>
        if tag.lower() == "title":

            self.inside_title = True

        # <a href="...">
        elif tag.lower() == "a":

            href = attrs.get("href")

            if href:

                self.links.append(href)

        # <img src="...">
        elif tag.lower() == "img":

            src = attrs.get("src")

            if src:

                self.images.append(src)

    # --------------------------------------------------------
    # Read text inside title
    # --------------------------------------------------------

    def handle_data(self, data):

        if self.inside_title:

            self.title += data.strip()

    # --------------------------------------------------------
    # Detect </title>
    # --------------------------------------------------------

    def handle_endtag(self, tag):

        if tag.lower() == "title":

            self.inside_title = False


# ============================================================
# MINI BROWSER
# ============================================================

class MiniBrowser:

    def __init__(self):

        # ----------------------------------------------------
        # Cookie storage
        # ----------------------------------------------------

        self.cookie_jar = http.cookiejar.CookieJar()

        # ----------------------------------------------------
        # Create HTTP/HTTPS opener
        # ----------------------------------------------------

        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(
                self.cookie_jar
            )
        )

        # ----------------------------------------------------
        # Browser User-Agent
        # ----------------------------------------------------

        self.opener.addheaders = [
            (
                "User-Agent",
                "Mozilla/5.0 MiniBrowser/1.0"
            )
        ]

        # ----------------------------------------------------
        # History
        # ----------------------------------------------------

        self.history = []

        # ----------------------------------------------------
        # Current page
        # ----------------------------------------------------

        self.current_url = None

        # ----------------------------------------------------
        # Download directory
        # ----------------------------------------------------

        self.download_folder = "downloads"

        os.makedirs(
            self.download_folder,
            exist_ok=True
        )

    # ========================================================
    # OPEN URL
    # ========================================================

    def open_page(self, url):

        try:

            # ------------------------------------------------
            # Add protocol if user forgot it
            # ------------------------------------------------

            if not url.startswith(
                ("http://", "https://")
            ):

                url = "https://" + url

            print("\n" + "=" * 70)

            print("REQUEST")

            print("=" * 70)

            print("URL:", url)

            # ------------------------------------------------
            # Create request
            # ------------------------------------------------

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent":
                    "Mozilla/5.0 MiniBrowser/1.0"
                }
            )

            # ------------------------------------------------
            # Send request
            #
            # urllib supports HTTPS.
            # Redirects are handled automatically.
            # ------------------------------------------------

            response = self.opener.open(
                request,
                timeout=30
            )

            # ------------------------------------------------
            # Final URL
            #
            # Important for redirects.
            # ------------------------------------------------

            final_url = response.geturl()

            # ------------------------------------------------
            # Status Code
            # ------------------------------------------------

            status_code = response.status

            print("\nSTATUS CODE")

            print(status_code)

            # ------------------------------------------------
            # Check redirect
            # ------------------------------------------------

            if final_url != url:

                print("\nREDIRECT")

                print("From:", url)

                print("To:", final_url)

            # ------------------------------------------------
            # Response Headers
            # ------------------------------------------------

            print("\n" + "=" * 70)

            print("RESPONSE HEADERS")

            print("=" * 70)

            for name, value in response.headers.items():

                print(
                    f"{name}: {value}"
                )

            # ------------------------------------------------
            # Content Type
            # ------------------------------------------------

            content_type = response.headers.get(
                "Content-Type",
                ""
            )

            print("\nCONTENT TYPE")

            print(content_type)

            # ------------------------------------------------
            # Read response body
            # ------------------------------------------------

            data = response.read()

            # ------------------------------------------------
            # If not HTML
            # ------------------------------------------------

            if "text/html" not in content_type.lower():

                print(
                    "\nThis resource is not HTML."
                )

                self.current_url = final_url

                self.history.append(
                    final_url
                )

                return

            # ------------------------------------------------
            # Decode HTML
            # ------------------------------------------------

            html = data.decode(
                "utf-8",
                errors="ignore"
            )

            # ------------------------------------------------
            # Parse HTML
            # ------------------------------------------------

            parser = WebParser()

            parser.feed(html)

            # ------------------------------------------------
            # Page Title
            # ------------------------------------------------

            print("\n" + "=" * 70)

            print("PAGE TITLE")

            print("=" * 70)

            if parser.title:

                print(
                    parser.title
                )

            else:

                print(
                    "No title found."
                )

            # ------------------------------------------------
            # Save current URL
            # ------------------------------------------------

            self.current_url = final_url

            # ------------------------------------------------
            # History
            # ------------------------------------------------

            if not self.history:

                self.history.append(
                    final_url
                )

            else:

                if self.history[-1] != final_url:

                    self.history.append(
                        final_url
                    )

            # ------------------------------------------------
            # Display links
            # ------------------------------------------------

            print("\n" + "=" * 70)

            print("LINKS")

            print("=" * 70)

            if parser.links:

                for number, link in enumerate(
                    parser.links,
                    start=1
                ):

                    full_link = urllib.parse.urljoin(
                        final_url,
                        link
                    )

                    print(
                        f"{number}. {full_link}"
                    )

            else:

                print(
                    "No links found."
                )

            # ------------------------------------------------
            # Display images
            # ------------------------------------------------

            print("\n" + "=" * 70)

            print("IMAGES")

            print("=" * 70)

            if parser.images:

                for number, image in enumerate(
                    parser.images,
                    start=1
                ):

                    full_image = urllib.parse.urljoin(
                        final_url,
                        image
                    )

                    print(
                        f"{number}. {full_image}"
                    )

            else:

                print(
                    "No images found."
                )

            print("\n" + "=" * 70)

        except urllib.error.HTTPError as error:

            print("\nHTTP ERROR")

            print(
                "Status:",
                error.code
            )

        except urllib.error.URLError as error:

            print("\nURL ERROR")

            print(
                error.reason
            )

        except TimeoutError:

            print(
                "\nConnection timed out."
            )

        except Exception as error:

            print("\nERROR")

            print(error)

    # ========================================================
    # SHOW HISTORY
    # ========================================================

    def show_history(self):

        print("\n" + "=" * 70)

        print("BROWSER HISTORY")

        print("=" * 70)

        if not self.history:

            print(
                "History is empty."
            )

            return

        for number, url in enumerate(
            self.history,
            start=1
        ):

            print(
                f"{number}. {url}"
            )

    # ========================================================
    # SHOW COOKIES
    # ========================================================

    def show_cookies(self):

        print("\n" + "=" * 70)

        print("COOKIES")

        print("=" * 70)

        cookies = list(
            self.cookie_jar
        )

        if not cookies:

            print(
                "No cookies stored."
            )

            return

        for cookie in cookies:

            print(
                f"Name: {cookie.name}"
            )

            print(
                f"Value: {cookie.value}"
            )

            print(
                f"Domain: {cookie.domain}"
            )

            print("-" * 50)

    # ========================================================
    # DOWNLOAD IMAGE
    # ========================================================

    def download_image(self, image_url):

        try:

            if not image_url.startswith(
                ("http://", "https://")
            ):

                image_url = urllib.parse.urljoin(
                    self.current_url,
                    image_url
                )

            print(
                "\nDownloading:"
            )

            print(
                image_url
            )

            request = urllib.request.Request(
                image_url,
                headers={
                    "User-Agent":
                    "Mozilla/5.0 MiniBrowser/1.0"
                }
            )

            response = self.opener.open(
                request,
                timeout=30
            )

            data = response.read()

            # ------------------------------------------------
            # Extract filename
            # ------------------------------------------------

            parsed = urllib.parse.urlparse(
                image_url
            )

            filename = os.path.basename(
                parsed.path
            )

            if not filename:

                filename = "image.bin"

            # ------------------------------------------------
            # Remove query parameters
            # ------------------------------------------------

            filename = filename.split("?")[0]

            filepath = os.path.join(
                self.download_folder,
                filename
            )

            # ------------------------------------------------
            # Save image
            # ------------------------------------------------

            with open(
                filepath,
                "wb"
            ) as file:

                file.write(data)

            print(
                "Saved to:",
                filepath
            )

        except Exception as error:

            print(
                "Image download error:",
                error
            )

    # ========================================================
    # DOWNLOAD ALL IMAGES
    # ========================================================

    def download_images_from_page(
        self,
        url
    ):

        try:

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent":
                    "Mozilla/5.0 MiniBrowser/1.0"
                }
            )

            response = self.opener.open(
                request,
                timeout=30
            )

            content_type = response.headers.get(
                "Content-Type",
                ""
            )

            if "text/html" not in content_type.lower():

                print(
                    "Page is not HTML."
                )

                return

            html = response.read().decode(
                "utf-8",
                errors="ignore"
            )

            parser = WebParser()

            parser.feed(html)

            if not parser.images:

                print(
                    "No images found."
                )

                return

            for image in parser.images:

                image_url = urllib.parse.urljoin(
                    url,
                    image
                )

                self.download_image(
                    image_url
                )

        except Exception as error:

            print(
                "Error:",
                error
            )

    # ========================================================
    # SHOW CURRENT PAGE
    # ========================================================

    def show_current_page(self):

        if self.current_url:

            print(
                "\nCurrent page:",
                self.current_url
            )

        else:

            print(
                "\nNo page opened."
            )


# ============================================================
# MAIN MENU
# ============================================================

def main():

    browser = MiniBrowser()

    while True:

        print("\n")
        print("=" * 70)
        print("                 PYTHON MINI BROWSER")
        print("=" * 70)

        print("1. Open URL")
        print("2. Show History")
        print("3. Show Cookies")
        print("4. Show Current Page")
        print("5. Download Images From Current Page")
        print("6. Exit")

        print("=" * 70)

        choice = input(
            "Choose an option: "
        ).strip()

        # ----------------------------------------------------
        # Open URL
        # ----------------------------------------------------

        if choice == "1":

            url = input(
                "\nEnter URL: "
            ).strip()

            if url:

                browser.open_page(
                    url
                )

        # ----------------------------------------------------
        # History
        # ----------------------------------------------------

        elif choice == "2":

            browser.show_history()

        # ----------------------------------------------------
        # Cookies
        # ----------------------------------------------------

        elif choice == "3":

            browser.show_cookies()

        # ----------------------------------------------------
        # Current page
        # ----------------------------------------------------

        elif choice == "4":

            browser.show_current_page()

        # ----------------------------------------------------
        # Download images
        # ----------------------------------------------------

        elif choice == "5":

            if browser.current_url:

                browser.download_images_from_page(
                    browser.current_url
                )

            else:

                print(
                    "Open a page first."
                )

        # ----------------------------------------------------
        # Exit
        # ----------------------------------------------------

        elif choice == "6":

            print(
                "\nGoodbye!"
            )

            break

        else:

            print(
                "\nInvalid choice."
            )


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    main()
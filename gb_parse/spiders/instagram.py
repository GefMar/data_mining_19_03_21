import json
import scrapy


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    start_urls = ["https://www.instagram.com/"]
    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    _tag_path = "/explore/tags/"

    def __init__(self, username, enc_password, tags, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.username = username
        self.enc_password = enc_password
        self.tags = tags

    def auth(self, response):
        js_data = self.js_data_extract(response)
        return scrapy.FormRequest(
            self._login_url,
            method="POST",
            callback=self.parse,
            formdata={"username": self.username, "enc_password": self.enc_password,},
            headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
        )

    def parse(self, response):
        if b"json" in response.headers["Content-Type"]:
            if response.json().get("authenticated"):
                for tag in self.tags:
                    yield response.follow(f"{self._tag_path}{tag}/", callback=self.tag_parse)
        else:
            yield self.auth(response)

    def tag_parse(self, response):
        print(1)

    def js_data_extract(self, response):
        script = response.xpath(
            '//body/script[contains(text(), "window._sharedData")]/text()'
        ).extract_first()
        return json.loads(script[script.index("{") : -1])

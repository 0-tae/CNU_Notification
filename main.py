import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
from apscheduler.schedulers.background import BackgroundScheduler
from domain.slack.slack_api import slackAPI
from domain.slack.slack_auth import slack_auth
from view.util.block_builder import block_builder
import util.common_util as util

import time

CHANNEL_ID = slack_auth.get_from_credential("channel_id")
NOTIFICATION_DICT = [
    {
        "url": "bachelor.do",
        "category": "학사 공지",
    },
    {
        "url": "notice.do",
        "category": "교내 일반 소식",
    },
    {
        "url": "job.do",
        "category": "교외 활동, 인턴, 취업 소식",
    },
    {
        "url": "project.do",
        "category": "사업단 소식",
    },
    {
        "url": "cse.do",
        "category": "우리학부 News",
    },
]
POSTS = []


def make_block(category, notification_title, notification_url):
    return block_builder.compose(
        blocks=(
            block_builder.create_block_header(f"업로드된 {category}"),
            block_builder.create_block_divider(),
            block_builder.create_single_block_section("*공지 제목*"),
            block_builder.create_single_block_section(f"{notification_title}"),
            block_builder.create_single_block_section("*바로 가기*"),
            block_builder.create_single_block_section(f"{notification_url}"),
        )
    )


# Scheduled Funtion
def get_notification():
    for notification in NOTIFICATION_DICT:
        request_url = (
            f"https://computer.cnu.ac.kr/computer/notice/{notification.get('url')}"
        )
        notification_category = notification.get("category")
        response = requests.get(request_url)
        response.raise_for_status()
        soup = bs(response.text, "html.parser")

        # 오늘 날짜
        today = datetime.today().strftime("%Y.%m.%d")[2:]

        # 공지 날짜
        date_list = list(
            enumerate(
                map(
                    (lambda e: e.text.strip()),
                    soup.select("td.b-td-left div.b-m-con span.b-date"),
                )
            )
        )

        # 공지 번호
        post_num_list = list(
            enumerate(map((lambda e: e.text.strip()), soup.select("td.b-num-box")))
        )

        # 공지 내용
        content_list = list(
            enumerate(
                map(
                    (
                        lambda e: {
                            "title": e.attrs["title"],
                            "href": request_url + e.attrs["href"],
                        }
                    ),
                    soup.select("td.b-td-left div.b-title-box a"),
                )
            )
        )

        for index, date_element in enumerate(date_list):
            date_text = date_element[-1]
            post_num = post_num_list[index][-1]
            content = content_list[index][-1]

            # 공지가 오늘 날짜이면서, 이미 갱신된 POST가 아닐 경우에만
            if date_text == today and not post_num in POSTS:
                util.debug_message(f"content: {content}")
                util.debug_message(
                    f"today: {today}, posted_date: {date_text}, num: {post_num}"
                )
                POSTS.append(post_num)
                title = content["title"]
                url = content["href"]
                block = make_block(
                    category=notification_category,
                    notification_title=title,
                    notification_url=url,
                )
                response_text = slackAPI.post_message(
                    channel_id=CHANNEL_ID,
                    text=f"오늘의 {notification_category} 입니다.",
                    blocks=block,
                )
                util.debug_message(response_text)


def main():
    sched = BackgroundScheduler()
    sched.add_job(get_notification, "interval", seconds=300)
    sched.add_job(POSTS.clear, "cron", hour="12")
    sched.start()

    util.debug_message("Server Start")
    while True:
        time.sleep(0.001)


if __name__ == "__main__":
    main()

from tistory_util import *
import requests
from typing import List
import asyncio
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import SystemMessage

from langchain.utilities import DuckDuckGoSearchAPIWrapper
import tiktoken
import os
import openai
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
#openai.api_key = os.environ["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"]
openai.api_key = "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"

###########################################################
# Helpers
def build_summarizer(llm):
    system_message = "assistant는 user의 내용을 bullet point 5줄로 요약하라. 영어인 경우 한국어로 전문가 수준으로 번역해서 자연스럽게 요약하라. 농담을 섞은 친근한 말투로 작성하라."
    system_message_prompt = SystemMessage(content=system_message)

    human_template = "{text}\n---\n위 내용을 bullet point로 5줄로 한국어로 자연스럽게 전문가 수준으로 요약하라. 농담을 섞은 친근한 말투로 작성하라."
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                    human_message_prompt])

    chain = LLMChain(llm=llm, prompt=chat_prompt)
    return chain


def truncate_text(text, max_tokens=3000):
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:  # 토큰 수가 이미 3000 이하라면 전체 텍스트 반환
        return text
    return enc.decode(tokens[:max_tokens])


def clean_html(url):
    while (True):
        try:
            session = requests.Session()
            retry = Retry(connect=10, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            response = session.get(url)
        # response = requests.get(url)
            # requests 오류 시 아래 urlopen 을 사용 하여 data 불러 오는데 끊김이 없도록 실행
        except:
            page = urlopen(url)
            # bytes to string
            doc = page.read().decode('utf-8', 'ignore')
            # string to dictionary
            dic = json.loads(doc)
            result_dict = dic['result']['trades']

        else:
            break


    soup = BeautifulSoup(response.text, 'html.parser')
    text = ' '.join(soup.stripped_strings)
    return text


def task(search_result):
    title = search_result['title']
    url = search_result['link']
    snippet = search_result['snippet']

    content = clean_html(url)
    full_content = f"제목: {title}\n발췌: {snippet}\n전문: {content}"

    full_content_truncated = truncate_text(full_content, max_tokens=3500)

    summary = summarizer.run(text=full_content_truncated)

    result = {"title": title,
              "url": url,
              "content": content,
              "summary": summary
              }

    return result


###########################################################
# Instances
llm = ChatOpenAI(temperature=0.8)

search = DuckDuckGoSearchAPIWrapper()
search.region = 'kr-kr'
#enc = tiktoken.get_encoding("cl100k_base")
enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

summarizer = build_summarizer(llm)




def writer():

    star = random.choice(['강남구 부동산 소식', ' 서초구 부동산 뉴스'
,'서울 부동산 뉴스', '수도권 부동산 뉴스','성남시 부동산 뉴스', '용인시 부동산 뉴스', '분당구 부동산 뉴스', '수지구 부동산 뉴스', '수원시 부동산 뉴스'
                          ,'영통구 부동산 뉴스', '용산구 부동산 뉴스', '마곡 부동산 뉴스', '강서구 부동산 뉴스', '마용성 부동산 뉴스', '마포구 부동산 뉴스', '성동구 부동산 뉴스'
         , '일산시 부동산 뉴스', '인천시 부동산 뉴스', '하남시 부동산 뉴스', '광교 부동산 뉴스', '판교 부동산 뉴스', '동탄 부동산 뉴스'])

    search_results = search.results(star, num_results=10)
    i = 0
    record = [[0 for j in range(1)] for t in range(10)]
    for s in search_results:
       # record[i] = Data(title=s['title'],content=s['content'],url=s['url'],summary=s['summary'])
        #record[i] = s

        content = clean_html(s['link'])
        full_content = f"제목: {s['title']}\n발췌: {s['snippet']}\n전문: {content}"

        full_content_truncated = truncate_text(full_content, max_tokens=3000)

        summary = summarizer.run(text=full_content_truncated)

        record[i] = {"title": s['title'],
                  "url": s['link'],
                  "content": content,
                  "summary": summary
                  }
        i=i+1





    title2 = f"{star} ! 오늘은 무슨 일이!?"

    content2 = f'''
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br />
<span style="font-family: 'Noto Serif KR';">안녕하세요, 오늘은 {star}에 대해 어떤 기사들이 작성되었을까요?!<br/> 
오늘의 HOT한 뉴스만 정리했습니다<br />
링크도 있으니 함께 보시죠!</span></p>
<p>&nbsp;</p>


<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[2]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[2]['summary']}  </span></p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
  <a href="{record[2]['url']}">원본 LINK 바로가기</a></span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[3]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[3]['summary']}  </span></p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
  <a href="{record[3]['url']}">원본 LINK 바로가기</a></span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[4]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[4]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
  <a href="{record[4]['url']}">원본 LINK 바로가기</a></span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[5]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[5]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
  <a href="{record[5]['url']}">원본 LINK 바로가기</a></span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[6]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[6]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 <a href="{record[6]['url']}">원본 LINK 바로가기</a></span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[7]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[7]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
  <a href="{record[7]['url']}">원본 LINK 바로가기</a> </span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[8]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[8]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
  <a href="{record[8]['url']}">원본 LINK 바로가기</a></span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[9]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[9]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
  <a href="{record[9]['url']}">원본 LINK 바로가기</a></span></p>
<p>&nbsp;</p>



<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br />
<span style="font-family: 'Noto Serif KR';">오늘도 이슈가 많은 하루였네요.<br />
저는 내일도 새로운 뉴스를 가지고 오겠습니다., 편안한 하루 보내세요!</span></p>
<p>&nbsp;</p>
            '''

    return title2, content2


if __name__ == "__main__":
    title2, content2 = writer()

    blog_write(
        blog_name="honeybutterinfo",
        category_id="953968",
        title="[뉴스]"+title2,
        content=content2,
        tag=''
    )

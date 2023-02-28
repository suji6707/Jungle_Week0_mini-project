from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://jisu6707:test@cluster0.7kg6uhj.mongodb.net/?retryWrites=true&w=majority')
db = client.ecommerce

import requests
from bs4 import BeautifulSoup


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/show', methods=['GET'])
def show_group():
    result = list(db.product.find({}, {'_id':0}))
    # print(result)
    return jsonify({'lists': result})

# 입력받은 쿠팡 ulr로 데이터 DB에 넣기
@app.route('/submit', methods=['POST'])
def submit():
    url = request.form['url']
    getData(url)

    return jsonify({'return':'success'})

def getData(url):

    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'sec-ch-ua' : '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'cookie': 'cookie: PCID=16724534648113966367288; MARKETID=16724534648113966367288; X-CP-PT-locale=ko_KR; _fbp=fb.1.1672453465705.1131102584; gd1=Y; _ga=GA1.2.1134491595.1674487494; x-coupang-origin-region=KOREA; x-coupang-target-market=KR; sid=18882f29d5ae4c42980b569293359d2b2e194494; trac_src=1042016; trac_spec=10304903; trac_addtag=900; trac_ctag=HOME; trac_lptag=%EC%BF%A0%ED%8C%A1; FUN="{\'search\':[{\'reqUrl\':\'/search.pang\',\'isValid\':true}]}"; trac_itime=20230227204223; bm_sz=9719167E5555B9D6A80177C849F52A3C~YAAQJDMtF3dhVIiGAQAA5J7bkhLUUh+crqEIZ5jihQaNB9t6OD0SAddIVJ/NLDFTMVj6YaOxQClyca9XpqUjjWoFwqrTHCiEnqHB819z0Q1v7dIi2bivahIOjAvN+LawTDwtK71EihyA0VGnJwtT5QiZvCmBYU9JW9tz1fx/omrEkR/3zkl0Pa1Aqyhna0U5LuiVi7Vn4XaDeFAW70SKq1HtfhxxWidSV2OSt2JyXCorsK/lGtXo4VlTAztj14lnAhFefhHjMEdcy6sL/f7HXviqhntH9tILcpdcaWdrwyu84iwy~3682610~3617845; overrideAbTestGroup=%5B%5D; searchKeyword=%EC%8B%9D%EB%B9%B5%7C%EB%94%B8%EA%B8%B0%EC%9E%BC%7C%EC%BB%A4%ED%94%BC%7C%EC%BB%A4%ED%94%BC%EB%AF%B9%EC%8A%A4%7C%EC%83%9D%EC%88%98%7C%EC%9A%B0%EC%9C%A0; searchKeywordType=%7B%22%EC%8B%9D%EB%B9%B5%22%3A0%7D%7C%7B%22%EB%94%B8%EA%B8%B0%EC%9E%BC%22%3A0%7D%7C%7B%22%EC%BB%A4%ED%94%BC%22%3A0%7D%7C%7B%22%EC%BB%A4%ED%94%BC%EB%AF%B9%EC%8A%A4%22%3A0%7D%7C%7B%22%EC%83%9D%EC%88%98%22%3A0%7D%7C%7B%22%EC%9A%B0%EC%9C%A0%22%3A0%7D; ak_bmsc=FEAE38E2A1BDEE4B88DC98453F60C905~000000000000000000000000000000~YAAQivkrF1dFszWGAQAAImnxkhLsf+Et3xPVRT3KuKh0dEViuabNWW3fBvIh5tH6N6r2KtOCcdh2WLHE1pfR3IkcLlKmhOVHChBti4xCkBHNxpLav3wtqgmJhjJq0urrJ70h/xaELjL7Sa8Tqb3+doQGLeTsekqcrMu0g0kWwDaulfyXKpSE+GH510wvq94oZKA7DwmlffhYPyUNjpTcht79c0A3DU5Z3faIlxgn4nlxoWlcsqHOxnbDIt4AGbrshfcJJszN9ArWtnB67oNKzzSLGfigN7LkfmXfXFdrnQC5xyQj5NG6N2baYrmddcsJPOy3i5JbUJqwRv6B+/3zeR/rdxJpppM1WLx8k1SdjSSGxi18BCTCGaXMAojz2MYCQozTWEetJpBF+A12aHo/ISAuC4Ds03Z2rbqzEwqmhbhfiPhobNyKyhUDxQnpJAwcWB4eWTf0vAv9en2472RZe/0m42SHIfNyUZ2DaTk1MD+an3vQjhr8hglKgZ78; _abck=DF13EA24D5308A4D1C9C54E04D8E63E7~0~YAAQivkrF3VFszWGAQAATmzxkgk4C1+nXwsmj5XWhbx8f2nSy8xYNFUEWU5QrsVLDCuygG3wwIVjhlQw8X9RmLl8jJlFI7sETRPSJ7XnclKJ+x7HyBea5vCV5gU5/LkyeIH7XuQXPK+FrzLm4bo1YJtWc8s1eljEBegJVUIj1Sb4PJz1Wlj5P2TqOqGOEPoxGCW5oooR+7ke2/0Zzh2P/WpVLiw4hx/U7b1aqiFrs63iQKVYUr7004/KjQSS7jDpeybNlD0uGuOelBL8WeWfnRrgAdBGVaB8CutB1y+k5wPVXhPoM/FOl28XiEUlqncdr7HQHSug4tl0BHaSKUBueQVSiShzv7+yd1feJVMY6ZEH92tRYyPkS0UqYI5jYlUBj1ujL/+1BDSLOHEDBlcjDsM5d54atsa9QBKQpvxLzYNp6aO3YhQC~-1~-1~-1; x-coupang-accept-language=ko_KR; cto_bundle=oAp7Rl9Gb2lwUjE4R2dHR0Z6cXFlM3M2a3R4JTJCJTJGUjFVbzhlT3UyUm4lMkI5STFlNW5TekxZJTJCaEtITklkOUdNMzlWZTBXa1Vkb0RMamhPczNJNjg4cDkwMG5XdGZhZDF2UWpHUmZIb2I2SWMlMkY1MThzMG4yUEZUbyUyQnFGJTJGQk5HTVVIQ05NczN6VFhTOXJSUk5CR0Q0bmZCZ1RoRmVUZyUzRCUzRA; baby-isWide=wide; bm_sv=F30C34C52364D585D706942D4850CFCD~YAAQivkrF+NIszWGAQAAYRDykhIHrw/k0QCmneVwmPeRiRNTrUtfcWTa/bW8trRtgq6NylsTEess5QzvZ/f0WuaCwyZyF2fGM7HA4bm7x5vZgMX2DNFqdiXeaPDcRZsg1x9NEbEVBECMzlmpzBytn6FShUu41PRroC/MQGbuw+30VSbPuJ2Z6fgAThWI1Ld8eCPxIG8DeSZBOZuQgolZ9vgMC+CvDdJEOhfDBQNtEqSHpxM6BCni0z5XvphMArXcRg==~1'
        }

    data = requests.get(url, headers = headers, verify=False)

    soup = BeautifulSoup(data.text, 'html.parser')

    name = soup.select_one('.prod-buy-header__title').text
    price = soup.select_one('.total-price').text.replace('원','').replace(',','')
    imgUrl = "https:" + soup.select_one('.prod-image__detail')['src']

    doc = {
        'name': name, 
        'price' : int(price),
        'imgUrl' : imgUrl
    }

    db.product.insert_one(doc)
    print(name, price, imgUrl)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)









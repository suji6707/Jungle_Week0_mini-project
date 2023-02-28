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

@app.route('/group-list', methods=['GET'])
def show_group():
    all_group = db.list_collection_names()
    print(all_group)
    return jsonify({'result': all_group})


# 클릭한 카테고리에 해당하는 DB 가져오기
@app.route('/list', methods=['GET'])
def show_products():
    keyword = request.args.get('keyword')
    products = list(db[keyword].find({}, {'_id':False}).sort('likes', -1))
    print(products)

    return jsonify({'lists': products})


# 입력받은 쿠팡 ulr로 데이터 DB에 넣기
@app.route('/submit', methods=['POST'])
def submit():
    url = request.form['url']
    category = request.form['category']
    count = request.form['count']

    getData(url, category, count)

    return jsonify({'return':'success'})

def getData(url, category, count):

    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'sec-ch-ua' : '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'cookie': 'cookie: PCID=16724534648113966367288; MARKETID=16724534648113966367288; X-CP-PT-locale=ko_KR; _fbp=fb.1.1672453465705.1131102584; gd1=Y; x-coupang-origin-region=KOREA; x-coupang-target-market=KR; sid=18882f29d5ae4c42980b569293359d2b2e194494; trac_src=1042016; trac_addtag=900; trac_ctag=HOME; _gid=GA1.2.757949308.1677514728; _ga=GA1.1.1134491595.1674487494; _ga_WQ2R3HQM0J=GS1.1.1677514727.1.1.1677514829.37.0.0; overrideAbTestGroup=%5B%5D; bm_sz=9E19B98853797B32CAA533A2FD8F70A1~YAAQrJ/YF/7c1pOGAQAAGnFQlhIDyBSl9VLIjS3k5vb55FNO8SV9ojpZOT8n4sCB3JfbPRdOJcTLkI0/cH46sf4f5YrdQZGbT/yQyupfLDSKGFbYZGIc+UwT7sNIfhpAnNO4SDaug4gGVGJULuegwRLDzQjzY0oSjp48Emn6+Z5zd4jx0eneJ9PH7Do9WiET+4mILs6oWacUaSBtEV7w6ifWnNvX3hPiP9Xj/P28pvsTch+bNHK9BOQj7V2qpxfZR2Fe2Z8fTGDuHcQYwbkvwwtKVMMMvx+Ua20mU7re/05geFfG~3684676~3486002; trac_spec=10304902; trac_lptag=coupang; trac_itime=20230228133820; bm_mi=A208EC8D3DC4A9B46B4AD7C8C8BBDE3D~YAAQrJ/YFzHe1pOGAQAAOndQlhIStvKO1h0FHFWUBUl9m2bS2FhcrWZBnwAfUu33bWBpgSKBJDVhsXS62R61Lis7Uu4EjmwlJgPyV6485UOVcDmO0InFqWTEbL+k2fjq7OxSoHIO1IQ1yW/TUEjv5FYGqe6yT7DrlYFO+4Q2fRRPo1MMByehb3H5iWkYO7rY47U0E1gXRsaoEJm2CiyMdlA2k1YhJq4oL0gXE/X+lwYFgaLZLNwVrOKY2C/3D96FmEpJ3dY3y1viTcs0iWZJQ0skTp86F8Bgvi0Ehaoq2w3pJe8/GfvPf+nlzqKPiA==~1; ak_bmsc=77642B58EEEAF0DB4911CB467BDC9A53~000000000000000000000000000000~YAAQrJ/YFyrf1pOGAQAAh3tQlhLUeLcYUgZ4w6Eol4FsfA1pwlyRUsLdUQqSi1rWhjyhUsbIGEuCiYTaAzH6trjmlh9LQ/y+LV4VHkUIykeeqUlMVT4yDISa6lXeOSY1WOP5gEWeHAkEf7BTypxfHJbdvizAkAA9CPNJvgL+FNk84pouKJrA56ygghiBFdXuGd2VMiC/yOFPNLdRwb0iHZsqfbJJW0YpFgI8OrPqZr+5DfyL2fz17HvtFf9UEO90ZHjD2I46IT2pAu/BKOAAawV/QQFb06U33tA/rx0dxlo5mMMjwvWmlp6UNPduJmdt/yCD5//R6ZCaUdKA64sAS2KELozkeHlxIvI//WVn8Spquk/C0umYOKfhkwoTSgVNC0kuKFTn5YNzeijRyHvFsXtd5ozW79J8csSh02ZMmZDh6zYxa6WLFNIkHQ8ds3KgToGlroqYmuDVVSNhPP6ScmisIWIi6Vr25XG1YUmUHnBQq1eHS9wgRKdcP3xEgSJdqAkf; searchKeyword=%EC%8B%9D%EB%B9%B5%7C%EB%94%B8%EA%B8%B0%EC%9E%BC%7C%EC%BB%A4%ED%94%BC%7C%EC%BB%A4%ED%94%BC%EB%AF%B9%EC%8A%A4%7C%EC%83%9D%EC%88%98%7C%EC%9A%B0%EC%9C%A0%7C%EC%B4%88%EC%BD%94%EC%9A%B0%EC%9C%A0%7C%EC%82%AC%EA%B3%BC; searchKeywordType=%7B%22%EC%8B%9D%EB%B9%B5%22%3A0%7D%7C%7B%22%EB%94%B8%EA%B8%B0%EC%9E%BC%22%3A0%7D%7C%7B%22%EC%BB%A4%ED%94%BC%22%3A0%7D%7C%7B%22%EC%BB%A4%ED%94%BC%EB%AF%B9%EC%8A%A4%22%3A0%7D%7C%7B%22%EC%83%9D%EC%88%98%22%3A0%7D%7C%7B%22%EC%9A%B0%EC%9C%A0%22%3A0%7D%7C%7B%22%EC%B4%88%EC%BD%94%EC%9A%B0%EC%9C%A0%22%3A0%7D%7C%7B%22%EC%82%AC%EA%B3%BC%22%3A0%7D; FUN="{\'search\':[{\'reqUrl\':\'/search.pang\',\'isValid\':true}]}"; _abck=DF13EA24D5308A4D1C9C54E04D8E63E7~0~YAAQrJ/YFwPj1pOGAQAAV4xQlgkFK+eX7qIKxvkA9HIAMVATQW5MwAh3Qc6ARd2nDv+Ma37GHxrktgNLTQF91beMCWIdJYz5UURf8cBjiYA7PpFAKY+6UbofslEIh9d/4ajdK38MRJaxxG9gYYDDh+P8pI1g4fy/8+/vTkcve3r1nZTWvgoibYStwr637ipQAEkbtgx4mtFAtaglOZ7hrP283EFKxKNfA3wbw2Q8xhLnEew06j8HLrrsZOH8E0H8g64JmoImQ3/LZEzKae4zDgQOct0sFavAYZfKHo4z5lh4XGs/TKL40oPrtaO62mtEcZIx9vi3xlTjUgiGXPyRL0P0T/TCjnHnxim/66ICa+3N/9OWW4IdLJAUZvyW3/EeewdoKUCjwO1JqzMDXpJb51OTOemnEaSjQS4lZ4wRGI4j388vPPx3~-1~-1~-1; x-coupang-accept-language=ko_KR; cto_bundle=FfpqUF9Gb2lwUjE4R2dHR0Z6cXFlM3M2a3Q4NVYlMkJFNk5reXprTGdaVDh5NXpCeEUxTWNBRG9wJTJGeUFmS0lrbmo1TEczZnhjUmxYOWtMeHJRTG42bW9Wdjd5aVNCaVV5MU5Fa2lIRkc0RnNNTkthZDdmaW92a0NMeFVaN3Z0ckFJQ0ZXNHJvV3JHTGFYaWd6JTJCYzZkR01QJTJCcTdzUSUzRCUzRA; baby-isWide=small; bm_sv=F9722E32B7697E466B2A924352F50257~YAAQRJlMF0+djYiGAQAAdq1hlhJ2G3UcpWxyymKgX1Wa1lb8JqNetDJqJ08LSEke7chMPs/YqYjm497KJSNj1j1KMLp11J5VEe37yPRM6fY8bNj/eY+uCpVAbwdFnay6MGqUZq1HSECEmk6x1WPgxJSpVySk1domrOMMZBMmG/GN+H3EVaaI0fdqZXpGu2qkmNBbdY/hAXEraLUhMQr4Pyd+iCcJZcz/WuU4kCr5RtI4qCX4USZukvoVP5Uz1Xdff4E=~1'
        }

    data = requests.get(url, headers = headers, verify=False)

    soup = BeautifulSoup(data.text, 'html.parser')

    name = soup.select_one('.prod-buy-header__title').text
    price = soup.select_one('.total-price').text.replace('원','').replace(',','')
    imgUrl = "https:" + soup.select_one('.prod-image__detail')['src']

    doc = {
        'name': name, 
        'price' : int(price),
        'imgUrl' : imgUrl,
        'catetory' : category,
        'count' : count,
        'likes' : 0
    }

    db[category].insert_one(doc)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)








# 웹 스크래핑 TEST
# url = 'https://www.coupang.com/vp/products/4550236145?itemId=12725041643&vendorItemId=84999675267&q=%EC%BB%A4%ED%94%BC%EB%AF%B9%EC%8A%A4&itemsCount=36&searchId=831f6f55a7e44a87b9b6d4711fbc6632&rank=0&isAddedCart='

# headers = {
#     'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
#     'sec-ch-ua' : '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'cookie': 'PCID=16724534648113966367288; MARKETID=16724534648113966367288; X-CP-PT-locale=ko_KR; _fbp=fb.1.1672453465705.1131102584; gd1=Y; _ga=GA1.2.1134491595.1674487494; x-coupang-origin-region=KOREA; x-coupang-target-market=KR; sid=18882f29d5ae4c42980b569293359d2b2e194494; bm_sz=ADF76A16FF5AE717392CABEAC96B12EF~YAAQBqPBF/++p1aGAQAAD8P9kRI3/Rt+T/TAfNZSkvuwT3thQ6tnV8fXCCGvHVx7wae0msKB+FBzVk3hvjNsnRfzuo06ODHyIcR1q5V5DdChPRbNf5UWEUgiQk/oJk6bF75DOR/CPCgZ356N5qBlC7DvSPNyM+7AtPk+T/shk+5GduwSOrkfqmsOtyfsnn3h1wuT+SB6NTgcmDEWX7t4A6jqaQWFk5Njj2QXT/ZNcpPVW8fbl1o6GwmEZpHTjKkcFmaPUGLqPkGfftBSUAJqrCUf4RU2qUi3Wf+/y+C7LRWqQODw~3294003~4342584; trac_src=1042016; trac_spec=10304903; trac_addtag=900; trac_ctag=HOME; trac_lptag=%EC%BF%A0%ED%8C%A1; FUN="{\'search\':[{\'reqUrl\':\'/search.pang\',\'isValid\':true}]}"; bm_mi=8DBE51F90E69DC025E5D4F1019196C7E~YAAQJ3pGaC8lnzOGAQAA++CHkhIT5OW6gdNyjc0MMbG4a5EqdhrsBjm9ar/hqjaX3AfNhlbH28DdbcAJZlc/120lAeKXkXgqT7yZjZA/U4TPJbOUXcsVltmmd9keKF9LZ6a/UoWaXjb00ryElkaWVobCQMB2ig+ONB67qRzW1cs1PKApX9JUPtL+3jPzQfqIvfyzRZALbnU1RUm0Jd2eQ2bkD/ZOWmLgTI5STmdK+8GH2GKKswqi1noOx+WPW9Bb2A+ZmhkT58dm5aUPX7I5FSdliyOieiaro5CgGX7/kIF7YkNbk6nzW41MZ8MTs1eYaOiXwqXdbDBGm7qwokSNCJ0Uw3g=~1; ak_bmsc=0D453390AB4E3D69D8D57471097D30BF~000000000000000000000000000000~YAAQJ3pGaJwlnzOGAQAAFeeHkhL2nI0OR2B6qghIQjJve7/jETqJzD/gkqlKf6iBw/+aOwB+JQDKWjXMCFQfR+nZAd2siwy0H9xBDjDmN6F64RwXJo7O7WUtrxMkFiloqOHIDh/65Y3WtElkiz0ETXHO9GNdZ5nPYXvlBzzp+TEtsc5uwY0yXOm2JZ7zLzFDEHvuvheDa7pLp1BCFmcacWqTOuukS6TgWn+wWc3+fVMnldtvWc+zRmkqO3QsoKaAxfgOBOl0L8qSB20eGF8XOi+o5Q5/JoFCkM72Y28ykMGhx/J+VoiPd1r8jmO+N4BaWQtF5xuQ6EOdDyHng+bMzzF7J/kou1+wePuiuysmdLuuaZdnfJqeTM++nfd1ppMlfxCtyphstdDDeKGvYV/6Cx5utrkjwhj3NsXKkSXhqt6a6O2s4AImGKtOtvTkvzFG4OWTBRs=; trac_itime=20230227204223; overrideAbTestGroup=%5B%5D; searchKeyword=%EC%8B%9D%EB%B9%B5%7C%EB%94%B8%EA%B8%B0%EC%9E%BC%7C%EC%BB%A4%ED%94%BC%7C%EC%BB%A4%ED%94%BC%EB%AF%B9%EC%8A%A4; searchKeywordType=%7B%22%EC%8B%9D%EB%B9%B5%22%3A0%7D%7C%7B%22%EB%94%B8%EA%B8%B0%EC%9E%BC%22%3A0%7D%7C%7B%22%EC%BB%A4%ED%94%BC%22%3A0%7D%7C%7B%22%EC%BB%A4%ED%94%BC%EB%AF%B9%EC%8A%A4%22%3A0%7D; _abck=DF13EA24D5308A4D1C9C54E04D8E63E7~0~YAAQRTMtFzmrmDSGAQAAX0DCkgk6kkemtNIKLXrBAsinqL/2J3jsb9ls0uzexYuRuTo+1qWmf7wRStvbl1QMj49pSMYLM81JKQJsAwA8YdpnDTpq8wAaeuCPrfTuGuLQXm/jaAY2pZWgl0ppcg7jonmRUVJmV1+MeTfkQI6FfoPuKefsB52WF9BFu4QamNv4lSRXF9cMzN1wf16D6JxOmogisFmE8keSz2S35yqydQjZ+yWy5SlNM7W2o0Kt4EMEPvnOMcKGYSCEnMcSS6RjE/Nmn9ZR4asUn9VQ1k88nDXtjWIwz9Wupb765EKKvPdeuvwqRPef/HhnQdgpGUcB2Y2ldR7iluecFwniN4k3VuxDelZWcpRDgXvaXcS1HEmIegOszPPgqdjAVvOxrBOuONb+uGNtJOTUZnMsmoa0QQjHLHs9UrSt~-1~-1~-1; x-coupang-accept-language=ko_KR; cto_bundle=WtO5E19Gb2lwUjE4R2dHR0Z6cXFlM3M2a3QxczhJRjFSQzhzdUU5V01HZlV5WUszVTc5NWNLOGg1RzJHWSUyQjdhSVVsR1p4ZXRxVSUyQnFJbXlDUElqd0NvU1BnM01mUzlNMlJwU3M2VnMxOFFBJTJCZkhraDdlNDF6RDF6NjklMkZSUnRmTURTN2gzRThtSjVpNjBSS0NTY3RJaGtpMnQ2USUzRCUzRA; bm_sv=38CF9C3659D898F7B451193E3FB9F0D5~YAAQRTMtF5GrmDSGAQAAAV7CkhI47fPUIc5VdVShvfLyyZHnJlqKuA1H/QtXdKJ7kHuMFuRasBAMrXwzUPED4+UP/ZS1ePZjL4K2GFnQkGy8lF0WzUKJPP4jw+6lMTWlHx+TBDGpBBlPDmU5k4e9fr+dLaNNKJVnL4pByrS84uYcKZVit+C+Jx2VDsVxT+6j7xDEMazYgca/kj74qSUb/2SwM1a8QWlPAYLAFSU2r7En+rro1Ll0Gdz1ALQgD+AA7I0=~1; baby-isWide=wide'
#     }

# data = requests.get(url, headers = headers, verify=False)

# soup = BeautifulSoup(data.text, 'html.parser')

# name = soup.select_one('.prod-buy-header__title').text
# price = soup.select_one('.total-price').text.replace('원','').replace(',','')
# imgUrl = "https:" + soup.select_one('.prod-image__detail')['src']

# print(name, price, imgUrl)



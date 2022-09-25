import requests, bs4, time, html
from mTransKey.transkey import mTransKey

def charge(id, pw, code):
    code = code.split("-")

    not_code = {"result": False, "amount": 0, "reason": "잘못된 핀코드 형식", "time": 0}

    try:
        cc = 0
        for i in code: 
            int(i)
            if cc == 3 and (len(i) != 6 and len(i) != 4):
                return not_code
            if cc != 3 and len(i) != 4:
                return not_code
            cc +=  1
        if len(code) != 4: 
            return not_code
    except:
        return not_code
    sess = requests.session()
    
    mtk = mTransKey(sess, "https://m.cultureland.co.kr/transkeyServlet")
    pw_pad = mtk.new_keypad("qwerty", "passwd", "passwd", "password")

    encrypted = pw_pad.encrypt_password(pw)
    hm = mtk.hmac_digest(encrypted.encode())
    sess.cookies.set("KeepLoginConfig", 'TbllLVgHzXQMqmxTzLJEg0ZkBh%2BNkgFc2%2FoI3S2MIlK5R0zJptTVju3wwcxoOoiV', domain="m.cultureland.co.kr") #쿠키 KeepLoginConfig
    k = sess.post("https://m.cultureland.co.kr/mmb/loginProcess.do", data={
        "agentUrl": "",
        "returnUrl": "",
        "keepLoginInfo": "",
        "phoneForiOS": "",
        "hidWebType": "other",
        "userId": id,
        "passwd": "*"*len(pw),
        "transkeyUuid": mtk.get_uuid(),
        "transkey_passwd": encrypted,
        "transkey_HM_passwd": hm
    })
    k = sess.get("https://m.cultureland.co.kr/mmb/isLogin.json").text
    if k == "false":
        return {"result": False, "amount": 0, "reason": "잘못된 계정 정보"}

    pad = mtk.new_keypad("number", "txtScr14", "scr14", "password")
    encrypted = pad.encrypt_password(code[3])

    hm = mtk.hmac_digest(encrypted.encode())

    if len(code[3]) == 4:
        sess.get("https://m.cultureland.co.kr/csh/cshGiftCard.do")
    else:
        sess.get("https://m.cultureland.co.kr/csh/cshGiftCardOnline.do")

    data={
        "scr11": code[0],
        "scr12": code[1],
        "scr13": code[2],
        "scr14": "*" * len(code[3]),
        "transkeyUuid": mtk.get_uuid(),
        "transkey_txtScr14": encrypted,
        "transkey_HM_txtScr14": hm
    }
    if len(code[3]) == 4:
        k = sess.post("https://m.cultureland.co.kr/csh/cshGiftCardProcess.do", data=data)
    else:
        k = sess.post("https://m.cultureland.co.kr/csh/cshGiftCardOnlineProcess.do", data=data)
    
    soup = bs4.BeautifulSoup(k.text, "html.parser")
    result = soup.select("b")[0].text
    
    if result == "컬쳐캐쉬로 충전 불가능":
        return {"result": False, "amount": 0, "reason": result}
    else:
        amount = int(soup.select("dd")[0].text.replace("원", "").replace(",", ""))
        return {"result": bool(amount), "amount": amount, "reason": result}
    

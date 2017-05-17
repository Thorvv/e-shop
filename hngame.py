# coding=utf-8
from flask import Flask
from flask import render_template, request, session, redirect, jsonify
import MySQLdb
import os
import random
import time, datetime
import requests
import urllib
import re
import subprocess


app = Flask(__name__)
app.secret_key = os.urandom(24)

APPID = 'xxx'
URL = 'xxx'
REDIRECT_URL = urllib.urlencode({'name': URL})[5:]
RESPONSE_TYPE = 'xxx'
SCOPE = 'xxx'
SECRET = 'xxx'
HOST = 'xxx'



class Mysql(object):
    def __init__(self, db):
        self.conn = MySQLdb.connect(host="127.0.0.1", user="xx", passwd="xx", db=db, charset="utf8")
        self.conn.autocommit(1)
        self.cursor = self.conn.cursor()


def get_deskey(password):
    my_cmd = 'php /php_getkey/get_des.php ' + str(password)
    proc = subprocess.Popen(my_cmd, shell=True,
    stdout=subprocess.PIPE)
    script_response = proc.stdout.read()
    return script_response


@app.route('/judge_wechat', methods=['GET', 'POST'])
def judge_wechat():
    state = request.form.get('state')
    my_type = request.form.get('type')
    my_sql = Mysql('hngame')
    if state is not None and my_type == 'wechat':
	sql = "insert into judge_wechat set state = '%s', my_type = '%s'" % (str(state), str(my_type))
        my_sql.cursor.execute(sql)
 	return 'ok'
    return 'error'


@app.route('/get_QR')
def get_QR():
    state = generate_verification_code(len=12)
    code_dict = {'appid': APPID, 'scope': SCOPE, 'redirect_url': REDIRECT_URL,
                 'state': state}
    session['state'] = state
    return jsonify(code_dict)


@app.route('/check_token', methods=['GET', 'POST'])
def check_token():
    token = request.form.get('token')
    now_time = time.time()
    log_time = request.form.get('log_time')
    log_time = float(log_time)
    if int(now_time - log_time) >= 43200:
        session['username'] = ""
        session['userid'] = ""
        session['logged_in'] = "logged_out"
        session['log_time'] = ""
        return jsonify({'status': 'false'})
    else:
        return jsonify({'status': 'true'})


@app.route('/ask_supercode')
def generate_verification_code(len=4):
    code_list = []
    for i in range(10):
        code_list.append(str(i))
    for i in range(65, 91):
        code_list.append(chr(i))
    for i in range(97, 123):
        code_list.append(chr(i))
    myslice = random.sample(code_list, len)
    verification_code = ''.join(myslice)
    return verification_code


def check_ident(realname, identify):
    Errors = ['验证通过!', '身份证号码位数不对!', '身份证号码出生日期超出范围或含有非法字符!', '身份证号码校验错误!', '身份证地区非法!']
    area = {"11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古", "21": "辽宁", "22": "吉林",
            "23": "黑龙江", "31": "上海", "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建", "36": "江西",
            "37": "山东", "41": "河南", "42": "湖北", "43": "湖南", "44": "广东", "45": "广西", "46": "海南",
            "50": "重庆", "51": "四川", "52": "贵州", "53": "云南", "54": "西藏", "61": "陕西", "62": "甘肃",
            "63": "青海", "64": "宁夏", "65": "新疆", "71": "台湾", "81": "香港", "82": "澳门", "91": "国外"}
    idcard = str(identify)
    idcard = idcard.strip()
    idcard_list = list(idcard)
    # 地区校验
    if not area[idcard[0:2]]:
        return Errors[4]
    # 15位身份号码检测
    if len(idcard) == 15:
        if ((int(idcard[6:8]) + 1900) % 4 == 0 or (
                            (int(idcard[6:8]) + 1900) % 100 == 0 and (int(idcard[6:8]) + 1900) % 4 == 0)):
            erg = re.compile(
                '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|'
                '(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')  # //测试出生日期的合法性
        else:
            ereg = re.compile(
                '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|'
                '(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')  # //测试出生日期的合法性
        if re.match(ereg, idcard):
            return "ok"
        else:
            return Errors[2]
    # 18位身份号码检测
    elif len(idcard) == 18:
        # 出生日期的合法性检查
        # 闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
        # 平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
        if int(idcard[6:10]) % 4 == 0 or (int(idcard[6:10]) % 100 == 0 and int(idcard[6:10]) % 4 == 0):
            ereg = re.compile(
                '[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|'
                '(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')  # //闰年出生日期的合法性正则表达式
        else:
            ereg = re.compile(
                '[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|'
                '(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')  # //平年出生日期的合法性正则表达式
        # //测试出生日期的合法性
        if re.match(ereg, idcard):
            # //计算校验位
            S = (int(idcard_list[0]) + int(idcard_list[10])) * 7 + (int(idcard_list[1]) + int(idcard_list[11])) * 9 + \
                (int(idcard_list[2]) + int(idcard_list[12])) * 10 + (int(idcard_list[3]) + int(idcard_list[13])) * 5 + \
                (int(idcard_list[4]) + int(idcard_list[14])) * 8 + (int(idcard_list[5]) + int(idcard_list[15])) * 4 + \
                (int(idcard_list[6]) + int(idcard_list[16])) * 2 + int(idcard_list[7]) * 1 + int(idcard_list[8]) * 6 + \
                int(idcard_list[9]) * 3
            Y = S % 11
            M = "F"
            JYM = "10X98765432"
            M = JYM[Y]  # 判断校验位
            if M == idcard_list[17]:  # 检测ID的校验位
                return "ok"
            else:
                return Errors[3]
        else:
            return Errors[2]
    else:
        return Errors[1]
    return "ok"


def save_wechat(user_json, flag, state):
    my_sql = Mysql('hngame')
    # nickname = user_json['nickname'].encode('raw_unicode_escape')
    # nickname = user_json['nickname'].encode('utf8')
    nickname = user_json['nickname']
    nickname = user_json['nickname'].encode('raw_unicode_escape')
    nickname = unicode(nickname, "utf-8")
    sex = user_json['sex']
    province = user_json['province']
    city = user_json['city']
    country = user_json['country']
    headimgurl = user_json['headimgurl']
    privilege = user_json['privilege']
    username = user_json['unionid']
    password = generate_verification_code(len=8)

    now_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    if flag == 1:
        password = get_deskey(password)
    	sql1 = "insert into tbl_account set account = '%s', pwd = '%s', login_time = '%s', create_time = '%s', channel = 'weixin'" % (username, password, now_time, now_time)
        my_sql.cursor.execute(sql1)

        sql_id = "select userid from tbl_account where account = '%s'" % username
        my_sql.cursor.execute(sql_id)
        userid = my_sql.cursor.fetchone()[0]
    
        try:
            sql2 = "insert into tbl_playerinfo set userid = '%s', nickname = '%s', second_pwd = '%s', sex = %s, create_time = '%s'" % (userid, nickname, password, sex, now_time)
            my_sql.cursor.execute(sql2)
        except:
            nickname = '??' + str(userid)
	    sql2 = "insert into tbl_playerinfo set userid = '%s', nickname = '%s', second_pwd = '%s', sex = %s, create_time = '%s'" % (userid, nickname, password, sex, now_time)
	    my_sql.cursor.execute(sql2)
    wechat_code = generate_verification_code(len=8)
    sql_id = "select userid from tbl_account where account = '%s'" % username
    my_sql.cursor.execute(sql_id)
    userid = my_sql.cursor.fetchone()[0]
    try:
        sql3 = "insert into wechat_detail set userid = '%s', username = '%s', nickname = '%s', sex = %s, province = '%s', city = '%s', country = '%s', headimgurl = '%s',password = '%s', create_time = '%s', wechat_code = '%s'" % \
		(userid, username, nickname, sex, province, city, country, headimgurl, password, now_time, wechat_code)
        my_sql.cursor.execute(sql3)
    except:
	nickname = '??' + str(userid)
	sql3 = "insert into wechat_detail set userid = '%s', username = '%s', nickname = '%s', sex = %s, province = '%s', city = '%s', country = '%s', headimgurl = '%s',password = '%s', create_time = '%s', wechat_code = '%s'" % \
		(userid, username, nickname, sex, province, city, country, headimgurl, password, now_time, wechat_code)
        my_sql.cursor.execute(sql3)
    session['username'] = username
    session['userid'] = userid
    session['logged_in'] = "logged_in"
    # my_url = 'http://' + HOST + '/user?code=' + wechat_code
    # return redirect(my_url)
    sql3 = "select my_type from judge_wechat where state = '%s'" % state
    my_sql.cursor.execute(sql3)
    result = my_sql.cursor.fetchone()
    if result is not None and result[0] == "wechat":
        my_url = 'http://' + HOST + '/#/m/user?code=' + wechat_code
    else:
        my_url = 'http://' + HOST + '/#/pc/user?code=' + wechat_code
    return redirect(my_url)


def handle_wechat(get_json):
    my_sql = Mysql('hngame')
    access_token = get_json['access_token']
    openid = get_json['openid']
    my_url = 'https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s' % (access_token, openid)
    user_json = requests.get(my_url).json()

    if user_json['unionid'] is None:
        return wechat("授权失败！请重新登录")
    else:
        unionid = user_json['unionid']
	state = get_json['state']
        sql1 = "select userid from tbl_account where account = '%s'" % unionid
        my_sql.cursor.execute(sql1)
        result = my_sql.cursor.fetchone()
        if result is None or result[0] is None or result[0] == "":
            return save_wechat(user_json, 1, state)
        else:
            sql2 = "select wechat_code from wechat_detail where username = '%s'" % unionid
            my_sql.cursor.execute(sql2)
	    result = my_sql.cursor.fetchone()
	    if result is None or result[0] is None or result[0] == "":
	    	return save_wechat(user_json, 0, state)
	  
	    wechat_code = str(result[0])
	 
	    sql3 = "select my_type from judge_wechat where state = '%s'" % state
	    my_sql.cursor.execute(sql3)
	    result = my_sql.cursor.fetchone()
	    if result is not None and result[0] == "wechat":
		my_url = 'http://' + HOST + '/#/m/user?code=' + wechat_code
	    else:
                my_url = 'http://' + HOST + '/#/pc/user?code=' + wechat_code
            return redirect(my_url)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/index')
def main_index():
    return render_template("index.html")


@app.route('/code_token', methods=['GET', 'POST'])
def code_token():
    code = request.form.get('code')
    my_sql = Mysql('hngame')
    sql = "select userid, username from wechat_detail where wechat_code = '%s'" % code
    my_sql.cursor.execute(sql)
    result = my_sql.cursor.fetchone()
    if result is None:
        return jsonify({'msg': 'no such wechat code'})
    userid = result[0]
    username = result[1]
    return jsonify({'token': userid, 'username': username, 'log_time': time.time()})


@app.route('/user')
def user():
    #return render_template("index.html")
    
    code = request.args.get('code')
    url = '/user?code=' + code
    return redirect(url)
    


@app.route('/get_user_detail', methods=['GET', 'POST'])
def get_user_detail():
    jsondict = {}
    username = request.form.get('username')
    userid = request.form.get('token')
    begin = request.form.get('begin')
    end = request.form.get('end')
    my_sql = Mysql('hngame')
    sql2 = "select nickname, sex, gold, honor, identify, realname from tbl_playerinfo where userid = '%s'" % userid
    my_sql.cursor.execute(sql2)
    result_all = my_sql.cursor.fetchone()
    if result_all is None:
        return ""
    else:
        nickname = result_all[0]
        # nickname = unicode(result_all[0].encode('utf8', 'ignore'), 'utf-8')
        sex = result_all[1]
        gold = result_all[2]
        honor = result_all[3]
        identify = result_all[4]
        realname = result_all[5]
        sql_add = "select address from user_address where userid = '%s'" % userid
        my_sql.cursor.execute(sql_add)
        result_add = my_sql.cursor.fetchone()
        if result_add is None:
            address = ''
        else:
            address = result_add[0]

        sql_wechat = "select headimgurl from wechat_detail where userid = '%s'" % userid
        my_sql.cursor.execute(sql_wechat)
        result_wechat = my_sql.cursor.fetchone()
        if result_wechat is None:
            if sex == '1' or sex == 1:
                head_photo = "/static/user_photo/man.png"
            else:
                head_photo = "/static/user_photo/woman.png"
        else:
            head_photo = result_wechat[0]

        member_dict = {'id': userid, 'username': username, 'gold': gold, 'honor': honor, 'nickname': nickname,
                       'sex': sex, 'address': address, 'head_photo': head_photo}

        sql3 = "select pwd from tbl_account where userid = '%s'" % userid
        my_sql.cursor.execute(sql3)
        result_pwd = my_sql.cursor.fetchone()
        if result_pwd is None:
            return ""
        else:
            old_pwd = result_pwd[0]
        password_dict = {'oldpassword': old_pwd}
        addiction_dict = {'realname': realname, 'identify': identify}

        sql4 = "select goods_id, amount, honor_used, exc_time, status, gift_detail, id from exchange_order" \
               " where userid = '%s' order by exc_time desc" % userid
        my_sql.cursor.execute(sql4)
        result_all = my_sql.cursor.fetchall()
        exchange_order_list = []
        for res in result_all[int(begin)-1: int(end)]:
            if res is not None:
                goods_id = res[0]
                amount = res[1]
                honor_used = res[2]
                exc_time = res[3]
                status = res[4]
                gift_detail = res[5]
                id = res[6]
                if gift_detail is not None:
                    sql = "update exchange_order set status = 1 where id = %d" % id
                    my_sql.cursor.execute(sql)
                    status = 1
                else:
                    status = 0
                    gift_detail = ''

                sql5 = "select gift from cfg_honor2gift where id = '%s'" % goods_id
                my_sql.cursor.execute(sql5)
                gift = my_sql.cursor.fetchone()[0]
                exchange_order_dict = {'gift_name': gift, 'amount': amount, 'honor_used': honor_used,
                                       'exc_time': exc_time, 'status': status, 'gift_detail': gift_detail}
                exchange_order_list.append(exchange_order_dict)
        sql6 = "select count(*) from exchange_order where userid = '%s'" % userid
        my_sql.cursor.execute(sql6)
        total = my_sql.cursor.fetchone()[0]
        exorder_dict = {'exorder_list': exchange_order_list, 'total': total}
        final_dict = {'1': member_dict, '2': password_dict, '3': addiction_dict, '4': exorder_dict}
        return jsonify(final_dict)


@app.route('/change_user_detail', methods=['GET', 'POST'])
def user_op():
    msg = ""
    userid = request.form.get('token')
    num = request.form.get('num')
    if userid is None:
        msg = "请重新登录"
        return jsonify({'status': 'flase', 'msg': msg})

    my_sql = Mysql('hngame')
    if request.method == 'POST':
        if num == "1":
            nickname = request.form.get('nickname')
            sex = request.form.get('sex')
            address = request.form.get('address')
            sql1 = "update tbl_playerinfo set nickname = '%s', sex = %s " \
                   "where userid = '%s'" % (nickname, sex, userid)
            my_sql.cursor.execute(sql1)
            sql_add = "select address from user_address where userid = '%s'" % (userid)
            my_sql.cursor.execute(sql_add)
            result_add = my_sql.cursor.fetchone()
            if result_add is None:
                sql_insert = "insert into user_address set userid = '%s', address = '%s'" % (userid, address)
                my_sql.cursor.execute(sql_insert)
            else:
                sql2 = "update user_address set address = '%s' where userid = '%s'" % (address, userid)
                my_sql.cursor.execute(sql2)
            msg = "修改成功"
            return jsonify({'status': 'true', 'msg': msg})

        if num == "2":
            new_pwd = request.form.get('new_password')
            user_old_pwd = request.form.get('old_password')
            new_pwd = get_deskey(new_pwd)
            user_old_pwd = get_deskey(user_old_pwd)
            sql1 = "select pwd from tbl_account where userid = '%s'" % userid
            my_sql.cursor.execute(sql1)
            old_pwd = my_sql.cursor.fetchone()[0]
            if user_old_pwd != old_pwd:
                msg = "旧密码错误！"
                return jsonify({'status': 'false', 'msg': msg})
            if old_pwd == new_pwd:
                msg = "密码不可与旧密码相同！"
                return jsonify({'status': 'false', 'msg': msg})

            sql2 = "update tbl_account set pwd = '%s' where userid = '%s'" % (new_pwd, userid)
            my_sql.cursor.execute(sql2)
            msg = "修改成功"
            return jsonify({'status': 'true', 'msg': msg})

        if num == "3":
            realname = request.form.get('realname')
            identify = request.form.get('identify')
            msg = check_ident(realname, identify)
            sql = "select identify from tbl_playerinfo where identify = '%s'" % identify
            my_sql.cursor.execute(sql)
            result = my_sql.cursor.fetchone()
            if result is not None and result[0] != '' and result[0] is not None:
                msg = "身份证号已存在！"
                return jsonify({'status': 'false', 'msg': msg})
            if msg == "ok":
                sql1 = "update tbl_playerinfo set realname = '%s', identify = '%s' " \
                       "where userid = '%s'" % (realname, identify, userid)
                my_sql.cursor.execute(sql1)
                msg = "修改成功"
                return jsonify({'status': 'true', 'msg': msg})
            else:
                return jsonify({'status': 'false', 'msg': msg})


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        usercode = request.form.get('usercode')
        supercode = request.form.get('supercode')

        password = get_deskey(password)
        if usercode.lower() == supercode.lower():
            my_sql = Mysql('hngame')
            sql1 = "select pwd, userid from tbl_account where account = '%s'" % username
            my_sql.cursor.execute(sql1)
            result = my_sql.cursor.fetchone()
            if result is None:
                msg = "用户名或密码错误！"
                fina_dict = {'status': 'false', 'msg': msg}
                return jsonify(fina_dict)
            else:
                if password == result[0]:
                    session['username'] = username
                    session['userid'] = result[1]
                    session['logged_in'] = "logged_in"
                    session['log_time'] = datetime.datetime.now()
                    # return render_template("user.html")
                    # fina_dict = {'status': 'ture', 'token': session['userid']}
                    fina_dict = {'status': 'ture', 'token': result[1], 'username': username,
                                 'log_time': time.time()}
                    return jsonify(fina_dict)
                else:
                    msg = "用户名或密码错误！"
                    fina_dict = {'status': 'false', 'msg': msg}
                    return jsonify(fina_dict)
        else:
            msg = "验证码错误！"
            fina_dict = {'status': 'false', 'msg': msg}
            return jsonify(fina_dict)
    # return render_template("login.html")
    return render_template("index.html")


def checkContainUpper(flag):
    pattern = re.compile('[A-Z]+')
    match = pattern.findall(flag)
    if match:
        return 1
    else:
        return 0


def checkContainLower(flag):
    pattern = re.compile('[a-z]+')
    match = pattern.findall(flag)
    if match:
        return 1
    else:
        return 0


def checkContainNum(flag):
    pattern = re.compile('[0-9]+')
    match = pattern.findall(flag)
    if match:
        return 1
    else:
        return 0


@app.route('/logon', methods=['GET', 'POST'])
def logon():
    msg = ""
    if request.method == 'POST':
        username = request.form.get('username')
        nickname = request.form.get('nickname')
        sex = request.form.get('sex')
        password = request.form.get('password')
        sec_pwd = request.form.get('sec_pwd')

        usercode = request.form.get('usercode')
        supercode = request.form.get('supercode')
        if usercode.lower() == supercode.lower():
            if password != sec_pwd:
                msg = "两次输入密码不同！"
                fina_dict = {'status': 'false', 'msg': msg}
                return jsonify(fina_dict)

            if len(username) < 6:
                msg = "请设置六位或以上的用户名"
                fina_dict = {'status': 'false', 'msg': msg}
                return jsonify(fina_dict)

            if len(username) > 20:
                msg = "用户名过长"
                fina_dict = {'status': 'false', 'msg': msg}
                return jsonify(fina_dict)

            if len(password) < 6:
                msg = "请设置六位或以上的密码"
                fina_dict = {'status': 'false', 'msg': msg}
                return jsonify(fina_dict)

            if len(password) > 20:
                msg = "密码过长"
                fina_dict = {'status': 'false', 'msg': msg}
                return jsonify(fina_dict)

            if checkContainNum(password) == 0 or (checkContainLower(password) == 0 and checkContainUpper(password) == 0):
                msg = "密码过于简单！请包含数字及字母"
                fina_dict = {'status': 'false', 'msg': msg}
                return jsonify(fina_dict)

            username = str(username)
            if checkContainLower(username[0]) == 0:
                if checkContainUpper(username[0]) == 0:
                    msg = "用户名必须以字母开头"
                    fina_dict = {'status': 'false', 'msg': msg}
                    return jsonify(fina_dict)

            my_sql = Mysql('hngame')
            sql1 = "select userid from tbl_account where account = '%s'" % username
            my_sql.cursor.execute(sql1)
            userid = my_sql.cursor.fetchone()
            if userid is not None and userid[0] is not None and userid[0] != '':
                msg = "用户名已存在！"
                fina_dict = {'status': 'false', 'msg': msg}
                return jsonify(fina_dict)

            sql2 = "select nickname from tbl_playerinfo where nickname = '%s'" % nickname
            my_sql.cursor.execute(sql2)
            result_2 = my_sql.cursor.fetchone()
            if result_2 is not None and result_2[0] is not None and result_2[0] != '':
                msg = "昵称已存在"
                fina_dict = {'status': 'false', 'msg': msg}
                return jsonify(fina_dict)

            now_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            password = get_deskey(password)
            sql3 = "insert into tbl_account set account = '%s', pwd = '%s', login_time = '%s', create_time = '%s', channel = 'game'" \
                   % (username, password, now_time, now_time)
            my_sql.cursor.execute(sql3)

            sql_id = "select userid from tbl_account where account = '%s'" % username
            my_sql.cursor.execute(sql_id)
            userid = my_sql.cursor.fetchone()[0]

            sql4 = "insert into tbl_playerinfo set userid = '%s', nickname = '%s', second_pwd = '%s', sex = %s, " \
                   "create_time = '%s'" % (userid, nickname, password, sex, now_time)
            my_sql.cursor.execute(sql4)

            session['username'] = username
            session['userid'] = userid
            session['logged_in'] = "logged_in"
            session['log_time'] = datetime.datetime.now()

            fina_dict = {'status': 'ture', 'token': userid, 'username': username, 'log_time': time.time()}
            return jsonify(fina_dict)
        else:
            msg = "验证码错误！"
            return jsonify({'status': 'false', 'msg': msg})
    return render_template("index.html")


@app.route('/get_gift', methods=['GET', 'POST'])
def get_gift():
    begin = request.form.get('begin')
    end = request.form.get('end')
    my_sql = Mysql('hngame')
    sql1 = "select count(*) from cfg_honor2gift"
    my_sql.cursor.execute(sql1)
    count_all = my_sql.cursor.fetchone()[0]
    sql2 = "select id, honor, gift from cfg_honor2gift where id >= %d and id <= %d" % (int(begin), int(end))
    my_sql.cursor.execute(sql2)
    result_all = my_sql.cursor.fetchall()
    gift_list = []
    for result in result_all:
        line_dict = {'id': result[0], 'honor': result[1], 'gift': unicode(result[2].encode('utf8', 'ignore'), 'utf-8')}
        gift_list.append(line_dict)
    final_dict = {'total': count_all, 'gift': gift_list}
    return jsonify(final_dict)


@app.route('/shop')
def shop():
    return render_template("index.html")


@app.route('/buy_gift', methods=['GET', 'POST'])
def buy_gift():
    my_sql = Mysql('hngame')
    userid = request.form.get('token')
    id = int(request.form.get('id'))
    address = request.form.get('address')
    amount = int(request.form.get('amount'))
    if address == '' or address is None:
        sql_add = "select address from user_address where userid = '%s'" % userid
        my_sql.cursor.execute(sql_add)
        result_add = my_sql.cursor.fetchone()
        if result_add is None:
            return jsonify({'status': 'false', 'msg': '请绑定收货地址'})
        else:
            address = result_add[0]
    else:
        sql_add = "select address from user_address where userid = '%s'" % userid
        my_sql.cursor.execute(sql_add)
        result_add = my_sql.cursor.fetchone()
        if result_add is None:
            sql_insert = "insert into user_address set address = '%s', userid = '%s'" % (address, userid)
            my_sql.cursor.execute(sql_insert)
        else:
            sql = "update user_address set address = '%s' where userid = '%s'" % (address, userid)
            my_sql.cursor.execute(sql)

    sql1 = "select honor from tbl_playerinfo where userid = '%s'" % userid
    my_sql.cursor.execute(sql1)
    result_all = my_sql.cursor.fetchone()
    if result_all is None:
        return jsonify({'status': 'false', 'msg': '用户不存在'})
    else:
        user_honor = int(result_all[0])

    sql2 = "select honor from cfg_honor2gift where id = %d" % id
    my_sql.cursor.execute(sql2)
    result = my_sql.cursor.fetchone()
    if result is None:
        return jsonify({'status': 'false', 'msg': '商品不存在'})
    else:
        gift_honor = int(result[0])
        gift_honor *= amount

    if user_honor < gift_honor:
        return jsonify({'status': 'false', 'msg': '荣誉值不足'})
    else:
        after_honor = user_honor - gift_honor

        sql1 = "update tbl_playerinfo set honor = %d where userid = '%s'" % (after_honor, userid)
        my_sql.cursor.execute(sql1)

        now_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        sql2 = "insert into exchange_order set userid = '%s', goods_id = %d, amount = %d, honor_before = %d, " \
               "honor_used = %d, honor_after = %d, exc_time = '%s', status = 0, address = '%s'" % \
               (userid, id, amount, user_honor, gift_honor, after_honor, now_time, address)
        my_sql.cursor.execute(sql2)
        return jsonify({'status': 'true', 'msg': '购买成功，请查看兑换记录状态'})


@app.route('/shop_detail', methods=['GET', 'POST'])
def shop_detail():
    if request.method == 'GET':
        return "use post pls"
    if request.method == 'POST':
        userid = request.form.get('token')
        id = request.form.get('id')
        my_sql = Mysql('hngame')
        id = int(id)
        sql1 = "select honor from tbl_playerinfo where userid = '%s'" % userid
        my_sql.cursor.execute(sql1)
        result_all = my_sql.cursor.fetchone()
        if result_all is None:
            return jsonify({'status': 'false', 'msg': '用户不存在'})
        else:
            user_honor = int(result_all[0])

        sql2 = "select honor, gift from cfg_honor2gift where id = %d" % id
        my_sql.cursor.execute(sql2)
        result = my_sql.cursor.fetchone()
        if result is None:
            return jsonify({'status': 'false', 'msg': '商品不存在'})
        else:
            gift_honor = int(result[0])
            gift = result[1]

        sql_3 = "select address from user_address where userid = '%s'" % userid
        my_sql.cursor.execute(sql_3)
        result_add = my_sql.cursor.fetchone()
        if result_add is None:
            address = ""
        else:
            address = result_add[0]

        return jsonify({'gift_honor': gift_honor, 'gift': gift, 'user_honor': user_honor, 'address': address})


@app.route('/wechat')
def wechat(msg=""):
    STATE = generate_verification_code(len=12)
    my_url = 'https://open.weixin.qq.com/connect/qrconnect?' \
             'appid=%s&redirect_uri=%s&response_type=%s&scope=%s&state=%s#wechat_redirect' % \
             (APPID, REDIRECT_URL, RESPONSE_TYPE, SCOPE, STATE)
    session['state'] = STATE
    return redirect(my_url)


@app.route('/get_wechat')
def get_wechat():
    msg = ""
    code = request.args.get('code')
    state = request.args.get('state')
    if code is None:
        msg = "您已禁止授权！"
    else:
        my_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?' \
                 'appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (APPID, SECRET, code)
        get_json = requests.get(my_url).json()
        access_token = get_json['access_token']
	get_json['state'] = state
        if access_token is None:
            msg = 'errcode ' + get_json['errcode'] + ' errmsg ' + get_json['errmsg']
        else:
            return handle_wechat(get_json)
    return wechat(msg)


@app.route('/appdown.py')
def mobile_redirect():
    return render_template("index.html")

@app.route('/chat')
def chat():
    return render_template("chat.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7777)

from flask import render_template, url_for
from flask import Flask, session, redirect, url_for, escape, request
from sqlalchemy import func, and_, or_, between, exists
from . import main
from ..models import *
from ..models import User as user
from .. import db
from config import role  # 系統角色
import json
import os
import datetime

# 初始化一個Flask實例
app = Flask(__name__)
# 裝飾器設定路由
global message
message = None
global error
error = None
global authority
authority = None


@main.route('/')
def index():
    global authority
    global message
    if role == "Gateway" and db.session.query(User).first() is None:
        return render_template('index.html', role=role, setting="setting")
    elif 'account' in session:
        if message == "Register Successful":
            return render_template("index.html", message=message, session_user_name=session['account'], authority=authority, role=role)
        account = db.session.query(User.authority).filter(
            User.account == session['account']).first()
        authority = account.authority
        if authority is None:
            return render_template('index.html', role=role)
        else:
            return render_template('index.html', session_user_name=session['account'],  authority=authority, role=role)
    elif message:
        return render_template("index.html", message=message, role=role)
    elif error:
        return render_template("index.html", error=error)
    else:
        return render_template('index.html', role=role)


@main.route('/register', methods=['GET', 'POST'])
def register():
    global authority
    global message
    if request.method == 'POST':
        account = request.form['inputaccount']
        password = request.form['inputpassword']
        register_result = user.register_user(account, password)
        # 無此帳號創建帳號並存取權限
        if register_result is False:
            account_authority = db.session.query(
                User.authority).filter(User.account == account).first()
            session['account'] = account
            authority = account_authority.authority
            message = "Register Successful"
            return redirect(url_for('main.index'))
        # 相同帳號
        else:
            message = "Your account already exist"
            return redirect(url_for('main.index'))
    else:
        return render_template("index.html")


@main.route('/login', methods=['GET', 'POST'])
def login():
    global error
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        result = db.session.query(User).filter(User.account == account).first()
        if result:
            rs = user.check_password(result.password, password)
            if rs:
                session['account'] = request.form['account']
                return redirect(url_for('main.index'))
            else:
                error = "Invalid Password"
                return redirect(url_for('main.index'))
        else:
            error = "Invalid Account"
        return redirect(url_for('main.index'))
    return redirect(url_for('main.index'))


@main.route('/setting', methods=['GET', 'POST'])
def setting():
    global error
    if request.method == 'POST':
        account = request.form['settingaccount']
        password = request.form['settingpassword']
        mqtt_host = request.form['setting_mqtt_host']
        gateway_UID = request.form['setting_gateway_UID']
        cloud_ip = request.form['setting_cloud_ip']
        cloud_port = request.form['setting_cloud_port']
        cloud_path = request.form['setting_cloud_path']
        cloud_key = request.form['setting_cloud_key']
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filex = open(
            "/var/www/dae-web/app/api_1_0/resident/method/config/gateway_setting.py", 'w', encoding='utf-8')
        filex.write('uid = "%s"\n' % (gateway_UID))
        filex.write('mqtt_host = "%s"' % (mqtt_host))
        filex.close()
        db.session.query(Links).delete()
        insert_data = Links(None, cloud_ip, cloud_path,
                            cloud_port, cloud_key, current_time, current_time)
        db.session.add(insert_data)
        insert_data = Gateway(None,  gateway_UID, None,
                              None, None, "gateway", None)
        db.session.add(insert_data)
        user.register_user(account, password)
        db.session.query(User).update({User.authority: "1"})
        db.session.commit()
        return redirect(url_for('main.index'))


# pop所有相關session


@main.route('/logout')
def logout():
    global authority
    global message
    global error
    authority = None
    message = None
    error = None
    session.pop('account', None)
    session.pop('p_id', None)
    session.pop('gateway_name', None)
    session.pop('gateway_uid', None)
    return redirect(url_for('main.index'))


@main.route('/project')
def project():
    if 'account' in session:
        return render_template('project.html', session_user_name=session['account'])
    else:
        return redirect(url_for('main.index'))


@main.route('/gateway_setting', methods=['GET', 'POST'])
def gateway_setting():
    global authority
    if 'account' in session:
        session.pop('uid', None)
        if request.method == 'POST':
            session['p_id'] = request.form['pid']
            session.pop('uid', None)
            p_name = project_page()
            return render_template('gateway_setting.html', p_name=p_name, p_id=session['p_id'], session_user_name=session['account'], authority=authority)
        else:
            p_name = project_page()
            return render_template('gateway_setting.html', p_name=p_name, p_id=session['p_id'], session_user_name=session['account'], authority=authority)

    else:
        return redirect(url_for('main.index'))


@main.route('/client_page', methods=['GET', 'POST'])
def client_page():
    global authority
    if role == "Gateway":
        if 'account' in session:
            gateway_data = db.session.query(Gateway).filter().first()
            session['gateway_name'], session['gateway_uid'] = gateway_data.gateway_name, gateway_data.uid
            return render_template('client_page.html', role=role, session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
        else:
            return redirect(url_for('main.index'))
    elif role == "Cloud":
        if 'account' in session:
            if request.method == 'POST':
                gateway_uid = request.form['uid']
                gateway_data = db.session.query(Gateway.gateway_name, Gateway.uid).filter(
                    and_(Gateway.uid == gateway_uid, Gateway.project_id == session['p_id'])).first()
                session['gateway_name'], session['gateway_uid'] = gateway_data.gateway_name, gateway_data.uid
                query_data = db.session.query(User.authority).filter(
                    User.account == session['account']).first()
                authority = query_data.authority
                return render_template('client_page.html', role=role, session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
            else:
                return render_template('client_page.html', role=role, session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
        else:
            return redirect(url_for('main.index'))


@main.route('/gateway')
def gateway():
    if 'account' in session:
        query_data = db.session.query(User.authority).filter(
            User.account == session['account']).first()
        authority = query_data.authority
        if authority == '0':
            return render_template('gateway.html', session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
        else:
            return render_template('gateway.html', role=role, session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
    else:
        return redirect(url_for('main.index'))


@main.route('/device', methods=['GET', 'POST'])
def device():
    if role == "Gateway":
        if 'account' in session:
            gateway_data = db.session.query(Gateway).filter().first()
            session['gateway_name'], session['gateway_uid'] = gateway_data.gateway_name, gateway_data.uid
            return render_template('device.html', role=role, session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
        else:
            return redirect(url_for('main.index'))
    elif role == "Cloud":
        if 'account' in session:
            if request.method == 'POST':
                gateway_uid = request.form['uid']
                gateway_data = db.session.query(Gateway.gateway_name, Gateway.uid).filter(
                    and_(Gateway.uid == gateway_uid, Gateway.project_id == session['p_id'])).first()
                session['gateway_name'], session['gateway_uid'] = gateway_data.gateway_name, gateway_data.uid
                return render_template('device.html', role=role, session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
            else:
                return render_template('device.html', role=role, session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
        else:
            return redirect(url_for('main.index'))


@main.route('/schedule')
def schedule():
    if 'account' in session:
        query_data = db.session.query(User.authority).filter(
            User.account == session['account']).first()
        authority = query_data.authority
        if authority == '0':
            return render_template('schedule.html', session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
        else:
            return render_template('schedule.html', role=role, session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
    else:
        return redirect(url_for('main.index'))


@main.route('/festival')
def festival():
    if 'account' in session:
        query_data = db.session.query(User.authority).filter(
            User.account == session['account']).first()
        authority = query_data.authority
        if authority == '0':
            return render_template('festival.html', session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
        else:
            return render_template('festival.html', role=role, session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
    else:
        return redirect(url_for('main.index'))


@main.route('/files')
def files():
    if 'account' in session:
        query_data = db.session.query(User.authority).filter(
            User.account == session['account']).first()
        authority = query_data.authority
        if authority == '0':
            return render_template('file.html', session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
        else:
            return render_template('file.html', role=role, session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
    else:
        return redirect(url_for('main.index'))


def project_page():
    query_data = db.session.query(Project.project_name).filter(
        Project.id == session['p_id']).first()
    p_name = query_data.project_name
    return (p_name)


if __name__ == '__main__':
    app.run(debug=True)


@main.route('/client_forms')
def forms():
    if 'account' in session:
        query_data = db.session.query(User.authority).filter(
            User.account == session['account']).first()
        authority = query_data.authority
        if authority == '0':
            return render_template('client_forms.html', role=role, session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
    else:
        return render_template('client_forms.html')


@main.route('/client_tables')
def tables():
    if 'account' in session:
        query_data = db.session.query(User.authority).filter(
            User.account == session['account']).first()
        authority = query_data.authority
        if authority == '0':
            return render_template('client_tables.html', session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
        else:
            return render_template('client_tables.html', session_user_name=session['account'], gateway_name=session['gateway_name'], gateway_uid=session['gateway_uid'], authority=authority)
    else:
        return render_template('client_tables.html')


@main.route('/client_power')
def power():
    if 'account' in session:
        query_data = db.session.query(User.authority).filter(
            User.account == session['account']).first()
        authority = query_data.authority
        if authority == '0':
            return render_template('client_forms.html', session_user_name=session['account'], authority=authority)
    else:
        return render_template('client_power.html')


@main.route('/admin_page')
def admin_page():
    if 'account' in session:
        query_data = db.session.query(User.authority).filter(
            User.account == session['account']).first()
        authority = query_data.authority
        if authority == '0':
            return render_template('admin_page.html', session_user_name=session['account'], authority=authority)
    else:
        return render_template('admin_page.html')

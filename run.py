from flask import Flask, render_template, request, url_for, session, app, redirect
import sqlite3
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = 'hahaha'

@app.route('/')
def main():
    if session.get('logged_in') ==  True:
        return render_template('index.html', username = session['username'])
    return render_template("index.html")

@app.route('/register', methods=["GET"])
def init_register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    if not request.form['ID']:
        error = "아이디를 입력하세요"
    elif not request.form['password']:
        error = "비밀번호를 입력하세요"
    elif not request.form['re-password']:
        error = "비밀번호 확인을 입력하세요"
    elif not request.form['username']:
        error = "유저 이름을 입력하세요"
    else:
        ID = request.form['ID']
        password = sha256_crypt.encrypt((str(request.form['password'])))
        username = request.form['username']

        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        sql = "insert into user (ID, password, username) VALUES (?, ?, ?)"
        cur.execute(sql, (ID, password, username))
        conn.commit()
        conn.close()
        return redirect("login")
        
    return render_template("register.html", error=error)

@app.route('/login', methods=["GET"])
def init_login():
    return render_template("login.html")

@app.route('/login', methods=["POST"])
def login():
    if not request.form['ID']:
        error = "아이디를 입력하세요"
    elif not request.form['password']:
        error = "비밀번호를 입력하세요"
    else:
        try:
            ID = request.form['ID']
            password = request.form['password']

            conn = sqlite3.connect("data.db")
            cur = conn.cursor()
            cur.execute("select * from user where ID ='%s'" % (ID))
            rows = cur.fetchall()
            if sha256_crypt.verify(password, rows[0][1]):
                session['logged_in'] = True
                session['username'] = rows[0][2]
                session['ID'] = ID
                return redirect("/")
            conn.close()
        except:
            return render_template("login.html", error="에러")

    return render_template("login.html", error = error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('ID', None)
    return redirect('/login')

@app.route("/board")
def init_report():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    rows = [(i[0], i[1], i[2], i[3], i[4]) for i in cur.execute("select * from board")]
    print(rows)
    conn.close()
    return render_template("board_list.html", data = rows)

@app.route("/board/<num>")
def board(num):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("select * from board where idx = '%s'" % (num))
    rows = cur.fetchall()
    idx = rows[0][0]
    title = rows[0][2]
    content = rows[0][3]
    count = rows[0][4]
    conn.close()
    return render_template("board.html", idx = idx, title = title, content = content, count = count)

@app.route('/updown/<idx>', methods=["POST"])
def updown(idx):
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("select * from board where idx = '%s'" % (idx))
    rows = cur.fetchall()
    count = int(rows[0][4])
    count += 1
    print (count)
    sql = "update board set updown ='%s' where idx='%s'" % (count, idx)
    cur.execute(sql)
    conn.commit()
    conn.close()
    return redirect("/board/"+idx)

@app.route("/write", methods=["GET"])
def init_write():
    return render_template("write.html")

@app.route("/write", methods=["POST"])
def write():
    title = request.form['title']
    content = request.form['content']

    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    sql = "insert into board (username, title, content, updown) VALUES (?, ?, ?, ?)"
    cur.execute(sql, (session['username'], title, content, "0"))
    conn.commit()
    conn.close()
    return redirect("/board")

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)

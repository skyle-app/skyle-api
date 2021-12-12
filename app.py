# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import *
import werkzeug
import pymysql
import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

SECRET_KEY = "Skyle"
app.secret_key = "Skyle"

CORS(app, resources={r'*': {'origins': '*'}})

def create_token(id, password):

    encoded = jwt.encode(
		{
			'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1000*10),
			'id': id,
			'password': password
		}, SECRET_KEY, algorithm='HS256'
	)

    return encoded

def validate_token(token):
    try:
        jwt.decode(token, SECRET_KEY, algorithms='HS256')
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
    else:
        return True

def decode_token(token):
    try:
        tokenv = jwt.decode(token, SECRET_KEY, algorithms='HS256')
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
    else:
        return tokenv

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.

@app.route('/')
# ‘/’ URL is bound with root() function.
def root():
	#return 'Hello World'
	return redirect(url_for("api"))

@app.route('/api')
@app.route('/api/')
# ‘/api’ URL is bound with api() function.
def api():
	return jsonify({"status": 200, "version": {
		"v0": "unavailable",
		"v1": "available",
		"v2": "unavailable",
	}})

@app.route('/api/v1/')
# ‘/v1 URL is bound with v1() function.
def v1():
	return jsonify({"status": 200, "message": "Happy Hacking"})

@app.route("/api/v1/check_session", methods=["POST"])
# ‘/v1/check_session URL is bound with v1_check_session() function.
def v1_check_session():
	if request.form['token'] != None or request.form['token'] != "":
		if (validate_token(request.form['token'])):
			return jsonify({"status": 200, "message": "Valid Token"})
		else:
			return jsonify({"status": 401, "message": "Not Valid Token", "error": "Not Valid Token"})
	else:
		return jsonify({"status": 401, "message": "토큰 값을 찾을 수 없습니다.", "error": "토큰 값을 찾을 수 없습니다."})


@app.route("/api/v1/signin", methods=["POST"])
# ‘/v1/signin URL is bound with v1_signin() function.
def v1_signin():
	if not request.form['id'] == None or request.form['password'] == None:
		if not request.form['id'] == "" or request.form['password'] == "":
			try:
				conn = pymysql.connect(host='192.168.0.6', user='root', password='1234', db='skyle', charset='utf8') 
				cursor = conn.cursor(pymysql.cursors.DictCursor) 
				sql = "SELECT * from Users WHERE id=%s;"

				cursor.execute(sql, request.form['id'])

				rows = cursor.fetchall()

				if rows != ():
					for rows in rows:
						if check_password_hash(rows.get("password"), request.form['password']):
							return jsonify({"status": 200, "message": "로그인에 성공했습니다.", "token": create_token(request.form['id'], request.form['password'])})
						else:
							return jsonify({"status": 401, "message": "아이디 혹은 비밀번호가 틀립니다.", "error": "아이디 혹은 비밀번호가 틀립니다."})
				else:
					return jsonify({"status": 401, "message": "아이디 혹은 비밀번호가 틀립니다.", "error": "아이디 혹은 비밀번호가 틀립니다."})

				conn.close()
						
			except pymysql.err.OperationalError as error: 
				return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
			except Exception as error: 
				return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
		else:
			return jsonify({"status": 401, "message": "아이디 혹은 비밀번호가 틀립니다.", "error": "아이디 혹은 비밀번호가 틀립니다."})
	else:
		return jsonify({"status": 401, "message": "아이디 혹은 비밀번호가 틀립니다.", "error": "아이디 혹은 비밀번호가 틀립니다."})


@app.route("/api/v1/child_signin", methods=["POST"])
# ‘/v1/child_signin URL is bound with v1_child_signin() function.
def v1_child_signin():
	if not request.form['id'] == None or request.form['password'] == None:
		if not request.form['id'] == "" or request.form['password'] == "":
			try:
				conn = pymysql.connect(host='192.168.0.6', user='root', password='1234', db='skyle', charset='utf8') 
				cursor = conn.cursor(pymysql.cursors.DictCursor) 
				sql = "SELECT * from Child WHERE id=%s;"

				cursor.execute(sql, request.form['id'])

				rows = cursor.fetchall()

				if rows != ():
					for rows in rows:
						id = rows.get('parent')
						conn = pymysql.connect(host='192.168.0.6', user='root', password='1234', db='skyle', charset='utf8') 
						cursor = conn.cursor(pymysql.cursors.DictCursor) 
						sql = "SELECT * from Users WHERE id=%s;"

						cursor.execute(sql, id)

						rows = cursor.fetchall()
						
						for rows in rows:
							if check_password_hash(rows.get("password"), request.form['password']):
								return jsonify({"status": 200, "message": "로그인에 성공했습니다.", "token": create_token(request.form['id'], request.form['password'])})
							else:
								return jsonify({"status": 401, "message": "아이디 혹은 비밀번호가 틀립니다.", "error": "아이디 혹은 비밀번호가 틀립니다."})
				else:
					return jsonify({"status": 401, "message": "아이디 혹은 비밀번호가 틀립니다.", "error": "아이디 혹은 비밀번호가 틀립니다."})

				conn.close()
						
			except pymysql.err.OperationalError as error: 
				return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
			except Exception as error: 
				return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
		else:
			return jsonify({"status": 401, "message": "아이디 혹은 비밀번호가 틀립니다.", "error": "아이디 혹은 비밀번호가 틀립니다."})
	else:
		return jsonify({"status": 401, "message": "아이디 혹은 비밀번호가 틀립니다.", "error": "아이디 혹은 비밀번호가 틀립니다."})

@app.route("/api/v1/get_boho", methods=["POST"])
# ‘/v1/get_boho URL is bound with v1_get_boho() function.
def get_boho():
	if request.form['token'] != None or request.form['token'] != "":
		if (validate_token(request.form['token'])):
			try:
				conn = pymysql.connect(host='192.168.0.6', user='root', password='1234', db='skyle', charset='utf8') 
				cursor = conn.cursor(pymysql.cursors.DictCursor) 
				sql = "SELECT id, email, birth, name, phone from Users WHERE id=%s;"

				cursor.execute(sql, decode_token(request.form['token']).get('id'))

				rows = cursor.fetchall()

				if rows != ():
					conn.close()
					for rows in rows:
						return jsonify({"status": 200, "rows": rows})
				else:
					conn.close()
					return jsonify({"status": 404, "message": "보호자 로그인 세션이 잘못되어 보호 대상자 조회에 실패했습니다.", "error": "보호자 로그인 세션이 잘못되어 보호 대상자 조회에 실패했습니다."})
						
			except pymysql.err.OperationalError as error: 
				return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
			except Exception as error: 
				return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
		else:
			return jsonify({"status": 401, "message": "보호자 로그인 세션이 만료되어 보호 대상자 조회에 실패했습니다.", "error": "보호자 로그인 세션이 만료되어 보호 대상자 조회에 실패했습니다."})
	else:
		return jsonify({"status": 401, "message": "보호자 로그인 세션이 잘못되어 보호 대상자 조회에 실패했습니다.", "error": "보호자 로그인 세션이 잘못되어 보호 대상자 조회에 실패했습니다."})


@app.route("/api/v1/get_child", methods=["POST"])
# ‘/v1/get_child URL is bound with v1_get_child() function.
def v1_get_child():
	if request.form['token'] != None or request.form['token'] != "":
		if (validate_token(request.form['token'])):
			try:
				conn = pymysql.connect(host='192.168.0.6', user='root', password='1234', db='skyle', charset='utf8') 
				cursor = conn.cursor(pymysql.cursors.DictCursor) 
				sql = "SELECT * from Child WHERE parent=%s;"

				cursor.execute(sql, decode_token(request.form['token']).get('id'))

				rows = cursor.fetchall()

				if rows != ():
					conn.close()
					return jsonify({"status": 200, "rows": rows})
				else:
					conn.close()
					return jsonify({"status": 404, "message": "보호 대상자 정보가 없습니다.", "error": "보호 대상자 정보가 없습니다."})
						
			except pymysql.err.OperationalError as error: 
				return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
			except Exception as error: 
				return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
		else:
			return jsonify({"status": 401, "message": "보호자 로그인 세션이 만료되어 보호 대상자 조회에 실패했습니다.", "error": "보호자 로그인 세션이 만료되어 보호 대상자 조회에 실패했습니다."})
	else:
		return jsonify({"status": 401, "message": "보호자 로그인 세션이 잘못되어 보호 대상자 조회에 실패했습니다.", "error": "보호자 로그인 세션이 잘못되어 보호 대상자 조회에 실패했습니다."})

@app.route('/api/v1/load_maps')
# ‘/v1/load_maps URL is bound with v1_load_maps() function.
def v1_load_maps():
	try:
		conn = pymysql.connect(host='192.168.0.6', user='root', password='1234', db='skyle', charset='utf8') 
		cursor = conn.cursor(pymysql.cursors.DictCursor) 
		sql = "SELECT * from Child WHERE id=%s;" 

		cursor.execute(sql, request.args.get('id'))

		rows = cursor.fetchall()

		if rows != ():
			try:
				sql = "SELECT * from Map WHERE userid=%s;" 

				cursor.execute(sql, request.args.get('id'))

				rows = cursor.fetchall()
				
			except pymysql.err.OperationalError as error: 
				return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
			except werkzeug.exceptions.BadRequestKeyError as error: 
				return render_template("error_id.html"), 500
			except Exception as error: 
				return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
		else:
				return render_template("error_notuser.html")
		
	except pymysql.err.OperationalError as error: 
		return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
	except werkzeug.exceptions.BadRequestKeyError as error: 
		return render_template("error_id.html"), 400
	except Exception as error: 
		return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
	else:
		if rows == (): 
			return render_template("error_notdata.html")
		return render_template("load_maps.html", len=len, rows=rows)
	finally:
		conn.close()

@app.route('/api/v1/add_maps', methods=["POST"])
def v1_add_maps():
		try:
			conn = pymysql.connect(host='192.168.0.6', user='root', password='1234', db='skyle', charset='utf8') 
			cursor = conn.cursor(pymysql.cursors.DictCursor) 
			sql = "SELECT * from Child WHERE id=%s;" 

			cursor.execute(sql, decode_token(request.form['token']).get('id'))

			rows = cursor.fetchall()

			if rows != ():
				try:
					now = datetime.datetime.now()
					sql = f"INSERT INTO Map (userid, latitude, longitude, time) VALUES (%s, %s, %s, %s)" 

					cursor.execute(sql, (decode_token(request.form['token']).get('id'), request.form['latitude'], request.form['longitude'], datetime.datetime(now.year,now.month,now.day,now.hour,now.minute,now.second))) 

					conn.commit() 
					
				except pymysql.err.OperationalError as error: 
					conn.close() 
					return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
				except Exception as error: 
					conn.close() 
					return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
				else:
					conn.close() 
					return jsonify({"status": 200, "message": "성공적으로 현재 위치 정보를 입력했습니다."})
			else:
				conn.close() 
				return jsonify({"status": 400, "message": "해당 유저가 DB에 없어 API 접근이 차단되었습니다."}), 400

		except pymysql.err.OperationalError as error: 
			conn.close() 
			return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
		except werkzeug.exceptions.BadRequestKeyError as error:
			conn.close() 
			return jsonify({"status": 400, "message": "DB에 입력할 값이 입력되지 않아 API 접근이 차단되었습니다.", "error": f"{error}"}), 400

@app.route('/api/v1/add_user', methods=["POST"])
def v1_add_user():
		try:
			conn = pymysql.connect(host='192.168.0.6', user='root', password='1234', db='skyle', charset='utf8') 
			cursor = conn.cursor(pymysql.cursors.DictCursor) 
			sql = "SELECT * from Users WHERE id=%s;" 

			cursor.execute(sql, decode_token(request.form['token']).get('id'))

			rows = cursor.fetchall()

			if rows != ():
				try:
					sql = "INSERT INTO Child (id, name, birth, phone, parent) VALUES (%s, %s, %s, %s, %s)" 

					cursor.execute(sql,(request.form['id'], request.form['name'], request.form['birth'], request.form['phone'], decode_token(request.form['token']).get('id'))) 

					conn.commit() 
					conn.close() 
				except pymysql.err.OperationalError as error: 
					return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
				except werkzeug.exceptions.BadRequestKeyError as error:
					return jsonify({"status": 400, "message": "보호 대상자 추가에 필요한 값이 입력되지 않아 회원가입에 실패했습니다.", "error": f"{error}"})
				except Exception as error: 
					erstr = f"{error}"
					if erstr.find('Duplicate entry') != -1:
						return jsonify({"status": 500, "message": "이미 해당 아이디로 가입된 유저가 있습니다.", "error": f"{error}"})
					else:
						return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
				else:
					return jsonify({"status": 200, "message": "성공적으로 유저 정보를 입력했습니다."})
			else:
				conn.close() 
				return jsonify({"status": 401, "message": "보호자 로그인 세션이 만료되어 회원가입에 실패했습니다."}),
		except pymysql.err.OperationalError as error: 
			conn.close() 
			return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
		except werkzeug.exceptions.BadRequestKeyError as error:
			conn.close() 
			return jsonify({"status": 400, "message": "보호 대상자 추가에 필요한 값이 입력되지 않아 회원가입에 실패했습니다.", "error": f"{error}"})
			

@app.route('/api/v1/signup', methods=["POST"])
def v1_signup():
		try:
			conn = pymysql.connect(host='192.168.0.6', user='root', password='1234', db='skyle', charset='utf8') 
			cursor = conn.cursor() 
			sql = "INSERT INTO Users (id, name, birth, email, phone, password) VALUES (%s, %s, %s, %s, %s, %s)"

			cursor.execute(sql,(request.form['id'], request.form['name'], request.form['birth'], request.form['email'], request.form['phone'], generate_password_hash(request.form['password']))) 

			conn.commit() 
			conn.close() 
		except pymysql.err.OperationalError as error: 
			return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
		except werkzeug.exceptions.BadRequestKeyError as error:
			return jsonify({"status": 400, "message": "회원 가입에 필요한 값이 입력되지 않아 회원가입에 실패했습니다.", "error": f"{error}"})
		except Exception as error: 
			erstr = f"{error}"
			if erstr.find('Duplicate entry') != -1:
				return jsonify({"status": 500, "message": "이미 해당 아이디로 가입된 유저가 있습니다.", "error": f"{error}"})
			else:
				return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
		else:
			return jsonify({"status": 200, "message": "성공적으로 유저 정보를 입력했습니다."})
			

@app.route('/api/v1/edit_boho', methods=["POST"])
def v1_edit_boho():
		try:
			conn = pymysql.connect(host='192.168.0.6', user='root', password='1234', db='skyle', charset='utf8') 
			cursor = conn.cursor() 
			sql = "UPDATE Users SET name=%s, email=%s, phone=%s, password=%s WHERE id=%s;"

			cursor.execute(sql,(request.form['name'], request.form['email'], request.form['phone'], generate_password_hash(request.form['password']), decode_token(request.form['token']).get('id'))) 

			conn.commit() 
			conn.close() 
		except pymysql.err.OperationalError as error: 
			return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
		except werkzeug.exceptions.BadRequestKeyError as error:
			return jsonify({"status": 400, "message": "회원 정보 수정에 필요한 값이 입력되지 않아 회원 정보 수정에 실패했습니다.", "error": f"{error}"})
		except Exception as error: 
			return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
		else:
			return jsonify({"status": 200, "message": "성공적으로 보호자 정보를 수정했습니다. 변경 사항을 저장하기 위해 재로그인 해주세요."})

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({"status": 404, "message": "요청하신 URL에 페이지가 존재하지 않습니다.", "error": f"{error}"}), 404

@app.errorhandler(405)
def method_error(error):
    return jsonify({"status": 405, "message": "요청한 URL에는 메서드가 허용되지 않습니다.", "error": f"{error}"}), 405

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"status": 500, "message": "서버에서 요청을 수행하지 못했습니다.", "error": f"{error}"}), 500

# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application
	# on the local development server.
	app.run(host="0.0.0.0", port=4000, debug=True, load_dotenv=True)
# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import *
import werkzeug
import pymysql
import datetime

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

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

@app.route('/api/v1/load_maps')
# ‘/v1/load_maps URL is bound with v1_load_maps() function.
def v1_load_maps():
		if not request.args.get('id') == None:
			if not request.args.get('id') == "":
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
						except Exception as error: 
							return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
					else:
							return render_template("error_notuser.html"), 400
					
				except pymysql.err.OperationalError as error: 
					return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
				except Exception as error: 
					return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
				else:
					if rows == (): 
						return render_template("error_notdata.html")
					return render_template("load_maps.html", len=len, rows=rows)
				finally:
					conn.close()
			else:
				return render_template("error_id.html")
		else:
			return render_template("error_id.html")

@app.route('/api/v1/add_maps', methods=["POST"])
def v1_add_maps():
		try:
			conn = pymysql.connect(host='192.168.0.6', user='root', password='1234', db='skyle', charset='utf8') 
			cursor = conn.cursor(pymysql.cursors.DictCursor) 
			sql = "SELECT * from Child WHERE id=%s;" 

			cursor.execute(sql, request.form['id'])

			rows = cursor.fetchall()

			if rows != ():
				try:
					now = datetime.datetime.now()
					sql = f"INSERT INTO Map (userid, latitude, longitude, time) VALUES (%s, %s, %s, %s)" 

					cursor.execute(sql, (request.form['id'], request.form['latitude'], request.form['longitude'], datetime.datetime(now.year,now.month,now.day,now.hour,now.minute,now.second))) 

					conn.commit() 
					conn.close() 
					
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

			cursor.execute(sql, request.form['parent'])

			rows = cursor.fetchall()

			if rows != ():
				try:
					sql = "INSERT INTO Child (id, name, birth, phone, parent) VALUES (%s, %s, %s, %s, %s)" 

					cursor.execute(sql,(request.form['id'], request.form['name'], request.form['birth'], request.form['phone'], request.form['parent'])) 

					conn.commit() 
					conn.close() 
				except pymysql.err.OperationalError as error: 
					return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
				except werkzeug.exceptions.BadRequestKeyError as error:
					return jsonify({"status": 400, "message": "DB에 입력할 값이 입력되지 않아 API 접근이 차단되었습니다.", "error": f"{error}"}), 400
				except Exception as error: 
					erstr = f"{error}"
					if erstr.find('Duplicate entry') != -1:
						return jsonify({"status": 500, "message": "이미 해당 아이디로 가입된 유저가 있습니다.", "error": f"{error}"}), 500
					else:
						return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
				else:
					return jsonify({"status": 200, "message": "성공적으로 유저 정보를 입력했습니다."})
			else:
				conn.close() 
				return jsonify({"status": 400, "message": "해당 보호자가 DB에 없어 API 접근이 차단되었습니다."}), 400
		except pymysql.err.OperationalError as error: 
			conn.close() 
			return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
		except werkzeug.exceptions.BadRequestKeyError as error:
			conn.close() 
			return jsonify({"status": 400, "message": "DB에 입력할 값이 입력되지 않아 API 접근이 차단되었습니다.", "error": f"{error}"}), 400
			

@app.route('/api/v1/signup', methods=["POST"])
def v1_signup():
		try:
			conn = pymysql.connect(host='192.168.0.6', user='root', password='1234', db='skyle', charset='utf8') 
			cursor = conn.cursor() 
			sql = "INSERT INTO Users (id, name, birth, email, phone, password) VALUES (%s, %s, %s, %s, %s, %s)" 

			cursor.execute(sql,(request.form['id'], request.form['name'], request.form['birth'], request.form['email'], request.form['phone'], request.form['password'])) 

			conn.commit() 
			conn.close() 
		except pymysql.err.OperationalError as error: 
			return jsonify({"status": 500, "message": "DB에 연결하지 못했습니다.", "error": f"{error}"}), 500
		except werkzeug.exceptions.BadRequestKeyError as error:
			return jsonify({"status": 400, "message": "DB에 입력할 값이 입력되지 않아 API 접근이 차단되었습니다.", "error": f"{error}"}), 400
		except Exception as error: 
			erstr = f"{error}"
			if erstr.find('Duplicate entry') != -1:
				return jsonify({"status": 500, "message": "이미 해당 아이디로 가입된 유저가 있습니다.", "error": f"{error}"}), 500
			else:
				return jsonify({"status": 500, "message": "DB에 쿼리를 실행하지 못했습니다.", "error": f"{error}"}), 500
		else:
			return jsonify({"status": 200, "message": "성공적으로 유저 정보를 입력했습니다."})

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
try:
	# from cinemawebapp import app, db, models
	import unittest
	import os
	import sys
	from flask import Flask
	from flask_sqlalchemy import SQLAlchemy
	from run import *

except Exception as e:
	print("Some modules are Missing {} ".format(e))

class TestCase(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
	    pass

	# Check for response 200
	def test_popular(self):
		tester = app.test_client(self)
		response = tester.get("/popular")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)

	def test_foryou(self):
		tester = app.test_client(self)
		response = tester.get("/foryou")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)

	def test_admin(self):
		tester = app.test_client(self)
		response = tester.get("/admin")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)

	def test_about(self):
		tester = app.test_client(self)
		response = tester.get("/about")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)

	def test_login(self):
		tester = app.test_client(self)
		response = tester.get("/login")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)

	def test_register(self):
		tester = app.test_client(self)
		response = tester.get("/register")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)

	def test_search(self):
		tester = app.test_client(self)
		response = tester.get("/search")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)


if __name__ == '__main__':
	unittest.main()

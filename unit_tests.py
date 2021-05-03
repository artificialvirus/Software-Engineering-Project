try:
	# from cinemawebapp import app, db, models
	import unittest
	import os
	import sys
	from flask import Flask
	from flask_sqlalchemy import SQLAlchemy
	from flask_login import  login_user, logout_user, login_required, current_user

	from cinemawebapp import *
	from run import *
	from cinemawebapp.models import User
	from cinemawebapp.routes import *

except Exception as e:
	print("Some modules are Missing {} ".format(e))

class TestCase(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
	    pass

	# PAGE RESPONSE TESTS
	def test_popular(self):
		tester = app.test_client(self)
		response = tester.get("/popular")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)
	def test_landing_aliases(self):
		tester = app.test_client(self)
		response = tester.get("/")
		statuscode = response.status_code
		self.assertEqual(statuscode, 302)
	def test_foryou(self):
		tester = app.test_client(self)
		response = tester.get("/foryou")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)
	def test_admin(self):
		tester = app.test_client(self)
		response = tester.get("/admin")
		statuscode = response.status_code
		self.assertEqual(statuscode, 308)
	@unittest.skip("skipped about page response")
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
		response = tester.get("/signup")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)
	def test_search(self):
		tester = app.test_client(self)
		response = tester.get("/search")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)
	def test_movie(self):
		tester = app.test_client(self)
		response = tester.get("/movie/1")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)
	def test_ticket(self):
		tester = app.test_client(self)
		response = tester.get("/ticket/1")
		statuscode = response.status_code
		self.assertEqual(statuscode, 302)
	@unittest.skip("skipped about page response")
	def test_ticket_email(self):
		tester = app.test_client(self)
		response = tester.get("/ticket/email/1")
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)
	def test_ticket_download(self):
		tester = app.test_client(self)
		response = tester.get("/ticket/download/1")
		statuscode = response.status_code
		self.assertEqual(statuscode, 302)

	# USER REGISTRATION FORM TEST
	def test_user_registration(self):
		tester = app.test_client(self)
		response = tester.get("/signup", data=dict(
			username='user', email='email@email.com', password='password', repeatPassword='password'),
		follow_redirects=True)
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)
		self.assertIn(b'Login', response.data)
	# USER REGISTRATION FORM FAIL (Validation) TEST
	def test_user_registration(self):
		tester = app.test_client(self)
		response = tester.get("/signup", data=dict(
			username='user', email='email@email.com', password='password', repeatPassword='notpass'),
		follow_redirects=True)
		statuscode = response.status_code
		self.assertEqual(statuscode, 200)
		self.assertIn(b'Register', response.data)
	
	# POPULAR PAGE CONTENT TEST
	def test_popular_page_data(self):		
		tester = app.test_client(self)
		response = tester.get("/popular", follow_redirects=True)
		self.assertIn(b'Trending', response.data)

	# LOGIN INCORRECT TEST
	def test_failed_login(self):
		tester = app.test_client(self)
		response = tester.post("/login", data=dict(username="123", password="123"), follow_redirects=True)
		self.assertIn(b'login', response.data)
	# LOGIN CORRECT TEST
	@unittest.skip("skipped login check")
	def test_correct_login(self):
		with app.test_client(self):
			tester = app.test_client(self)
			response = tester.post("/login", data=dict(username="123", password="123",signin="", LoginForm=""), follow_redirects=True)
			# self.assertTrue(current_user.is_authenticated)
			self.assertIn(b'New releases', response.data)


	# LOGIN REQUIRED TESTS
	@unittest.skip("skipped admin login")
	def test_admin_requires_login(self):
		tester = app.test_client(self)
		response = tester.get("/admin", follow_redirects=True)
		self.assertIn(b'login', response.data)
	def test_member_requires_login(self):
		tester = app.test_client(self)
		response = tester.get("/member", follow_redirects=True)
		self.assertIn(b'Login', response.data)
	def test_logout_requires_login(self):
		tester = app.test_client(self)
		response = tester.get("/logout", follow_redirects=True)
		self.assertIn(b'Login', response.data)
	def test_payment_requires_login(self):
		tester = app.test_client(self)
		response = tester.get("/payment", follow_redirects=True)
		self.assertIn(b'Login', response.data)
	def test_booking_requires_login(self):
		tester = app.test_client(self)
		response = tester.get("/booking", follow_redirects=True)
		self.assertIn(b'Login', response.data)
	def test_ticket_requires_login(self):
		tester = app.test_client(self)
		response = tester.get("/ticket", follow_redirects=True)
		self.assertIn(b'Login', response.data)
	def test_sales_requires_login(self):
		tester = app.test_client(self)
		response = tester.get("/sales", follow_redirects=True)
		self.assertIn(b'Login', response.data)
	def test_week_takings_requires_login(self):
		tester = app.test_client(self)
		response = tester.get("/takingperweek", follow_redirects=True)
		self.assertIn(b'Login', response.data)
	def test_movie_takings_requires_login(self):
		tester = app.test_client(self)
		response = tester.get("/takingspermovie", follow_redirects=True)
		self.assertIn(b'Login', response.data)
	def test_foryou_page_requires_login(self):
		tester = app.test_client(self)
		response = tester.get("/foryou", follow_redirects=True)
		self.assertIn(b'Login', response.data)


	# SEARCH FUNCTIONALITY
	@unittest.skip("skipped search incomplete")
	def test_movie_search(self):
		tester = app.test_client(self)
		response = tester.post("/popular", data=dict(search='Funny'), follow_redirects=True)
		self.assertIn(b'Movie', response.data)


	# TEST MOVIE DATA VISIBLE ON HOME PAGE
	def test_movie_show_up_on_main_page(self):
		tester = app.test_client(self)
		response = tester.get("/popular", follow_redirects=True)
		self.assertIn(b'Movie', response.data)




if __name__ == '__main__':
	unittest.main()

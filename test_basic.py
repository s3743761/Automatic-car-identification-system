import os
import unittest
from django_webtest import WebTest
 
from app import app, db
 
TEST_DB = 'test.db'
 
class BasicTests(unittest.TestCase):
 
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        self.assertEqual(app.debug, False)
 
    # executed after each test
    def tearDown(self):
        pass
 
 
###############
#### tests ####
###############
 
    def test_login_page(self):
        """
        Loading the login page
        """
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_logout(self):
        """
        logout the account logged in
        """
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_adding_car(self):
        """
        admin able to add a car to the database
        """
        response = self.app.get('/add', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_adding_user(self):
        """
        admin able to add a user to the database
        """
        response = self.app.get('/addUser', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_editing_car(self):
        """
        admin able to edit a car
        """
        response = self.app.get(
                '/edit',
                data=dict(car_id="20"),
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)

    def test_editing_user(self):
        """
        admin able to edit a user
        """
        response = self.app.get(
                '/editUser',
                data=dict(username="prabhav"),
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        """
        admin able to delete a user
        """
        response = self.app.get(
                '/deleteUser',
                data=dict(username="prabhav"),
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)

    def test_delete_car(self):
        """
        admin able to delete a car
        """
        response = self.app.get(
                '/delete',
                data=dict(username="20"),
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        """
        Loading the registration page
        """
        response = self.app.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_all_car(self):
        """
        Loading the all cars page for admin
        """
        response = self.app.get('/all_car', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_all_reports(self):
        """
        Loading the all reports page for engineer
        """
        response = self.app.get('/allReports', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_bar_chart(self):
        """
        Loading the bar chart page for manager
        """
        response = self.app.get('/bar', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_line_chart(self):
        """
        Loading the line chart page for manager
        """
        response = self.app.get('/line', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
 
    def test_pie_chart(self):
        """
        Loading the pie chart page for manager
        """
        response = self.app.get('/pie', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_report_map(self):
        """
        Loading the reported cars in google map page for manager
        """
        response = self.app.get('/map', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
 
if __name__ == "__main__":
    unittest.main()

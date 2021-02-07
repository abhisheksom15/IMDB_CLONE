import unittest,json
from app import app
from random import randint
from base64 import b64encode


class FlaskTestCase(unittest.TestCase):
    #Checking whether server are running or not
    username=""
    password= "12345678"
    TOKEN=""
    def test_Server(self):
        tester=app.test_client(self)
        response=tester.get('API/',content_type='application/json')
        self.assertEqual(response.json["status"],"Server is running")
        self.assertEqual(response.status_code,200)

    #Checking whether sign-up API is working or not
    def test_signup(self):
        tester=app.test_client(self)
        self.username="user"+str(randint(0,100000))+"@gmail.com"
        payload = json.dumps({
            "username": self.username,
            "password": self.password,
            "name":"user one",
            "admin_key":app.config["ADMIN_KEY"]
        })
        response=tester.post('API/signup',content_type='application/json',data=payload)
        self.assertEqual("Sign-Up successful", response.json['message'])
        self.assertEqual(response.status_code,200)

    def test_signup_login(self):
        tester=app.test_client(self)
        self.username="user"+str(randint(100000,200000))+"@gmail.com"
        payload = json.dumps({
            "username": self.username,
            "password": self.password,
            "name":"user one",
            "admin_key":app.config["ADMIN_KEY"]
        })
        response=tester.post('API/signup',content_type='application/json',data=payload)
        self.assertEqual("Sign-Up successful", response.json['message'])
        self.assertEqual(response.status_code,200)
        response=tester.post('API/login',headers={"Content_Type":'application/json','Authorization': 'Basic ' + b64encode(("{0}:{1}".format(self.username, self.password)).encode("utf-8")).decode("utf-8")})
        self.assertEqual("Login successful!!!", response.json['message'])
        self.assertEqual(response.status_code,200)
        try:
            self.TOKEN=response.json['token']
        except:
            pass
        return self.TOKEN

    def test_load_Movies(self):
        tester=app.test_client(self)
        payload = json.dumps([
        {
            "99popularity": 66.0,
            "director": "Giovanni Pastrone",
            "genre": [
              "Adventure",
              " Drama",
              " War"
            ],
            "imdb_score": 6.6,
            "name": "Cabiria"
          },
          {
            "99popularity": 87.0,
            "director": "Alfred Hitchcock",
            "genre": [
              "Horror",
              " Mystery",
              " Thriller"
            ],
            "imdb_score": 8.7,
            "name": "Psycho"
          }
        ]
        )
        self.token=self.test_signup_login()
        response=tester.post('API/loadMovies',headers={"Content_Type":'application/json','x-access-token': self.token},data=payload)
        self.assertEqual("Cabiria added successful to Database # Psycho added successful to Database # ", response.json['result'])
        self.assertEqual(response.status_code,200)

    def test_get_Movies_by_id(self):
        tester=app.test_client(self)
        response=tester.get('API/Movie/5',headers={"Content_Type":'application/json'})
        self.assertEqual(str, type(response.json['movie']))
        self.assertEqual(response.status_code,200)
    def test_update_Movies_by_id(self):
        tester=app.test_client(self)
        self.token=self.test_signup_login()
        data={"99popularity": "83","director":"Abhishek"}
        payload = json.dumps(data)
        response=tester.post('API/updateMovie/5',headers={"Content_Type":'application/json','x-access-token': self.token}, data=payload)
        self.assertEqual(str, type(response.json['message']))
        self.assertEqual(response.status_code,200)
    def test_delete_Movies_by_id(self):
        tester=app.test_client(self)
        self.token=self.test_signup_login()
        response=tester.delete('API/Movie/10',headers={"Content_Type":'application/json','x-access-token': self.token})
        self.assertEqual(str, type(response.json['message']))
        self.assertEqual(response.status_code,200)
    def test_search_Movies(self):
        tester=app.test_client(self)
        self.token=self.test_signup_login()
        response=tester.get('API/SearchMovie?query=Psycho',headers={"Content_Type":'application/json'})
        results=response.json
        movie_name=""
        for result in results:
            try:
                movie_name=result["movie"]
            except:
                pass
        self.assertEqual("Psycho", movie_name)
        self.assertEqual(response.status_code,200)
if __name__=='__main__':
    unittest.main()

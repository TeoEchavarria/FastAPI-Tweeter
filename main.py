# Python
import json
from uuid import UUID
from datetime import date
from datetime import datetime
from typing import Optional, List

# Pydantic
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

# FastAPI
from fastapi import FastAPI
from fastapi import status
from fastapi import Body, Form, Query , Path

app = FastAPI()

# ----------------------------------------
#                 Models
#-----------------------------------------

class UserBase(BaseModel):
    user_id: UUID = Field(...)
    email: EmailStr = Field(...)

class UserLogin(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=64
    )

class LoginOut(BaseModel): 
    id: EmailStr = Field(...)
    message: str = Field(default="Login Successfully!")

class User(UserBase):
    first_name: str = Field(
        ...,
        min_lenght=1,
        max_length=50
    )
    last_name: str = Field(
        ...,
        min_lenght=1,
        max_length=50
    )
    birth_date: Optional[date] = Field(default=None)

class UserRegister(User):
    password: str = Field(
        ...,
        min_length=8,
        max_length=64
    )

class Tweet(BaseModel):
    tweet_id: UUID = Field(...)
    content:str = Field(
        ...,
        min_length=1,
        max_length=256
    )
    created_at: datetime = Field(default=datetime.now())
    updated_at: Optional[datetime] = Field(default=None)
    by: User = Field(...)


# ----------------------------------------
#            Path Operations
#-----------------------------------------

## Users

### Register a user
@app.post(
    path="/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a User",
    tags=["Users"]
)
def signup(user: UserRegister = Body(...)):
    """
    Signup

    This path operations register a user in the app

    Parameters:
    - Request body parameter
        - user: UserRegister

    Return a json with the basic user information:
    - user_id: UUID
    - email: Emailstr
    - first_name: str
    - last_name: str
    - birth_date: datetime
    """
    with open("users.json", "r+", encoding="utf-8") as f: 
        results = json.loads(f.read())
        user_dict = user.dict()
        user_dict["user_id"] = str(user_dict["user_id"])
        user_dict["birth_date"] = str(user_dict["birth_date"])
        results.append(user_dict)
        f.seek(0)
        f.write(json.dumps(results))
        return user
    
### Login a user
@app.post(
    path="/login",
    response_model=LoginOut,
    status_code=status.HTTP_200_OK,
    summary="Login a User",
    tags=["Users"]
    )
def Login(email: EmailStr  = Form(...), password: str = Form(...)):
    """
    Login

    This path operation login a Person in the app

    Parameters:
    - Request body parameters:
        - email: EmailStr
        - password: str

    Returns a LoginOut model with username and message
    """
    with open("users.json", "r+", encoding="utf-8") as f: 
        data = json.loads(f.read())
        for user in data:
            if email == user['email'] and password == user['password']:
                return LoginOut(id=email)
        return LoginOut(id=email, message="Login Unsuccessfully!")

### Show all user
@app.get(
    path="/users",
    response_model=List[User],
    status_code=status.HTTP_200_OK,
    summary="Show all users",
    tags=["Users"]
)
def show_all_users():
    """
    This path operation shows all users in the app

    Parameters:
    -

    Returns a json list with all users in the app, with the following keys:
    - user_id: UUID
    - email: Emailstr
    - first_name: str
    - last_name: str
    - birth_date: datetime
    """
    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        return results

### Show a user

## Show a user by his ID
@app.get(
    path="/users/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="show a User by ID",
    tags=["Users"]
)
def show_a_user_id(
    user_id : Optional[UUID] = Path(
        None,
        title = "User ID",
        example = "3fa85f64-5717-4562-b3fc-2c966f66afa6"
    )):
    """
    Show a user by his id

    This path operation Show a User in the app.

    Parameters:
    - Request path parameter
        - user_id: UUID

    Returns a json with the basic user information:
    - user_id: UUID
    - email: Emailstr
    - first_name: str
    - last_name: str
    - birth_date: datetime
    """
    with open("users.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        for user in data:
            if user['user_id'] == str(user_id):
                return user

@app.get(
    path="/users/{first_or_last_name}/search",
    response_model=List[User],
    status_code=status.HTTP_200_OK,
    summary="show a User by his first name or his last name",
    tags=["Users"]
)
def show_a_user_name(
    first_name : Optional[str] = Query(
    None,
    min_length = 1, 
    max_length=50,
    title = "First Name User",
    example = "string"
    ), 
    last_name : Optional[str] = Query(
    None,
    min_length = 1, 
    max_length=50,
    title = "Last Name User",
    example = "string"
    )):
    """
    Show a user by first or last name

    This path operation show a User in the app

    Parameters:
    - Request Query parameters:
        - first_name: Optional[str]
        - last_name : Optional[str]

    Returns a List of all users that meet the search values
    """
    with open("users.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        users = []
        for user in data:
            if user['first_name'] == first_name or user['last_name'] == last_name:
                users.append(user)
        return users

### Delete a user
@app.delete(
    path="/users/{user_id}/delete",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Delete a User",
    tags=["Users"]
)
def delete_a_user(user_id : UUID = Path(...)):
    """
    Delete a User

    This path operation delete a user in the app

    Parameters:
        - user_id: UUID

    Returns a json with deleted user data:
        - user_id: UUID
        - email: Emailstr
        - first_name: str
        - last_name: str
        - birth_date: datetime
    """
    with open("users.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        for user in results:
            if str(user_id) == str(user["user_id"]):
                results.remove(user)
                with open("users.json", "w", encoding="utf-8") as f:
                    f.write(json.dumps(results))
                    return user

### Update a user
@app.put(
    path="/users/{user_id}/update",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Update a User",
    tags=["Users"]
)
def update_a_user(user_update : UserRegister = Body(...)):
    """
    Update User

    This path operation update a user information in the app and save in the database

    Parameters:
    - user_id: UUID
    - Request body parameter:
        - **user: User** -> A user model with user_id, email, first name, last name, birth date and password
    
    Returns a user model with user_id, email, first_name, last_name and birth_date
    """
    user_dict = user_update.dict()
    user_dict["user_id"] = str(user_dict["user_id"])
    user_dict["birth_date"] = str(user_dict["birth_date"])
    with open("users.json", "r+", encoding="utf-8") as f: 
        results = json.loads(f.read())
        for user in results:
            if user["user_id"] == user_dict["user_id"] and user["password"] == user_dict["password"]:
                if user_dict["first_name"] != "":
                    results[results.index(user)]["first_name"] = user_dict["first_name"]
                if user_dict["last_name"] != "":
                    results[results.index(user)]["last_name"] = user_dict["last_name"]
                if user_dict["email"] != "":
                    results[results.index(user)]["email"] = user_dict["email"]
                with open("users.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(results))
                return user

## Tweets

### Show all tweets
@app.get(
    path="/",
    response_model=List[Tweet],
    status_code=status.HTTP_200_OK,
    summary="Show all tweets",
    tags=["Tweets"]
)
def home():
    """
    This path operation shows all tweets in the app

    Parameters:
    -

    Returns a json list with all tweets in the app, with the following keys:
    - tweet_id: UUID
    - content:str
    - created_at: datetime
    - updated_at: Optional[datetime]
    - by: User
    """
    with open("tweets.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        return results

### Post a tweet
@app.post(
    path="/post",
    response_model=Tweet,
    status_code=status.HTTP_201_CREATED,
    summary="Post a tweet",
    tags=["Tweets"]
)
def post(tweet: Tweet = Body(...)):
    """
    Post a Tweet

    This path operations post a tweet in the app

    Parameters:
    - Request body parameter
        - tweet: Tweet

    Return a json with the basic tweet information:
    - tweet_id: UUID
    - content:str
    - created_at: datetime
    - updated_at: Optional[datetime]
    - by: User
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        tweet_dict = tweet.dict()
        tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
        tweet_dict["created_at"] = str(tweet_dict["created_at"])
        if tweet_dict["updated_at"] is not None:
            tweet_dict["updated_at"] = str(tweet_dict["updated_at"])
        tweet_dict["by"]["user_id"] = str(tweet_dict["by"]["user_id"])
        tweet_dict["by"]["birth_date"] = str(tweet_dict["by"]["birth_date"])
        results.append(tweet_dict)
        f.seek(0)
        f.write(json.dumps(results))
        return tweet

### Show a tweet
@app.get(
    path="/tweets/{tweet_id}",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Show a tweet",
    tags=["Tweets"]
)
def show_a_tweet(
    tweet_id : Optional[UUID] = Path(
        None,
        title = "User ID",
        example = "3fa85f64-5717-4562-b3fc-2c966f66afa6"
    )):
    """
    Show a tweet by his id

    This path operation Show a tweet in the app.

    Parameters:
    - Request path parameter
        - tweet_id: UUID

    Returns a json with the basic user information:
    - tweet_id: UUID
    - email: Emailstr
    - first_name: str
    - last_name: str
    - birth_date: datetime
    """

    with open("tweets.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        for tweet in data:
            if tweet['tweet_id'] == str(tweet_id):
                return tweet

### Delete a tweet
### Delete a tweet
@app.delete(
    path="/tweets/{tweet_id}/delete",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Delete a tweet",
    tags=["Tweets"]
)
### Delete a tweet
@app.delete(
    path="/tweets/{tweet_id}/delete",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Delete a tweet",
    tags=["Tweets"]
)
def delete_a_tweet(tweet_id : UUID = Path(...)):
    """
    Delete a Tweet

    This path operation delete a Tweet in the app

    Parameters:
        - tweet_id: UUID

    Returns a json with deleted tweet data:
        - tweet_id: UUID
        - email: Emailstr
        - first_name: str
        - last_name: str
        - birth_date: datetime
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        for tweet in results:
            if str(tweet_id) == str(tweet["tweet_id"]):
                results.remove(tweet)
                with open("tweets.json", "w", encoding="utf-8") as f:
                    f.write(json.dumps(results))
                    return tweet

### Update a tweet
@app.put(
    path="/tweets/{tweet_id}/update",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Update a tweet",
    tags=["Tweets"]
)
def update_a_tweet(tweet_update : Tweet = Body(...)):
    """
    Update User

    This path operation update a user information in the app and save in the database

    Parameters:
    - user_id: UUID
    - Request body parameter:
        - **user: User** -> A user model with user_id, email, first name, last name, birth date and password
    
    Returns a user model with user_id, email, first_name, last_name and birth_date
    """
    tweet_dict = tweet_update.dict()
    tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
    with open("tweets.json", "r+", encoding="utf-8") as f: 
        results = json.loads(f.read())
        for tweet in results:
            if tweet["tweet_id"] == tweet_dict["tweet_id"]:
                if tweet_dict["content"] != "":
                    results[results.index(tweet)]["content"] = tweet_dict["content"]
                with open("tweets.json", "w", encoding="utf-8") as f:
                    f.seek(0)
                    f.write(json.dumps(results))
                return tweet

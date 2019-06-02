from flask import Flask, render_template, request, redirect
from random import choice
from keys import KEY1, KEY2
from wtforms import Form, validators, StringField, IntegerField
"""
Twitter Deepfake --> Use it wisely
"""


def generate_model(text, order):
    model = {}
    for i in range(0, len(text) - order):
        fragment = text[i:i+order]
        next_letter = text[i+order]
        if fragment not in model:
            model[fragment] = {}
        if next_letter not in model[fragment]:
            model[fragment][next_letter] = 1
        else:
            model[fragment][next_letter] += 1
    return model

def get_next_character(model, fragment):
    letters = []
    for letter in model[fragment].keys():
        for times in range(0, model[fragment][letter]):
            letters.append(letter)
    return choice(letters)


def generate_text(text, order, length):
    text = text.replace("\n", "")
    model = generate_model(text, order)
    currentFragment = text[0:order]
    output = ""
    for i in range(0, length-order):
        newCharacter = get_next_character(model, currentFragment)
        output += newCharacter
        currentFragment = currentFragment[1:] + newCharacter
    return output

class ComputeForm(Form):
    username = StringField('', [validators.Length(min=0, max=1000)], render_kw={'class':'form-control', 'placeholder':'Username'})
    length = IntegerField('', [validators.DataRequired(), validators.NumberRange(min=0, max=280)], render_kw={'class':'form-control', 'placeholder':'Length'})
    order = IntegerField('', [validators.DataRequired(), validators.NumberRange(min=0, max=20)], render_kw={'class':'form-control', 'placeholder':'Order'})

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def home():
    form = ComputeForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect("/generate/{}?length={}&order={}".format(form.username.data, form.length.data, form.order.data))
    else:
        markov_text = generate_text("""
        Yeah. It’s pretty interesting what my most ... What people are most interested in, like some little tweet about “I love anime.” That was it. But it was lowercase “i”, black heart, “anime,” and people loved that. That was like one of my most popular tweets.
        """, 4, 140)
        return render_template("index.html", text=markov_text, form=form)

@app.route('/generate/<username>/', methods=['GET'])
def generate_response(username):
    form = ComputeForm(request.form)
    length = int(request.args.get("length"))
    order = int(request.args.get("order"))
    import tweepy
    auth = tweepy.OAuthHandler(*KEY1)
    auth.set_access_token(*KEY2)
    api = tweepy.API(auth)
    user = api.get_user(username)
    tweets=""
    for tweet in api.user_timeline(screen_name=username, count=100, include_rts=False, tweet_mode="extended"):
        if not tweet.retweeted:
            tweets += tweet.full_text + " "
    generated = generate_text(tweets, order, length)
    print(generated)
    return render_template("fake_tweet.html", username=username, name=user.name, picture=user.profile_image_url, body=generated, verified = user.verified, form=form)


if __name__ == '__main__':
    app.run()

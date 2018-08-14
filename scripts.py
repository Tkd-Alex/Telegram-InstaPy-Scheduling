import random, time, traceback, instapy

def awesome(username, password):
    try:
        session = instapy.InstaPy(username=username, password=password)
        session.login()
        session.end()
    except:
        print(traceback.format_exc())

def biglikers(username, password):
    try:
        session = instapy.InstaPy(username=username, password=password)
        session.login()
        session.end()
    except:
        print(traceback.format_exc())

functions = [f for fname, f in sorted(globals().items()) if callable(f)]
scripts = {}
for function in functions:
    scripts[str(function.__name__).lower()] = function
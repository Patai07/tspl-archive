import urllib.request
response = urllib.request.urlopen("http://localhost:5556")
html = response.read().decode('utf-8')

import js2py
# We can't easily parse dom, but we can check if there's an obvious syntax error

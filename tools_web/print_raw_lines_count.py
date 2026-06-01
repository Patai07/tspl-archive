import urllib.request

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQUvalU42uqVFSoJ3O-WkoaQCBVmiawl7DHNO-DNsYL3iiWfxKERjiQI4SpiVqDxzEYLPlLFJTqSFCy/pub?gid=494156669&single=true&output=csv"
response = urllib.request.urlopen(url)
content = response.read().decode('utf-8')
lines = content.splitlines()
print(f"Total lines fetched via urllib: {len(lines)}")

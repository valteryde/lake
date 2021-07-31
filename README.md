# lake

To get started create a main.py file

main.py
```python
from lake import *
from flask import *

app = Lake()
remote = app.remote


@app.route('/app')
def appView():
    return render_template('index.html')


@remote.function
def aFunctionThatCanBeExecutedFromTheBrowser():
    print('Hejsa fra browseren')

if __name__ == '__main__':
    app.run()

```

# Lake

Lake is a lightweight framework build around existing webtechnology.
An app is deplyed by flask and served in the users standard webbrowser.

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


# remote functions can take obj/dict, str, number/int and arrays
# as paramters sent from the browser/app
@remote.function
def aFunctionThatCanBeCalledByTheBrowser(*args):
    print('Hejsa fra browseren', *list(map(type, args)))

if __name__ == '__main__':
    app.run()

```

To make an landing page pass a function to the lake class.
```python
def landing():
    return render_template('index.html')

app = Lake(landing)
```


The important classes are the app and remote class.
The app servers only one function; serving the app to the user, while the
remote function handles the direct communcation between the "backend" and "frontend" of the
app.

The remote on the backend has a decorator used to target the exposed function which can be used in the browser.
To expose a function to the frontend use
```python
@remote.function
def myFunction():
    print('Hello world!')
```

And in the browser the functions is now accesiable throug the window.remote object's method "do".
```javascript
window.remote.do('myFunction')
```

Visa versa a function can be exposed to the backend:
```javascript
function myFunction() {
    console.log('Hello world')
}
expose(myFunction)
```

And access in python with
```python
remote.do('myFunction')
```

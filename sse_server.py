from flask import Flask, Response
from flask_cors import CORS
from datetime import datetime
import queue

app = Flask(__name__)
CORS(app, supports_credentials=True)

class MessageAnnouncer:

    def __init__(self):
        self.listeners = []

    def listen(self):
        self.listeners.append(queue.Queue(maxsize=5))
        return self.listeners[-1]

    def announce(self, msg):
        # We go in reverse order because we might have to delete an element, which will shift the
        # indices backward
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]


announcer = MessageAnnouncer()


def format_sse(data: str, event=None) -> str:
    """Formats a string and an event name in order to follow the event stream convention.
    >>> format_sse(data=json.dumps({'abc': 123}), event='Jackson 5')
    'event: Jackson 5\\ndata: {"abc": 123}\\n\\n'
    """
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg

@app.route('/ping')
def ping():
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    msg = format_sse(data='pong + {0}'.format(date_time), event='vijai')
    announcer.announce(msg=msg)
    return {}, 200

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/chatroom")
def chat_room():
    return "Dummy text"


@app.route('/listen', methods=['GET'])
def listen():

    def stream():
        messages = announcer.listen()  # returns a queue.Queue
        while True:
            msg = messages.get()  # blocks until a new message arrives
            yield msg

    return Response(stream(), mimetype='text/event-stream')


if __name__ == "__main__":
    app.run(threaded=True,debug=True)
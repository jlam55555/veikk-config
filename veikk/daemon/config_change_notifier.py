import os
from threading import Thread


class ConfigChangeNotifier:

    def __init__(self, pipe_path: str):
        self._pipe_path = pipe_path
        self._create_named_pipe()

    def _create_named_pipe(self):
        try:
            if os.path.exists(self._pipe_path):
                print(f'Warning: {self._pipe_path} pipe already exists; '
                      f'overwriting...')
                os.remove(self._pipe_path)

            os.mkfifo(self._pipe_path)
        except OSError as err:
            print(f'Failed to make fifo: {err.strerror}')
        else:
            pass
        self._pipe = open(self._pipe_path, 'r')

    def listen_thread(self):
        while True:
            line = self._pipe.read()

            print(f'Got {line}')

    def _cleanup(self):
        # TODO: when should this get called?
        self._pipe.close()
        os.remove(self._pipe_path)

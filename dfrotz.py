# abstraction layer for dfrotz
# parts for non-blocking communication are taken from
# https://gist.github.com/EyalAr/7915597

# this code is still somewhat shitty...

import os
import queue
import subprocess
import sys
import threading

class DFrotz():
    def __init__(self, arg_frotz_path, arg_game_path):
        self.frotz_path = arg_frotz_path
        self.game_path = arg_game_path
        #print(os.path.abspath(self.frotz_path))
        try:
            self.frotz = subprocess.Popen(
                [self.frotz_path, self.game_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,    
                bufsize=1        
            )
        except OSError:
            print('Couldn\'t run Frotz. Maybe wrong architecture?')
            sys.exit(0)
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.enqueue, args=(self.frotz.stdout, self.queue))
        self.thread.daemon = True
        self.thread.start()

    def enqueue(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def send(self, command):
        self.frotz.stdin.write(command.encode('utf-8'))
        try:
            self.frotz.stdin.flush()
        except BrokenPipeError:
            debug_string = '[DEV] Pipe is broken. Please tell @mrtnb what you did.'
            return debug_string

    def generate_output(self):
        self.raw_output = ''.join(self.lines)

        # clean up Frotz' output
        self.output = self.raw_output.replace('> > ', '')
        self.output = self.output.replace('\n.\n', '\n\n')

        return self.output


    def get(self):
        self.lines = []
        while True:
            try:
                try:
                    self.line = self.queue.get(timeout=0.5).decode('utf-8')
                except UnicodeDecodeError:
                    return 'Don\'t you dare to post special characters.'
                else:
                    self.line = '\n'.join(' '.join(line_.split()) for line_ in self.line.split('\n'))
            except queue.Empty:
                print('', end='')
                break
            else:
                #print(self.line)
                self.lines.append(self.line)

        return self.generate_output()

def main():
    f = DFrotz()

    while True:
        print(f.get())
        cmd = '%s\r\n' % input()
        f.send(cmd)

if __name__ == '__main__':
    main()
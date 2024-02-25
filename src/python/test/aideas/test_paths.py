import glob
import os

if __name__ == '__main__':
    d = '/Users/chinomso/dev_chinomso/automate-idea-to-social/src/python/test/aideas/action'
    print(f'Current directory: {d}')
    files = [f for f in glob.glob(f"{d}/*.py")]
    print(f'Files: {files}')
    files = [os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]
    print(f'Files: {files}')
